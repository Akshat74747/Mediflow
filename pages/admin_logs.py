import streamlit as st
import os
import json
import pandas as pd

LOG_FILE = "data/agent_logs.jsonl"

st.set_page_config(page_title="🧠 Agent Logs", layout="wide")
st.title("📊 Agent Call Logs")

if not os.path.exists(LOG_FILE):
    st.warning("No log file found yet.")
else:
    logs = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except:
                continue

    if not logs:
        st.info("No logs to display.")
    else:
        df = pd.DataFrame(logs)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values(by="timestamp", ascending=False)

        agents = df["agent"].unique().tolist()
        selected_agent = st.selectbox("🔍 Filter by Agent", ["All"] + agents)

        if selected_agent != "All":
            df = df[df["agent"] == selected_agent]

        st.markdown(f"### Showing {len(df)} log entries")

        for idx, row in df.iterrows():
            with st.expander(f"[{row['timestamp']}] {row['agent']}"):
                st.markdown("**📥 Input:**")
                st.json(row["input"], expanded=False)
                st.markdown("**📤 Output:**")
                st.json(row["output"], expanded=False)
