"""
Shared agent singletons — populated once at startup by lifecycle.py.
Generic run_agent handler used by LangGraph registry for all worker agents.
"""
import asyncio
import logging
from agents import Runner
from agents.stream_events import RawResponsesStreamEvent

logger = logging.getLogger(__name__)

# Explicit agent registry — lifecycle.py populates this at startup
agents: dict = {}

# Set by stream_graph_workflow before each run — receives token events from agents
token_queue: asyncio.Queue | None = None


async def run_agent(agent_name: str, state: dict) -> dict:
    agent = agents.get(agent_name)
    if agent is None:
        raise ValueError(f"Agent '{agent_name}' not initialized in store.")

    available_results = state.get("results", {})

    context_parts = [state["user_query"]]
    if available_results:
        for name, result in available_results.items():
            context_parts.append(f"\n[Context from {name}]:\n{str(result)[:1000]}")

    input_text = "\n".join(context_parts)

    streamed_result = Runner.run_streamed(agent, input=input_text)

    async for event in streamed_result.stream_events():
        token = None
        if hasattr(event, "type") and event.type == "response.output_text.delta":
            token = getattr(event, "delta", "")
        elif isinstance(event, RawResponsesStreamEvent):
            data = event.data
            if hasattr(data, "type") and data.type == "response.output_text.delta":
                token = getattr(data, "delta", "")

        if token and token_queue is not None:
            await token_queue.put({"agent": agent_name, "token": token})

    if token_queue is not None:
        await token_queue.put({"agent": agent_name, "done": True})

    full_output = streamed_result.final_output or ""

    return {
        "results": {
            **available_results,
            agent_name: full_output,
        },
        "intermediate_steps": state.get("intermediate_steps", []) + [{
            "agent": agent_name,
            "output": full_output,
        }],
    }
