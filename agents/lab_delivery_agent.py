from google.adk.agents import Agent
from pydantic import PrivateAttr
from typing import Any
from utils.gemini import summarize_text
from utils.patient_utils import update_patient_record, load_patient_by_name
from utils.pdf_utils import generate_lab_pdf
import random


class LabDeliveryAgent(Agent):
    _gemini: Any = PrivateAttr()

    def __init__(self):
        super().__init__(name="lab_delivery_agent")
        from google.generativeai import GenerativeModel
        self._gemini = GenerativeModel("gemini-2.0-flash")

    def run(self, task_request: dict) -> dict:
        patient_name = task_request.get("patient_name")
        if not patient_name:
            return {"output": {"error": "Missing patient name."}}

        # 🔍 Load patient record
        patient = load_patient_by_name(patient_name)
        if not patient:
            return {"output": {"error": "Patient not found."}}

        tests = patient.get("recommended_tests", [])
        if not tests:
            return {"output": {"error": "No recommended tests found for this patient."}}

        # 🧠 Create mock test results
        test_results = {}
        for test in tests:
            test_results[test] = {
                "value": f"{random.randint(80, 150)} units",
                "status": random.choice(["Normal", "High", "Low"])
            }

        # 🧠 Generate summary using Gemini
        test_list = ", ".join(tests)
        prompt = (
            f"Generate a mock lab summary for a patient named {patient_name} who underwent the following tests: "
            f"{test_list}. Return a professional medical summary."
        )
        lab_summary = summarize_text(prompt)

        # 🧾 Generate Lab Report PDF
        pdf_bytes = generate_lab_pdf(patient_name, results_dict=test_results, summary=lab_summary)

        # ✅ Preserve existing notifications and other fields
        existing_notifications = patient.get("notifications", [])
        existing_notifications.append("🧪 Your lab report is ready and available for download.")

        # 💾 Update patient record safely
        update_patient_record(patient_name, {
            "lab_results": test_results,
            "lab_report": lab_summary,
            "lab_pdf_bytes": pdf_bytes.getvalue().decode("latin1"),
            "status": "lab_results_ready",
            "notifications": existing_notifications
        })

        return {
            "output": {
                "summary": lab_summary,
                "results": test_results,
                "lab_results": test_results  # used by workflow_agent
            }
        }
