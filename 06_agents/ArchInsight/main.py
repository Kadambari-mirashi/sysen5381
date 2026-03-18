# main.py
# ArchInsight — VLM-Powered Multi-Agent Architecture Review
# Kadambari Mirashi

# This script orchestrates a 3-agent pipeline that analyzes a software
# architecture diagram and produces a structured architecture review.
#
# Agent 1 (Visual Interpreter): Interprets an architecture diagram image via VLM
# Agent 2 (Systems Analyst):    Analyzes the architecture for strengths and risks
# Agent 3 (Solution Architect): Recommends improvements and delivers a final review
#
# Usage:
#   python main.py                     # runs with sample fallback data
#   python main.py path/to/diagram.png # runs with a real diagram image

# 0. SETUP ###################################

## 0.1 Load Packages #################################

import sys   # for command-line arguments
import os    # for file path checks
import time  # for timing each agent

## 0.2 Load Project Modules #################################

from prompts import (
    VISUAL_INTERPRETER_PROMPT,
    SYSTEMS_ANALYST_PROMPT,
    SOLUTION_ARCHITECT_PROMPT
)
from agents import run_visual_interpreter, run_text_agent, VLM_MODEL, TEXT_MODEL
from sample_data import SAMPLE_IMAGE_PATH, SAMPLE_ARCHITECTURE_DESCRIPTION

## 0.3 Configuration #################################

# Separator for clean terminal output (easy to screenshot)
SEP = "=" * 72


# 1. DETERMINE INPUT MODE ###################################

# Check if user provided an image path as a command-line argument
if len(sys.argv) > 1:
    image_path = sys.argv[1]
else:
    image_path = SAMPLE_IMAGE_PATH

# Decide whether to use the VLM or fall back to sample data
use_vlm = os.path.exists(image_path)

print(SEP)
print("  ArchInsight — Multi-Agent Architecture Review")
print(SEP)
print()

if use_vlm:
    print(f"  Mode:       VLM analysis (image: {image_path})")
    print(f"  VLM Model:  {VLM_MODEL}")
else:
    print(f"  Mode:       Fallback (using sample architecture description)")
    print(f"  Note:       To use VLM, provide a valid image path:")
    print(f"              python main.py path/to/diagram.png")

print(f"  Text Model: {TEXT_MODEL}")
print()


# 2. AGENT 1 — VISUAL ARCHITECTURE INTERPRETER ###################################

print(SEP)
print("  AGENT 1: Visual Architecture Interpreter")
print(SEP)
print()

start = time.time()

if use_vlm:
    # Run the VLM agent on the actual diagram image
    print("  Sending image to vision-language model...")
    print()
    try:
        agent1_output = run_visual_interpreter(
            image_path=image_path,
            system_prompt=VISUAL_INTERPRETER_PROMPT
        )
    except Exception as e:
        print(f"  VLM call failed: {e}")
        print("  Falling back to sample architecture description.")
        print()
        agent1_output = SAMPLE_ARCHITECTURE_DESCRIPTION
else:
    # Use the pre-written sample description as fallback
    agent1_output = SAMPLE_ARCHITECTURE_DESCRIPTION

elapsed = time.time() - start

print(agent1_output)
print()
print(f"  [Agent 1 completed in {elapsed:.2f}s]")
print()


# 3. AGENT 2 — SYSTEMS / INTEGRATION ANALYST ###################################

print(SEP)
print("  AGENT 2: Systems / Integration Analyst")
print(SEP)
print()

start = time.time()

# Build the task for Agent 2: provide Agent 1's output as context
agent2_task = (
    "Below is a structured architecture description produced by a visual interpreter. "
    "Analyze this architecture and produce your assessment.\n\n"
    f"{agent1_output}"
)

try:
    agent2_output = run_text_agent(
        role=SYSTEMS_ANALYST_PROMPT,
        task=agent2_task
    )
except Exception as e:
    print(f"  Agent 2 failed: {e}")
    print("  Make sure Ollama is running: ollama serve")
    sys.exit(1)

elapsed = time.time() - start

print(agent2_output)
print()
print(f"  [Agent 2 completed in {elapsed:.2f}s]")
print()


# 4. AGENT 3 — SOLUTION ARCHITECT ADVISOR ###################################

print(SEP)
print("  AGENT 3: Solution Architect Advisor")
print(SEP)
print()

start = time.time()

# Build the task for Agent 3: provide both Agent 1 and Agent 2 outputs
agent3_task = (
    "Below are two inputs for your review.\n\n"
    "--- ARCHITECTURE DESCRIPTION (from Visual Interpreter) ---\n\n"
    f"{agent1_output}\n\n"
    "--- ARCHITECTURE ANALYSIS (from Systems Analyst) ---\n\n"
    f"{agent2_output}\n\n"
    "Synthesize both inputs and produce your recommendations and final review."
)

try:
    agent3_output = run_text_agent(
        role=SOLUTION_ARCHITECT_PROMPT,
        task=agent3_task
    )
except Exception as e:
    print(f"  Agent 3 failed: {e}")
    print("  Make sure Ollama is running: ollama serve")
    sys.exit(1)

elapsed = time.time() - start

print(agent3_output)
print()
print(f"  [Agent 3 completed in {elapsed:.2f}s]")
print()


# 5. FINAL SUMMARY ###################################

print(SEP)
print("  ArchInsight Review Complete")
print(SEP)
print()
print("  All 3 agents finished successfully.")
print("  Scroll up to review each agent's output.")
print()
print(f"  Agent 1 — Visual Architecture Interpreter  (model: {VLM_MODEL if use_vlm else 'fallback'})")
print(f"  Agent 2 — Systems / Integration Analyst     (model: {TEXT_MODEL})")
print(f"  Agent 3 — Solution Architect Advisor         (model: {TEXT_MODEL})")
print()
print(SEP)
