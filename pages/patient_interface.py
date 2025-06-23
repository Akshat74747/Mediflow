import streamlit as st
import json
import os
from agents.workflow_agent import WorkflowAgent
from utils.pdf_utils import generate_report_pdf, generate_lab_pdf
from io import BytesIO

PATIENTS_DB = "data/patients_db.json"
workflow_agent = WorkflowAgent()

st.set_page_config(page_title="🧑‍⚕️ Patient Portal", layout="centered")
st.title("👤 Patient Portal")

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 New Admission",
    "📁 My Profile & Reports",
    "🧪 Test Approval & Billing",
    "💬 My Doctor's Comments"
])


# ---------------------
# 📝 NEW ADMISSION TAB
# ---------------------
with tab1:
    st.subheader("Submit a new admission request")
    st.markdown("Describe your symptoms, name, age, and insurance in one message.")
    user_input = st.text_area("🗣️ Admission Message", height=180)

    if st.button("Submit Admission"):
        if not user_input.strip():
            st.warning("Please enter a message first.")
        else:
            with st.spinner("Processing your admission request..."):
                try:
                    result = workflow_agent.run({
                        "task_type": "admission",
                        "text": user_input
                    })
                    output = result["output"]
                    admission = output.get("admission", {})

                    st.subheader("🏥 Admission Status")
                    if admission.get("status") == "validated":
                        patient = admission.get("patient", {})
                        name = patient.get("name", "Unknown")
                        age = patient.get("age", "N/A")
                        insurance = patient.get("insurance_provider", "N/A")
                        symptoms = ", ".join(patient.get("symptoms", []))
                        st.success(f"✅ **{name}** (Age {age}) is admitted with symptoms: **{symptoms}**. Insurance: **{insurance}**")
                    else:
                        st.error(f"❌ Admission rejected. Reason: {admission.get('reason', 'Unknown')}")

                    st.subheader("📅 Scheduling Result")
                    scheduling = output.get("scheduling")
                    if scheduling:
                        match = scheduling.get("match", {})
                        st.success(
                            f"📌 Appointment scheduled with **{match.get('doctor', 'Unknown')}** "
                            f"({match.get('department', 'Unknown')}) between **{match.get('availability', 'Unavailable')}**."
                        )
                    else:
                        st.info("No appointment scheduled due to admission failure.")

                except Exception as e:
                    st.error("An error occurred while processing your request.")
                    st.exception(e)

# ---------------------
# 📁 PROFILE & REPORT TAB
# ---------------------
with tab2:
    st.subheader("🔐 Access your profile and records")
    name_check = st.text_input("Enter your full name", key="report_search")

    if name_check:
        try:
            if os.path.exists(PATIENTS_DB):
                with open(PATIENTS_DB, "r") as f:
                    patients = json.load(f)
            else:
                patients = []

            patient = next((p for p in patients if p["name"].lower() == name_check.strip().lower()), None)

            if not patient:
                st.warning("No patient record found.")
            else:
                st.markdown("### 🧍 Profile Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Name:** {patient.get('name', '-')}")
                    st.markdown(f"**Age:** {patient.get('age', '-')}")
                    st.markdown(f"**Insurance:** {patient.get('insurance_provider', '-')}")
                    st.markdown(f"**Status:** `{patient.get('status', '-')}`")
                with col2:
                    st.markdown(f"**Symptoms:** {', '.join(patient.get('symptoms', []))}")
                    st.markdown(f"**Assigned Doctor:** {patient.get('assigned_doctor', '-')}")
                    st.markdown(f"**Department:** {patient.get('department', '-')}")

                st.markdown("### 🔔 Notifications")
                if patient.get("notifications"):
                    for note in patient["notifications"]:
                        st.info(f"🔔 {note}")
                else:
                    st.info("No notifications at this time.")

                st.markdown("### 📄 Doctor Report")
                if patient.get("report"):
                    st.success("📝 A report from your doctor is available.")
                    pdf_file = generate_report_pdf(patient["name"], patient["report"])
                    st.download_button(
                        label="⬇️ Download Your Medical Report (PDF)",
                        data=pdf_file,
                        file_name=f"{patient['name']}_report.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.info("Your report is not yet available.")

                st.markdown("### 🧪 Lab Test Results Summary")
                if patient.get("lab_results"):
                    for test, result in patient["lab_results"].items():
                        value = result.get("value", "-")
                        status = result.get("status", "-")
                        st.success(f"**{test}**: {value} ({status})")

                    lab_pdf = generate_lab_pdf(patient["name"], patient["lab_results"])
                    st.download_button(
                        label="⬇️ Download Lab Report (PDF)",
                        data=lab_pdf,
                        file_name=f"{patient['name']}_lab_report.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.info("Lab test results are not available yet.")

        except Exception as e:
            st.error("Unable to load your record.")
            st.exception(e)

# ---------------------
# 🧪 TEST APPROVAL & BILLING TAB
# ---------------------
with tab3:
    st.subheader("🔍 View Your Doctor's Summary and Approve Tests")
    confirm_name = st.text_input("Enter your full name to continue:", key="confirm_test")

    if confirm_name:
        result = workflow_agent.run({
            "task_type": "summary_confirmation",
            "patient_name": confirm_name
        })
        output = result.get("output", {})

        if "error" in output:
            st.error(output["error"])
        else:
            st.markdown("### 📝 Summary from Your Doctor")
            st.info(output["summary"])

            if output.get("tests"):
                st.markdown("### 🧪 Recommended Tests")
                st.markdown(", ".join(output["tests"]))

            col1, col2 = st.columns(2)

            if os.path.exists(PATIENTS_DB):
                with open(PATIENTS_DB, "r") as f:
                    patients = json.load(f)

            matched = False
            for p in patients:
                if p["name"].lower() == confirm_name.strip().lower():
                    matched = True
                    with col1:
                        if st.button("✅ Proceed with Tests"):
                            p["status"] = "tests_approved"
                            st.success("✅ You have opted to proceed with the tests.")

                            # 🔁 Billing
                            billing_result = workflow_agent.run({
                                "task_type": "billing",
                                "patient_name": p["name"],
                                "tests": p.get("recommended_tests", []),
                                "insurance": p.get("insurance_provider", None)
                            })
                            bill = billing_result.get("output", {})
                            if "error" in bill:
                                st.error(f"Billing Error: {bill['error']}")
                            else:
                                st.markdown("### 💰 Billing & Lab Delivery")
                                st.info(f"Total for {len(bill.get('tests', []))} tests: ₹{bill.get('total_before_discount', 'N/A')}")
                                if bill.get("insurance_applied"):
                                    st.info(f"Insurance Applied: ✅ {bill.get('discount_percent', 0)}% off")
                                st.success(f"🧾 Final Amount Payable: ₹{bill.get('final_total', 'N/A')}")

                                # 🧪 Trigger lab test delivery
                                lab_result = workflow_agent.run({
                                    "task_type": "lab_delivery",
                                    "patient_name": p["name"]
                                })

                                if "error" in lab_result.get("output", {}):
                                    st.warning("⚠️ Lab result generation failed.")
                                else:
                                    st.success("🧪 Lab results have been delivered.")
                                    if p.get("lab_results"):
                                        lab_pdf = generate_lab_pdf(p["name"], p["lab_results"])
                                        st.download_button(
                                            label="⬇️ Download Lab Report (PDF)",
                                            data=lab_pdf,
                                            file_name=f"{p['name']}_lab_report.pdf",
                                            mime="application/pdf"
                                        )

                    with col2:
                        if st.button("❌ Skip Tests"):
                            p["status"] = "tests_skipped"
                            st.info("You have chosen not to proceed with the tests.")
                    break

            if matched:
                # ✅ REFRESH data after lab delivery to avoid stale overwrites
                with open(PATIENTS_DB, "r") as f:
                    updated_patients = json.load(f)
                with open(PATIENTS_DB, "w") as f:
                    json.dump(updated_patients, f, indent=4)

# ---------------------
# 💬 COMMENTS TAB
# ---------------------

with tab4:
    st.subheader("💬 View Comments from Your Doctor")
    patient_name = st.text_input("Enter your full name to view comments:", key="view_comments")

    if patient_name:
        with open(PATIENTS_DB, "r") as f:
            patients = json.load(f)

        patient = next((p for p in patients if p["name"].lower() == patient_name.strip().lower()), None)

        if not patient:
            st.warning("No patient found.")
        else:
            st.markdown(f"### 👤 {patient['name']} (Age: {patient.get('age', '-')})")
            comments = patient.get("doctor_comments", [])
            if comments:
                for c in comments:
                    st.info(f"🗨️ {c}")
            else:
                st.info("No comments added yet.")

