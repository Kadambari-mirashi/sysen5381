#!/usr/bin/env python3
# decider_activity.py
# AI Decider: Wedding Venue Comparison
# Pairs with ACTIVITY_decider.md
# Tim Fraser
#
# This script demonstrates how to send structured prompt instructions plus raw prose
# venue descriptions to a local Ollama model, then compare recommendation changes
# across two different client-priority scenarios.

# 0. Setup #################################

## 0.1 Load Packages ############################

import json
import os
from pathlib import Path
from urllib import error, request

## 0.2 Configuration ############################

# Read endpoint/model from environment so students can switch models without code edits.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


# 1. Prompt Content #################################

SYSTEM_PROMPT = """You are a structured data extractor and decision analyst.
Your job is to extract key attributes from unstructured venue descriptions,
build a comparison table, and recommend the top 3 venues based on the client's priorities.

Always return:
1. A markdown table with columns: Venue, Capacity, Approx. Price/Night, Catering, Outdoor, Parking, Vibe (1 word)
2. A ranked shortlist of top 3 venues with 1-sentence justification each
3. One sentence noting any venues you had to exclude due to missing information

Be concise. Do not invent data that is not in the descriptions."""

PRIORITIES_STAGE_1 = """Here are the couple's priorities:
- Budget: under $8,000 for venue rental
- Guest count: ~120 people
- Vibe: romantic, not too corporate
- Must have outdoor ceremony option
- Catering must be in-house or on an approved vendor list

Here are descriptions of 16 venues. Please analyze and recommend."""

PRIORITIES_STAGE_2 = """Here are the couple's priorities:
- Budget: flexible, up to $15,000
- Guest count: ~200 people
- Vibe: elegant, grand
- Outdoor is a nice-to-have but not required
- No catering constraint

Here are descriptions of 16 venues. Please analyze and recommend."""

VENUE_DATA = """Venue 1 — The Rosewood Estate
A sprawling property in the Hudson Valley with manicured gardens and a restored barn.
Capacity up to 175 guests. Rental fee is $17,500 Friday–Sunday. They have a preferred
catering list with 4 approved vendors. Outdoor ceremony space available with a rain
backup tent. Parking for ~80 cars on site.

Venue 2 — The Grand Metropolitan Hotel
Downtown ballroom, seats up to 300. In-house catering only. Pricing starts at $12,000
for the ballroom rental, catering packages extra. Valet parking. No outdoor space.

Venue 3 — Lakeview Pavilion
Outdoor lakeside pavilion. No indoor backup. BYOB catering. Fits about 90 people
comfortably, 110 at a squeeze. Very affordable — around $2,500 for a weekend.

Venue 4 — Thornfield Manor
Historic manor house, 8 acres. Exclusive use for the weekend. Price: $18,000.
In-house catering team. Ceremony can be held on the grounds or in the chapel.
Capacity 150. Featured in several bridal magazines.

Venue 5 — The Foundry at Millworks
Industrial-chic converted factory. Very trendy. Capacity 250. Bring your own vendors.
Rental is $5,000. Rooftop available for cocktail hour. No on-site parking — street
parking and nearby garage only.

Venue 6 — Sunrise Farm & Vineyard
Working vineyard with barn and outdoor ceremony terrace. Stunning views. Capacity 130.
Weekend rental $9,800. Catering through their in-house team or 2 approved vendors.
Ample parking. Very popular — books 18 months out.

Venue 7 — The Atrium Club
Corporate event space that does weddings on weekends. Very flexible on catering.
Fits 300+. Located downtown. Pricing on request — sales team says "typically $9,000–$14,000
depending on date." Not particularly romantic but very professional.

Venue 8 — Cedar Hollow Retreat
Rustic woodland lodge. Intimate and cozy. Max 60 guests. $3,200 for a Saturday.
Outside catering allowed. No formal parking lot — guests park in a field.

Venue 9 — The Belvedere
Upscale rooftop venue with skyline views. Indoor/outdoor setup. Capacity 180.
In-house catering required. Rental + minimum catering spend is $28,000.
Very elegant. Valet only.

Venue 10 — Harborside Event Center
Waterfront venue, brand new. Capacity 220. Pricing TBD — still finalizing packages.
Flexible on catering. Outdoor terrace available. Large parking lot.

Venue 11 — The Ivy House
Garden venue in a residential neighborhood. Permits outdoor ceremonies.
Capacity 100. $4,500 rental. BYOB catering. Street parking only — coordinator
recommends a shuttle from a nearby lot.

Venue 12 — Maple Ridge Country Club
Classic country club setting. Capacity 160. In-house catering only, known for
being very good. Rental from $28,500. Golf course backdrop for photos.
Ample parking. Private feel.

Venue 13 — The Glasshouse Conservatory
All-glass event space surrounded by botanical gardens. Very dramatic.
Capacity 140. $18,000 rental, catering open. Outdoor garden available for ceremonies.
Parking on site. Popular for spring weddings.

Venue 14 — Millbrook Inn
Country inn with event lawn. Venue rental $10,500. Capacity 120. Outside catering
allowed. Some overnight rooms available for wedding party. Very charming.

Venue 15 — The Warehouse District Loft
Raw, urban space. Very minimal. No catering kitchen. Capacity 200.
$8,800 rental. Not ideal for traditional weddings.

Venue 16 — Cloverfield Farms
Family-owned working farm. Barn + outdoor space. Capacity 135.
$6,000 Friday–Sunday. Preferred caterer list (3 vendors).
Casual, warm atmosphere. Lots of parking. Dogs welcome."""


# 2. Helper Functions #################################

def call_ollama(system_prompt, user_prompt):
    """Send a non-streaming chat request to local Ollama and return assistant text."""
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        f"{OLLAMA_BASE_URL}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=120) as response:
            response_body = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", "ignore").strip()
        except Exception:
            detail = ""
        message = f"Ollama HTTP error {exc.code}: {exc.reason}"
        if detail:
            message = f"{message}. Response: {detail}"
        raise RuntimeError(message) from exc
    except error.URLError as exc:
        raise RuntimeError(
            f"Unable to connect to Ollama at {OLLAMA_BASE_URL}. "
            "Make sure Ollama is running and reachable."
        ) from exc
    except TimeoutError as exc:
        raise RuntimeError("Request to Ollama timed out after 120 seconds.") from exc

    try:
        parsed = json.loads(response_body)
        return parsed["message"]["content"].strip()
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise RuntimeError("Unexpected Ollama response format.") from exc


def build_user_prompt(priorities_block):
    """Combine priorities and shared venue descriptions into one user prompt."""
    return f"{priorities_block}\n\n{VENUE_DATA}"


def save_markdown(path, title, content):
    """Write stage response to a markdown file with a simple heading."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n\n{content}\n", encoding="utf-8")


# 3. Main Run #################################

def main():
    print("=== Stage 1: Base Priorities ===")
    stage_1_prompt = build_user_prompt(PRIORITIES_STAGE_1)
    stage_1_response = call_ollama(SYSTEM_PROMPT, stage_1_prompt)
    print(stage_1_response)
    save_markdown(OUTPUT_DIR / "decider_stage1.md", "Stage 1 Output", stage_1_response)
    print(f"\nSaved: {OUTPUT_DIR / 'decider_stage1.md'}")

    print("\n=== Stage 2: Shifted Priorities ===")
    stage_2_prompt = build_user_prompt(PRIORITIES_STAGE_2)
    stage_2_response = call_ollama(SYSTEM_PROMPT, stage_2_prompt)
    print(stage_2_response)
    save_markdown(OUTPUT_DIR / "decider_stage2.md", "Stage 2 Output", stage_2_response)
    print(f"\nSaved: {OUTPUT_DIR / 'decider_stage2.md'}")

    print(
        "\nComparison prompt for reflection: Which venues moved up or down between Stage 1 and Stage 2, and why?"
    )


if __name__ == "__main__":
    main()
