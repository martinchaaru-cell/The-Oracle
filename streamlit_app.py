# quick_test.py
import requests
import json

HIGHLIGHTLY_HOST = "sport-highlights-api.p.rapidapi.com"
HIGHLIGHTLY_KEY = "b8c5a121-de03-40a2-825a-63f7407a961a"  # Replace with your actual key

HEADERS = {
    "x-rapidapi-host": HIGHLIGHTLY_HOST,
    "x-rapidapi-key": HIGHLIGHTLY_KEY
}

def test_api():
    print("Testing Highlightly API...")
    
    # Test 1: Get countries
    print("\n1. Fetching countries...")
    url = f"https://{HIGHLIGHTLY_HOST}/football/countries"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success! Found {len(data.get('data', []))} countries")
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"   {response.text}")
        return False
    
    # Test 2: Search for Vikingur Gota
    print("\n2. Searching for Vikingur Gota...")
    url = f"https://{HIGHLIGHTLY_HOST}/football/teams"
    params = {"name": "Vikingur"}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        data = response.json()
        teams = data.get("data", [])
        print(f"   ✅ Found {len(teams)} teams")
        for team in teams[:3]:
            print(f"      - {team.get('name')} (ID: {team.get('id')})")
    else:
        print(f"   ❌ Failed: {response.status_code}")
    
    # Test 3: Get today's matches
    print("\n3. Fetching today's matches...")
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    params = {"date": today, "limit": 5}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        data = response.json()
        matches = data.get("data", [])
        print(f"   ✅ Found {len(matches)} matches today")
        for match in matches[:3]:
            home = match.get("homeTeam", {}).get("name", "?")
            away = match.get("awayTeam", {}).get("name", "?")
            league = match.get("league", {}).get("name", "?")
            print(f"      - {home} vs {away} ({league})")
    else:
        print(f"   ❌ Failed: {response.status_code}")
    
    return True

if __name__ == "__main__":
    test_api()
