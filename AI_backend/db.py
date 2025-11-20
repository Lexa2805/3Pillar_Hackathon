import os
import ssl
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

try:
    import certifi
    ca_file = certifi.where()
except ImportError:
    ca_file = None

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "hackathon_db")

client = None
db = None

def init_db(app: FastAPI):
    global client, db

    if not MONGO_URL:
        raise RuntimeError("MONGO_URL is missing or failed to load from .env")

    print(f"Connecting to MongoDB...")
    print(f"Connection string: {MONGO_URL[:50]}...")
    print(f"Using CA file: {ca_file if ca_file else 'None (will skip verification)'}")
    
    # Create SSL context
    ssl_context = ssl.create_default_context(cafile=ca_file)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connection_params = {
        "serverSelectionTimeoutMS": 10000,
        "connectTimeoutMS": 10000,
        "socketTimeoutMS": 10000,
        "tls": True,
        "tlsAllowInvalidCertificates": True,
    }
    
    if ca_file:
        connection_params["tlsCAFile"] = ca_file
    
    client = AsyncIOMotorClient(MONGO_URL, **connection_params)
    db = client[DB_NAME]
    
    print(f"MongoDB client initialized for database: {DB_NAME}")

    @app.on_event("shutdown")
    async def shutdown_db():
        if client:
            client.close()
