# agents.py
# Agent Functions for ArchInsight Multi-Agent Architecture Review
# Pairs with prompts.py, main.py
# Kadambari Mirashi

# This module provides agent functions for the ArchInsight pipeline.
# It extends the Ollama HTTP chat pattern from 06_agents/functions.py
# with support for vision-language models (VLMs) via base64 image input.

# 0. SETUP ###################################

## 0.1 Load Packages #################################

import requests  # for HTTP requests to Ollama
import base64    # for encoding images to base64
import os        # for file path operations
import sys       # for exit on fatal errors

## 0.2 Configuration #################################

# Default Ollama connection settings
PORT = 11434
OLLAMA_HOST = f"http://localhost:{PORT}"
CHAT_URL = f"{OLLAMA_HOST}/api/chat"

# Default models
# VLM_MODEL is used for Agent 1 (vision-language interpretation)
# TEXT_MODEL is used for Agents 2 and 3 (text-only analysis)
VLM_MODEL = "llava"
TEXT_MODEL = "smollm2:1.7b"


# 1. UTILITY FUNCTIONS ###################################

def load_image_as_base64(image_path):
    """
    Read an image file and return its base64-encoded string.
    Ollama's chat API accepts images as base64 strings in the 'images' field.

    Parameters:
    -----------
    image_path : str
        Path to the image file (PNG, JPG, etc.)

    Returns:
    --------
    str
        Base64-encoded image string
    """

    if not os.path.exists(image_path):
        print(f"Error: Image file not found at '{image_path}'")
        sys.exit(1)

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    return base64.b64encode(image_bytes).decode("utf-8")


# 2. CORE AGENT FUNCTION ###################################

def agent_chat(messages, model=TEXT_MODEL, images=None):
    """
    Send a chat request to the Ollama API and return the response text.
    Extends the agent() pattern from 06_agents/functions.py with optional
    image support for vision-language models.

    Parameters:
    -----------
    messages : list
        List of message dicts with 'role' and 'content' keys.
        Example: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
    model : str
        Ollama model name (default: TEXT_MODEL)
    images : list, optional
        List of base64-encoded image strings for VLM input.
        When provided, images are attached to the last user message.

    Returns:
    --------
    str
        The model's response content
    """

    # If images are provided, attach them to the user message
    # Ollama expects images in the user message's 'images' field
    if images:
        for msg in messages:
            if msg["role"] == "user":
                msg["images"] = images
                break

    # Build the request body (same pattern as functions.py)
    body = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    # Send the request to Ollama
    response = requests.post(CHAT_URL, json=body)
    response.raise_for_status()

    # Parse and return the assistant's response
    result = response.json()
    return result["message"]["content"]


# 3. AGENT RUNNER FUNCTIONS ###################################

def run_visual_interpreter(image_path, system_prompt, model=VLM_MODEL):
    """
    Run the Visual Architecture Interpreter agent (Agent 1).
    Sends an architecture diagram image to a vision-language model
    and returns a structured architecture description.

    Parameters:
    -----------
    image_path : str
        Path to the architecture diagram image
    system_prompt : str
        The system prompt defining the interpreter's role and output format
    model : str
        VLM model name (default: VLM_MODEL, e.g., "llava")

    Returns:
    --------
    str
        Structured markdown description of the architecture
    """

    # Load and encode the image
    image_b64 = load_image_as_base64(image_path)

    # Build the message list with system prompt and user request
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Analyze this architecture diagram and produce your structured review."}
    ]

    # Call the VLM with the image attached
    return agent_chat(messages=messages, model=model, images=[image_b64])


def run_text_agent(role, task, model=TEXT_MODEL):
    """
    Run a text-only agent (Agents 2 and 3).
    Equivalent to agent_run() from 06_agents/functions.py.

    Parameters:
    -----------
    role : str
        The system prompt defining the agent's role
    task : str
        The user message / task content for the agent
    model : str
        Ollama model name (default: TEXT_MODEL)

    Returns:
    --------
    str
        The agent's response
    """

    # Build the message list
    messages = [
        {"role": "system", "content": role},
        {"role": "user", "content": task}
    ]

    # Run the agent
    return agent_chat(messages=messages, model=model)
