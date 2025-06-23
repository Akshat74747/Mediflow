import streamlit as st

st.set_page_config(page_title="Mediflow")

st.title("🏥 Welcome to Mediflow the Hospital Workflow Automator")
st.markdown("Please choose your role:")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🧑‍🤝‍🧑 I'm a Patient"):
        st.switch_page("pages/patient_interface.py")

with col2:
    if st.button("🩺 I'm a Doctor"):
        st.switch_page("pages/doctor_dashboard.py")

with col3:
    if st.button("🧠 Admin (View Logs)"):
        st.switch_page("pages/admin_logs.py")
