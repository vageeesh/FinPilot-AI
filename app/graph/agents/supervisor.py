from app.core.config import settings
from agents import Agent, Runner
from pydantic import BaseModel
from typing import Optional, List
from app.graph.core.state import AgentState


class SupervisorOutput(BaseModel):
    action: str                            # "PLAN" or "DONE"
    phases: Optional[List[List[str]]] = None  # when action == "PLAN"
    reasoning: str
    final_answer: Optional[str] = None     # when action == "DONE"


SUPERVISOR_INSTRUCTIONS = """You are the brain of a multi-agent personal finance system.

You are called in two situations:
1. FIRST CALL — No results yet. Analyze the query and create an execution plan.
2. AFTER EXECUTION — Results are available. Review and either produce the final answer or plan more work.

Output rules:
- action="PLAN": Set phases (list of lists). Each inner list = agents that run IN PARALLEL. Phases run sequentially.
  - Put independent agents in the SAME phase (parallel).
  - Put dependent agents in LATER phases (sequential — they'll see earlier results).
- action="DONE": Set final_answer with a clean, concise, well-structured markdown response.
  - Synthesize all agent results naturally into one cohesive answer.
  - Directly address the user's query. Never mention agents, steps, or system internals.

Special cases:
- If the query is conversational (greetings, chitchat) and needs NO tools → immediately return action="DONE" with a direct answer.
- If results are incomplete after execution → return action="PLAN" with additional phases.
- Only use agent keys from the available agents list.

Examples:
- "Plan my budget" → PLAN, phases=[["budget_agent"]]
- "Plan budget and calculate tax" → PLAN, phases=[["budget_agent", "tax_agent"]]  (independent, parallel)
- "Plan budget then suggest investments based on surplus" → PLAN, phases=[["budget_agent"], ["investment_agent"]]
- "Hello!" → DONE, final_answer="Hello! How can I help with your finances today?"
"""


def _build_prompt(state: AgentState) -> str:
    from app.graph.core.registry import AGENT_REGISTRY

    agents_block = "\n".join([
        f"- {name}: {meta.description}"
        for name, meta in AGENT_REGISTRY.items()
    ])

    results = state.get("results", {})
    if results:
        results_block = "\n\n".join([
            f"[{agent}]:\n{str(output)[:800]}"
            for agent, output in results.items()
        ])
    else:
        results_block = "No results yet."

    return f"""User query: {state['user_query']}

Available agents:
{agents_block}

Collected results:
{results_block}

Decide: PLAN (which agents to run next) or DONE (produce final answer)."""


MAX_ITERATIONS = 5


async def supervisor_step(state: AgentState) -> AgentState:
    """Single supervisor — plans execution and produces final answer."""
    from app.graph.core.registry import AGENT_REGISTRY

    iteration = state.get("iteration", 0) + 1

    # Guard: force DONE if too many iterations
    if iteration > MAX_ITERATIONS:
        results = state.get("results", {})
        fallback = "\n\n".join(str(v)[:500] for v in results.values()) if results else "Unable to complete the request."
        return {
            **state,
            "iteration": iteration,
            "final_answer": fallback,
            "done": True,
        }

    supervisor = Agent(
        name="Supervisor",
        instructions=SUPERVISOR_INSTRUCTIONS,
        output_type=SupervisorOutput,
        model=settings.OPENAI_MODEL,
    )

    result = await Runner.run(supervisor, input=_build_prompt(state))
    decision: SupervisorOutput = result.final_output

    if decision.action == "DONE":
        return {
            **state,
            "iteration": iteration,
            "final_answer": decision.final_answer,
            "plan_reasoning": decision.reasoning,
            "done": True,
        }

    # action == "PLAN" — validate and set phases
    valid_agents = set(AGENT_REGISTRY.keys())
    validated_phases = [
        [a for a in phase if a in valid_agents]
        for phase in (decision.phases or [])
    ]
    validated_phases = [p for p in validated_phases if p]

    # Safety: if LLM returns empty plan, force DONE
    if not validated_phases:
        return {
            **state,
            "final_answer": decision.reasoning,
            "plan_reasoning": decision.reasoning,
            "done": True,
        }

    return {
        **state,
        "iteration": iteration,
        "plan": validated_phases,
        "current_phase": 0,
        "plan_reasoning": decision.reasoning,
        "done": False,
    }