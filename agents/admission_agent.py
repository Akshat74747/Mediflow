from google.adk.agents import Agent
from google.generativeai import configure, GenerativeModel
import os
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

class AdmissionAgent(Agent):
    def __init__(self):
        super().__init__(name="admission_agent")
        configure(api_key=API_KEY)
        self.model = GenerativeModel("gemini-2.0-flash")

    def parse_patient_info(self, text):
        prompt = f"""
        Extract the following fields from this hospital admission message. 
        Respond ONLY with valid JSON — no explanation, no markdown, no text before or after.

        Fields:
        - name
        - age
        - symptoms (as a list)
        - insurance_provider

        Message: "{text}"
        """

        response = self.model.generate_content(prompt)
        raw_output = response.text.strip()

        # Clean possible Markdown/code formatting
        if raw_output.startswith("```"):
            raw_output = raw_output.strip("`").replace("json", "").strip()

        try:
            parsed = json.loads(raw_output)
            return parsed
        except json.JSONDecodeError as e:
            print("[ERROR] Gemini response was not valid JSON:\n", response.text)
            raise e

    def run(self, task_request: dict) -> dict:
        user_text = task_request["text"]
        patient_data = self.parse_patient_info(user_text)

        if patient_data["insurance_provider"] in ["HealthSure", "LifeShield"]:
            result = {"status": "validated", "patient": patient_data}
        else:
            result = {"status": "rejected", "reason": "Unsupported insurance"}

        return {"output": result}
