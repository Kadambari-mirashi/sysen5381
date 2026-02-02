import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv(".env")
nyt_api_key = os.getenv("NYT_API_KEY")

if not nyt_api_key:
    print("NYT_API_KEY not found. Set the environment variable or add it to .env:")
    print("  NYT_API_KEY=your_real_nyt_key_here")
    sys.exit(2)

# Use the NYTimes Books API. The NYT expects the API key as the

# query parameter named `api-key`, not an `x-api-key` header.
url = "https://api.nytimes.com/svc/books/v3/lists/overview.json"
params = {"api-key": nyt_api_key}

try:
    response = requests.get(url, params=params, timeout=10)
except requests.RequestException as e:
    print("Request failed:", e)
    sys.exit(3)

print(response.status_code)

data = response.json()
#print("Response status:", data.get("status"))


# Overview endpoint returns multiple lists
lists = data.get("results", {}).get("lists", [])
#print("Number of lists returned:", len(lists))

sliced_json = {    
    "results": {
        "lists": []
    }
}

for lst in data["results"]["lists"][:2]:
    sliced_json["results"]["lists"].append({
        "list_name": lst["list_name"],
        "books": lst["books"][:2]   # keep only first 2 books
    })

# Print ONLY JSON
print(json.dumps(sliced_json, indent=2))