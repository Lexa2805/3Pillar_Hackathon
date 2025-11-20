# main.py
from datetime import datetime

from fastapi import FastAPI

import db  # <--- import the module, not "from db import db"

app = FastAPI()

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
        "timestamp": datetime.utcnow(),
    }
    result = await db.db.test.insert_one(doc)  # <--- use db.db here
    return {"inserted_id": str(result.inserted_id)}
