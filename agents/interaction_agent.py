from google.adk.agents import Agent

class InteractionAgent(Agent):
    def __init__(self):
        super().__init__(name="interaction_agent")

    def run(self, task_request: dict) -> dict:
        patient_name = task_request.get("patient_name")
        return {
            "output": {
                "message": f"📝 New report available for {patient_name}. Please check your dashboard to view and download it."
            }
        }
