#LAB: Create an API query that returns substantial data (more than 1 row) 
# useful for building a reporter application.

"""

LAB: Good API Query for Reporter App

API: New York Times Books API
Endpoint: GET https://api.nytimes.com/svc/books/v3/lists/current/{list_name_encoded}.json
Auth: api-key query param (loaded from .env as NYT_API_KEY)

Query design:
- list_name_encoded = "hardcover-fiction"
- returns ~15 book records (>= 10-20 rows requirement)

Expected data:
- JSON with top-level: status, results
- results.books: list of book objects with rank/title/author/weeks_on_list/publisher/etc.

"""


import os
import sys
import requests
from dotenv import load_dotenv

def main():
    load_dotenv(".env")
    api_key = os.getenv("NYT_API_KEY")

    if not api_key or "your_" in api_key:
        print("RROR: NYT_API_KEY missing or still placeholder in .env")
        sys.exit(1)

    list_name_encoded = "hardcover-fiction"
    url = f"https://api.nytimes.com/svc/books/v3/lists/current/{list_name_encoded}.json"
    params = {"api-key": api_key}

    try:
        resp = requests.get(url, params=params, timeout=20)
    except requests.RequestException as e:
        print("ERROR: Request failed:", e)
        sys.exit(2)

    print("Response Status Code:", resp.status_code)

    if resp.status_code != 200:
        try:
            print("Error JSON:", resp.json())
        except ValueError:
            print("Error text:", resp.text[:500])
        sys.exit(3)

    data = resp.json()
    books = data.get("results", {}).get("books", [])
    print(f"Number of books returned: {len(books)}")

    print("\nPreview (top 15):")
    for book in books[:15]:
        print(f"- Rank {book.get('rank')}: '{book.get('title')}' by {book.get('author')}"
              f"(Weeks on list: {book.get('weeks_on_list')})")

if __name__ == "__main__":
    main()


