import datetime
import os
import json

LOG_FILE = "data/agent_logs.jsonl"
os.makedirs("data", exist_ok=True)

def log_agent_call(agent_name: str, input_data: dict, output_data: dict):
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "agent": agent_name,
        "input": input_data,
        "output": output_data
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
