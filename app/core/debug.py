"""
Debug logging module.

Controls what gets logged at each level. Set DEBUG_LEVEL in .env:
  DEBUG_LEVEL=off      - no debug output (production default)
  DEBUG_LEVEL=agent    - agent lifecycle only (tool calls, responses)
  DEBUG_LEVEL=mcp      - agent + MCP manifest and tool execution
  DEBUG_LEVEL=llm      - agent + MCP + full OpenAI HTTP payloads (most verbose)
"""

import os
import json
import logging
import httpx
from typing import Any

DEBUG_LEVEL = os.getenv("DEBUG_LEVEL", "llm").lower()

# ── Formatters ────────────────────────────────────────────────────────────────

class PrettyJSONFormatter(logging.Formatter):
    """Formats log records that carry a 'payload' dict as indented JSON."""

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        if hasattr(record, "payload"):
            pretty = json.dumps(record.payload, indent=2, default=str)
            return f"{base}\n{pretty}"
        return base


def _get_handler() -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setFormatter(
        PrettyJSONFormatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    return handler


# ── OpenAI HTTP interceptor ───────────────────────────────────────────────────

class OpenAIRequestLogger:
    """
    Intercepts every outgoing HTTP request to the OpenAI API.
    Logs the full request body so you can see exactly what tools array
    and messages are sent to the LLM on each call.
    """

    def __init__(self):
        self.logger = logging.getLogger("debug.openai.request")

    async def __call__(self, request: httpx.Request) -> None:
        if "openai" not in str(request.url):
            return

        try:
            body = json.loads(request.content.decode())
        except Exception:
            return

        tools = body.get("tools", [])
        messages = body.get("messages", [])
        model = body.get("model", "unknown")

        # Always log a compact summary
        self.logger.info(
            f"→ OpenAI API call | model={model} | "
            f"messages={len(messages)} | tools={len(tools)}"
        )

        # Log tool names so you can see what manifest was sent
        if tools:
            tool_names = [t.get("function", {}).get("name", "?") for t in tools]
            self.logger.info(f"  Tools in request: {tool_names}")

        # Full payload only at llm level
        if DEBUG_LEVEL == "llm":
            record = self.logger.makeRecord(
                self.logger.name, logging.DEBUG,
                "(interceptor)", 0,
                "Full OpenAI request payload", (), None
            )
            record.payload = body
            self.logger.handle(record)


class OpenAIResponseLogger:
    """
    Intercepts every response from the OpenAI API.
    Logs tool_calls the LLM decided to make so you can see
    whether it picked the right tool.
    """

    def __init__(self):
        self.logger = logging.getLogger("debug.openai.response")

    async def __call__(self, response: httpx.Response) -> None:
        if "openai" not in str(response.url):
            return

        # Log basic response info regardless of body parse success
        status = response.status_code
        self.logger.info(f"← OpenAI response | status={status} | url={response.url}")

        try:
            await response.aread()
            body = response.json()
        except Exception:
            # Likely a streaming response — can't parse body
            self.logger.debug("  (streaming response — body not parseable)")
            return

        choices = body.get("choices", [])
        output = body.get("output", [])

        # Handle Responses API format (/v1/responses)
        if output:
            for item in output:
                if item.get("type") == "message":
                    content = item.get("content", [])
                    for block in content:
                        text = block.get("text", "")[:200]
                        self.logger.info(f"  Response content: {text}...")
                elif item.get("type") == "function_call":
                    name = item.get("name", "?")
                    self.logger.info(f"  LLM called tool: {name}")

            if DEBUG_LEVEL == "llm":
                record = self.logger.makeRecord(
                    self.logger.name, logging.DEBUG,
                    "(interceptor)", 0,
                    "Full OpenAI response output", (), None
                )
                record.payload = output
                self.logger.handle(record)
            return

        # Handle Chat Completions API format (/v1/chat/completions)
        for i, choice in enumerate(choices):
            finish_reason = choice.get("finish_reason")
            message = choice.get("message", {})
            tool_calls = message.get("tool_calls", [])

            if tool_calls:
                names = [tc.get("function", {}).get("name", "?") for tc in tool_calls]
                self.logger.info(
                    f"← OpenAI response | finish_reason={finish_reason} | "
                    f"LLM decided to call tools: {names}"
                )
            else:
                content_preview = str(message.get("content", ""))[:120]
                self.logger.info(
                    f"← OpenAI response | finish_reason={finish_reason} | "
                    f"content preview: {content_preview}..."
                )

            if DEBUG_LEVEL == "llm":
                record = self.logger.makeRecord(
                    self.logger.name, logging.DEBUG,
                    "(interceptor)", 0,
                    f"Full OpenAI response choice[{i}]", (), None
                )
                record.payload = choice
                self.logger.handle(record)


def _patch_openai_http_client():
    """
    Monkey-patches the OpenAI SDK's default httpx client to inject
    request/response logging hooks.
    """
    try:
        import openai
        req_logger = OpenAIRequestLogger()
        res_logger = OpenAIResponseLogger()

        original_init = openai.AsyncOpenAI.__init__

        def patched_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self._client.event_hooks["request"].append(req_logger)
            self._client.event_hooks["response"].append(res_logger)

        openai.AsyncOpenAI.__init__ = patched_init
        logging.getLogger("debug.openai").info(
            "OpenAI HTTP interceptor installed — will log all API calls."
        )
    except Exception as e:
        logging.getLogger("debug.openai").warning(
            f"Could not install OpenAI HTTP interceptor: {e}"
        )


# ── MCP manifest logger ───────────────────────────────────────────────────────

def _patch_mcp_client():
    """
    Patches MCPServerStreamableHttp to log the tool manifest
    returned by the MCP server at startup.
    """
    try:
        from agents.mcp import MCPServerStreamableHttp
        mcp_logger = logging.getLogger("debug.mcp")

        original_list = MCPServerStreamableHttp.list_tools

        async def patched_list_tools(self):
            tools = await original_list(self)
            mcp_logger.info(
                f"MCP manifest received — {len(tools)} tool(s) registered:"
            )
            for t in tools:
                name = getattr(t, "name", "?")
                desc = (getattr(t, "description", "") or "")[:100]
                schema = getattr(t, "inputSchema", {})
                params = list((schema.get("properties") or {}).keys())
                mcp_logger.info(f"  • {name}({', '.join(params)}) — {desc}")
            return tools

        MCPServerStreamableHttp.list_tools = patched_list_tools
        mcp_logger.info("MCP manifest interceptor installed.")
    except Exception as e:
        logging.getLogger("debug.mcp").warning(
            f"Could not install MCP interceptor: {e}"
        )


# ── Agent runner logger ───────────────────────────────────────────────────────

def _configure_agent_logger():
    """Configures the runner logger to show query/response lifecycle."""
    logger = logging.getLogger("app.agents_runner.lifecycle")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(_get_handler())


# ── Public entry point ────────────────────────────────────────────────────────

def setup_debug_logging():
    """
    Call once at app startup (main.py).
    Controlled entirely by DEBUG_LEVEL env var — no code changes needed.

    DEBUG_LEVEL=off    → nothing enabled
    DEBUG_LEVEL=agent  → agent lifecycle logs
    DEBUG_LEVEL=mcp    → agent + MCP manifest logs
    DEBUG_LEVEL=llm    → agent + MCP + full OpenAI HTTP payloads
    """
    if DEBUG_LEVEL == "off":
        return

    root_debug_logger = logging.getLogger("debug")
    root_debug_logger.setLevel(logging.DEBUG)
    if not root_debug_logger.handlers:
        root_debug_logger.addHandler(_get_handler())

    _configure_agent_logger()

    if DEBUG_LEVEL in ("mcp", "llm"):
        _patch_mcp_client()

    if DEBUG_LEVEL == "llm":
        _patch_openai_http_client()

    logging.getLogger("debug").info(
        f"Debug logging active — level={DEBUG_LEVEL.upper()}"
    )
