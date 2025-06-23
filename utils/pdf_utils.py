from fpdf import FPDF
from io import BytesIO

def generate_report_pdf(patient_name, report_text):
    """
    Generate a PDF file for the doctor's diagnosis report.
    
    Parameters:
        patient_name (str): Name of the patient.
        report_text (str): The full textual medical report.
    
    Returns:
        BytesIO: PDF as a byte stream suitable for download.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Medical Report for {patient_name}", ln=True, align="C")
    pdf.ln(10)

    for line in report_text.split("\n"):
        pdf.multi_cell(0, 10, txt=line)

    # Output to BytesIO
    pdf_output = BytesIO()
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output


def generate_lab_pdf(patient_name, results_dict, summary=None):
    """
    Generate a PDF file for lab test results.

    Parameters:
        patient_name (str): Name of the patient.
        results_dict (dict): Dictionary of lab results. 
                             Each test is a key with a value/status pair.
        summary (str, optional): Optional summary or interpretation of the lab results.

    Returns:
        BytesIO: PDF as a byte stream suitable for download.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Lab Test Results for {patient_name}", ln=True, align="C")
    pdf.ln(10)

    if summary:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, txt="Summary:", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=summary)
        pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 10, "Test", border=1)
    pdf.cell(60, 10, "Value", border=1)
    pdf.cell(60, 10, "Status", border=1)
    pdf.ln()

    pdf.set_font("Arial", size=12)
    for test, data in results_dict.items():
        pdf.cell(60, 10, test, border=1)
        pdf.cell(60, 10, str(data.get("value", "-")), border=1)
        pdf.cell(60, 10, data.get("status", "-"), border=1)
        pdf.ln()

    # Output to BytesIO
    pdf_output = BytesIO()
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output
