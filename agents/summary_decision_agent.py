from google.adk.agents import Agent
from utils.gemini import summarize_text 
import json
import os

PATIENTS_DB_PATH = "data/patients_db.json"

class SummaryDecisionAgent(Agent):
    def __init__(self):
        super().__init__(name="summary_decision_agent")

    def run(self, task_request: dict) -> dict:
        patient_name = task_request.get("patient_name")

        # Load patient data
        if not os.path.exists(PATIENTS_DB_PATH):
            return {"output": {"error": "Patient database not found."}}

        with open(PATIENTS_DB_PATH, "r") as f:
            patients = json.load(f)

        patient = next((p for p in patients if p["name"].lower() == patient_name.lower()), None)

        if not patient or "report" not in patient:
            return {"output": {"error": "Report not found for the patient."}}

        # Use Gemini to summarize
        report_text = patient["report"]
        summary = summarize_text(report_text)

        return {
            "output": {
                "summary": summary,
                "tests": patient.get("recommended_tests", []),
                "patient_name": patient_name
            }
        }
