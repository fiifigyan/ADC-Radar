"""
Setup Notion database for Africa Digital Consultancy Radar - UPDATED FOR NEW NOTION API
"""
import os
import re
from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError

load_dotenv()

def extract_page_id_from_url(url: str) -> str:
    """Extract page ID from Notion URL"""
    if not url:
        return ""
    
    url = url.split('?')[0]
    
    # Find 32-char ID
    pattern = r'([a-f0-9]{32})'
    matches = re.findall(pattern, url.lower())
    
    if matches:
        return matches[-1]
    
    # If URL has dashes, take last part
    if '-' in url:
        last_part = url.split('-')[-1]
        if len(last_part) == 32:
            return last_part
    
    return url.strip()

def create_notion_database():
    """Create the Notion database with proper schema"""
    
    # Get API key
    api_key = os.getenv('NOTION_API_KEY')
    if not api_key:
        print("❌ NOTION_API_KEY not found in .env file")
        print("Get it from: https://www.notion.so/my-integrations")
        api_key = input("Enter your Notion API key (starts with 'ntn_'): ").strip()
        
        # Check for both old and new formats
        if not (api_key.startswith('ntn_') or api_key.startswith('secret_')):
            print("❌ Invalid API key format. Should start with 'ntn_' or 'secret_'")
            print(f"You entered: {api_key[:20]}...")
            return
    
    print(f"✅ API Key format OK: {api_key[:20]}...")
    
    # Initialize Notion client
    notion = Client(auth=api_key)
    
    # Database properties
    properties = {
        "Opportunity Title": {"title": {}},
        "Organization": {"rich_text": {}},
        "Source Platform": {
            "select": {
                "options": [
                    {"name": "Devex", "color": "blue"},
                    {"name": "Impactpool", "color": "green"},
                    {"name": "UNDP", "color": "orange"},
                    {"name": "UNOPS", "color": "red"},
                    {"name": "Inspira", "color": "purple"},
                    {"name": "TED", "color": "pink"},
                    {"name": "DevelopmentAid", "color": "brown"},
                    {"name": "World Bank", "color": "blue"},
                    {"name": "e-Vergabe", "color": "green"},
                    {"name": "DTVP", "color": "orange"},
                    {"name": "exfitender", "color": "red"},
                    {"name": "Mock Data", "color": "gray"}
                ]
            }
        },
        "Contract Type": {
            "select": {
                "options": [
                    {"name": "Individual Consultancy", "color": "blue"},
                    {"name": "ICA", "color": "green"},
                    {"name": "Short-term Expert", "color": "orange"},
                    {"name": "Roster", "color": "red"}
                ]
            }
        },
        "Roster Call": {"checkbox": {}},
        "Country": {"multi_select": {}},
        "Region": {
            "select": {
                "options": [
                    {"name": "West Africa", "color": "blue"},
                    {"name": "East Africa", "color": "green"},
                    {"name": "Southern Africa", "color": "orange"},
                    {"name": "Central Africa", "color": "red"},
                    {"name": "North Africa", "color": "purple"},
                    {"name": "Pan-African", "color": "pink"},
                    {"name": "Global w/ Africa focus", "color": "gray"}
                ]
            }
        },
        "Primary Skill": {
            "multi_select": {
                "options": [
                    {"name": "Data", "color": "blue"},
                    {"name": "Digital", "color": "green"},
                    {"name": "ICT", "color": "orange"},
                    {"name": "AI", "color": "red"},
                    {"name": "Analytics", "color": "purple"},
                    {"name": "Digital Trade", "color": "pink"},
                    {"name": "MIS", "color": "brown"},
                    {"name": "Dashboards", "color": "gray"}
                ]
            }
        },
        "Secondary Skills": {"multi_select": {}},
        "Relevance Score": {"number": {"format": "number"}},
        "Priority": {
            "select": {
                "options": [
                    {"name": "High", "color": "red"},
                    {"name": "Medium", "color": "orange"},
                    {"name": "Low", "color": "green"}
                ]
            }
        },
        "Deadline": {"date": {}},
        "Posted Date": {"date": {}},
        "Original Link": {"url": {}},
        "AI Summary": {"rich_text": {}},
        "Why This Matters": {"rich_text": {}},
        "Confidence Score": {"number": {"format": "number"}},
        "Days Left": {
            "formula": {
                "expression": "dateBetween(prop(\"Deadline\"), now(), \"days\")"
            }
        },
        "Week Added": {
            "formula": {
                "expression": "formatDate(now(), \"WW\")"
            }
        }
    }
    
    # Get parent page
    print("\n📄 Step 1: Get Parent Page")
    print("-" * 40)
    print("Create a NEW page in Notion (blank page)")
    print("Name it: 'Africa Digital Radar Database'")
    print("\nThen copy its URL")
    
    page_input = input("\n📋 Paste your NEW page URL: ").strip()
    parent_page_id = extract_page_id_from_url(page_input)
    
    print(f"Using page ID: {parent_page_id}")
    
    try:
        # Test connection first
        print("\n🔍 Testing connection to Notion...")
        user = notion.users.me()
        print(f"✅ Connected as: {user.get('name', 'Unknown User')}")
        
        # Create the database
        print("\n🔄 Creating database...")
        
        database = notion.databases.create(
            parent={"page_id": parent_page_id},
            title=[{
                "type": "text", 
                "text": {"content": "Africa Digital Consultancy Radar"}
            }],
            icon={
                "type": "emoji",
                "emoji": "🌍"
            },
            properties=properties
        )
        
        print("\n" + "="*50)
        print("✅ DATABASE CREATED SUCCESSFULLY!")
        print("="*50)
        print(f"📊 Database ID: {database['id']}")
        print(f"🔗 View it at: {database['url']}")
        
        # Save to .env file
        env_file = '.env'
        env_content = ""
        
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                env_content = f.read()
        
        # Update API key if needed
        if 'NOTION_API_KEY=' not in env_content:
            env_content += f"\n# Notion Configuration\nNOTION_API_KEY={api_key}\n"
        else:
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('NOTION_API_KEY='):
                    lines[i] = f"NOTION_API_KEY={api_key}"
            env_content = '\n'.join(lines)
        
        # Add database ID
        if 'NOTION_DATABASE_ID=' not in env_content:
            env_content += f"NOTION_DATABASE_ID={database['id']}\n"
        else:
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('NOTION_DATABASE_ID='):
                    lines[i] = f"NOTION_DATABASE_ID={database['id']}"
            env_content = '\n'.join(lines)
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"📝 Updated {env_file}")
        
        # Next steps
        print("\n" + "="*50)
        print("🎯 NEXT STEPS:")
        print("="*50)
        print("1. Open your database:")
        print(f"   {database['url']}")
        print("\n2. Add integration to database:")
        print("   • Click ••• (top right)")
        print("   • Click 'Add connections'")
        print("   • Search for 'Africa Digital Radar'")
        print("   • Click to add it")
        print("\n3. Test with a quick scan:")
        print("   python scripts/run_scan.py")
        
        return database
        
    except APIResponseError as e:
        print(f"❌ Notion API error: {e}")
        if "unauthorized" in str(e).lower():
            print("\n⚠️  Common fixes:")
            print("   • Make sure integration is in your workspace")
            print("   • Try re-creating the integration")
            print("   • Check API key is correct")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    print("🌍 Africa Digital Consultancy Radar - Notion Setup")
    print("=" * 50)
    create_notion_database()