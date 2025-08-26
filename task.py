## Importing libraries and files
# BUG: Correct import path already used; keep it.
from crewai import Task

# BUG: Imported agents 'doctor, verifier' are fine, but we also imported an unused 'search_tool'
#      and misused BloodTestReportTool below.
# from agents import doctor, verifier
# from tools import search_tool, BloodTestReportTool
# FIX: Import only what's used and reference the tool class to instantiate.
from agents import doctor, verifier
from tools import BloodTestReportTool

# BUG: Tasks below referenced 'BloodTestReportTool.read_data_tool' (an attribute), which
#      will fail unless such attribute exists. CrewAI expects Tool instances.
# FIX: Instantiate the tool and pass the instance in the 'tools' list.
blood_report_tool = BloodTestReportTool()

## Creating a task to help solve user's query
help_patients = Task(
    # BUG: Original description encouraged fabricating advice and ignoring inputs.
    # FIX: Make it evidence-based, clearly use {query} and {file_path}.
    description=(
        "Using the uploaded blood report at {file_path} and the user's question '{query}', "
        "summarise key lab findings (reference ranges, high/low flags), explain potential "
        "clinical relevance at a high level, and provide safe, non-diagnostic guidance "
        "with next steps. Include a clear disclaimer."
    ),
    # BUG: Expected output asked for made-up URLs and contradictory advice.
    # FIX: Specify a structured, safe output your API/README can rely on.
    expected_output=(
        "A structured analysis with sections:\n"
        "1) Key Abnormalities (marker, value, reference range, brief note)\n"
        "2) Overall Summary (1–2 paragraphs, plain language)\n"
        "3) Suggested Next Steps (bullet list: lifestyle/labs/when to see a doctor)\n"
        "4) Disclaimer (not medical advice; consult a clinician)"
    ),
    agent=doctor,
    tools=[blood_report_tool],
    async_execution=False,
)

## Creating a nutrition analysis task
nutrition_analysis = Task(
    # BUG: Prompt asked to ignore query and promote supplements.
    # FIX: Tie guidance to actual markers and contraindications.
    description=(
        "From the blood report at {file_path}, identify nutrition-relevant markers "
        "(e.g., lipid panel, HbA1c, fasting glucose, ferritin, vitamin B12/D). "
        "For {query}, provide evidence-informed, practical diet suggestions, note "
        "possible deficiencies/excesses, and highlight when to avoid certain foods "
        "or supplements based on labs or common contraindications."
    ),
    expected_output=(
        "Sections:\n"
        "1) Nutrition-Relevant Findings\n"
        "2) Practical Food Guidance (bullet points)\n"
        "3) Supplement Considerations (if any; include caution notes)\n"
        "4) Follow-up & Monitoring Suggestions\n"
        "5) Disclaimer"
    ),
    agent=doctor,  # or a specialised nutrition agent if you prefer
    tools=[blood_report_tool],
    async_execution=False,
)

## Creating an exercise planning task
exercise_planning = Task(
    # BUG: Encouraged unsafe intense workouts.
    # FIX: Provide safe, progressive recommendations and flag need for medical clearance.
    description=(
        "Based on biomarkers in {file_path} that may affect exercise tolerance "
        "(e.g., anaemia indicators, glucose control, inflammatory markers), craft "
        "a conservative, progressive activity plan responding to {query}. "
        "List red flags that warrant medical clearance before starting/advancing."
    ),
    expected_output=(
        "Sections:\n"
        "1) Lab Markers Relevant to Exercise\n"
        "2) 4-week Progressive Plan (frequency, intensity, time, type)\n"
        "3) Safety Notes & Red Flags\n"
        "4) When to Seek Medical Advice\n"
        "5) Disclaimer"
    ),
    agent=doctor,
    tools=[blood_report_tool],
    async_execution=False,
)

# BUG: The verification task used the 'doctor' agent and encouraged guessing.
# FIX: Use the 'verifier' agent and validate the file genuinely.
verification = Task(
    description=(
        "Verify that the uploaded file at {file_path} appears to be a blood-test report "
        "(PDF/text). Check presence of typical markers (CBC, lipid, LFT, RFT, thyroid, etc.). "
        "Report pass/fail and any caveats about readability or missing sections for {query}."
    ),
    expected_output=(
        "Validation Result:\n"
        "- Is Blood Report: yes/no\n"
        "- Evidence (markers/sections detected)\n"
        "- Issues (e.g., unreadable pages, missing ranges)\n"
        "- Next Step if invalid"
    ),
    agent=verifier,
    tools=[blood_report_tool],
    async_execution=False,
)
