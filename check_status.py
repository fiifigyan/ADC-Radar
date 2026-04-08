import requests

# Get opportunities from all sources
sources = ['Devex', 'UNDP', 'World Bank', 'DevelopmentAid', 'Impactpool']

print("Current Scraper Status:")
print("=" * 80 + "\n")

for source in sources:
    response = requests.get(f'http://localhost:5000/api/opportunities?source={source}&limit=1')
    data = response.json()
    
    if data and len(data) > 0:
        opp = data[0]
        title = opp.get('title', 'N/A')
        org = opp.get('organization', 'N/A')
        status = "✓ Good" if (title != "Untitled Opportunity" and org != "Unknown Organization") else "✗ Issue"
        
        print(f"{source} {status}:")
        print(f"  Title: {title}")
        print(f"  Org: {org}")
        print()
    else:
        print(f"{source}: No data")
        print()
