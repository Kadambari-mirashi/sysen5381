# 02_function_calling.py
# Basic Function Calling Example
# Pairs with 02_function_calling.R
# Tim Fraser

# This script demonstrates how to use function calling with an LLM in Python.
# Students will learn how to define functions as tools and execute tool calls.

# Further reading: https://docs.ollama.com/function-calling

# 0. SETUP ###################################

## 0.1 Load Packages #################################

import requests  # for HTTP requests
import json      # for working with JSON

# If you haven't already, install the requests package...
# pip install requests

## 0.2 Configuration #################################

# Select model of interest
# Note: Function calling requires a model that supports tools (e.g., smollm2:1.7b)
MODEL = "smollm2:1.7b"

# Set the port where Ollama is running
PORT = 11434
OLLAMA_HOST = f"http://localhost:{PORT}"
CHAT_URL = f"{OLLAMA_HOST}/api/chat"

# 1. DEFINE A FUNCTION TO BE USED AS A TOOL ###################################

# Define a function to be used as a tool
# This function must be defined in the global scope so it can be called
def add_two_numbers(x, y):
    """
    Add two numbers together.
    
    Parameters:
    -----------
    x : float
        First number
    y : float
        Second number
    
    Returns:
    --------
    float
        Sum of x and y
    """
    return x + y

# Define a second function to be used as a tool
# This gives the LLM a choice between multiple tools
def multiply_two_numbers(x, y):
    """
    Multiply two numbers together.
    
    Parameters:
    -----------
    x : float
        First number
    y : float
        Second number
    
    Returns:
    --------
    float
        Product of x and y
    """
    return x * y

# 2. DEFINE TOOL METADATA ###################################

# Define the tool metadata as a dictionary
# This tells the LLM what the function does and what parameters it needs
tool_add_two_numbers = {
    "type": "function",
    "function": {
        "name": "add_two_numbers",
        "description": "Add two numbers",
        "parameters": {
            "type": "object",
            "required": ["x", "y"],
            "properties": {
                "x": {
                    "type": "number",
                    "description": "first number"
                },
                "y": {
                    "type": "number",
                    "description": "second number"
                }
            }
        }
    }
}

# Define tool metadata for the multiply function
# Same structure as above, but describes multiplication
tool_multiply_two_numbers = {
    "type": "function",
    "function": {
        "name": "multiply_two_numbers",
        "description": "Multiply two numbers",
        "parameters": {
            "type": "object",
            "required": ["x", "y"],
            "properties": {
                "x": {
                    "type": "number",
                    "description": "first number"
                },
                "y": {
                    "type": "number",
                    "description": "second number"
                }
            }
        }
    }
}

# 3. CREATE CHAT REQUESTS WITH TOOLS ###################################

# Both tools are available for every request
# The LLM picks the right one based on the user's question
tools = [tool_add_two_numbers, tool_multiply_two_numbers]

# Friendly labels so we can print descriptive output
operation_labels = {
    "add_two_numbers": "Addition",
    "multiply_two_numbers": "Multiplication"
}
operation_symbols = {
    "add_two_numbers": "+",
    "multiply_two_numbers": "*"
}

# Two questions: one that should trigger addition, one multiplication
questions = [
    "What is 3 + 2?",
    "What is 7 * 4?"
]

# 4. EXECUTE THE TOOL CALLS ###################################

for question in questions:
    print(f"\nQuestion: {question}")

    # Build and send the request
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": question}],
        "tools": tools,
        "stream": False
    }
    response = requests.post(CHAT_URL, json=body)
    response.raise_for_status()
    result = response.json()

    # The LLM returns a tool_calls array with the function name and arguments
    if "tool_calls" in result.get("message", {}):
        for tool_call in result["message"]["tool_calls"]:
            func_name = tool_call["function"]["name"]
            raw_args = tool_call["function"].get("arguments", {})
            # Ollama may return args as a JSON string or an already-parsed dict
            func_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args

            func = globals().get(func_name)
            if func:
                output = func(**func_args)
                label = operation_labels.get(func_name, func_name)
                symbol = operation_symbols.get(func_name, "?")
                x, y = func_args.get("x"), func_args.get("y")
                print(f"  Tool chosen: {func_name}")
                print(f"  {label} of {x} {symbol} {y} is {output}")
    else:
        print("  No tool calls in response")
