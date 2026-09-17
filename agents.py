import streamlit as st
import os

# Inject secrets into env before any client is instantiated
os.environ["MISTRAL_API_KEY"] = st.secrets["MISTRAL_API_KEY"]

from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import (
    extract_inspection_report,
    extract_thermal_report,
    extract_images,
    structure_inspection_data,
    structure_thermal_data,
    merge_reports,
    export_docx
)

# --------------------------------------------------
# LLM
# --------------------------------------------------

llm = ChatMistralAI(
    model="mistral-small-2506",
    temperature=0
)

# --------------------------------------------------
# Agent 1
# Inspection Agent
# --------------------------------------------------

def build_inspection_agent():

    return create_agent(
        model=llm,
        tools=[
            extract_inspection_report,
            structure_inspection_data
        ]
    )

# --------------------------------------------------
# Agent 2
# Thermal Agent
# --------------------------------------------------

def build_thermal_agent():

    return create_agent(
        model=llm,
        tools=[
            extract_thermal_report,
            structure_thermal_data
        ]
    )

# --------------------------------------------------
# Agent 3
# Image Extraction Agent
# --------------------------------------------------

def build_image_agent():

    return create_agent(
        model=llm,
        tools=[
            extract_images
        ]
    )

# --------------------------------------------------
# Agent 4
# Reasoning Agent
# --------------------------------------------------

def build_reasoning_agent():

    return create_agent(
        model=llm,
        tools=[
            merge_reports
        ]
    )

# --------------------------------------------------
# Agent 5
# Export Agent
# --------------------------------------------------

def build_export_agent():

    return create_agent(
        model=llm,
        tools=[
            export_docx
        ]
    )

# --------------------------------------------------
# DDR Writer Chain
# --------------------------------------------------

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a senior structural inspection engineer.

Your responsibility is to produce a professional
Detailed Defect Report (DDR).

Never invent information.

If information is missing write:

Not Available

If two reports disagree, clearly mention the conflict.

Write in a professional engineering style.
"""
    ),

    (
        "human",
        """
Using the merged inspection data below, create a professional
Detailed Defect Report.

Merged Data

{merged_report}

The report MUST contain:

1. Property Issue Summary

2. Area-wise Observations

For every room include

- Observation
- Thermal Findings
- Inspection Findings
- Images (if available)

3. Probable Root Cause

4. Severity Assessment

5. Recommended Actions

6. Missing Information

7. Conflicts (if any)

Do not hallucinate.

Return the report in clean markdown.
"""
    ),
])

writer_chain = writer_prompt | llm | StrOutputParser()

# --------------------------------------------------
# Validation Chain
# --------------------------------------------------

validator_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an experienced quality assurance engineer.

Review the generated DDR report.

Check for:

• Hallucinations
• Missing sections
• Incorrect reasoning
• Missing room information
• Conflict handling
• Missing Information section
• Professional formatting

Never rewrite the report.

Only review it.
"""
    ),

    (
        "human",
        """
Review the report below.

{report}

Respond exactly in this format.

Overall Score: X/10

Strengths

- ...

- ...

Issues Found

- ...

- ...

Missing Sections

- ...

Final Verdict

...
"""
    ),
])

validator_chain = validator_prompt | llm | StrOutputParser()
