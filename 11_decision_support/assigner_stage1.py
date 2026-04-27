#!/usr/bin/env python3
# assigner_stage1.py
# AI Assigner: Staff-Client Assignment (Stage 1)
# Pairs with ACTIVITY_assigner.md
# Tim Fraser
#
# This script runs only Stage 1 of the assignment activity by sending
# staff/client descriptions to a local Ollama model and saving the result.

# 0. Setup #################################

## 0.1 Load Packages ############################

import json
import os
from pathlib import Path
from urllib import error, request

## 0.2 Configuration ############################

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "smollm2:1.7b")
OUTPUT_PATH = Path(__file__).resolve().parent / "output" / "assigner_stage1.md"


# 1. Prompt Content #################################

SYSTEM_PROMPT = """You are a managing partner at a consulting firm making staffing assignments.
Your job is to read unstructured descriptions of staff members and clients,
then assign each staff member to exactly 2 clients based on fit.

Return:
1. An assignment table with columns: Staff Member | Client 1 | Client 2 | Rationale (1 sentence)
2. A brief paragraph (3–5 sentences) summarizing your overall assignment logic

Rules:
- Each staff member gets exactly 2 clients
- Each client is assigned to exactly 1 staff member
- No client may be left unassigned
- Base assignments on demonstrated fit — skills, experience, communication style
- Flag any assignments where fit is weak and explain why"""

USER_PROMPT = """Below are descriptions of our 6 staff members and 12 clients.
Please make the best possible assignments.

--- STAFF ---

Alex Chen
Senior consultant, 9 years experience. Background in financial services and
regulatory compliance. Known for being methodical and detail-oriented.
Prefers clients who are organized and have clear deliverables.
Not great with ambiguous or fast-moving projects.

Brianna Okafor
Mid-level consultant, 4 years experience. Specialist in nonprofit and public
sector work. Very strong communicator — clients love her. Comfortable with
messy, evolving scopes. Has done a lot of stakeholder engagement work.

Carla Mendez
Senior consultant, 7 years experience. Deep expertise in healthcare and life
sciences. Data-heavy work is her strength — she's built several dashboards and
automated reporting tools. Tends to be blunt and efficient; not the warmest
bedside manner but clients respect her results.

Dana Park
Junior consultant, 2 years experience. Background is in marketing and consumer
research. Eager and creative. Better on smaller, well-defined tasks.
Still building confidence with senior client stakeholders.

Elliot Vasquez
Partner-level, 15 years experience. Generalist with a strong track record in
strategy and organizational change. Good relationship manager. Prefers high-stakes,
high-visibility engagements. Gets bored on smaller tactical work.

Fiona Marsh
Mid-level consultant, 5 years experience. Former journalist turned researcher.
Excellent writer and communicator. Often assigned to deliverable-heavy projects
(reports, white papers, presentations). Works well independently.
Prefers clients who give her creative latitude.

--- CLIENTS ---

Client A — Riverdale Community Health Clinic
Small nonprofit health clinic undergoing a strategic planning process.
Moderate budget. Stakeholders include the board, medical staff, and community
advocates. Very collaborative, but decisions are slow due to committee structure.
Main need: facilitation support and a written strategic plan.

Client B — Atlas Financial Group
Large regional bank. Highly regulated environment. Project involves auditing
their compliance documentation and recommending process improvements.
Very organized client — they have a detailed project plan. Expects formal
deliverables and regular status reports.

Client C — BrightPath Schools (Charter Network)
Fast-growing charter school network. Expanding from 3 to 8 schools.
Needs help with org design and HR policy. Client is enthusiastic but somewhat
disorganized. Decision-maker is the founder/CEO — she's visionary but hard to pin
down for meetings.

Client D — Nexagen Pharmaceuticals
Mid-size pharma company. Project is a data audit and KPI dashboard buildout
for their clinical operations team. Technical stakeholders who want results,
not hand-holding. Timeline is tight.

Client E — Greenway Transit Authority
Regional transit agency. Unionized workforce. Project involves a service
redesign study with significant community engagement components.
Political sensitivities — several board members have conflicting opinions.
Long timeline, phased project.

Client F — Solstice Consumer Goods
Consumer packaged goods brand. Needs a market research summary and brand
positioning analysis ahead of a product launch. Fun client, collaborative,
lots of back and forth. Not a huge budget. Creative work valued.

Client G — Meridian Capital Partners
Private equity firm. Fast-moving, high-expectations. Needs an org assessment
of a portfolio company. Very low patience for process — they want findings fast.
Elliot has a pre-existing relationship with the managing partner.

Client H — Harbor City Government (Parks Dept.)
Municipal parks department doing a 10-year capital planning study.
Lots of stakeholders — parks staff, city council, community groups.
Needs public engagement support and a formal report for the city council.

Client I — ClearView Diagnostics
Healthcare tech startup. Building a clinical decision support tool.
Needs help structuring their regulatory strategy and drafting FDA submission
materials. Technical and regulatory complexity is high. Startup culture —
informal, fast, sometimes chaotic.

Client J — The Holloway Foundation
Private philanthropy. Wants a landscape scan and strategic options memo on
workforce development funding. Small team, thoughtful, low-maintenance.
Primarily needs a polished, well-written deliverable.

Client K — Summit Retail Group
Multi-location retail chain. Undergoing a cost reduction initiative.
Wants operational benchmarking and process recommendations.
Client stakeholders are skeptical of consultants — they've had bad experiences
before. Need someone who can build trust quickly.

Client L — Vance Biomedical Research Institute
Academic research institute. Needs help redesigning their grant reporting
process and building a data tracking system. Methodical, detail-oriented
stakeholders. Comfortable with technical complexity."""


# 2. Helper Function #################################

def call_ollama(system_prompt, user_prompt):
    """Send a non-streaming chat request to local Ollama and return response text."""
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
        with request.urlopen(req, timeout=180) as response:
            response_body = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore").strip()
        raise RuntimeError(f"Ollama HTTP error {exc.code}: {exc.reason}. {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(
            f"Unable to connect to Ollama at {OLLAMA_BASE_URL}. Is 'ollama serve' running?"
        ) from exc
    except TimeoutError as exc:
        raise RuntimeError("Ollama request timed out after 180 seconds.") from exc

    parsed = json.loads(response_body)
    return parsed["message"]["content"].strip()


# 3. Run Stage 1 #################################

def main():
    print("=== ACTIVITY_assigner Stage 1 ===")
    print(f"Model: {OLLAMA_MODEL}")
    response_text = call_ollama(SYSTEM_PROMPT, USER_PROMPT)
    print("\n=== Model Output ===\n")
    print(response_text)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(f"# Stage 1 Output\n\n{response_text}\n", encoding="utf-8")
    print(f"\nSaved markdown output to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
