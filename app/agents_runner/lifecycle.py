import os
import logging
from agents.mcp import MCPServerStreamableHttp
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.agents_runner import runner
from app.graph.core.registry import load_registry, AGENT_REGISTRY
from app.graph.workflow import build_graph
from app.core.config import settings

logger = logging.getLogger(__name__)

MCP_BASE_URL = os.getenv("MCP_SERVER_URL", "http://mcp-server:8001")


class AppLifecycle:
    """Manages MCP connections, agent creation, and graph compilation.

    To add a new agent:
    1. Create app/agents/<name>.py with create_agent(mcp_servers) function
    2. Add entry in registry.py (name, description, factory, mcp_url)
    That's it — no other changes needed.
    """

    def __init__(self):
        self._mcp_connections: dict[str, MCPServerStreamableHttp] = {}
        self._checkpointer = None
        self.graph = None

    async def startup(self):
        """Open MCP connections, create agents, build graph."""
        load_registry()

        for agent_key, meta in AGENT_REGISTRY.items():
            mcp_servers = []
            if meta.mcp_url:
                # Reuse existing connection or open a new one
                if meta.mcp_url not in self._mcp_connections:
                    url = f"{MCP_BASE_URL}{meta.mcp_url}"
                    conn = MCPServerStreamableHttp(params={"url": url})
                    await conn.__aenter__()
                    self._mcp_connections[meta.mcp_url] = conn
                    logger.info(f"MCP connection opened: {meta.mcp_url}")
                mcp_servers = [self._mcp_connections[meta.mcp_url]]

            runner.agents[agent_key] = meta.factory(mcp_servers=mcp_servers)
            logger.info(f"Agent created: {agent_key} (MCP: {meta.mcp_url or 'none'})")

        # Set up LangGraph checkpointer for state persistence
        self._checkpointer_ctx = AsyncPostgresSaver.from_conn_string(settings.DATABASE_URL)
        self._checkpointer = await self._checkpointer_ctx.__aenter__()
        await self._checkpointer.setup()

        self.graph = build_graph(checkpointer=self._checkpointer)
        logger.info(f"Graph compiled with {len(AGENT_REGISTRY)} agents.")

    async def shutdown(self):
        """Close all MCP connections cleanly."""
        await self._checkpointer_ctx.__aexit__(None, None, None)
        for path, conn in self._mcp_connections.items():
            await conn.__aexit__(None, None, None)
            logger.info(f"MCP connection closed: {path}")


# Single instance — used by main.py and stream.py
app_lifecycle = AppLifecycle()
