from google.adk.agents import Agent
import pandas as pd

class SchedulingAgent(Agent):
    def __init__(self):
        super().__init__(name="scheduling_agent")

    def match_doctor(self, symptoms):
        doctors = pd.read_csv(r'Data/doctors.csv')
        for _, row in doctors.iterrows():
            specialties = [s.strip().lower() for s in row["specialties"].split(";")]
            if any(symptom.lower() in specialties for symptom in symptoms):
                return {
                    "doctor": row["name"],
                    "department": row["department"],
                    "availability": row["availability"]
                }
        return {
            "doctor": "No match found",
            "reason": "No available doctor for listed symptoms."
        }

    def run(self, task_request: dict) -> dict:
        patient_data = task_request.get("patient", {})
        symptoms = patient_data.get("symptoms", [])

        match = self.match_doctor(symptoms)

        return {
            "output": {
                "patient": patient_data,
                "match": match
            }
        }
