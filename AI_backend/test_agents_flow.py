import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def print_separator(title):
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50)

def test_health():
    print_separator("Testing Health/DB")
    try:
        response = requests.get(f"{BASE_URL}/debug-db")
        print(f"Debug DB: {response.json()}")
        
        response = requests.get(f"{BASE_URL}/test-insert")
        print(f"Test Insert: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_brainstorm_flow():
    print_separator("Testing Full Brainstorm Flow")
    
    # 1. Create a session
    print("1. Creating a new session...")
    session_data = {
        "title": "Test Brainstorm Session",
        "description": "Testing the multi-agent flow with Critic and Builder"
    }
    response = requests.post(f"{BASE_URL}/api/sessions", json=session_data)
    if response.status_code != 200:
        print(f"Failed to create session: {response.text}")
        return
    
    session = response.json()
    session_id = session["session_id"]
    print(f"Session created: {session_id}")
    
    # 2. Run Brainstorming
    print("\n2. Running brainstorming (Idea -> Critic -> Builder)...")
    print("This may take a minute as agents are working...")
    
    prompt_data = {
        "prompt": "I want to build a mobile app for student productivity and time management. The app should help students organize their tasks, set reminders, and track their study time effectively.",
        "session_id": session_id,
        "use_web_search": True
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/brainstorm", json=prompt_data)
    duration = time.time() - start_time
    
    if response.status_code != 200:
        print(f"Failed to brainstorm: {response.text}")
        return
        
    result = response.json()
    print(f"Brainstorming completed in {duration:.2f} seconds")
    
    print("\n--- Idea Agent Response ---")
    print(result["idea_response"][:500] + "...")
    
    print("\n--- Critic Agent Response ---")
    print(result["critic_response"][:500] + "...")
    
    print("\n--- Builder Agent Response ---")
    print(result["builder_response"][:500] + "...")
    
    # 3. Verify Session History
    print("\n3. Verifying session history...")
    response = requests.get(f"{BASE_URL}/api/sessions/{session_id}")
    session_details = response.json()
    
    message_count = len(session_details["messages"])
    print(f"Session has {message_count} messages stored.")
    for msg in session_details["messages"]:
        print(f"- [{msg['agent']}] {msg['timestamp']}")

if __name__ == "__main__":
    print("Starting Agent Flow Test...")
    print(f"Targeting: {BASE_URL}")
    
    test_health()
    test_brainstorm_flow()
