# render_mermaid.py
# Quick utility to render a mermaid diagram to PNG via mermaid.ink
# Usage: python3 render_mermaid.py

import base64
import urllib.request

# Mermaid diagram from 02_productivity/shiny_app/TOOL_design.md
MERMAID_CODE = """
flowchart LR
    subgraph inputs["Inputs"]
        API[NYT Books API]
        JSON[(bestsellers.json)]
    end

    subgraph tool["Bestseller Explorer"]
        FETCH[Fetch / load list data]
        FORMAT_T[Format to table]
        FORMAT_G[Format to top-10 chart]
        SORT[Sort by rank / weeks / title / author]
    end

    subgraph outputs["Outputs"]
        TABLE[Recommendations table]
        CHART[Weeks-on-list bar chart]
    end

    API --> FETCH
    JSON --> FETCH
    FETCH --> SORT
    SORT --> FORMAT_T
    SORT --> FORMAT_G
    FORMAT_T --> TABLE
    FORMAT_G --> CHART
""".strip()

# Use kroki.io to render the mermaid diagram to PNG
url = "https://kroki.io/mermaid/png"

payload = MERMAID_CODE.encode("utf-8")
req = urllib.request.Request(url, data=payload, method="POST")
req.add_header("Content-Type", "text/plain")

print("Fetching rendered diagram from kroki.io...")
response = urllib.request.urlopen(req)
data = response.read()

with open("diagram.png", "wb") as f:
    f.write(data)

print(f"Saved diagram.png ({len(data)} bytes)")
