import streamlit as st
import tempfile
import os

from pipeline import run_ddr_pipeline

st.set_page_config(
    page_title="AI Property Inspection Report Generator",
    page_icon="🏠",
    layout="wide"
)

# --------------------------------------------------------
# Header
# --------------------------------------------------------

st.title("🏠 AI Property Inspection Report Generator")

st.markdown(
"""
Upload:

- Inspection Report (PDF)
- Thermal Report (PDF)

The AI will:

✅ Extract text

✅ Extract images

✅ Merge both reports

✅ Detect conflicts

✅ Generate a Detailed Defect Report (DDR)

✅ Export a DOCX report
"""
)

st.divider()

# --------------------------------------------------------
# Upload PDFs
# --------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    inspection_pdf = st.file_uploader(
        "Upload Inspection Report",
        type=["pdf"]
    )

with col2:
    thermal_pdf = st.file_uploader(
        "Upload Thermal Report",
        type=["pdf"]
    )

st.divider()

# --------------------------------------------------------
# Run Pipeline
# --------------------------------------------------------

if st.button("🚀 Generate DDR", use_container_width=True):

    if inspection_pdf is None or thermal_pdf is None:

        st.warning("Please upload both PDF files.")

    else:

        with tempfile.TemporaryDirectory() as tmpdir:

            inspection_path = os.path.join(
                tmpdir,
                inspection_pdf.name
            )

            thermal_path = os.path.join(
                tmpdir,
                thermal_pdf.name
            )

            with open(inspection_path, "wb") as f:
                f.write(inspection_pdf.read())

            with open(thermal_path, "wb") as f:
                f.write(thermal_pdf.read())

            with st.spinner("AI Agents are analyzing the reports..."):

                state = run_ddr_pipeline(
                    inspection_path,
                    thermal_path
                )

        st.success("DDR Generated Successfully!")

        # --------------------------------------------------------
        # Inspection Data
        # --------------------------------------------------------

        with st.expander("📄 Inspection Report Data"):

            st.write(state["inspection_data"])

        # --------------------------------------------------------
        # Thermal Data
        # --------------------------------------------------------

        with st.expander("🌡 Thermal Report Data"):

            st.write(state["thermal_data"])

        # --------------------------------------------------------
        # Merged Findings
        # --------------------------------------------------------

        with st.expander("🔄 Merged Findings"):

            st.write(state["merged_report"])

        # --------------------------------------------------------
        # DDR Report
        # --------------------------------------------------------

        st.subheader("📋 Detailed Defect Report")

        st.markdown(state["ddr_report"])

        # --------------------------------------------------------
        # Validation
        # --------------------------------------------------------

        st.subheader("✅ Quality Review")

        st.markdown(state["validation"])

        # --------------------------------------------------------
        # Download Report
        # --------------------------------------------------------

        if os.path.exists(state["output_file"]):

            with open(state["output_file"], "rb") as file:

                st.download_button(

                    label="⬇ Download DDR Report",

                    data=file,

                    file_name="DDR_Report.docx",

                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",

                    use_container_width=True
                )
