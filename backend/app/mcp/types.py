# Minimal MCP type stubs for Routine Doctor backend

class TextContent:
    def __init__(self, type: str, text: str):
        self.type = type
        self.text = text

class Tool:
    def __init__(self, name: str, description: str, input_schema: dict):
        self.name = name
        self.description = description
        self.input_schema = input_schema

class ListToolsResult:
    def __init__(self, tools: list):
        self.tools = tools

class CallToolResult:
    def __init__(self, content: list = None, isError: bool = False):
        self.content = content or []
        self.isError = isError
