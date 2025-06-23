from google.adk.agents import Agent
from agents.admission_agent import AdmissionAgent
from agents.scheduling_agent import SchedulingAgent
from agents.report_generation_agent import ReportGenerationAgent
from agents.record_update_agent import RecordUpdateAgent
from agents.interaction_agent import InteractionAgent
from agents.summary_decision_agent import SummaryDecisionAgent
from agents.billing_agent import BillingAgent
from agents.lab_delivery_agent import LabDeliveryAgent
from utils.agent_logger import log_agent_call  # Workflow agent is the main coordinator agent
import os
import json

PATIENTS_DB = "data/patients_db.json"

class WorkflowAgent(Agent):
    def __init__(self):
        super().__init__(name="workflow_agent")

    def run(self, task_request: dict) -> dict:
        task_type = task_request.get("task_type") or task_request.get("stage")

        if task_type == "report_submission":
            return self.handle_report_submission(task_request)
        elif task_type == "summary_confirmation":
            return self.handle_summary_confirmation(task_request)
        elif task_type == "admission":
            return self.handle_admission_and_scheduling(task_request)
        elif task_type == "billing":
            return self.handle_billing(task_request)
        elif task_type == "lab_delivery":
            return self.handle_lab_delivery(task_request)
        else:
            return {"output": {"error": "Unknown task_type provided."}}

    def handle_report_submission(self, task_request: dict) -> dict:
        report_agent = ReportGenerationAgent()
        update_agent = RecordUpdateAgent()
        notify_agent = InteractionAgent()

        report_result = report_agent.run(task_request)
        report_text = report_result["output"]["report"]
        recommended_tests = task_request.get("tests", [])

        update_agent_result = update_agent.run({
            "patient_name": task_request["patient"]["name"],
            "report": report_text,
            "recommended_tests": recommended_tests
        })

        notify_result = notify_agent.run({
            "patient_name": task_request["patient"]["name"]
        })

        final_output = {
            "report": report_text,
            "notification": notify_result["output"]["message"]
        }

        log_agent_call("ReportGenerationAgent", task_request, report_result)
        log_agent_call("RecordUpdateAgent", task_request, update_agent_result)
        log_agent_call("InteractionAgent", task_request, notify_result)

        return {"output": final_output}

    def handle_summary_confirmation(self, task_request: dict) -> dict:
        summary_agent = SummaryDecisionAgent()
        result = summary_agent.run(task_request)
        log_agent_call("SummaryDecisionAgent", task_request, result)
        return result

    def handle_admission_and_scheduling(self, task_request: dict) -> dict:
        admission_agent = AdmissionAgent()
        scheduling_agent = SchedulingAgent()

        admission_result = admission_agent.run(task_request)
        log_agent_call("AdmissionAgent", task_request, admission_result)

        admission_output = admission_result["output"]

        if admission_output.get("status") == "validated":
            patient_data = admission_output["patient"]

            scheduling_result = scheduling_agent.run({"patient": patient_data})
            log_agent_call("SchedulingAgent", {"patient": patient_data}, scheduling_result)

            scheduling_output = scheduling_result["output"]["match"]
            patient_data["assigned_doctor"] = scheduling_output.get("doctor", "Unassigned")
            patient_data["department"] = scheduling_output.get("department", "Unknown")
            patient_data["status"] = "scheduled"
            self.save_to_db(patient_data)

            return {
                "output": {
                    "admission": admission_output,
                    "scheduling": scheduling_result["output"]
                }
            }

        return {
            "output": {
                "admission": admission_output,
                "scheduling": None
            }
        }

    def handle_billing(self, task_request: dict) -> dict:
        billing_agent = BillingAgent()
        result = billing_agent.run(task_request)
        log_agent_call("BillingAgent", task_request, result)
        return result

    def handle_lab_delivery(self, task_request: dict) -> dict:
        lab_agent = LabDeliveryAgent()
        result = lab_agent.run(task_request)
        log_agent_call("LabDeliveryAgent", task_request, result)

        if "output" in result and "lab_results" in result["output"]:
            name = task_request.get("patient_name")
            if name and os.path.exists(PATIENTS_DB):
                with open(PATIENTS_DB, "r") as f:
                    patients = json.load(f)

                for p in patients:
                    if p["name"].lower() == name.lower():
                        p["lab_results"] = result["output"]["lab_results"]
                        break

                with open(PATIENTS_DB, "w") as f:
                    json.dump(patients, f, indent=4)

        return result

    def save_to_db(self, new_patient):
        os.makedirs("data", exist_ok=True)

        if os.path.exists(PATIENTS_DB):
            with open(PATIENTS_DB, "r") as f:
                try:
                    patients = json.load(f)
                except json.JSONDecodeError:
                    patients = []
        else:
            patients = []

        patients.append(new_patient)

        with open(PATIENTS_DB, "w") as f:
            json.dump(patients, f, indent=4)
