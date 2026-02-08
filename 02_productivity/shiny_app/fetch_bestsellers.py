# fetch_bestsellers.py
# Full NYT Bestseller Data for Shiny Dashboard
# Pairs with 02_productivity/shiny_app (app.R) and 01_query_api/my_good_query.py
#
# Fetches all list names from the NYT Books API, then for each list fetches
# the full current bestseller list (all book fields). Saves one JSON file
# so the Shiny app can show full data and the dashboard graph (top 10 weeks on list).

# 0. Setup #################################

## 0.1 Load packages ############################

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

## 0.2 Environment and paths ###############################

# .env: project root (dsai), next to this script, or current working directory
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
cwd = Path.cwd()
env_paths = [
    project_root / ".env",
    script_dir / ".env",
    cwd / ".env",
    cwd.parent.parent / ".env",
]
env_loaded = None
for p in env_paths:
    if p.exists():
        load_dotenv(p)
        env_loaded = p
        break
if env_loaded is None:
    load_dotenv()

api_key = os.getenv("NYT_API_KEY")
if not api_key or "your_" in api_key.lower():
    tried = [str(p) for p in env_paths]
    print("ERROR: NYT_API_KEY missing or still a placeholder.")
    print("  Create a .env file in your project root (the 'dsai' folder) with:")
    print("    NYT_API_KEY=your_real_nyt_api_key")
    print("  Get a key at: https://developer.nytimes.com/get-started")
    print("  Script looked for .env in:", *tried, sep="\n    ")
    sys.exit(1)

BASE_URL = "https://api.nytimes.com/svc/books/v3"
OUT_DIR = script_dir / "data"
OUT_FILE = OUT_DIR / "bestsellers.json"


# 1. API helpers #################################

def nyt_get(path, params=None):
    """GET a NYT Books API endpoint; returns parsed JSON or None."""
    params = dict(params or {}, **{"api-key": api_key})
    url = f"{BASE_URL}/{path}"
    try:
        resp = requests.get(url, params=params, timeout=25)
    except requests.RequestException as e:
        print(f"ERROR: Request failed: {e}")
        return None
    if resp.status_code != 200:
        print(f"ERROR: Status {resp.status_code} for {path}")
        return None
    data = resp.json()
    if data.get("status") != "OK":
        return None
    return data


def _encode_list_name(name):
    """Encode list name for API: lowercase, spaces to hyphens, remove apostrophes."""
    if not name:
        return ""
    s = name.lower().strip().replace("'", "").replace(" ", "-")
    return "".join(c for c in s if c.isalnum() or c == "-")


def get_list_names():
    """Fetch list names from overview (lists/names.json returns 404 for this API)."""
    out = nyt_get("lists/overview.json")
    if not out:
        return []
    lists_raw = (out.get("results") or {}).get("lists") or []
    result = []
    seen_encoded = set()
    for lst in lists_raw:
        name = lst.get("list_name") or lst.get("list_name_encoded") or ""
        encoded = lst.get("list_name_encoded") or _encode_list_name(name)
        if not name or not encoded:
            continue
        if encoded in seen_encoded:
            continue
        seen_encoded.add(encoded)
        result.append({"list_name": name, "list_name_encoded": encoded})
    return result


def get_current_list(list_name_encoded):
    """Fetch full current list for one genre; returns list of full book objects."""
    out = nyt_get(f"lists/current/{list_name_encoded}.json")
    if not out:
        return []
    books = (out.get("results") or {}).get("books") or []
    # Keep entire book object (rank, title, author, weeks_on_list, description, book_image, publisher, etc.)
    return list(books)


# 2. Fetch all data #################################

def main():
    print("Fetching list names...")
    lists_meta = get_list_names()
    if not lists_meta:
        print("ERROR: No list names returned. Check API key and network.")
        sys.exit(2)

    print(f"Found {len(lists_meta)} lists. Fetching current books for each...")
    payload = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lists": [],
    }

    for i, meta in enumerate(lists_meta):
        if i > 0:
            time.sleep(1.5)  # Avoid 429 rate limit when fetching many lists
        name = meta["list_name"]
        encoded = meta["list_name_encoded"]
        books = get_current_list(encoded)
        payload["lists"].append({
            "list_name": name,
            "list_name_encoded": encoded,
            "books": books,
        })
        print(f"  [{i+1}/{len(lists_meta)}] {name}: {len(books)} books")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"Saved to {OUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
