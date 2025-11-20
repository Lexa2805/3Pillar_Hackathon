"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Union, Any
from datetime import datetime


class PromptRequest(BaseModel):
    """Request model for sending a prompt"""
    prompt: str = Field(..., description="The user's prompt for idea generation")
    session_id: Optional[str] = Field(None, description="Optional session ID for context")
    use_web_search: Optional[bool] = Field(True, description="Enable web search for current information")
    max_revisions: Optional[int] = Field(3, description="Maximum number of revision loops allowed (default: 3)")
    target_agent: Optional[str] = Field(None, description="Specific agent to talk to (idea, critic, builder)")


class IdeaResponse(BaseModel):
    """Response model from Idea Agent"""
    agent: str = Field(..., description="The agent that generated the response")
    response: str = Field(..., description="The agent's response content")
    user_prompt: str = Field(..., description="The original user prompt")
    session_id: Optional[str] = Field(None, description="Session ID if applicable")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class SessionCreate(BaseModel):
    """Request model for creating a new session"""
    title: str = Field(..., description="Title of the brainstorming session")
    description: Optional[str] = Field(None, description="Description of the session")
    user_email: Optional[str] = Field(None, description="Email of the user who created the session")


class SessionResponse(BaseModel):
    """Response model for session data"""
    session_id: str = Field(..., description="Unique session identifier")
    title: str = Field(..., description="Session title")
    description: Optional[str] = Field(None, description="Session description")
    user_email: Optional[str] = Field(None, description="Email of the user who created the session")
    created_at: datetime = Field(..., description="Session creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class Message(BaseModel):
    """Model for a message in a session"""
    message_id: str = Field(..., description="Unique message identifier")
    session_id: str = Field(..., description="Associated session ID")
    agent: str = Field(..., description="Agent that generated the message")
    content: Any = Field(..., description="Message content (text or structured data)")
    user_prompt: Optional[str] = Field(None, description="Original user prompt if applicable")
    timestamp: datetime = Field(..., description="Message timestamp")


class SessionWithMessages(SessionResponse):
    """Session response with associated messages"""
    messages: List[Message] = Field(default_factory=list, description="Messages in the session")


class VectorSearchRequest(BaseModel):
    """Request model for vector similarity search"""
    query: str = Field(..., description="Search query text")
    limit: int = Field(5, description="Number of results to return")
    agent_filter: Optional[str] = Field(None, description="Filter by agent (idea, critic, builder)")
    session_id: Optional[str] = Field(None, description="Filter by session ID")


class VectorSearchResult(BaseModel):
    """Result from vector similarity search"""
    content: str = Field(..., description="Chunk content")
    agent: str = Field(..., description="Agent that generated this content")
    user_prompt: Optional[str] = Field(None, description="Original user prompt")
    session_id: Optional[str] = Field(None, description="Session ID")
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    chunk_index: int = Field(..., description="Index of the chunk")
    timestamp: datetime = Field(..., description="Creation timestamp")


class ChunkData(BaseModel):
    """Model for chunk data with embedding"""
    chunk_index: int = Field(..., description="Index of the chunk")
    chunk_text: str = Field(..., description="The text content of the chunk")
    embedding: List[float] = Field(..., description="Vector embedding")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class UserStats(BaseModel):
    """Response model for user statistics"""
    total_sessions: int = Field(..., description="Total number of sessions")
    ideas_generated: int = Field(..., description="Total number of ideas generated")
    knowledge_chunks: int = Field(..., description="Total number of knowledge chunks")
    active_agents: int = Field(..., description="Number of active agents")
