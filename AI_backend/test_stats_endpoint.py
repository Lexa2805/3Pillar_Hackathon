import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_stats():
    print("\n📊 Testing stats endpoint...")
    # Use a dummy email or one that likely exists
    email = "test@example.com" 
    try:
        response = requests.get(f"{BASE_URL}/api/stats?user_email={email}")
        if response.status_code == 200:
            print(f"✅ Stats fetched successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Failed to fetch stats: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_stats()
