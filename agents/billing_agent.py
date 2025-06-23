from google.adk.agents import Agent
import random

class BillingAgent(Agent):
    def __init__(self):
        super().__init__(name="billing_agent")

    def run(self, task_request: dict) -> dict:
        patient_name = task_request.get("patient_name")
        tests = task_request.get("tests", [])
        insurance = task_request.get("insurance", None)

        if not tests:
            return {"output": {"error": "No tests provided for billing."}}

        base_price = 500  # Example base per-test price
        total = base_price * len(tests)

        discount = 0.2 if insurance else 0  # 20% discount if insured
        final_total = int(total * (1 - discount))

        breakdown = {
            "patient_name": patient_name,
            "tests": tests,
            "price_per_test": base_price,
            "insurance_applied": bool(insurance),
            "total_before_discount": total,
            "discount_percent": discount * 100,
            "final_total": final_total
        }

        return {"output": breakdown}
