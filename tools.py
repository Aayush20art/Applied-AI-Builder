import fitz  # PyMuPDF
import os
from langchain.tools import tool
from PIL import Image
import io
import json

@tool
def extract_inspection_report(pdf_path: str) -> str:
    """
    Extract text from an inspection report PDF.
    Returns the complete extracted inspection report text.
    """

    try:
        doc = fitz.open(pdf_path)

        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()

        return text

    except Exception as e:
        return f"Error extracting inspection report: {str(e)}"
    

@tool
def extract_thermal_report(pdf_path: str) ->str:
    """
    Extract text from a thermal report PDF.
    Returns thermal observations and temperature information.
    """

    try:
        doc = fitz.open(pdf_path)

        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()

        return text

    except Exception as e:
        return f"Error extracting thermal report: {str(e)}"
    

@tool
def extract_images(pdf_path: str, output_folder: str = "images") -> str:
    """
    Extract all images from a PDF.
    Saves images into the specified folder.
    Returns the list of extracted image paths.
    """

    try:

        os.makedirs(output_folder, exist_ok=True)

        doc = fitz.open(pdf_path)

        image_paths = []

        count = 1

        for page_index in range(len(doc)):

            page = doc.load_page(page_index)

            images = page.get_images(full=True)

            for img in images:

                xref = img[0]

                base_image = doc.extract_image(xref)

                image_bytes = base_image["image"]

                ext = base_image["ext"]

                filename = os.path.join(
                    output_folder,
                    f"image_{count}.{ext}"
                )

                with open(filename, "wb") as f:
                    f.write(image_bytes)

                image_paths.append(filename)

                count += 1

        doc.close()

        return json.dumps(image_paths)

    except Exception as e:
        return f"Error extracting images: {str(e)}"
    

@tool
def structure_inspection_data(report_text: str) -> str:
    """
    Convert raw inspection report text into structured JSON grouped by location.
    """

    prompt = f"""
    You are an inspection parser.

    Convert the following report into JSON.

    For every room identify

    - Room Name
    - Issues
    - Observations
    - Damage
    - Notes

    Return ONLY valid JSON.

    Report:

    {report_text}
    """

    return prompt


@tool
def structure_thermal_data(report_text: str) -> str:
    """
    Convert raw thermal report into structured JSON.
    """

    prompt = f"""
    You are a thermal report parser.

    Extract

    - Room
    - Thermal Findings
    - Temperature Difference
    - Moisture Indicators
    - Notes

    Return ONLY JSON.

    Report

    {report_text}
    """

    return prompt


@tool
def merge_reports(inspection_json: str, thermal_json: str) -> str:
    """
    Merge inspection and thermal findings into a single structured report.
    Detect conflicts and missing information.
    """

    prompt = f"""
    You are an expert building inspection engineer.

    Merge the two reports.

    Rules:

    1. Match rooms.

    2. Combine findings.

    3. If one report is missing data write

    Not Available

    4. If reports disagree

    Mention both findings.

    Never choose one.

    5. Determine

    - Observation
    - Root Cause
    - Severity
    - Recommendation

    Inspection

    {inspection_json}

    Thermal

    {thermal_json}

    Return JSON only.
    """

    return prompt


@tool
def generate_ddr(reasoning_json: str) -> str:
    """
    Generate the final Detailed Defect Report (DDR) in professional format.
    """

    prompt = f"""
    Create a professional Detailed Defect Report.

    Include

    Property Summary

    Area Wise Observations

    Root Causes

    Severity

    Recommendations

    Missing Information

    Report

    {reasoning_json}
    """

    return prompt


from docx import Document


@tool
def export_docx(report: str, filename: str = "DDR_Report.docx") -> str:
    """
    Export the generated DDR report into a Word document.
    """

    try:

        doc = Document()

        doc.add_heading("Detailed Defect Report", level=1)

        doc.add_paragraph(report)

        doc.save(filename)

        return filename

    except Exception as e:

        return f"Error: {str(e)}"
    

