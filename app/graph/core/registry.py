from __future__ import annotations

from pydantic import BaseModel
from typing import Callable, Any

from app.agents.constants import (
    BUDGET_AGENT, TAX_AGENT, INVESTMENT_AGENT, DEBT_AGENT, SQL_AGENT,
)


class AgentMeta(BaseModel):
    name: str
    description: str
    factory: Callable[..., Any]  # create_agent(mcp_servers) → Agent
    mcp_url: str | None = None   # MCP endpoint path (relative to MCP_BASE_URL)

    model_config = {"arbitrary_types_allowed": True}


# ── Registry ─────────────────────────────────────────────────────────
# Single source of truth for all agents.
# To add a new agent:
#   1. Create app/agents/<name>.py with create_agent(mcp_servers) function
#   2. Add entry below — that's it.

def _get_registry() -> dict[str, AgentMeta]:
    from app.agents.budget_agent import create_agent as create_budget_agent
    from app.agents.tax_agent import create_agent as create_tax_agent
    from app.agents.investment_agent import create_agent as create_investment_agent
    from app.agents.debt_agent import create_agent as create_debt_agent
    from app.agents.sql_agent import create_agent as create_sql_agent

    return {
        BUDGET_AGENT: AgentMeta(
            name=BUDGET_AGENT,
            description=(
                "Personal finance advisor for budget planning and financial health. "
                "Allocates monthly income using invest-first approach, assesses financial "
                "health score (1-10), and flags unhealthy spending patterns."
            ),
            factory=create_budget_agent,
            mcp_url="/budget/mcp",
        ),
        TAX_AGENT: AgentMeta(
            name=TAX_AGENT,
            description=(
                "Indian income tax calculator and ITR filing guide. Compares New vs Old "
                "regime, handles multi-head income (salary, rental, capital gains, FD), "
                "optimizes deductions (80C, 80D, HRA, NPS), and generates ITR field mapping."
            ),
            factory=create_tax_agent,
            mcp_url="/tax/mcp",
        ),
        INVESTMENT_AGENT: AgentMeta(
            name=INVESTMENT_AGENT,
            description=(
                "Investment strategy and goal planning. Suggests asset allocation based on "
                "age and risk tolerance, shows compounding projections, and calculates "
                "SIP needed for financial goals (education, house, retirement)."
            ),
            factory=create_investment_agent,
            mcp_url="/investment/mcp",
        ),
        DEBT_AGENT: AgentMeta(
            name=DEBT_AGENT,
            description=(
                "Debt payoff advisor. Compares Avalanche vs Snowball strategies, simulates "
                "payoff timelines, and shows interest savings from extra payments."
            ),
            factory=create_debt_agent,
            mcp_url="/debt/mcp",
        ),
        # ── Future agents — just add here ─────────────────────────────
        # "document_agent": AgentMeta(
        #     name="document_agent",
        #     description="Parses Form 16, bank statements, AIS PDFs...",
        #     handler=partial(run_agent, "document_agent"),
        #     mcp_url="/documents/mcp",
        # ),
    }


AGENT_REGISTRY: dict[str, AgentMeta] = {}


def load_registry():
    global AGENT_REGISTRY
    AGENT_REGISTRY = _get_registry()