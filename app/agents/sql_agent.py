from agents import Agent
from app.core.config import settings

AGENT_NAME = "SQL Agent"

SYSTEM_PROMPT = """You are a database query agent. You translate user questions into SQL queries and return structured results.

Your capabilities:
- Query the internal database for financial records, transactions, and reports
- Return structured tabular data

Rules:
- Only use SELECT queries — never INSERT, UPDATE, DELETE, or DROP.
- Limit results to 50 rows unless user asks for more.
- Format output as clean tables or lists.
- If the query is ambiguous, ask for clarification before running SQL.
"""


def create_agent(mcp_servers: list = None) -> Agent:
    return Agent(
        name=AGENT_NAME,
        model=settings.OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        mcp_servers=mcp_servers or [],
    )
