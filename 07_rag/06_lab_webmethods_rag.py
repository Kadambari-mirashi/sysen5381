# 06_lab_webmethods_rag.py
# Custom RAG Workflow: IBM webMethods Interview Prep
# Refers to 01_ollama.py and functions.py
# Tim Fraser (lab adaptation)
#
# This script builds a complete custom RAG workflow using a text dataset derived
# from IBM webMethods documentation. It demonstrates how to retrieve relevant
# chunks from a local knowledge base, then generate grounded answers with Ollama.

# 0. SETUP ###################################

## 0.1 Load Packages #################################

import json      # for serializing retrieved chunks into JSON
import os        # for file path operations
import runpy     # for executing 01_ollama.py (start local Ollama server)
import requests  # for handling HTTP errors from model calls

## 0.2 Working Directory #################################

# Set working directory to this script folder so relative paths are stable.
script_dir = os.path.dirname(os.path.abspath(__name__))
os.chdir(script_dir)

## 0.3 Start Ollama Server #################################

# Reuse the local startup pattern from 01_ollama.py.
ollama_script_path = os.path.join(os.getcwd(), "01_ollama.py")
_ = runpy.run_path(ollama_script_path)

## 0.4 Load Functions #################################

# Reuse helper wrapper for Ollama chat calls.
from functions import agent_run

## 0.5 Configuration #################################

# Choose an installed non-smol model for stronger interview-style answers.
# If you want another model, run `ollama list` and set the exact name shown.
MODEL = "llama3:latest"
DOCUMENT = "data/webmethods_interview_rag.txt"


# 1. SEARCH FUNCTION ###################################

def load_chunks(document_path):
    """
    Read the text file and split it into paragraph-level chunks.
    This gives more context than line-level matching and stays simple to inspect.
    """
    with open(document_path, "r", encoding="utf-8") as f:
        text = f.read()
    chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    return chunks


def score_chunk(query, chunk):
    """
    Score a chunk using simple keyword overlap.
    Higher score means more query words appear in the chunk.
    """
    query_words = set(query.lower().split())
    chunk_words = set(chunk.lower().split())
    return len(query_words.intersection(chunk_words))


def search_text_chunks(query, document_path, limit=4):
    """
    Return top matching chunks as a structured list.
    """
    chunks = load_chunks(document_path)
    scored = []
    for idx, chunk in enumerate(chunks):
        score = score_chunk(query=query, chunk=chunk)
        if score > 0:
            scored.append({"chunk_id": idx, "score": score, "text": chunk})

    # Sort from highest to lowest overlap score.
    scored_sorted = sorted(scored, key=lambda row: row["score"], reverse=True)
    return scored_sorted[:limit]


# 2. TEST SEARCH ###################################

print("--------------------------------")
print("TESTING SEARCH FUNCTION")
print("--------------------------------")

test_query = "How does webMethods support governance and data sovereignty?"
test_matches = search_text_chunks(test_query, DOCUMENT, limit=3)
print(f"Query: {test_query}")
print(f"Matches found: {len(test_matches)}")
print(json.dumps(test_matches, indent=2))
print()


# 3. RAG WORKFLOW ###################################

print("--------------------------------")
print("RAG WORKFLOW")
print("--------------------------------")

# You can change this query for your screenshot submission.
user_query = "Explain how webMethods Hybrid Integration balances agility with governance."

# Step 1: Retrieve relevant chunks.
retrieved_chunks = search_text_chunks(user_query, DOCUMENT, limit=4)
retrieved_json = json.dumps(retrieved_chunks, indent=2)

print("Retrieved context:")
print(retrieved_json)
print()

# Step 2: Ask LLM to answer from retrieved context only.
role = (
    "You are an interview prep assistant for IBM webMethods Hybrid Integration. "
    "Use only the provided retrieved context. "
    "If the context is insufficient, explicitly say: Not enough context provided. "
    "Return markdown with these sections: "
    "1) Short Answer, 2) Key Points, 3) Interview Angle, 4) One Follow-up Question."
)

task = f"User question: {user_query}\n\nRetrieved context JSON:\n{retrieved_json}"

try:
    rag_output = agent_run(role=role, task=task, model=MODEL, output="text")
except requests.exceptions.HTTPError as e:
    print("LLM request failed.")
    print(f"Model attempted: {MODEL}")
    print("Tip: run `ollama list` and update MODEL to an installed name.")
    raise e

print("Generated RAG answer:")
print(rag_output)
