import streamlit as st
import requests
import pandas as pd
import json
import re

import os
API_URL = os.getenv("API_URL", "http://localhost:8000")


def extract_visualization(response_text):
    """Extract visualization JSON from agent response if present."""
    # Try fenced code block format: ```visualization\n{...}\n```
    pattern_fenced = r"```visualization\s*\n(.*?)\n```"
    match = re.search(pattern_fenced, response_text, re.DOTALL)
    
    if not match:
        # Try inline format: visualization{...}
        pattern_inline = r"visualization\s*(\{.*\})"
        match = re.search(pattern_inline, response_text, re.DOTALL)
    
    if match:
        try:
            viz_data = json.loads(match.group(1))
            clean_text = response_text[:match.start()] + response_text[match.end():]
            return clean_text.strip(), viz_data
        except json.JSONDecodeError:
            return response_text, None
    return response_text, None


def render_visualization(viz_data):
    """Render a chart or table from visualization data."""
    chart_type = viz_data.get("chart_type", "table")
    title = viz_data.get("title", "")
    data = viz_data.get("data", [])

    if not data:
        return

    df = pd.DataFrame(data)

    if title:
        st.subheader(title)

    if chart_type == "line":
        x = viz_data.get("x_axis")
        y = viz_data.get("y_axis")
        if x and y and x in df.columns and y in df.columns:
            df = df.sort_values(by=x)
            st.line_chart(df, x=x, y=y)
        else:
            st.dataframe(df)

    elif chart_type == "bar":
        x = viz_data.get("x_axis")
        y = viz_data.get("y_axis")
        if x and y and x in df.columns and y in df.columns:
            st.bar_chart(df, x=x, y=y)
        else:
            st.dataframe(df)

    elif chart_type == "table":
        st.dataframe(df, use_container_width=True)

    else:
        st.dataframe(df, use_container_width=True)

st.title("Admin Reporting UI")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and "viz_data" in msg and msg["viz_data"]:
            st.write(msg["content"])
            render_visualization(msg["viz_data"])
        else:
            st.write(msg["content"])

prompt = st.chat_input("Ask something")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        viz_data = None
        progress_placeholder = st.empty()
        progress_lines = []

        with requests.post(
            f"{API_URL}/agent/query",
            json={"query": prompt, "session_id": "default"},
            stream=True
        ) as response:

            def token_stream():
                for line in response.iter_lines(chunk_size=1):
                    if not line:
                        continue
                    chunk = line.decode("utf-8")
                    if chunk.startswith("data: "):
                        chunk = chunk[6:]
                    try:
                        event = json.loads(chunk)
                    except json.JSONDecodeError:
                        continue

                    etype = event.get("type")

                    if etype == "status":
                        progress_lines.append(f"🔄 {event.get('message', '')}")
                        progress_placeholder.info("\n\n".join(progress_lines))
                    elif etype == "plan":
                        for i, phase in enumerate(event.get("phases", [])):
                            progress_lines.append(f"📋 Phase {i + 1}: **{', '.join(phase)}**")
                        progress_placeholder.info("\n\n".join(progress_lines))
                    elif etype == "result":
                        progress_lines.append(f"✅ **{event.get('agent', '')}** completed")
                        progress_placeholder.info("\n\n".join(progress_lines))
                    elif etype == "agent_start":
                        progress_placeholder.empty()
                    elif etype == "token":
                        yield event.get("content", "")
                    elif etype == "final":
                        progress_placeholder.empty()
                        if event.get("answer"):
                            yield event.get("answer", "")
                    elif etype == "error":
                        progress_placeholder.error(event.get("message", "Unknown error"))

            full_response = st.write_stream(token_stream())

        clean_text, viz_data = extract_visualization(full_response)
        if viz_data:
            render_visualization(viz_data)

    st.session_state.messages.append(
        {"role": "assistant", "content": clean_text, "viz_data": viz_data}
    )

if st.button("Clear Chat"):
    st.session_state.messages = []