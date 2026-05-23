import sys
from pathlib import Path

# Add workspace root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP

# Import Tools
from app.core.tools.budget_tools import allocate_monthly_finances, assess_financial_health
from app.core.tools.debt_tools import plan_debt_payoff
from app.core.tools.investment_tools import suggest_investment_strategy, calculate_compounding, plan_goal_investment
from app.core.tools.tax_tools import register_tax_tools

# ── Separate MCP server per domain ──────────────────────────────────
# Each agent only sees its own tools — supervisor decides who handles the query.

budget_mcp = FastMCP("budget-tools")
budget_mcp.tool()(allocate_monthly_finances)
budget_mcp.tool()(assess_financial_health)

tax_mcp = FastMCP("tax-tools")
register_tax_tools(tax_mcp)

investment_mcp = FastMCP("investment-tools")
investment_mcp.tool()(suggest_investment_strategy)
investment_mcp.tool()(calculate_compounding)
investment_mcp.tool()(plan_goal_investment)

debt_mcp = FastMCP("debt-tools")
debt_mcp.tool()(plan_debt_payoff)

# ── Compose via Starlette for path-based routing ─────────────────────
if __name__ == "__main__":
    import uvicorn
    from contextlib import asynccontextmanager, AsyncExitStack
    from starlette.applications import Starlette
    from starlette.routing import Mount

    sub_apps = {
        "/budget": budget_mcp.http_app(),
        "/tax": tax_mcp.http_app(),
        "/investment": investment_mcp.http_app(),
        "/debt": debt_mcp.http_app(),
    }

    @asynccontextmanager
    async def lifespan(app):
        async with AsyncExitStack() as stack:
            for sub_app in sub_apps.values():
                await stack.enter_async_context(sub_app.router.lifespan_context(app))
            yield

    app = Starlette(
        routes=[Mount(path, app=sub_app) for path, sub_app in sub_apps.items()],
        lifespan=lifespan,
    )
    uvicorn.run(app, host="0.0.0.0", port=8001)
