# lab_ai_reporter.py
# AI-Powered NYT Bestseller Reporter
# Pairs with 02_productivity/shiny_app/fetch_bestsellers.py
# Tim Fraser

# This script queries the NYT Books API for current bestseller data,
# processes it into a concise summary, and sends it to a local Ollama
# LLM to generate a useful reporting summary.

# 0. SETUP ###################################

## 0.1 Load Packages ############################

import os            # for environment variables
import json          # for working with JSON
import requests      # for HTTP requests
from dotenv import load_dotenv  # for loading .env file

## 0.2 Load Environment Variables ################

# Load .env from the project root
load_dotenv()

# Get NYT API key
NYT_API_KEY = os.getenv("NYT_API_KEY")
if not NYT_API_KEY:
    raise ValueError("NYT_API_KEY not found in .env file. Get one at https://developer.nytimes.com/get-started")

print("\n🚀 NYT Bestseller AI Reporter\n")

# 1. QUERY API ###################################

# Fetch the NYT Bestseller overview
# This returns all current lists with their top books in one call
print("📚 Fetching NYT Bestseller data...")

url = "https://api.nytimes.com/svc/books/v3/lists/overview.json"
params = {"api-key": NYT_API_KEY}

response = requests.get(url, params=params, timeout=25)
response.raise_for_status()

data = response.json()

# Extract the lists from the response
lists_raw = data.get("results", {}).get("lists", [])
print(f"   Found {len(lists_raw)} bestseller lists.\n")

# 2. PROCESS DATA ###################################

# Build a flat table of all books across all lists
# Keep key fields: list name, rank, title, author, weeks on list, publisher
print("🔧 Processing data...")

rows = []
for lst in lists_raw:
    list_name = lst.get("list_name", "Unknown")
    for book in lst.get("books", []):
        rows.append({
            "list": list_name,
            "rank": book.get("rank", None),
            "title": book.get("title", "Unknown"),
            "author": book.get("author", "Unknown"),
            "weeks_on_list": book.get("weeks_on_list", 0),
            "publisher": book.get("publisher", "Unknown"),
            "description": book.get("description", ""),
        })

print(f"   Total books across all lists: {len(rows)}")

# Aggregate some summary stats for the AI
total_books = len(rows)
unique_lists = set(r["list"] for r in rows)
total_lists = len(unique_lists)

# Get all #1 ranked books
top_ranked = [r for r in rows if r["rank"] == 1]

# Get top 10 books by weeks on list (longest-running bestsellers)
top_longevity = sorted(rows, key=lambda r: r["weeks_on_list"], reverse=True)[:10]

# Helper: format a list of book dicts as a readable table string
def format_table(books, columns):
    """Format a list of book dicts into aligned text columns."""
    header = " | ".join(col.ljust(20) for col in columns)
    lines = [header, "-" * len(header)]
    for b in books:
        line = " | ".join(str(b.get(col, "")).ljust(20) for col in columns)
        lines.append(line)
    return "\n".join(lines)

ranked_table = format_table(top_ranked, ["list", "title", "author", "weeks_on_list"])
longevity_table = format_table(top_longevity, ["list", "rank", "title", "author", "weeks_on_list"])

# Format processed data as structured text for the AI
data_summary = f"""NYT Bestseller Data (current week):
- Total lists: {total_lists}
- Total books: {total_books}

#1 Ranked Books by List:
{ranked_table}

Top 10 Books by Weeks on List (longest-running bestsellers):
{longevity_table}
"""

print(f"   Processed summary ready ({len(data_summary)} characters).\n")

# 3. AI REPORT ###################################

# Send the processed data to Ollama local for reporting
print("🤖 Generating AI report via Ollama...\n")

# Ollama local endpoint (default port)
PORT = 11434
OLLAMA_HOST = f"http://localhost:{PORT}"
ollama_url = f"{OLLAMA_HOST}/api/generate"

# Craft a clear prompt telling the AI what to produce
prompt = f"""You are a book industry analyst. Based on the following NYT Bestseller data,
write a brief report (5-8 bullet points) covering:
1. Key trends across the bestseller lists
2. Which books have the longest staying power and why that matters
3. Any notable patterns in genres or authors
4. One actionable insight for a reader looking for their next book

Use clear, concise language. Format as bullet points with a short title header.

DATA:
{data_summary}
"""

# Build the request body for Ollama
body = {
    "model": "smollm2:1.7b",  # Local model
    "prompt": prompt,
    "stream": False            # Wait for full response
}

# Send POST request to Ollama
ollama_response = requests.post(ollama_url, json=body, timeout=120)
ollama_response.raise_for_status()

# Extract the AI-generated report
report = ollama_response.json()["response"]

# 4. DISPLAY REPORT ###################################

print("=" * 60)
print("📊 AI-GENERATED BESTSELLER REPORT")
print("=" * 60)
print(report)
print("=" * 60)

# 5. SAVE REPORT ###################################

# Save the report as a text file for submission
output_path = "03_query_ai/lab_ai_reporter_report.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("AI-Generated NYT Bestseller Report\n")
    f.write("=" * 40 + "\n\n")
    f.write(report)
    f.write("\n\n--- Data Summary Used ---\n\n")
    f.write(data_summary)

print(f"\n💾 Report saved to {output_path}")
print("\n✅ AI Reporter complete.\n")
