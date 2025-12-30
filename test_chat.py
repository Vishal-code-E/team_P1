#!/usr/bin/env python3
import requests
import json
import time

print("Testing Backend Chat Endpoint...")
print("=" * 50)

time.sleep(2)  # Wait for backend to be fully ready

try:
    response = requests.post(
        "http://127.0.0.1:8000/chat",
        json={"message": "Hello, how are you?"},
        timeout=20
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    print("✅ Chat test successful!")
    
except requests.Timeout:
    print("❌ Request timed out")
except Exception as e:
    print(f"❌ Error: {e}")
