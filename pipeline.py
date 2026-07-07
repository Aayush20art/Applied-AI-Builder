from agents import (
    build_inspection_agent,
    build_thermal_agent,
    build_image_agent,
    build_reasoning_agent,
    build_export_agent,
    writer_chain,
    validator_chain
)


def run_ddr_pipeline(
    inspection_pdf: str,
    thermal_pdf: str
) -> dict:

    state = {}

    # =====================================================
    # STEP 1 - Inspection Agent
    # =====================================================

    print("\n" + "=" * 60)
    print("STEP 1 - Inspection Agent is processing inspection report...")
    print("=" * 60)

    inspection_agent = build_inspection_agent()

    inspection_result = inspection_agent.invoke({
        "messages": [
            (
                "user",
                f"""
                Read the inspection report located at:

                {inspection_pdf}

                Extract all observations and structure them.
                """
            )
        ]
    })

    state["inspection_data"] = inspection_result["messages"][-1].content

    print(state["inspection_data"])


    # =====================================================
    # STEP 2 - Thermal Agent
    # =====================================================

    print("\n" + "=" * 60)
    print("STEP 2 - Thermal Agent is processing thermal report...")
    print("=" * 60)

    thermal_agent = build_thermal_agent()

    thermal_result = thermal_agent.invoke({
        "messages": [
            (
                "user",
                f"""
                Read the thermal report located at:

                {thermal_pdf}

                Extract all thermal findings and structure them.
                """
            )
        ]
    })

    state["thermal_data"] = thermal_result["messages"][-1].content

    print(state["thermal_data"])


    # =====================================================
    # STEP 3 - Image Agent
    # =====================================================

    print("\n" + "=" * 60)
    print("STEP 3 - Extracting images...")
    print("=" * 60)

    image_agent = build_image_agent()

    inspection_images = image_agent.invoke({
        "messages": [
            (
                "user",
                f"Extract all images from {inspection_pdf}"
            )
        ]
    })

    thermal_images = image_agent.invoke({
        "messages": [
            (
                "user",
                f"Extract all images from {thermal_pdf}"
            )
        ]
    })

    state["inspection_images"] = inspection_images["messages"][-1].content
    state["thermal_images"] = thermal_images["messages"][-1].content

    print("Inspection Images:", state["inspection_images"])
    print("Thermal Images:", state["thermal_images"])


    # =====================================================
    # STEP 4 - Reasoning Agent
    # =====================================================

    print("\n" + "=" * 60)
    print("STEP 4 - Merging reports...")
    print("=" * 60)

    reasoning_agent = build_reasoning_agent()

    reasoning_result = reasoning_agent.invoke({
        "messages": [
            (
                "user",
                f"""
Inspection Data

{state['inspection_data']}

Thermal Data

{state['thermal_data']}

Merge the reports.

Detect conflicts.

Detect missing information.

Assign severity.

Determine root causes.

Recommend actions.
"""
            )
        ]
    })

    state["merged_report"] = reasoning_result["messages"][-1].content

    print(state["merged_report"])


    # =====================================================
    # STEP 5 - Generate DDR
    # =====================================================

    print("\n" + "=" * 60)
    print("STEP 5 - Generating Detailed Defect Report...")
    print("=" * 60)

    state["ddr_report"] = writer_chain.invoke({

        "merged_report": state["merged_report"]

    })

    print(state["ddr_report"])


    # =====================================================
    # STEP 6 - Validate DDR
    # =====================================================

    print("\n" + "=" * 60)
    print("STEP 6 - Validating report...")
    print("=" * 60)

    state["validation"] = validator_chain.invoke({

        "report": state["ddr_report"]

    })

    print(state["validation"])


    # =====================================================
    # STEP 7 - Export Report
    # =====================================================

    print("\n" + "=" * 60)
    print("STEP 7 - Exporting report...")
    print("=" * 60)

    export_agent = build_export_agent()

    export_result = export_agent.invoke({
        "messages": [
            (
                "user",
                f"""
Export the following report as a DOCX.

{state['ddr_report']}
"""
            )
        ]
    })

    state["output_file"] = export_result["messages"][-1].content

    print(state["output_file"])

    return state


if __name__ == "__main__":

    inspection_pdf = input("Enter Inspection Report PDF path: ")

    thermal_pdf = input("Enter Thermal Report PDF path: ")

    run_ddr_pipeline(
        inspection_pdf,
        thermal_pdf
    )