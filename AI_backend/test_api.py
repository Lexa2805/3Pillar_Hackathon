"""
Test script for TeamSpark AI API
Tests the Idea Agent endpoint with chunking and embeddings
"""
import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://127.0.0.1:8000"

def test_health_check():
    """Test if the API is running"""
    print("🔍 Testing API health check...")
    try:
        response = requests.get(f"{BASE_URL}/debug-db")
        print(f"✅ API is running! Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API is not running: {e}")
        print("💡 Make sure to start the server with: uvicorn main:app --reload")
        return False


def test_create_session():
    """Test creating a brainstorming session"""
    print("\n📝 Testing session creation...")
    try:
        data = {
            "title": "Test Session - Healthcare AI Ideas",
            "description": "Testing the TeamSpark AI API"
        }
        response = requests.post(f"{BASE_URL}/api/sessions", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Session created successfully!")
            print(f"   Session ID: {result['session_id']}")
            print(f"   Title: {result['title']}")
            return result['session_id']
        else:
            print(f"❌ Failed to create session: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_idea_agent(session_id=None):
    """Test the Idea Agent endpoint"""
    print("\n💡 Testing Idea Agent (with chunking and embeddings)...")
    try:
        data = {
            "prompt": "Give me 3 innovative startup ideas for using AI in healthcare.",
            "session_id": session_id
        }
        
        print(f"   Sending prompt: '{data['prompt']}'")
        print("   ⏳ Waiting for AI response (this may take 5-10 seconds)...")
        
        response = requests.post(f"{BASE_URL}/api/idea", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Idea Agent responded successfully!")
            print(f"\n📋 Generated Ideas:")
            print("=" * 60)
            print(result['response'])
            print("=" * 60)
            print(f"\n📊 Metadata:")
            print(f"   Agent: {result['agent']}")
            print(f"   Timestamp: {result['timestamp']}")
            if session_id:
                print(f"   Session ID: {result['session_id']}")
                print("   ✅ Ideas saved to database with chunks and embeddings!")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_list_sessions():
    """Test listing all sessions"""
    print("\n📋 Testing list sessions...")
    try:
        response = requests.get(f"{BASE_URL}/api/sessions")
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"✅ Found {len(sessions)} session(s)")
            for i, session in enumerate(sessions[:3], 1):
                print(f"   {i}. {session['title']} (ID: {session['session_id'][:8]}...)")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_vector_search():
    """Test vector similarity search"""
    print("\n🔍 Testing vector similarity search...")
    try:
        data = {
            "query": "artificial intelligence in schools",
            "limit": 3,
            "agent_filter": "idea"
        }
        
        print(f"   Searching for: '{data['query']}'")
        response = requests.post(f"{BASE_URL}/api/search/similar", json=data)
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Found {len(results)} similar chunk(s)")
            
            for i, result in enumerate(results, 1):
                print(f"\n   Result {i}:")
                print(f"   Similarity Score: {result['similarity_score']:.4f}")
                print(f"   Agent: {result['agent']}")
                print(f"   Content: {result['content'][:100]}...")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_chunk_stats():
    """Test chunk statistics endpoint"""
    print("\n📊 Testing chunk statistics...")
    try:
        response = requests.get(f"{BASE_URL}/api/chunks/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistics retrieved!")
            print(f"   Total chunks: {stats['total_chunks']}")
            print(f"   Agent breakdown: {stats['agent_breakdown']}")
            print(f"   Unique sessions: {stats['unique_sessions']}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 TeamSpark AI API Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n⚠️  Server is not running. Please start it first!")
        print("Run: uvicorn main:app --reload")
        return
    
    # Test 2: Create a session
    session_id = test_create_session()
    
    # Test 3: Test Idea Agent with chunking
    test_idea_agent(session_id)
    
    # Test 4: List sessions
    test_list_sessions()
    
    # Test 5: Test vector search (if chunks exist)
    test_vector_search()
    
    # Test 6: Get chunk statistics
    test_chunk_stats()
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("=" * 60)
    
    print("\n💡 Manual Testing Tips:")
    print("1. Test in browser: http://127.0.0.1:8000/docs")
    print("2. Try the /api/idea endpoint with different prompts")
    print("3. Check MongoDB to see chunks and embeddings stored")
    print("4. Test vector search with various queries")


if __name__ == "__main__":
    main()
