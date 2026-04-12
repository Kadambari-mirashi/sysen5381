# archinsight_qc.py
# AI Quality Control for ArchInsight Architecture Reviews
# Pairs with 06_agents/ArchInsight/main.py and 09_text_analysis/02_ai_quality_control.py

# This pilot script builds an AI-powered quality control system for ArchInsight's
# Agent 3 final review output. Two local Ollama models evaluate the same text on
# 3 metrics (completeness, specificity, faithfulness) and results are saved to CSV.
# Pilot runs 2 times per model; scale N_RUNS to 50 for the final submission.

# 0. Setup ###################################

## 0.1 Load Packages #################################

import sys
import os
import json
import re
import requests
import pandas as pd
from pathlib import Path

## 0.2 Configuration #################################

# Ollama connection settings
PORT = 11434
OLLAMA_HOST = f"http://localhost:{PORT}"

# Two Ollama models to compare as QC evaluators
MODEL_A = "llama3:latest"    # larger model — better reasoning, slower
MODEL_B = "smollm2:135m"     # tiny model — very fast, less capable

# Number of QC runs per model (pilot = 2; scale to 50 for final submission)
N_RUNS = 2

# Paths
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_CSV = DATA_DIR / "archinsight_qc_results.csv"

# ArchInsight project directory (two levels up from here, then into 06_agents)
ARCHINSIGHT_DIR = Path(__file__).parent.parent.parent / "06_agents" / "ArchInsight"

## 0.3 Import ArchInsight Modules #################################

# Add ArchInsight to sys.path so we can reuse its prompts and agent functions
sys.path.insert(0, str(ARCHINSIGHT_DIR))

from prompts import SYSTEMS_ANALYST_PROMPT, SOLUTION_ARCHITECT_PROMPT
from agents import run_text_agent
from sample_data import SAMPLE_ARCHITECTURE_DESCRIPTION

# Agent 1's output serves as the ground truth for our faithfulness check
SOURCE_CONTEXT = SAMPLE_ARCHITECTURE_DESCRIPTION

# 1. Fetch ArchInsight Agent 3 Output ###################################

print("=" * 60)
print("  ArchInsight QC — Pilot")
print("=" * 60)
print()

# Hardcoded fallback in case Ollama is not running when this script starts.
# This is a realistic example of what Agent 3 would produce for the sample architecture.
FALLBACK_AGENT3_OUTPUT = """### Recommended Improvements
- Introduce a circuit breaker (e.g., Resilience4j) between Order Service and Orders PostgreSQL to prevent cascade failures during database outages.
- Add a dead-letter queue to RabbitMQ for failed Notification Service events to prevent silent message loss.
- Implement API versioning (e.g., /v1/) at the API Gateway before the service surface area grows further.
- Add a read replica for the Orders PostgreSQL database to offload read-heavy reporting queries.

### Reliability and Scalability
- Horizontal scaling: All six microservices are stateless and can scale independently behind the API Gateway.
- Failover: RabbitMQ must be deployed as a mirrored cluster; a single-node broker is currently a SPOF.
- Load balancing: The API Gateway manages ingress traffic; internal service-to-service calls lack a load balancer.
- Data replication: PostgreSQL databases should use streaming replication with a warm standby replica.

### Observability and Security
- Adopt OpenTelemetry for distributed tracing across all six services; track RabbitMQ consumer lag as a key metric.
- Implement centralized logging with an ELK stack; correlate log entries by trace ID across services.
- Downstream services (Order, Inventory, User) must independently validate JWTs — confirm this is not gateway-only.
- Enable TLS for all inter-service communication and RabbitMQ connections; encryption in transit is not shown.

### Final Review Summary
This microservices e-commerce architecture demonstrates solid separation of concerns and appropriate use of asynchronous messaging via RabbitMQ. The polyglot persistence strategy (PostgreSQL, MongoDB, Redis) is well-matched to each service's data access patterns. However, three production-blocking risks exist: the RabbitMQ single point of failure, the absence of circuit breakers on database connections, and unconfirmed JWT validation at the service layer. The system is ready for staging, with the caveat that RabbitMQ clustering and circuit breaker patterns must be implemented before production release.""".strip()

print("Step 1 — Generate ArchInsight Agent 3 Output")
print("-" * 40)

try:
    # Run Agent 2 (Systems Analyst) on the sample architecture description
    print(f"  🔧 Running Agent 2 (Systems Analyst) via {MODEL_B}...")
    agent2_task = (
        "Below is a structured architecture description produced by a visual interpreter. "
        "Analyze this architecture and produce your assessment.\n\n"
        f"{SOURCE_CONTEXT}"
    )
    agent2_output = run_text_agent(role=SYSTEMS_ANALYST_PROMPT, task=agent2_task)
    print(f"  ✅ Agent 2 complete — {len(agent2_output.split())} words")

    # Run Agent 3 (Solution Architect) using both Agent 1 and Agent 2 outputs
    print(f"  🔧 Running Agent 3 (Solution Architect) via {MODEL_B}...")
    agent3_task = (
        "Below are two inputs for your review.\n\n"
        "--- ARCHITECTURE DESCRIPTION (from Visual Interpreter) ---\n\n"
        f"{SOURCE_CONTEXT}\n\n"
        "--- ARCHITECTURE ANALYSIS (from Systems Analyst) ---\n\n"
        f"{agent2_output}\n\n"
        "Synthesize both inputs and produce your recommendations and final review."
    )
    agent3_output = run_text_agent(role=SOLUTION_ARCHITECT_PROMPT, task=agent3_task)
    print(f"  ✅ Agent 3 complete — {len(agent3_output.split())} words")

except Exception as e:
    print(f"  ⚠️  Could not reach Ollama: {e}")
    print("  📄 Using hardcoded fallback Agent 3 output")
    agent3_output = FALLBACK_AGENT3_OUTPUT

# This is the text we will quality-control
REPORT_TEXT = agent3_output

print()
print(f"  📋 Report preview (first 200 chars):")
print(f"     {REPORT_TEXT[:200]}...")
print()

# 2. QC Prompt Design ###################################

## 2.1 Create QC Prompt #################################

# Build a prompt that injects Agent 3's output + Agent 1's description as ground truth.
# Asks for JSON with exactly 3 metrics so parsing is reliable.
def create_qc_prompt(review_text, source_context):
    return f"""You are a quality control validator for AI-generated architecture reviews.

Source Architecture Description (ground truth — use this to check faithfulness):
{source_context}

Architecture Review to Evaluate:
{review_text}

Evaluate the review on exactly these 3 criteria and return valid JSON only:

1. completeness (1-5): Are all required sections present and substantive?
   Required sections: Recommended Improvements, Reliability/Scalability, Observability/Security, Final Review Summary
   1 = missing sections or mostly empty, 5 = all sections thorough and detailed

2. specificity (1-5): Are recommendations concrete and component-specific?
   1 = vague generic advice only, 5 = every recommendation names specific components, patterns, or technologies

3. faithful (true/false): Does the review stay grounded in the source architecture description?
   true = only references components present in the source, false = introduces components not in the source

Return ONLY this JSON with no other text:
{{
  "completeness": 1-5,
  "specificity": 1-5,
  "faithful": true/false,
  "details": "10-30 word explanation of your assessment"
}}"""

## 2.2 Query Ollama #################################

# Send a QC prompt to a given Ollama model and return the raw string response
def query_ollama(prompt, model):
    url = f"{OLLAMA_HOST}/api/chat"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "format": "json",   # tells Ollama to enforce JSON output mode
        "stream": False
    }
    response = requests.post(url, json=body, timeout=120)
    response.raise_for_status()
    return response.json()["message"]["content"]

## 2.3 Parse QC Results #################################

# Extract JSON from the AI response and return a flat result dictionary
def parse_qc_results(json_response, run_id, model_name, response_text):
    # Some models wrap JSON in markdown code fences — extract the JSON block
    match = re.search(r"\{.*\}", json_response, re.DOTALL)
    if match:
        json_response = match.group(0)

    data = json.loads(json_response)

    return {
        "id": run_id,
        "response": response_text[:300],   # truncated for CSV readability
        "treatment": model_name,
        "completeness": data.get("completeness"),
        "specificity": data.get("specificity"),
        "faithful": data.get("faithful"),
        "details": data.get("details", "")
    }

# 3. Run Pilot ###################################

## 3.1 Pilot Loop #################################

# Run QC n_runs times for a given model and collect results as a list of dicts
def run_pilot(report_text, source_context, model, n_runs):
    results = []
    prompt = create_qc_prompt(report_text, source_context)

    for i in range(1, n_runs + 1):
        print(f"  ☁️  {model} — run {i}/{n_runs} ...")
        try:
            raw = query_ollama(prompt, model)
            result = parse_qc_results(raw, run_id=i, model_name=model, response_text=report_text)
            results.append(result)
            print(f"     ✅ completeness={result['completeness']}  specificity={result['specificity']}  faithful={result['faithful']}")
        except Exception as e:
            print(f"     ❌ Run {i} failed: {e}")

    return results

print("Step 2 — Run QC Pilot")
print("-" * 40)
print(f"  Models: {MODEL_A}  vs  {MODEL_B}")
print(f"  Runs per model: {N_RUNS}")
print()

results_a = run_pilot(REPORT_TEXT, SOURCE_CONTEXT, MODEL_A, N_RUNS)
print()
results_b = run_pilot(REPORT_TEXT, SOURCE_CONTEXT, MODEL_B, N_RUNS)
print()

# 4. Save and Display Results ###################################

print("Step 3 — Save Results")
print("-" * 40)

all_results = pd.concat(
    [pd.DataFrame(results_a), pd.DataFrame(results_b)],
    ignore_index=True
)

# Reassign sequential IDs across both models
all_results["id"] = range(1, len(all_results) + 1)

# Reorder columns to match the required CSV schema
all_results = all_results[["id", "response", "treatment", "completeness", "specificity", "faithful", "details"]]

all_results.to_csv(OUTPUT_CSV, index=False)
print(f"  💾 Saved  → {OUTPUT_CSV}")
print(f"  📊 Shape  → {len(all_results)} rows × {len(all_results.columns)} cols")
print()

print("Step 4 — Quality Control Results")
print("-" * 40)
print()

# Display full results table (excluding long response text for readability)
display_cols = ["id", "treatment", "completeness", "specificity", "faithful", "details"]
print(all_results[display_cols].to_string(index=False))
print()

# Mean scores per model — useful for the lab write-up comparison
summary = (
    all_results
    .groupby("treatment")[["completeness", "specificity"]]
    .mean()
    .round(2)
)
print("📊 Mean Scores by Model:")
print(summary.to_string())
print()

print("=" * 60)
print("  ✅ Pilot QC complete!")
print(f"  💡 Scale up: set N_RUNS = 50 and rerun for final submission.")
print("=" * 60)
