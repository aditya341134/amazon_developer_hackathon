# Setup

## Prereqs
- Python 3.11+
- Node 18+
- (Optional) cloudflared for HTTPS tunnel

## Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main

Backend: http://localhost:8000

## Frontend
cd frontend
npm install
cp .env.example .env
npm run dev

Frontend: http://localhost:5173

## Optional: HTTPS tunnel (remote URL realism)
cloudflared tunnel --url http://localhost:8000
Set BACKEND_PUBLIC_BASE_URL to the generated https://... URL so PRM metadata uses the canonical URI.

## Auth notes
- In dev mode, you may provide a “demo token mint” flow for convenience,
  but keep the well-known docs and endpoints present and correct.