# main.py
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import db  
from models import (
    PromptRequest, IdeaResponse, SessionCreate, SessionResponse, 
    SessionWithMessages, Message, VectorSearchRequest, VectorSearchResult,
    UserStats
)
from agents import run_idea_agent_only, run_all_agents, run_single_agent_chat
from vector_utils import vector_search, prepare_vector_document

app = FastAPI(title="TeamSpark AI API", version="1.0.0")

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MongoDB
db.init_db(app)


@app.on_event("startup")
async def startup_event():
    """Test MongoDB connection on startup"""
    try:
        # Test the connection
        await db.db.command("ping")
        print("✓ Successfully connected to MongoDB!")
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        print("Note: The app will still start, but database operations will fail.")


@app.get("/debug-db")
async def debug_db():
    """
    Check if the db object is initialized correctly.
    """
    return {"db_is_none": db.db is None}


@app.get("/test-insert")
async def test_insert():
    """
    Insert a simple document into MongoDB to verify connection.
    """
    doc = {
        "message": "hello from FastAPI",
        "timestamp": datetime.now(timezone.utc),
    }
    result = await db.db.test.insert_one(doc)  # <--- use db.db here
    return {"inserted_id": str(result.inserted_id)}


@app.get("/api/stats", response_model=UserStats)
async def get_user_stats(user_email: str):
    """
    Get statistics for a specific user.
    """
    if not user_email:
        raise HTTPException(status_code=400, detail="User email is required")

    # 1. Get all session IDs for the user
    cursor = db.db.sessions.find({"user_email": user_email}, {"session_id": 1})
    user_sessions = await cursor.to_list(length=None)
    session_ids = [s["session_id"] for s in user_sessions]
    
    total_sessions = len(session_ids)
    
    if total_sessions == 0:
        return UserStats(
            total_sessions=0,
            ideas_generated=0,
            knowledge_chunks=0,
            active_agents=3
        )

    # 2. Count ideas generated (messages from 'idea' agent in user's sessions)
    ideas_count = await db.db.messages.count_documents({
        "session_id": {"$in": session_ids},
        "agent": "idea"
    })

    # 3. Count knowledge chunks
    chunks_count = await db.db.idea_chunks.count_documents({
        "session_id": {"$in": session_ids}
    })

    return UserStats(
        total_sessions=total_sessions,
        ideas_generated=ideas_count,
        knowledge_chunks=chunks_count,
        active_agents=3  # Currently fixed at 3 (Idea, Critic, Builder)
    )


# ==================== IDEA AGENT ENDPOINTS ====================

@app.post("/api/idea", response_model=IdeaResponse)
async def generate_idea(request: PromptRequest):
    """
    Generate ideas using the Idea Agent only.
    This endpoint takes a user prompt and returns creative ideas.
    Chunks the response and stores embeddings in MongoDB.
    """
    try:
        # Run the idea agent with chunking
        result = run_idea_agent_only(request.prompt, request.session_id)
        
        # Save to MongoDB if session_id is provided
        if request.session_id:
            # Save the main message
            message_doc = {
                "session_id": request.session_id,
                "agent": "idea",
                "content": result["response"],
                "user_prompt": request.prompt,
                "timestamp": datetime.now(timezone.utc)
            }
            msg_result = await db.db.messages.insert_one(message_doc)
            message_id = str(msg_result.inserted_id)
            
            # Save chunks with embeddings
            chunk_docs = []
            for chunk in result["chunks"]:
                chunk_doc = {
                    "message_id": message_id,
                    "session_id": request.session_id,
                    "agent": "idea",
                    "content": chunk["chunk_text"],
                    "embedding": chunk["embedding"],
                    "chunk_index": chunk["chunk_index"],
                    "user_prompt": request.prompt,
                    "timestamp": datetime.now(timezone.utc)
                }
                chunk_docs.append(chunk_doc)
            
            if chunk_docs:
                await db.db.idea_chunks.insert_many(chunk_docs)
            
            # Update session's updated_at timestamp
            await db.db.sessions.update_one(
                {"session_id": request.session_id},
                {"$set": {"updated_at": datetime.now(timezone.utc)}}
            )
        
        return IdeaResponse(
            agent=result["agent"],
            response=result["response"],
            user_prompt=result["user_prompt"],
            session_id=request.session_id,
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating ideas: {str(e)}")


@app.post("/api/brainstorm", response_model=dict)
async def full_brainstorm(request: PromptRequest):
    """
    Run all three agents (Idea, Critic, Builder) with feedback loop.
    The Critic can send ideas back to the Idea Agent for revision.
    Returns responses from all agents with chunking and embeddings.
    """
    try:
        # Run all agents with chunking and revision loop
        result = run_all_agents(
            request.prompt, 
            request.session_id,
            max_revisions=request.max_revisions or 1,
            devils_advocate=request.devils_advocate or False
        )
        
        # Save to MongoDB if request.session_id is provided
        if request.session_id:
            # Save main messages
            messages = [
                {
                    "session_id": request.session_id,
                    "agent": "user",
                    "content": request.prompt,
                    "timestamp": datetime.now(timezone.utc)
                },
                {
                    "session_id": request.session_id,
                    "agent": "idea",
                    "content": result["idea_response"],
                    "user_prompt": request.prompt,
                    "timestamp": datetime.now(timezone.utc)
                },
                {
                    "session_id": request.session_id,
                    "agent": "critic",
                    "content": result["critic_response"],
                    "user_prompt": request.prompt,
                    "timestamp": datetime.now(timezone.utc),
                    "metadata": result.get("critic_metadata")
                },
                {
                    "session_id": request.session_id,
                    "agent": "builder",
                    "content": result["builder_response"],
                    "user_prompt": request.prompt,
                    "timestamp": datetime.now(timezone.utc)
                }
            ]
            
            msg_results = await db.db.messages.insert_many(messages)
            # Get inserted IDs - note that the first one is the user message
            message_ids = [str(mid) for mid in msg_results.inserted_ids]
            
            # Save chunks with embeddings for all agents
            all_chunks = []
            
            # Process idea chunks (associated with idea message, which is index 1)
            for chunk in result["idea_chunks"]:
                chunk_doc = {
                    "message_id": message_ids[1],
                    "session_id": request.session_id,
                    "agent": "idea",
                    "content": chunk["chunk_text"],
                    "embedding": chunk["embedding"],
                    "chunk_index": chunk["chunk_index"],
                    "user_prompt": request.prompt,
                    "timestamp": datetime.now(timezone.utc)
                }
                all_chunks.append(chunk_doc)
            
            # Process critic chunks
            for chunk in result["critic_chunks"]:
                chunk_doc = {
                    "message_id": message_ids[2],
                    "session_id": request.session_id,
                    "agent": "critic",
                    "content": chunk["chunk_text"],
                    "embedding": chunk["embedding"],
                    "chunk_index": chunk["chunk_index"],
                    "user_prompt": request.prompt,
                    "timestamp": datetime.now(timezone.utc)
                }
                all_chunks.append(chunk_doc)
            
            # Process builder chunks
            for chunk in result["builder_chunks"]:
                chunk_doc = {
                    "message_id": message_ids[3],
                    "session_id": request.session_id,
                    "agent": "builder",
                    "content": chunk["chunk_text"],
                    "embedding": chunk["embedding"],
                    "chunk_index": chunk["chunk_index"],
                    "user_prompt": request.prompt,
                    "timestamp": datetime.now(timezone.utc)
                }
                all_chunks.append(chunk_doc)
            
            if all_chunks:
                await db.db.idea_chunks.insert_many(all_chunks)
            
            # Update session's updated_at timestamp
            await db.db.sessions.update_one(
                {"session_id": request.session_id},
                {"$set": {"updated_at": datetime.now(timezone.utc)}}
            )
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during brainstorming: {str(e)}")


# ==================== SESSION MANAGEMENT ENDPOINTS ====================

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(session: SessionCreate):
    """
    Create a new brainstorming session.
    """
    try:
        from bson import ObjectId
        
        session_id = str(ObjectId())
        session_doc = {
            "session_id": session_id,
            "title": session.title,
            "description": session.description,
            "user_email": session.user_email,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.db.sessions.insert_one(session_doc)
        
        return SessionResponse(
            session_id=session_id,
            title=session.title,
            description=session.description,
            user_email=session.user_email,
            created_at=session_doc["created_at"],
            updated_at=session_doc["updated_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@app.get("/api/sessions", response_model=List[SessionResponse])
async def list_sessions(user_email: str = None):
    """
    Get all brainstorming sessions.
    """
    try:
        filter_query = {}
        if user_email:
            filter_query["user_email"] = user_email

        cursor = db.db.sessions.find(filter_query).sort("updated_at", -1)
        sessions = await cursor.to_list(length=100)
        
        return [
            SessionResponse(
                session_id=s["session_id"],
                title=s["title"],
                description=s.get("description"),
                user_email=s.get("user_email"),
                created_at=s["created_at"],
                updated_at=s["updated_at"]
            )
            for s in sessions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sessions: {str(e)}")


@app.get("/api/sessions/{session_id}", response_model=SessionWithMessages)
async def get_session(session_id: str):
    """
    Get a specific session with all its messages.
    """
    try:
        session = await db.db.sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get all messages for this session
        cursor = db.db.messages.find({"session_id": session_id}).sort("timestamp", 1)
        messages = await cursor.to_list(length=1000)
        
        return SessionWithMessages(
            session_id=session["session_id"],
            title=session["title"],
            description=session.get("description"),
            user_email=session.get("user_email"),
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            messages=[
                Message(
                    message_id=str(m["_id"]),
                    session_id=m["session_id"],
                    agent=m["agent"],
                    content=m["content"],
                    user_prompt=m.get("user_prompt"),
                    timestamp=m["timestamp"],
                    metadata=m.get("metadata")
                )
                for m in messages
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching session: {str(e)}")


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session and all its messages.
    """
    try:
        # Delete the session
        result = await db.db.sessions.delete_one({"session_id": session_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete all messages for this session
        await db.db.messages.delete_many({"session_id": session_id})
        
        # Delete all chunks for this session
        await db.db.idea_chunks.delete_many({"session_id": session_id})
        
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


# ==================== VECTOR SEARCH ENDPOINTS ====================

@app.post("/api/search/similar", response_model=List[VectorSearchResult])
async def search_similar_ideas(request: VectorSearchRequest):
    """
    Search for similar ideas using vector similarity.
    Uses embeddings to find semantically similar content.
    """
    try:
        # Build filter
        filter_dict = {}
        if request.agent_filter:
            filter_dict["agent"] = request.agent_filter
        if request.session_id:
            filter_dict["session_id"] = request.session_id
        
        # Perform vector search
        results = await vector_search(
            db.db,
            query_text=request.query,
            collection_name="idea_chunks",
            limit=request.limit,
            filter_dict=filter_dict if filter_dict else None
        )
        
        # Format results
        search_results = []
        for result in results:
            search_results.append(VectorSearchResult(
                content=result["content"],
                agent=result["agent"],
                user_prompt=result.get("user_prompt"),
                session_id=result.get("session_id"),
                similarity_score=result["similarity_score"],
                chunk_index=result["chunk_index"],
                timestamp=result["timestamp"]
            ))
        
        return search_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching ideas: {str(e)}")


@app.get("/api/search/context/{session_id}")
async def get_session_context(session_id: str, query: str, limit: int = 3):
    """
    Get relevant context from a specific session using vector search.
    Useful for retrieving past ideas when continuing a conversation.
    """
    try:
        results = await vector_search(
            db.db,
            query_text=query,
            collection_name="idea_chunks",
            limit=limit,
            filter_dict={"session_id": session_id}
        )
        
        context_items = []
        for result in results:
            context_items.append({
                "content": result["content"],
                "agent": result["agent"],
                "similarity_score": result["similarity_score"],
                "chunk_index": result["chunk_index"]
            })
        
        return {
            "session_id": session_id,
            "query": query,
            "context": context_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching context: {str(e)}")


@app.get("/api/chunks/stats")
async def get_chunk_statistics():
    """
    Get statistics about stored chunks and embeddings.
    """
    try:
        total_chunks = await db.db.idea_chunks.count_documents({})
        
        # Count by agent
        pipeline = [
            {"$group": {"_id": "$agent", "count": {"$sum": 1}}}
        ]
        agent_stats = await db.db.idea_chunks.aggregate(pipeline).to_list(length=10)
        
        # Count by session
        session_count = len(await db.db.idea_chunks.distinct("session_id"))
        
        return {
            "total_chunks": total_chunks,
            "agent_breakdown": {stat["_id"]: stat["count"] for stat in agent_stats},
            "unique_sessions": session_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")


@app.post("/api/chat", response_model=dict)
async def chat_with_agent(request: PromptRequest):
    """
    Chat with a specific agent (Idea, Critic, or Builder) with context.
    """
    try:
        if not request.target_agent:
            raise HTTPException(status_code=400, detail="Target agent is required for chat")
            
        # Fetch conversation history
        context = []
        if request.session_id:
            cursor = db.db.messages.find({"session_id": request.session_id}).sort("timestamp", 1)
            messages = await cursor.to_list(length=50) # Limit context window
            
            for msg in messages:
                role = "user" if msg["agent"] == "user" else msg["agent"]
                context.append({"role": role, "content": msg["content"]})
        
        # Run the specific agent
        result = run_single_agent_chat(
            agent_type=request.target_agent,
            user_prompt=request.prompt,
            context=context,
            session_id=request.session_id
        )
        
        # Save to MongoDB
        if request.session_id:
            # Save user message
            user_msg = {
                "session_id": request.session_id,
                "agent": "user",
                "content": request.prompt,
                "timestamp": datetime.now(timezone.utc)
            }
            await db.db.messages.insert_one(user_msg)
            
            # Save agent response
            agent_msg = {
                "session_id": request.session_id,
                "agent": request.target_agent,
                "content": result["response"],
                "user_prompt": request.prompt,
                "timestamp": datetime.now(timezone.utc)
            }
            msg_result = await db.db.messages.insert_one(agent_msg)
            message_id = str(msg_result.inserted_id)
            
            # Save chunks
            chunk_docs = []
            for chunk in result["chunks"]:
                chunk_doc = {
                    "message_id": message_id,
                    "session_id": request.session_id,
                    "agent": request.target_agent,
                    "content": chunk["chunk_text"],
                    "embedding": chunk["embedding"],
                    "chunk_index": chunk["chunk_index"],
                    "user_prompt": request.prompt,
                    "timestamp": datetime.now(timezone.utc)
                }
                chunk_docs.append(chunk_doc)
            
            if chunk_docs:
                await db.db.idea_chunks.insert_many(chunk_docs)
                
            # Update session timestamp
            await db.db.sessions.update_one(
                {"session_id": request.session_id},
                {"$set": {"updated_at": datetime.now(timezone.utc)}}
            )
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during chat: {str(e)}")
