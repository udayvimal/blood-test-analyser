🩺 Blood Test Report Analyser (CrewAI + FastAPI)

This project provides an API to analyse uploaded blood test reports (PDFs) and return a structured, evidence-informed summary with next steps. It uses FastAPI for serving endpoints, CrewAI for orchestration, and LangChain tools for reading PDF data.
 🐛 Bug Fix Log

Here’s a structured log of all bugs found and how they were fixed.

1. main.py

BUG: asyncio imported but unused.
FIX: Removed to keep code clean.

BUG: kickoff({'query': query}) did not pass file_path, breaking tasks needing {file_path}.
FIX: kickoff({'query': query, 'file_path': file_path}).

BUG: No validation for uploaded file type.
FIX: Added check to ensure only PDF files are accepted, else HTTPException(400).

BUG: Entire file read into memory at once.
FIX: Streamed upload to disk in 1MB chunks.

BUG: Query default check was loose (if query == "" or query is None).
FIX: Normalized with (query or "").strip() or "Summarise my Blood Test Report".

BUG: 500 error messages hid underlying issue.
FIX: Included str(e) in HTTPException detail for better debugging.

2. agents.py

BUG: Wrong import path: from crewai.agents import Agent.
FIX: from crewai import Agent.

BUG: llm = llm (undefined variable).
FIX: Instantiated ChatOpenAI with OPENAI_MODEL from .env.

BUG: Used tool=[...] instead of tools=[...].
FIX: Corrected to tools=[BloodTestReportTool()].

BUG: Passed unsupported args (memory, max_iter, max_rpm) to Agent.
FIX: Removed for CrewAI v0.28 compatibility.

BUG: Prompts encouraged unsafe/fabricated medical advice.
FIX: Rewrote goals/backstories to provide safe, evidence-based outputs with disclaimers.

3. task.py

BUG: tools=[BloodTestReportTool.read_data_tool] passed a method, not a tool instance.
FIX: Instantiated tool:

blood_report_tool = BloodTestReportTool()
tools=[blood_report_tool]


BUG: Verification task used doctor agent.
FIX: Assigned to verifier.

BUG: Tasks ignored {file_path}, making file input useless.
FIX: Added {file_path} placeholder in all descriptions.

BUG: Prompts encouraged fake URLs, contradictions, unsafe plans.
FIX: Rewrote task descriptions + expected outputs to structured, safe formats.

BUG: Unused import search_tool.
FIX: Removed.

4. tools.py

BUG: Wrong import: from crewai_tools import tools.
FIX: Correct import:

from crewai_tools.tools import BaseTool
from crewai_tools.tools.serper_dev_tool import SerperDevTool


BUG: PDFLoader referenced but never imported.
FIX: Imported PyPDFLoader from langchain_community.document_loaders.

BUG: BloodTestReportTool was a plain class with async method (read_data_tool), not CrewAI-compatible.
FIX: Subclassed BaseTool, implemented _run(self, path).

BUG: No check for file existence or type.
FIX: Added os.path.exists + extension check.

BUG: Whitespace handling weak (only replaced \n\n).
FIX: Collapsed multiple spaces/newlines, cleaned text properly.

BUG: Could return empty text for scanned PDFs.
FIX: Added guard: return helpful OCR message if no text extracted.

BUG: NutritionTool/ExerciseTool async methods not CrewAI-compatible.
FIX: Converted to BaseTool subclasses with _run stubs.

📦 Setup & Installation
1. Clone repo & create venv
git clone <your-repo-url>
cd blood-test-analyser
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

2. Install dependencies
pip install -r requirements.txt


requirements.txt

fastapi
uvicorn
crewai
crewai-tools
python-dotenv
langchain
langchain-community
langchain-openai
pydantic>=2

3. Environment variables

Create a .env file:

OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini
SERPER_API_KEY=your_serper_key   # optional if using search tool

4. Run server
uvicorn main:app --reload --port 8000


Health check: http://localhost:8000

📡 API Documentation
POST /analyze

Upload a PDF + optional query.

Form fields

file → PDF (required)

query → string (optional, default = “Summarise my Blood Test Report”)

Example request

curl -X POST http://localhost:8000/analyze \
  -F "file=@data/sample.pdf" \
  -F "query=Summarise abnormalities and next steps"


Response

{
  "status": "success",
  "query": "Summarise abnormalities and next steps",
  "analysis": "<CrewAI analysis>",
  "file_processed": "sample.pdf"
}


🏆 Bonus Improvements (optional ideas)

Queue worker (Celery/Redis) for concurrent requests.

Database integration (PostgreSQL/SQLite) to store results.

Streamlit/React dashboard for visualization.
