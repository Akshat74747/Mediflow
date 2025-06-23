# Hospital Workflow Automator 🏥

A multi-agent healthcare automation system built using Google’s Agent Development Kit (ADK) and Streamlit.

## 🔧 Features
- Multi-agent architecture for patient admission, scheduling, diagnostics, billing, and lab reporting.
- Doctor and patient dashboards.
- AI-generated reports and lab summaries using Gemini.
- Downloadable PDFs for reports and lab results.
- Agent call logging and comment tracking.

## 📁 Folder Structure
- agents/ # All agent logic
- configs/ # Agent config file
- Data/ # Patient DB, logs, doctor info
- pages/ # Streamlit frontend pages
- utils/ # Utility modules (Gemini, PDF, logger)
- app.py # Streamlit launcher


## 🧠 Powered by
- Google ADK
- Streamlit
- Gemini (for AI-generated summaries)
- FPDF (for PDFs)

---

## 🚀 Run it locally
```bash
streamlit run app.py