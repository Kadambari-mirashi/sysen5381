# 03_agents_2chain.py
# 2-Agent Workflow: Summary → Formatted Output
# Pairs with multi-agent activity (Stage 2)
# Tim Fraser

# This script demonstrates a simple 2-agent chain:
# Agent 1 takes raw data and produces a summary.
# Agent 2 takes the summary and produces formatted output.

# 0. SETUP ###################################

import os
from pathlib import Path

# Use script directory so "from functions import ..." works
os.chdir(Path(__file__).resolve().parent)

from functions import agent_run

# 1. CONFIGURATION ###################################
# Requires Ollama running (e.g. run "ollama serve" or start the Ollama app) on port 11434.
# Pull the model if needed: ollama pull smollm2:135m

MODEL = "smollm2:135m"

# 2. RAW DATA ###################################

raw_data = """
Sales Q1: North 100 units, South 150 units, East 120 units.
Sales Q2: North 110, South 160, East 115.
Issues: East had supply delays in March. South had a strong February.
"""

# 3. AGENT 1 — SUMMARIZER ###################################

role1 = "You are a summarizer. You read the user's text and produce a clear, concise summary in 2-4 sentences."
summary = agent_run(role=role1, task=raw_data, model=MODEL, output="text")

print("=" * 50)
print("AGENT 1 OUTPUT (Summary):")
print("=" * 50)
print(summary)
print()

# 4. AGENT 2 — FORMATTER (input = Agent 1 output) ###################################

role2 = "You are a formatter. The user gives you a summary. You output the same information as a short bullet-point list with a one-line title."
formatted = agent_run(role=role2, task=summary, model=MODEL, output="text")

print("=" * 50)
print("AGENT 2 OUTPUT (Formatted):")
print("=" * 50)
print(formatted)
