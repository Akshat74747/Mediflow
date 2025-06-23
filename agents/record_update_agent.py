from google.adk.agents import Agent
import json
import os

PATIENTS_DB = "data/patients_db.json"

class RecordUpdateAgent(Agent):
    def __init__(self):
        super().__init__(name="record_update_agent")

    def run(self, task_request: dict) -> dict:
        patient_name = task_request.get("patient_name")
        report_data = task_request.get("report")
        tests_data = task_request.get("recommended_tests", None)

        # Load patients DB
        if os.path.exists(PATIENTS_DB):
            with open(PATIENTS_DB, "r") as f:
                patients = json.load(f)
        else:
            return {"output": {"status": "error", "message": "Patient DB not found"}}

        # Update the correct patient's record
        for p in patients:
            if p["name"].lower() == patient_name.lower():
                if report_data:
                    p["report"] = report_data
                    p["status"] = "report_submitted"
                if tests_data is not None:
                    p["recommended_tests"] = tests_data
                if "notifications" not in p:
                    p["notifications"] = []
                p["notifications"].append("📝 Your doctor's report has been submitted.")

                break
        else:
            return {"output": {"status": "error", "message": "Patient not found"}}

        # Save back to DB
        with open(PATIENTS_DB, "w") as f:
            json.dump(patients, f, indent=4)

        return {"output": {"status": "updated", "message": "Patient record updated"}}
