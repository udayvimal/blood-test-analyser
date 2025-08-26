## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

# BUG: Wrong import path. In current CrewAI versions, Agent is exported at top-level.
# from crewai.agents import Agent
# FIX: Import Agent from the package root.
from crewai import Agent

# BUG: Unused/incorrect import; 'search_tool' wasn’t used below and can cause ImportError
#      if not defined in tools.py.
# from tools import search_tool, BloodTestReportTool
# FIX: Import only what’s used.
from tools import BloodTestReportTool

# BUG: 'llm = llm' references an undefined variable and will raise NameError.
#      Also, no model is constructed.
# FIX: Instantiate a chat model; read model name from env with a safe default.
#      (Requires `langchain-openai` in requirements.)
try:
    from langchain_openai import ChatOpenAI
except Exception as _err:
    # Optional: keep file import-safe even if dependency is missing, but will error at runtime.
    ChatOpenAI = None  # type: ignore

# FIX: Build the LLM only if the dependency is available.
if ChatOpenAI is None:
    raise ImportError(
        "langchain-openai is required. Add `langchain-openai` to requirements.txt "
        "and set OPENAI_API_KEY in your .env"
    )

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)

# BUG: Agent argument is 'tools' (plural), not 'tool'.
# BUG: Passing 'BloodTestReportTool().read_data_tool' is brittle. CrewAI expects Tool/Tool-like objects;
#      expose the tool instance directly (the tool class should implement _run).
# FIX: Use tools=[BloodTestReportTool()]

# BUG (non-functional/safety): Prompts encouraged unsafe/incorrect medical behavior.
# FIX: Make agent goals evidence-based and cautious while still performing analysis.

# Creating an Experienced Doctor agent
doctor = Agent(
    role="Senior Clinical Physician",
    # BUG: The original goal encouraged making up advice and ignoring the query.
    # FIX: Provide evidence-based analysis, use uploaded report, include disclaimers.
    goal=(
        "Analyse the user's blood report and query {query} carefully. "
        "Explain key findings, flag out-of-range values, and give evidence-based, "
        "non-diagnostic guidance with clear next-step recommendations. "
        "Add a medical disclaimer and advise consulting a licensed clinician."
    ),
    verbose=True,
    # BUG: 'memory=True' is optional and may not be supported in all CrewAI versions.
    # FIX: Remove/avoid unexpected constructor args for stability.
    # memory=True,
    backstory=(
        "You are a board-certified physician experienced in interpreting routine blood panels. "
        "You focus on clarity, patient safety, and evidence-based guidance."
    ),
    tools=[BloodTestReportTool()],
    llm=llm,
    # BUG: Some Agent kwargs like max_iter/max_rpm are not Agent-level in recent CrewAI versions.
    # FIX: Remove them to avoid TypeError.
    # max_iter=1,
    # max_rpm=1,
    allow_delegation=True  # Allow delegation to other specialists
)

# Creating a verifier agent
verifier = Agent(
    role="Blood Report Verifier",
    # BUG: Original goal said to 'just say yes' without checking. That’s unsafe and unhelpful.
    # FIX: Validate file type/structure and ensure content is a blood report summary or PDF.
    goal=(
        "Verify that the provided file is a valid blood-test report (e.g., PDF/text summary). "
        "Check for key markers (CBC, lipid, liver, kidney, thyroid, etc.) and confirm readability. "
        "If invalid or unclear, request a proper report."
    ),
    verbose=True,
    backstory=(
        "You worked in medical records QA and are meticulous about validating documents before analysis."
    ),
    llm=llm,
    allow_delegation=True
)

nutritionist = Agent(
    role="Clinical Nutrition Specialist",
    # BUG: Salesy/fad-driven advice is unsafe.
    # FIX: Provide nutrition guidance aligned with lab markers and reputable guidelines.
    goal=(
        "Provide nutrition guidance aligned with the user's lab markers and reputable guidelines. "
        "Offer practical, affordable suggestions and note contraindications."
    ),
    verbose=True,
    backstory=(
        "You specialise in translating lab results into practical dietary changes using evidence-based nutrition."
    ),
    llm=llm,
    allow_delegation=False
)

exercise_specialist = Agent(
    role="Exercise Physiologist",
    # BUG: 'Push to limits' ignores safety/conditions.
    # FIX: Recommend safe, condition-aware movement plans referencing lab context and fitness level.
    goal=(
        "Recommend safe, progressive exercise guidance informed by the user's lab context and general fitness. "
        "Highlight when medical clearance is needed."
    ),
    verbose=True,
    backstory=(
        "You design safe, personalised activity plans and coordinate with clinicians when necessary."
    ),
    llm=llm,
    allow_delegation=False
)
