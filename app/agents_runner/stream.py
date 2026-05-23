import json
import logging
from agents import Runner
from agents.stream_events import (
    RawResponsesStreamEvent,
    RunItemStreamEvent,
    AgentUpdatedStreamEvent,
)
from app.core.redis import RedisClient

logger = logging.getLogger(__name__)

_redis_client = RedisClient()


async def stream_agent(agent, query: str, session_id: str = "default"):
    """
    Generic streaming function — works with any agent.
    Handles SSE event parsing, response accumulation, and memory persistence.

    Override behavior by wrapping this or passing a different agent.
    """
    logger.info(f"Streaming [{agent.name}] query: {query}")

    history = await _redis_client.load_memory(session_id)
    input_messages = history + [{"role": "user", "content": query}]

    full_response = ""

    result = Runner.run_streamed(agent, input_messages)

    async for event in result.stream_events():
        if hasattr(event, "type") and event.type == "response.output_text.delta":
            if hasattr(event, "delta") and event.delta:
                full_response += event.delta
                yield event.delta
        elif isinstance(event, RawResponsesStreamEvent):
            if hasattr(event.data, "type") and event.data.type == "response.output_text.delta":
                if hasattr(event.data, "delta") and event.data.delta:
                    full_response += event.data.delta
                    yield event.data.delta
            elif isinstance(event.data, str) and event.data:
                full_response += event.data
                yield event.data
        elif isinstance(event, (RunItemStreamEvent, AgentUpdatedStreamEvent)):
            pass

    logger.info(f"Completed streaming [{agent.name}] for session '{session_id}'.")
    await _redis_client.save_turn(session_id, query, full_response)


async def stream_graph_workflow(query: str, session_id: str = "default"):
    """Stream the plan-and-execute multi-agent workflow with phase updates."""
    from app.agents_runner.lifecycle import app_lifecycle

    logger.info(f"Streaming graph workflow for: {query}")

    initial_state = {
        "user_query": query,
        "results": {},
        "intermediate_steps": [],
        "current_phase": 0,
        "done": False,
    }

    final_answer = None

    config = {"configurable": {"thread_id": session_id}}

    async for event in app_lifecycle.graph.astream(initial_state, config=config, stream_mode="updates"):
        for _, state_update in event.items():

            # Agent execution results
            steps = state_update.get("intermediate_steps", [])
            for step in steps:
                yield json.dumps({
                    "type": "result",
                    "agent": step.get("agent", ""),
                    "output": str(step.get("output", ""))[:500],
                }) + "\n"

            # Plan announced
            if state_update.get("plan") and not state_update.get("done"):
                yield json.dumps({
                    "type": "plan",
                    "phases": state_update["plan"],
                    "reasoning": state_update.get("plan_reasoning", ""),
                }) + "\n"

            # Final answer (from supervisor synthesis or single-agent shortcut)
            if state_update.get("done") and state_update.get("final_answer"):
                final_answer = state_update["final_answer"]
                yield json.dumps({
                    "type": "final",
                    "answer": final_answer,
                }) + "\n"

    if not final_answer:
        final_answer = "No answer produced."
        yield json.dumps({
            "type": "final",
            "answer": final_answer,
        }) + "\n"

    await _redis_client.save_turn(session_id, query, final_answer)
