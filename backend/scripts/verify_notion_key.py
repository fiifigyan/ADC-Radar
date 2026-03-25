"""
Verify your Notion API key
"""
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('NOTION_API_KEY')

print("🔍 Verifying Notion API Key")
print("=" * 50)

if not api_key:
    print("❌ NOTION_API_KEY not found in .env")
    print("Add: NOTION_API_KEY=ntn_your_key_here")
    exit(1)

print(f"📋 Key: {api_key[:30]}...")
print(f"📏 Length: {len(api_key)} characters")

# Check format
if api_key.startswith('ntn_'):
    print("✅ Format: ntn_ (new format)")
elif api_key.startswith('secret_'):
    print("✅ Format: secret_ (old format)")
else:
    print(f"❌ Format: {api_key[:10]}... (should start with ntn_ or secret_)")

# Simple test without notion_client
import requests

# Test connection with requests
print("\n🔗 Testing connection...")
try:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # Simple GET request to Notion API
    response = requests.get(
        "https://api.notion.com/v1/users/me",
        headers=headers,
        timeout=10
    )
    
    print(f"📡 HTTP Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Connected! User: {data.get('name', 'Unknown')}")
        print(f"📧 Email: {data.get('person', {}).get('email', 'Not available')}")
    elif response.status_code == 401:
        print("❌ Unauthorized - Invalid API key")
        print("Get new key from: https://www.notion.so/my-integrations")
    elif response.status_code == 403:
        print("❌ Forbidden - Integration not added to workspace")
        print("Add integration to your workspace first")
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
except requests.exceptions.ConnectionError:
    print("❌ Connection failed - Check internet/firewall")
except Exception as e:
    print(f"❌ Error: {e}")