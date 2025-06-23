import google.generativeai as genai
import os

# Load your Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def summarize_text(report_text):
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""Summarize the following doctor report for a patient in simple language and extract any recommended tests.

Report:
{report_text}
"""
    response = model.generate_content(prompt)
    return response.text
