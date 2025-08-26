## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

# BUG: Unused/wrong import; 'from crewai_tools import tools' doesn't expose what we need
#      and can raise ImportError depending on the version.
# from crewai_tools import tools
# FIX: Import BaseTool to create custom CrewAI tools, and import SerperDevTool directly.
from crewai_tools.tools import BaseTool
from crewai_tools.tools.serper_dev_tool import SerperDevTool

# BUG: PDFLoader is referenced below but never imported; name error at runtime.
# FIX: Use the community PyPDF loader compatible with LangChain.
try:
    from langchain_community.document_loaders import PyPDFLoader
except Exception as _err:
    PyPDFLoader = None  # type: ignore

from typing import Optional

## Creating search tool
# NOTE: Requires SERPER_API_KEY in .env to function at runtime.
search_tool = SerperDevTool()

# BUG: The original BloodTestReportTool was a plain class with an async method
#      that CrewAI won't discover/call. CrewAI custom tools should subclass BaseTool
#      and implement `_run(self, ...)` (sync) or `arun` (async).
# FIX: Implement a proper CrewAI tool returning clean text from a PDF.

class BloodTestReportTool(BaseTool):
    name: str = "blood_test_report_reader"
    description: str = (
        "Read a blood-test PDF from disk and return a cleaned, plain-text version "
        "for analysis. Input is a file path."
    )

    # BUG: Missing constructor to optionally set a default path.
    # FIX: Allow an optional default path but still accept runtime args.
    def __init__(self, default_path: Optional[str] = None):
        super().__init__()
        self.default_path = default_path or "data/sample.pdf"

    # BUG: Original signature was `async def read_data_tool(path='...')` and used an
    #      undefined `PDFLoader`. It also returned raw, messy text with double newlines.
    # FIX: Implement `_run(self, path: str | None = None)` and use `PyPDFLoader`.
    def _run(self, path: Optional[str] = None) -> str:
        # Dependency sanity check
        if PyPDFLoader is None:
            raise ImportError(
                "langchain-community is required for PyPDFLoader. "
                "Add `langchain-community` to requirements.txt."
            )

        file_path = (path or self.default_path).strip()

        # Validate file existence and type
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.lower().endswith(".pdf"):
            raise ValueError(f"Expected a PDF file, got: {file_path}")

        # Load and concatenate pages
        docs = PyPDFLoader(file_path=file_path).load()

        full_report = []
        for d in docs:
            content = d.page_content or ""
            # Normalize whitespace
            content = content.replace("\r", "\n")
            # Collapse 3+ newlines to 2, then 2 to 1 iteratively
            while "\n\n\n" in content:
                content = content.replace("\n\n\n", "\n\n")
            while "\n\n" in content:
                content = content.replace("\n\n", "\n")
            # Collapse multiple spaces
            while "  " in content:
                content = content.replace("  ", " ")
            full_report.append(content.strip())

        text = "\n".join([t for t in full_report if t])

        # BUG: Could return empty string if OCR fails / blank PDF pages.
        # FIX: Guard with a helpful message for upstream agents.
        if not text.strip():
            return (
                "The PDF was readable but contains no extractable text. "
                "It may be scanned images without OCR. Please upload a text-based PDF."
            )

        return text


# (Optional) Nutrition/Exercise tools — left as placeholders but made CrewAI-compatible
# so you can wire them later if you want. They currently return a stub and won’t break imports.

class NutritionTool(BaseTool):
    name: str = "nutrition_analysis_stub"
    description: str = "Placeholder: analyze nutrition aspects from a blood report text."

    # BUG: Original method was async and not a CrewAI tool method.
    # FIX: Implement `_run` with a simple placeholder.
    def _run(self, blood_report_data: str) -> str:
        # Very light normalization (kept from original logic intent)
        processed = " ".join((blood_report_data or "").split())
        return (
            "Nutrition analysis functionality to be implemented.\n"
            f"(Received {len(processed)} characters of report text.)"
        )

class ExerciseTool(BaseTool):
    name: str = "exercise_plan_stub"
    description: str = "Placeholder: generate a safe exercise plan using report context."

    def _run(self, blood_report_data: str) -> str:
        return "Exercise planning functionality to be implemented."
