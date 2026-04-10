# 05_lab_multi_agent_workflow.py
# Lab: Multi-Agent Statistical Comparison Report
# Tim Fraser
#
# This script builds a 2-agent workflow using function calling.
# Agent 1 uses a custom tool (run_correlation) to compute correlation and
# regression statistics between two columns of a dataset.
# Agent 2 takes those results and writes a plain-English interpretation.

# 0. SETUP ###################################

## 0.1 Load Packages #################################

import requests  # for HTTP requests
import json      # for working with JSON
import pandas as pd  # for data manipulation
import numpy as np   # for numerical operations

# If you haven't already, install these packages...
# pip install requests pandas numpy

## 0.2 Load Functions #################################

# Load helper functions for agent orchestration
from functions import agent_run, df_as_text

## 0.3 Configuration #################################

# Select model of interest
MODEL = "smollm2:1.7b"

# Load datasets from Rdatasets (same source as the MCP server)
_DATASET_URLS = {
    "mtcars": "https://vincentarelbundock.github.io/Rdatasets/csv/datasets/mtcars.csv",
    "iris": "https://vincentarelbundock.github.io/Rdatasets/csv/datasets/iris.csv",
}
DATASETS = {name: pd.read_csv(url) for name, url in _DATASET_URLS.items()}

# 1. DEFINE CUSTOM TOOL FUNCTION ###################################

def run_correlation(dataset_name, col_x, col_y):
    """
    Compute Pearson correlation and simple linear regression between two
    numeric columns of a dataset.

    Parameters:
    -----------
    dataset_name : str
        Dataset to use ('mtcars' or 'iris')
    col_x : str
        Name of the x (predictor) column
    col_y : str
        Name of the y (response) column

    Returns:
    --------
    str
        JSON string with correlation, slope, intercept, r_squared, and n
    """
    if dataset_name not in DATASETS:
        raise ValueError(f"Unknown dataset: '{dataset_name}' — choose 'mtcars' or 'iris'")

    df = DATASETS[dataset_name]

    if col_x not in df.columns:
        raise ValueError(f"Column '{col_x}' not found. Available: {list(df.columns)}")
    if col_y not in df.columns:
        raise ValueError(f"Column '{col_y}' not found. Available: {list(df.columns)}")

    x = df[col_x].dropna()
    y = df[col_y].dropna()

    # Align on shared non-null indices
    shared = x.index.intersection(y.index)
    x = x.loc[shared]
    y = y.loc[shared]

    # Pearson correlation
    correlation = round(float(np.corrcoef(x, y)[0, 1]), 4)

    # Simple linear regression: y = slope * x + intercept
    slope, intercept = np.polyfit(x, y, 1)
    r_squared = round(correlation ** 2, 4)

    result = {
        "dataset": dataset_name,
        "col_x": col_x,
        "col_y": col_y,
        "n": int(len(shared)),
        "correlation": correlation,
        "slope": round(float(slope), 4),
        "intercept": round(float(intercept), 4),
        "r_squared": r_squared,
    }

    return json.dumps(result, indent=2)

# 2. DEFINE TOOL METADATA ###################################

# Tell the LLM what run_correlation does and what arguments it needs.
# The LLM reads this schema to decide when and how to call the tool.
tool_run_correlation = {
    "type": "function",
    "function": {
        "name": "run_correlation",
        "description": (
            "Compute Pearson correlation and simple linear regression (slope, intercept, R-squared) "
            "between two numeric columns of a dataset. Available datasets: 'mtcars' (columns: mpg, cyl, "
            "disp, hp, drat, wt, qsec, vs, am, gear, carb) and 'iris' (columns: Sepal.Length, "
            "Sepal.Width, Petal.Length, Petal.Width)."
        ),
        "parameters": {
            "type": "object",
            "required": ["dataset_name", "col_x", "col_y"],
            "properties": {
                "dataset_name": {
                    "type": "string",
                    "description": "Dataset to analyze. Options: 'mtcars' or 'iris'.",
                },
                "col_x": {
                    "type": "string",
                    "description": "Name of the x (predictor) column.",
                },
                "col_y": {
                    "type": "string",
                    "description": "Name of the y (response) column.",
                },
            },
        },
    },
}

# 3. MULTI-AGENT WORKFLOW ###################################

print("=" * 60)
print("  Multi-Agent Statistical Comparison Report")
print("=" * 60)

## 3.1 Agent 1: Data Analyst (with tool) #################################

# Agent 1 has access to the run_correlation tool.
# It receives a natural-language question and must decide
# which dataset and columns to pass to the tool.

role1 = (
    "You are a data analyst. Use the run_correlation tool to compute "
    "statistical relationships between variables in a dataset. "
    "Always call the tool — do not guess the numbers."
)

task1 = "Analyze the relationship between horsepower (hp) and fuel economy (mpg) in the mtcars dataset."

print()
print("Agent 1: Data Analyst")
print(f"  Task: {task1}")
print("  Running...")

result1_calls = agent_run(
    role=role1,
    task=task1,
    model=MODEL,
    output="tools",
    tools=[tool_run_correlation],
)

# Extract the tool output (JSON string with stats)
result1_output = (
    result1_calls[0].get("output", "{}")
    if isinstance(result1_calls, list) and len(result1_calls) > 0
    else "{}"
)

print()
print("Agent 1 Result (Statistical Analysis):")
print(result1_output)

## 3.2 Agent 2: Report Writer (no tools) #################################

# Agent 2 takes the raw statistics from Agent 1 and writes
# a clear, plain-English interpretation — no tools needed.

role2 = (
    "You are a statistics report writer. Given raw statistical output "
    "(correlation, slope, intercept, R-squared, sample size), write a "
    "clear 3-5 sentence interpretation in plain English. Explain the "
    "direction and strength of the relationship, what the slope means "
    "practically, and how much variance R-squared explains."
)

task2 = (
    f"Here are the statistical results to interpret:\n\n{result1_output}\n\n"
    "Write a brief plain-English report explaining these findings."
)

print()
print("Agent 2: Report Writer")
print("  Task: Interpret the statistical results")
print("  Running...")

result2 = agent_run(
    role=role2,
    task=task2,
    model=MODEL,
    output="text",
    tools=None,
)

print()
print("Agent 2 Result (Interpretation Report):")
print(result2)
print()
print("=" * 60)
print("  Workflow complete!")
print("=" * 60)
