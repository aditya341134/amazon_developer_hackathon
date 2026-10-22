from pydantic import BaseModel
import os


class Settings(BaseModel):
    # DB: when you run uvicorn from the backend/ folder,
    # this creates backend/data/routine_doctor.sqlite3 (clean)
    db_path: str = os.getenv("DB_PATH", "data/routine_doctor.sqlite3")

    # CORS (safer)
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    # MCP streamable-http behavior (SSE by default)
    mcp_json_response: bool = os.getenv("MCP_JSON_RESPONSE", "0") == "1"

    # Auth toggle (extra feature later)
    auth_enabled: bool = os.getenv("AUTH_ENABLED", "0") == "1"

    # Canonical public URL (for PRM metadata; optional in local dev)
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")


settings = Settings()