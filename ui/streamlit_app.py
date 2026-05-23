import streamlit as st
import requests
import pandas as pd
import json
import re

API_URL = "http://0.0.0.0:8000"
# If i Dockerise this, then update URL to 'API_URL = "http://api:8000"' because docker to docker communication via service name


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
        status_placeholder = st.empty()
        message_placeholder = st.empty()
        full_response = ""
        viz_data = None

        with requests.post(
            f"{API_URL}/agent/query",
            json={"query": prompt, "session_id": "default"},
            stream=True
        ) as response:
            for line in response.iter_lines():
                if line:
                    chunk = line.decode("utf-8")
                    try:
                        event = json.loads(chunk)
                    except json.JSONDecodeError:
                        continue

                    if event.get("type") == "step":
                        agent = event.get("agent", "")
                        reasoning = event.get("reasoning", "")
                        status_placeholder.info(f"🔄 Routing to **{agent}** — {reasoning}")

                    elif event.get("type") == "result":
                        agent = event.get("agent", "")
                        status_placeholder.info(f"✅ **{agent}** completed")

                    elif event.get("type") == "final":
                        full_response = event.get("answer", "")
                        status_placeholder.empty()

            clean_text, viz_data = extract_visualization(full_response)
            message_placeholder.markdown(clean_text)

            if viz_data:
                render_visualization(viz_data)

    st.session_state.messages.append(
        {"role": "assistant", "content": clean_text, "viz_data": viz_data}
    )

if st.button("Clear Chat"):
    st.session_state.messages = []