import json
import asyncio
import logging
import uuid
from agents.stream_events import RawResponsesStreamEvent, RunItemStreamEvent, AgentUpdatedStreamEvent
from app.core.redis import RedisClient

logger = logging.getLogger(__name__)

_redis_client = RedisClient()


async def stream_graph_workflow(query: str, session_id: str = "default"):
    """Stream the plan-and-execute multi-agent workflow with phase updates."""
    from app.agents_runner.lifecycle import app_lifecycle
    from app.agents_runner import runner

    logger.info(f"Streaming graph workflow for: {query}")

    # Build conversation context from Redis memory
    history = await _redis_client.load_memory(session_id)
    if history:
        history_text = "\n".join(
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in history
        )
        user_query_with_context = f"Previous conversation:\n{history_text}\n\nCurrent query: {query}"
    else:
        user_query_with_context = query

    initial_state = {
        "user_query": user_query_with_context,
        "results": {},
        "intermediate_steps": [],
        "current_phase": 0,
        "iteration": 0,
        "done": False,
    }

    final_answer = None
    config = {"configurable": {"thread_id": f"{session_id}_{uuid.uuid4().hex[:8]}"}}

    # Shared queue — runner.py pushes tokens into it, we drain it here
    queue = asyncio.Queue()
    runner.token_queue = queue

    _SENTINEL = object()

    async def run_graph():
        """Run the full LangGraph workflow, yield state events into the queue."""
        try:
            async for event in app_lifecycle.graph.astream(initial_state, config=config, stream_mode="updates"):
                for _, state_update in event.items():
                    await queue.put({"_state": state_update})
        finally:
            await queue.put(_SENTINEL)

    graph_task = asyncio.create_task(run_graph())

    current_agent = None

    try:
        while True:
            item = await queue.get()

            if item is _SENTINEL:
                break

            # Token from an agent
            if "token" in item:
                agent_name = item["agent"]
                if agent_name != current_agent:
                    current_agent = agent_name
                    yield json.dumps({"type": "agent_start", "agent": agent_name})
                yield json.dumps({"type": "token", "agent": agent_name, "content": item["token"]})

            # Agent finished streaming
            elif item.get("done") and "agent" in item:
                current_agent = None

            # LangGraph state update
            elif "_state" in item:
                state_update = item["_state"]

                steps = state_update.get("intermediate_steps", [])
                for step in steps:
                    yield json.dumps({
                        "type": "result",
                        "agent": step.get("agent", ""),
                        "output": str(step.get("output", ""))[:500],
                    })

                if state_update.get("plan") and not state_update.get("done"):
                    yield json.dumps({
                        "type": "plan",
                        "phases": state_update["plan"],
                        "reasoning": state_update.get("plan_reasoning", ""),
                    })

                if state_update.get("done") and state_update.get("final_answer"):
                    final_answer = state_update["final_answer"]
                    yield json.dumps({"type": "final", "answer": final_answer})

    finally:
        runner.token_queue = None
        await graph_task

    if not final_answer:
        final_answer = "No answer produced."
        yield json.dumps({"type": "final", "answer": final_answer})

    await _redis_client.save_turn(session_id, query, final_answer)
