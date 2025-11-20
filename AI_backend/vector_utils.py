"""
Vector utilities for text chunking and embeddings
"""
import os
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Initialize embedding model (lightweight and fast)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Split text into smaller chunks for better processing and storage.
    
    Args:
        text: The text to chunk
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks to maintain context
    
    Returns:
        List of text chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    return chunks


def generate_embedding(text: str) -> List[float]:
    """
    Generate vector embedding for a piece of text.
    
    Args:
        text: The text to embed
    
    Returns:
        Vector embedding as a list of floats
    """
    embedding = embedding_model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts efficiently.
    
    Args:
        texts: List of texts to embed
    
    Returns:
        List of vector embeddings
    """
    embeddings = embedding_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return [emb.tolist() for emb in embeddings]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
    
    Returns:
        Similarity score between -1 and 1
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


def chunk_and_embed_text(text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Chunk text and generate embeddings for each chunk.
    
    Args:
        text: The text to process
        metadata: Additional metadata to attach to each chunk
    
    Returns:
        List of dictionaries containing chunks, embeddings, and metadata
    """
    chunks = chunk_text(text)
    embeddings = generate_embeddings_batch(chunks)
    
    results = []
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_data = {
            "chunk_index": idx,
            "chunk_text": chunk,
            "embedding": embedding,
            "metadata": metadata or {}
        }
        results.append(chunk_data)
    
    return results


def prepare_vector_document(
    content: str,
    agent: str,
    session_id: str,
    user_prompt: str,
    message_id: str = None
) -> List[Dict[str, Any]]:
    """
    Prepare document chunks with embeddings for MongoDB insertion.
    
    Args:
        content: The agent's response content
        agent: The agent that generated the content
        session_id: The session ID
        user_prompt: The original user prompt
        message_id: Optional message ID reference
    
    Returns:
        List of documents ready for MongoDB insertion
    """
    from datetime import datetime
    
    metadata = {
        "agent": agent,
        "session_id": session_id,
        "user_prompt": user_prompt,
        "message_id": message_id,
        "timestamp": datetime.utcnow()
    }
    
    chunks_with_embeddings = chunk_and_embed_text(content, metadata)
    
    # Format for MongoDB
    documents = []
    for chunk_data in chunks_with_embeddings:
        doc = {
            "chunk_index": chunk_data["chunk_index"],
            "content": chunk_data["chunk_text"],
            "embedding": chunk_data["embedding"],
            "agent": agent,
            "session_id": session_id,
            "user_prompt": user_prompt,
            "message_id": message_id,
            "timestamp": datetime.utcnow()
        }
        documents.append(doc)
    
    return documents


async def vector_search(
    db,
    query_text: str,
    collection_name: str = "idea_chunks",
    limit: int = 5,
    filter_dict: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Perform vector similarity search in MongoDB.
    
    Args:
        db: MongoDB database instance
        query_text: The text to search for
        collection_name: Collection to search in
        limit: Number of results to return
        filter_dict: Optional filters (e.g., {"agent": "idea"})
    
    Returns:
        List of matching documents with similarity scores
    """
    # Generate embedding for query
    query_embedding = generate_embedding(query_text)
    
    # For MongoDB Atlas Vector Search, you would use:
    # pipeline = [
    #     {
    #         "$vectorSearch": {
    #             "index": "vector_index",
    #             "path": "embedding",
    #             "queryVector": query_embedding,
    #             "numCandidates": limit * 10,
    #             "limit": limit
    #         }
    #     }
    # ]
    
    # For now, we'll do client-side similarity search
    # (You should set up Atlas Vector Search for production)
    
    collection = db[collection_name]
    
    # Get all documents (with optional filter)
    query = filter_dict or {}
    cursor = collection.find(query).limit(100)
    documents = await cursor.to_list(length=100)
    
    # Calculate similarities
    results = []
    for doc in documents:
        if "embedding" in doc:
            similarity = cosine_similarity(query_embedding, doc["embedding"])
            doc["similarity_score"] = similarity
            results.append(doc)
    
    # Sort by similarity and return top results
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results[:limit]
