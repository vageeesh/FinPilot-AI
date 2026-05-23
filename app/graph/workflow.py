from __future__ import annotations

import asyncio
import logging
from langgraph.graph import StateGraph, END
from app.graph.core.state import AgentState
from app.graph.agents.supervisor import supervisor_step

logger = logging.getLogger(__name__)


async def _run_agent(agent_name: str, state: AgentState) -> tuple[str, dict]:
    """Run a single agent and return (name, result)."""
    from app.agents_runner.runner import run_agent

    try:
        result = await run_agent(agent_name, state)
        return agent_name, result
    except Exception as e:
        logger.error(f"Agent '{agent_name}' failed: {e}")
        return agent_name, {
            "results": {agent_name: f"Error: {str(e)}"},
            "intermediate_steps": [{"agent": agent_name, "output": f"Error: {str(e)}"}],
        }


async def execute_phase(state: AgentState) -> AgentState:
    """Execute the current phase — runs all agents in the phase in parallel."""
    plan = state.get("plan", [])
    current_phase = state.get("current_phase", 0)

    agents_in_phase = plan[current_phase]
    logger.info(f"Executing phase {current_phase + 1}/{len(plan)}: {agents_in_phase}")

    # Run all agents in this phase concurrently
    tasks = [_run_agent(agent_name, state) for agent_name in agents_in_phase]
    results_list = await asyncio.gather(*tasks)

    # Merge results
    merged_results = {**state.get("results", {})}
    new_steps = list(state.get("intermediate_steps", []))

    for agent_name, agent_result in results_list:
        agent_results = agent_result.get("results", {})
        merged_results.update(agent_results)
        new_steps.extend(agent_result.get("intermediate_steps", []))

    updated = {
        **state,
        "results": merged_results,
        "intermediate_steps": new_steps,
        "current_phase": current_phase + 1,
    }

    # Single-agent shortcut: if only one agent has ever run, skip supervisor synthesis
    if len(merged_results) == 1 and current_phase + 1 >= len(plan):
        agent_name = next(iter(merged_results))
        updated["final_answer"] = merged_results[agent_name]
        updated["done"] = True

    return updated


def _route_after_supervisor(state: AgentState) -> str:
    """After supervisor: if done → END, otherwise execute the plan."""
    return END if state.get("done") else "execute_phase"


def _route_after_execute(state: AgentState) -> str:
    """After executing a phase: more phases? Continue. Otherwise back to supervisor."""
    plan = state.get("plan", [])
    current_phase = state.get("current_phase", 0)

    if current_phase < len(plan):
        return "execute_phase"

    # Single-agent total — skip supervisor re-call, use agent output directly
    if state.get("done"):
        return END

    return "supervisor"


def build_graph(checkpointer=None) -> StateGraph:
    workflow = StateGraph(AgentState)

    # ── Nodes ────────────────────────────────────────────────────────
    workflow.add_node("supervisor", supervisor_step)
    workflow.add_node("execute_phase", execute_phase)

    # ── Entry ────────────────────────────────────────────────────────
    workflow.set_entry_point("supervisor")

    # ── Edges ────────────────────────────────────────────────────────
    workflow.add_conditional_edges("supervisor", _route_after_supervisor, {
        "execute_phase": "execute_phase",
        END: END,
    })

    workflow.add_conditional_edges("execute_phase", _route_after_execute, {
        "execute_phase": "execute_phase",
        "supervisor": "supervisor",
        END: END,
    })

    return workflow.compile(checkpointer=checkpointer)