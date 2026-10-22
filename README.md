# Routine Doctor (Alexa+ Track) — Smart Home Routine Failure Simulator

Routine Doctor is a web-based simulator that diagnoses **why smart home routines fail**, presenting results in two views:

- **Homeowner view**: plain-language explanation of *what broke, when it broke, why it broke, and what to do next*.
- **Developer view**: workflow graph, timestamps, evidence/trace, failure classification, and fix guidance.

This project was built for the **Amazon Developer Hackathon (Alexa+ Track)** and includes a compliant **MCP (Model Context Protocol)** server implementation for demo purposes.

---

## What This Project Demonstrates

### Devices simulated
- Smart light
- Motion sensor
- Smart lock

### Failure types simulated
- **F1 — Device unreachable**: the routine fails because a device cannot be contacted.
- **F2 — Stale / incorrect state**: the routine makes a decision using outdated device state (e.g., `timeOfSample` too old).
- **F3 — Capability mismatch**: the routine/integration expects a capability that the device does not actually support (declared vs actual mismatch).

### Fixes
- **Routine-level fixes** (safe to auto-apply): configuration changes to improve robustness.
- **Integration-level fixes** (manual guidance): recommendations for device/integration developers.

### Deterministic replay
After applying a compatible fix, you can replay the same scenario and see behavior change from **FAIL → PASS** (where applicable).

---

## Architecture Overview

### Frontend (Web UI)
- React + Vite + TypeScript
- React Router
- React Flow (workflow graph rendering)
- Uses **REST API endpoints** under: `http://localhost:8000/api/*`

> Note: The UI does **not** call MCP. MCP exists to meet hackathon requirements and is demoed separately.

### Backend (API + Simulator + MCP)
- FastAPI (Python 3.11+)
- SQLite persistence (`backend/data/routine_doctor.sqlite3`)
- REST API under `/api/*`
- MCP server mounted at `/mcp` using **Streamable HTTP**

### MCP Compliance Notes
- Implements MCP tools and Streamable HTTP transport aligned with the Alexa+ MCP QuickStart direction.
- OAuth metadata endpoints are present, but **auth enforcement is currently deferred** (demo-friendly local mode).

---

## Repository Layout (High Level)

- `backend/` — FastAPI app, simulator logic, SQLite DB, MCP server
- `frontend/` — React web UI

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** (recommended)
- Windows PowerShell / macOS Terminal / Linux shell

---

## Quick Start (Local)

### 1) Start the backend
From the repo root:

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

pip install --no-deps git+https://github.com/modelcontextprotocol/python-sdk.git@2af9e3089ac66b35c1550c500aae86a82efb1e17

uvicorn app.main:app --reload --port 8000

cd frontend
npm install
npm run dev
 
### 1) Initialize
## PowerShell

curl.exe -i -X POST "http://localhost:8000/mcp" `
  -H "Content-Type: application/json" `
  -H "MCP-Session-Id: demo" `
  --data '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"powershell-curl","version":"1.0"}}}'
### 2) tools/list
## PowerShell

curl.exe -s -X POST "http://localhost:8000/mcp" `
  -H "Content-Type: application/json" `
  -H "MCP-Session-Id: demo" `
  --data '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
### 3) tools/call (example: list_routines)
## PowerShell

curl.exe -s -X POST "http://localhost:8000/mcp" `
  -H "Content-Type: application/json" `
  -H "MCP-Session-Id: demo" `
  --data '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"list_routines","arguments":{}}}'

