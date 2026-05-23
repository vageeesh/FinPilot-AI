"""
Shared agent singletons — populated once at startup by lifecycle.py.
Generic run_agent handler used by LangGraph registry for all worker agents.
"""
from agents import Runner

# Explicit agent registry — lifecycle.py populates this at startup
agents: dict = {}


async def run_agent(agent_name: str, state: dict) -> dict:
    """
    Generic handler for any worker agent — called via LangGraph registry.
    Takes full state, extracts what it needs, returns partial state update.
    """
    agent = agents.get(agent_name)
    if agent is None:
        raise ValueError(f"Agent '{agent_name}' not initialized in store.")

    available_results = state.get("results", {})

    context_parts = [state["user_query"]]

    # To DO: smarter context construction per agent type,
    # e.g. Tax agent only gets tax-related results, investment agent gets investment data, etc. For now we just dump everything in and let the agent figure it out.
    # Revisit this logic, we have to think about how to do this in a way that doesn't leak info across agents in a way that breaks modularity. Maybe we can have some sort of tagging system for results that agents can choose to pull in or not?
    # and not restricting the input length here, since we want to give agents as much context as possible and let them figure out what to use. We can always add some heuristics later if we find that context length is an issue.
    if available_results:
        for name, result in available_results.items():
            context_parts.append(
                f"\n[Context from {name}]:\n{str(result)[:1000]}"
            )

    input_text = "\n".join(context_parts)
    result = await Runner.run(agent, input=input_text)
    output = result.final_output

    return {
        "results": {
            **available_results,
            agent_name: output,
        },
        "intermediate_steps": state.get("intermediate_steps", []) + [{
            "agent": agent_name,
            "output": output,
        }],
    }
