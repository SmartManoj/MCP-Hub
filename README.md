# MCP-Hub

A FastAPI-based MCP hub server that acts as the central entry point for routing and managing connections to multiple MCP services (such as linkup, mem0, and spotify). It supports Server-Sent Events (SSE) and message forwarding to backend MCP servers.


Install dependencies:
```bash
pip install -r requirements.txt
```

## Setup & Running
1. Clone or download this repository.
2. Start the hub server with Python:
   ```bash
   python mcp_hub.py
   ```
   Or run with uvicorn directly:
   ```bash
   uvicorn mcp_hub:app --host 0.0.0.0 --port 7000 --reload
   ```
   The server will run on `http://localhost:7000` by default.

