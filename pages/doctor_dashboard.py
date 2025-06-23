import streamlit as st
import json
import os
from agents.workflow_agent import WorkflowAgent
from utils.pdf_utils import generate_report_pdf, generate_lab_pdf
from io import BytesIO

PATIENTS_DB = "data/patients_db.json"
workflow_agent = WorkflowAgent()

st.set_page_config(page_title="Doctor Dashboard", page_icon="🩺")
st.title("🩺 Doctor Dashboard")

tab1, tab2, tab3 = st.tabs(["📅 Today's Appointments", "📁 Patient Reports Viewer", "💬 Patient Comments"])

# ------------------------------
# 📅 TAB 1: Diagnosis & Reporting
# ------------------------------
with tab1:
    try:
        with open(PATIENTS_DB, "r") as f:
            patients = json.load(f)
    except:
        patients = []

    today_patients = [p for p in patients if p.get("status") == "scheduled"]

    st.subheader("📅 Today's Appointments")

    if not today_patients:
        st.info("No patients scheduled today.")
    else:
        selected = st.selectbox("Select a patient", [p["name"] for p in today_patients])
        patient = next(p for p in today_patients if p["name"] == selected)

        st.markdown(f"""
            **👤 Name:** {patient['name']}  
            **🎂 Age:** {patient['age']}  
            **🤒 Symptoms:** {', '.join(patient['symptoms'])}
        """)

        st.subheader("📝 Enter Diagnosis Report")

        condition = st.text_input("Condition Diagnosed")
        prescription = st.text_area("Prescription")
        recommended_tests = st.text_area("Recommended Tests (comma-separated)")

        if st.button("Generate Report"):
            if not condition or not prescription:
                st.warning("Please fill in all fields before submitting.")
            else:
                agent = WorkflowAgent()
                result = agent.run({
                    "task_type": "report_submission",
                    "patient": patient,
                    "condition": condition,
                    "prescription": prescription,
                    "tests": [t.strip() for t in recommended_tests.split(",") if t.strip()]
                })

                report_text = result["output"]["report"]
                notification_msg = result["output"]["notification"]

                st.success("✅ Report submitted and patient notified!")
                st.info(f"🔔 {notification_msg}")

                pdf_file = generate_report_pdf(patient["name"], report_text)
                st.download_button(
                    label="⬇️ Download Report (PDF)",
                    data=pdf_file,
                    file_name=f"{patient['name']}_report.pdf",
                    mime="application/pdf"
                )

# ------------------------------
# 📁 TAB 2: Patient Reports Viewer
# ------------------------------
with tab2:
    st.subheader("📁 Search and View Patient Reports")
    patient_lookup = st.text_input("Enter patient's full name")

    if patient_lookup:
        try:
            with open(PATIENTS_DB, "r") as f:
                all_patients = json.load(f)

            match = next((p for p in all_patients if p["name"].lower() == patient_lookup.strip().lower()), None)

            if not match:
                st.warning("No patient found with that name.")
            else:
                st.markdown(f"### 👤 {match['name']} (Age: {match['age']})")

                # Diagnosis Report
                st.markdown("#### 📝 Doctor's Report")
                if match.get("report"):
                    st.success(match["report"])
                    pdf_file = generate_report_pdf(match["name"], match["report"])
                    st.download_button(
                        label="⬇️ Download Doctor's Report",
                        data=pdf_file,
                        file_name=f"{match['name']}_report.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.info("No doctor's report available.")

                # Lab Report
                st.markdown("#### 🧪 Lab Report")
                if match.get("lab_results"):
                    for test, data in match["lab_results"].items():
                        st.markdown(f"- **{test}**: {data.get('value', '-')}, *{data.get('status', '-')}*")

                    if match.get("lab_report"):
                        st.info(match["lab_report"])

                    lab_pdf = generate_lab_pdf(match["name"], match["lab_results"], summary=match.get("lab_report", ""))
                    st.download_button(
                        label="⬇️ Download Lab Report",
                        data=lab_pdf,
                        file_name=f"{match['name']}_lab_report.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.info("No lab results available.")

        except Exception as e:
            st.error("Error loading patient data.")
            st.exception(e)


# ------------------------------
# 💬 TAB 3: Comments
# ------------------------------
with tab3:
    st.subheader("💬 Leave Comments for Patients")
    patient_lookup = st.text_input("Enter patient's full name", key="comment_patient")

    if patient_lookup:
        with open(PATIENTS_DB, "r") as f:
            patients = json.load(f)

        patient = next((p for p in patients if p["name"].lower() == patient_lookup.strip().lower()), None)

        if not patient:
            st.warning("No patient found.")
        else:
            st.markdown(f"### 👤 {patient['name']} (Age {patient.get('age', '-')})")
            existing_comments = patient.get("doctor_comments", [])
            if existing_comments:
                st.markdown("#### Previous Comments:")
                for c in existing_comments:
                    st.info(f"🗨️ {c}")
            else:
                st.info("No comments yet.")

            new_comment = st.text_area("📝 Add a new comment")
            if st.button("Submit Comment"):
                if "doctor_comments" not in patient:
                    patient["doctor_comments"] = []
                patient["doctor_comments"].append(new_comment)

                # Save update
                with open(PATIENTS_DB, "w") as f:
                    json.dump(patients, f, indent=4)
                st.success("✅ Comment added!")
