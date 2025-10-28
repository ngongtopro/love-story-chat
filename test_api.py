import requests

# Test API endpoint
url = "http://localhost:8000/api/chat/profiles/"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nTotal profiles: {len(data)}")
        for profile in data[:5]:
            user = profile.get('user', {})
            print(f"  - {user.get('username')} (online={profile.get('is_online')})")
except Exception as e:
    print(f"Error: {e}")
