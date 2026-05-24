"""
Debug logging via SDK tracing processor.

Set DEBUG_LEVEL=on in .env to print the full chain to stdout:
  - Agent start with tools list
  - LLM input messages and output (text or tool calls)
  - Tool call arguments and results
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
except ImportError:
    pass

DEBUG_LEVEL = os.getenv("DEBUG_LEVEL", "off").lower()


class _ChainProcessor:

    def __init__(self):
        self._call_count = 0

    def on_trace_start(self, trace): pass
    def on_trace_end(self, trace): pass
    def on_span_start(self, span):
        data = span.span_data
        if getattr(data, "type", None) == "agent":
            tools = getattr(data, "tools", None) or []
            print(f"\n{'='*60}", flush=True)
            print(f"[AGENT] {data.name}  tools={tools}", flush=True)
            print(f"{'='*60}", flush=True)

    def on_span_end(self, span):
        data = span.span_data
        kind = getattr(data, "type", None)

        if kind == "agent":
            print(f"{'─'*60}", flush=True)
            print(f"[AGENT END] {data.name}", flush=True)
            print(f"{'─'*60}", flush=True)

        elif kind == "response":
            response = getattr(data, "response", None)
            inp = getattr(data, "input", None) or []
            if not response:
                return

            self._call_count += 1
            usage = getattr(response, "usage", None)
            model = getattr(response, "model", "?")
            in_tokens = getattr(usage, "input_tokens", "?") if usage else "?"
            out_tokens = getattr(usage, "output_tokens", "?") if usage else "?"

            print(f"\n{'─'*60}", flush=True)
            print(f"[LLM CALL #{self._call_count}] model={model}  in_tokens={in_tokens}  out_tokens={out_tokens}", flush=True)
            print(f"{'─'*60}", flush=True)

            instructions = getattr(response, "instructions", None)
            if instructions:
                print(f"  [SYSTEM]\n{instructions}\n", flush=True)

            for item in inp:
                role = item.get("role", "?")
                content = item.get("content", "")
                if isinstance(content, list):
                    content = " ".join(
                        b.get("text", "") if isinstance(b, dict) else str(b)
                        for b in content
                    )
                print(f"  [INPUT / {role.upper()}]\n{str(content)}\n", flush=True)

            print(f"  [RESPONSE]", flush=True)
            for item in getattr(response, "output", []):
                item_type = getattr(item, "type", None)
                if item_type == "message":
                    for block in getattr(item, "content", []):
                        text = getattr(block, "text", "")
                        print(f"{str(text)}\n", flush=True)
                elif item_type == "function_call":
                    name = getattr(item, "name", "?")
                    args = getattr(item, "arguments", "")
                    print(f"  tool_call → {name}\n  args: {str(args)}\n", flush=True)

        elif kind == "function":
            print(f"\n  [TOOL CALL] {data.name}", flush=True)
            print(f"  input:  {str(data.input)}", flush=True)
            print(f"  output: {str(data.output)}\n", flush=True)


def setup_debug_logging():
    if DEBUG_LEVEL == "off":
        return
    from agents import add_trace_processor
    add_trace_processor(_ChainProcessor())
    print("[debug] Chain tracing active", flush=True)
