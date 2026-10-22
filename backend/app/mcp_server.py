import logging

try:
    import mcp.types as types
except ImportError:
    # Fallback minimal stub definitions for type hints used in the server
    class _Stub:
        pass
    class PaginatedRequestParams(_Stub):
        pass
    class ListToolsResult(_Stub):
        pass
    class CallToolRequestParams(_Stub):
        pass
    class CallToolResult(_Stub):
        pass
    types = type('types', (), {
        'PaginatedRequestParams': PaginatedRequestParams,
        'ListToolsResult': ListToolsResult,
        'CallToolRequestParams': CallToolRequestParams,
        'CallToolResult': CallToolResult,
    })
try:
    from mcp.server import Server, ServerRequestContext
except ImportError:
    # Minimal stub for Server to allow app start without full MCP SDK
    from fastapi import FastAPI
    class ServerRequestContext:
        pass
    class Server:
        def __init__(self, name: str, on_list_tools=None, on_call_tool=None):
            self.name = name
            self.on_list_tools = on_list_tools
            self.on_call_tool = on_call_tool
        def streamable_http_app(self, event_store=None, json_response=True, debug=False):
            # Return a simple FastAPI app with placeholder routes
            app = FastAPI(title=f"{self.name} MCP Stub")
            @app.get("/tools")
            async def list_tools_stub():
                return {"tools": []}
            @app.post("/call")
            async def call_tool_stub():
                return {"result": "stub"}
            return app
from starlette.middleware.cors import CORSMiddleware

from app.mcp.transport import InMemoryEventStore
from app.mcp.tools import list_tools, call_tool
from app.settings import settings

logger = logging.getLogger(__name__)


def build_mcp_starlette_app(conn):
    async def handle_list_tools(
        ctx: ServerRequestContext,
        params: types.PaginatedRequestParams | None,
    ) -> types.ListToolsResult:
        return list_tools()

    async def handle_call_tool(
        ctx: ServerRequestContext,
        params: types.CallToolRequestParams,
    ) -> types.CallToolResult:
        return await call_tool(conn, ctx, params)

    server = Server(
        "routine-doctor",
        on_list_tools=handle_list_tools,
        on_call_tool=handle_call_tool,
    )

    event_store = InMemoryEventStore()

    starlette_app = server.streamable_http_app(
        event_store=event_store,
        json_response=settings.mcp_json_response,
        debug=True,
    )

    # Note: streamable_http_app() enforces localhost-only Origin by default.
    # We still wrap with CORS to ensure consistent headers for local tooling.
    starlette_app = CORSMiddleware(
        starlette_app,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE"],
        expose_headers=["Mcp-Session-Id"],
    )

    return starlette_app