# ArchInsight

**VLM-Powered Multi-Agent Architecture Review System**

ArchInsight is a 3-agent pipeline that analyzes software and integration architecture diagrams and produces a structured architecture review. It uses a vision-language model to interpret diagram images and two text-based LLM agents to assess strengths, risks, and recommend improvements.

---

## Architecture

```mermaid
flowchart TD
    input["diagram.png\n(Architecture Diagram)"]
    fallback["sample_data.py\n(Fallback Description)"]

    subgraph agent1 ["Agent 1 — Visual Architecture Interpreter"]
        A1_role["System Prompt:\nVISUAL_INTERPRETER_PROMPT"]
        A1_task["User Message:\nAnalyze this architecture diagram"]
        A1_img["Image: base64-encoded diagram"]
        A1_out["Output:\n- Architecture Type\n- Detected Components\n- Inferred Data Flow\n- Diagram Summary"]
    end

    subgraph agent2 ["Agent 2 — Systems / Integration Analyst"]
        A2_role["System Prompt:\nSYSTEMS_ANALYST_PROMPT"]
        A2_task["User Message:\nAgent 1 output"]
        A2_out["Output:\n- Strengths\n- Risks / Weaknesses\n- Assumptions\n- Overall Assessment"]
    end

    subgraph agent3 ["Agent 3 — Solution Architect Advisor"]
        A3_role["System Prompt:\nSOLUTION_ARCHITECT_PROMPT"]
        A3_task["User Message:\nAgent 1 + Agent 2 outputs"]
        A3_out["Output:\n- Recommended Improvements\n- Reliability / Scalability\n- Observability / Security\n- Final Review Summary"]
    end

    input -->|"VLM mode (llava)"| A1_img
    fallback -->|"Fallback mode"| A1_out
    A1_role --> A1_out
    A1_task --> A1_out
    A1_img --> A1_out

    A1_out -->|"agent1_output"| A2_task
    A2_role --> A2_out
    A2_task --> A2_out

    A1_out -->|"agent1_output"| A3_task
    A2_out -->|"agent2_output"| A3_task
    A3_role --> A3_out
    A3_task --> A3_out

    A3_out --> final["Final Review\n(printed to terminal)"]
```

---

## Agents

| Agent | Role | Model | Input | Output |
|-------|------|-------|-------|--------|
| **Agent 1** — Visual Architecture Interpreter | Interprets an architecture diagram image | VLM (`llava`) | Architecture diagram image | Architecture type, detected components, inferred data flow, summary |
| **Agent 2** — Systems / Integration Analyst | Analyzes the architecture critically | Text LLM (`smollm2:1.7b`) | Agent 1 output | Strengths, risks/weaknesses, assumptions, overall assessment |
| **Agent 3** — Solution Architect Advisor | Recommends improvements | Text LLM (`smollm2:1.7b`) | Agent 1 + Agent 2 outputs | Improvements, reliability/scalability, observability/security, final review |

---

## Project Structure

```
ArchInsight/
├── main.py          # Orchestrator — runs the 3-agent pipeline
├── prompts.py       # System prompts for all 3 agents
├── agents.py        # Agent functions with VLM support (extends course functions.py)
├── sample_data.py   # Fallback sample data when no VLM is available
└── README.md        # This file
```

---

## Setup

### 1. Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/) installed and running
- `requests` package (`pip install requests`)

### 2. Pull Models

```bash
# Vision-language model for Agent 1
ollama pull llava

# Text model for Agents 2 and 3
ollama pull smollm2:1.7b
```

### 3. Start Ollama

```bash
ollama serve
```

---

## Usage

### With a real architecture diagram

```bash
cd 06_agents/ArchInsight
python main.py path/to/your/diagram.png
```

Agent 1 will send the image to the `llava` VLM for interpretation.

### Without a diagram (fallback mode)

```bash
cd 06_agents/ArchInsight
python main.py
```

The pipeline uses a pre-written sample architecture description (a microservices e-commerce system) so you can test the full workflow without a VLM model.

---

## Prompt Iteration

The system prompts in `prompts.py` are designed as strong first drafts. Look for `# ITERATE:` comments throughout the file — these mark specific areas where you can refine the prompts based on actual model outputs:

- Adjust verbosity constraints if outputs are too long or too short
- Add domain-specific probes if analysis is too generic
- Tighten output format requirements if markdown structure drifts

---

## References

- [`02_using_ollama.py`](../02_using_ollama.py) — Basic Ollama system prompts
- [`03_agents.py`](../03_agents.py) — Multi-agent workflow example
- [`04_rules.py`](../04_rules.py) — Agent rules with YAML
- [`functions.py`](../functions.py) — Helper functions for agent orchestration
