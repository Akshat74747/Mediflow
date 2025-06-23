from google.adk.agents import Agent
from agents.admission_agent import AdmissionAgent
from agents.scheduling_agent import SchedulingAgent
import os
import json

PATIENTS_DB_PATH = "data/patients_db.json"

class RouterAgent(Agent):
    def __init__(self):
        super().__init__(name="router_agent")

    def run(self, task_request: dict) -> dict:
        # Instantiate agents here to avoid Pydantic issues
        admission_agent = AdmissionAgent()
        scheduling_agent = SchedulingAgent()

        # Step 1: Run admission
        admission_result = admission_agent.run(task_request)
        admission_output = admission_result["output"]

        if admission_output["status"] == "validated":
            patient_data = admission_output["patient"]

            # Step 2: Run scheduling
            scheduling_result = scheduling_agent.run({
                "patient": patient_data
            })
            scheduling_output = scheduling_result["output"]["match"]

            # Step 3: Enrich patient data
            assigned_doctor = scheduling_output.get("doctor", "Unassigned")
            department = scheduling_output.get("department", "Unknown")
            patient_data["assigned_doctor"] = assigned_doctor
            patient_data["department"] = department
            patient_data["status"] = "scheduled"

            # Step 4: Add default notification
            patient_data["notifications"] = [
                f"✅ Appointment scheduled with Dr. {assigned_doctor} in {department}."
            ]

            # Step 5: Save to central database
            self.save_to_db(patient_data)

            return {
                "output": {
                    "admission": admission_output,
                    "scheduling": scheduling_result["output"]
                }
            }

        else:
            return {
                "output": {
                    "admission": admission_output,
                    "scheduling": None
                }
            }

    def save_to_db(self, new_patient):
        os.makedirs("data", exist_ok=True)

        if os.path.exists(PATIENTS_DB_PATH):
            with open(PATIENTS_DB_PATH, "r") as f:
                try:
                    patients = json.load(f)
                except json.JSONDecodeError:
                    patients = []
        else:
            patients = []

        # Append new patient and write back
        patients.append(new_patient)
        with open(PATIENTS_DB_PATH, "w") as f:
            json.dump(patients, f, indent=4)
