from google.adk.agents import Agent

class ReportGenerationAgent(Agent):
    def __init__(self):
        super().__init__(name="report_generation_agent")

    def run(self, task_request: dict) -> dict:
        patient = task_request.get("patient", {})
        condition = task_request.get("condition", "Not provided")
        prescription = task_request.get("prescription", "None")
        tests = task_request.get("tests", [])

        report_text = f"""
        Patient Report - {patient.get('name')}
        ----------------------------
        Age: {patient.get('age')}
        Symptoms: {', '.join(patient.get('symptoms', []))}

        Condition: {condition}
        Prescription: {prescription}
        Recommended Tests: {', '.join(tests)}

        Insurance Provider: {patient.get('insurance_provider')}
        """

        return {
            "output": {
                "report": report_text.strip()
            }
        }
