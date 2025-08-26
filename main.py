from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
# BUG: Unused import; 'asyncio' is never referenced and can confuse linters/type-checkers.
# import asyncio
# FIX: Remove unused import to keep the module clean.

from crewai import Crew, Process
from agents import doctor
from task import help_patients

app = FastAPI(title="Blood Test Report Analyser")

def run_crew(query: str, file_path: str = "data/sample.pdf"):
    """To run the whole crew"""
    medical_crew = Crew(
        agents=[doctor],
        tasks=[help_patients],
        process=Process.sequential,
    )

    # BUG: Only 'query' was passed to kickoff; tasks that reference 'file_path'
    #      would receive no value and crash with a KeyError/validation error.
    # result = medical_crew.kickoff({'query': query})
    # FIX: Pass both 'query' and 'file_path' so the Task prompt/inputs can render.
    result = medical_crew.kickoff({'query': query, 'file_path': file_path})
    return result

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Blood Test Report Analyser API is running"}

@app.post("/analyze")
async def analyze_blood_report(
    file: UploadFile = File(...),
    query: str = Form(default="Summarise my Blood Test Report")
):
    """Analyze blood test report and provide comprehensive health recommendations"""

    # Generate unique filename to avoid conflicts
    file_id = str(uuid.uuid4())
    file_path = f"data/blood_test_report_{file_id}.pdf"

    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # BUG: No validation on uploaded content; non-PDF files would be saved and
        #      downstream tools expecting PDFs would fail.
        # FIX: Basic check using filename/content_type before saving.
        content_type = (file.content_type or "").lower()
        if not (file.filename.lower().endswith(".pdf") or content_type == "application/pdf"):
            raise HTTPException(status_code=400, detail="Please upload a PDF file.")

        # Save uploaded file
        # BUG: Reading entire file into memory may be unnecessary for large files.
        # with open(file_path, "wb") as f:
        #     content = await file.read()
        #     f.write(content)
        # FIX: Stream to disk in chunks to reduce memory pressure.
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB
                if not chunk:
                    break
                f.write(chunk)

        # Validate query
        # BUG: Loose check could leave whitespace; also 'None' or blank should default.
        # if query=="" or query is None:
        #     query = "Summarise my Blood Test Report"
        # FIX: Strip & fallback safely.
        query = (query or "").strip() or "Summarise my Blood Test Report"

        # Process the blood report with all specialists
        response = run_crew(query=query, file_path=file_path)

        return {
            "status": "success",
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename
        }

    except HTTPException:
        # Re-raise HTTP errors as-is
        raise
    except Exception as e:
        # BUG: Swallowing original error details makes debugging harder.
        # raise HTTPException(status_code=500, detail="Error processing blood report")
        # FIX: Include the exception string in the detail for visibility.
        raise HTTPException(status_code=500, detail=f"Error processing blood report: {str(e)}")

    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                # BUG: Bare except hides unexpected issues.
                # FIX: Keep silent by design during cleanup but be explicit.
                pass  # Ignore cleanup errors on purpose

if __name__ == "__main__":
    import uvicorn
    # BUG: reload=True in production can spawn multiple workers that duplicate Crew runs.
    #      It's fine for local dev; keep it but be aware. No functional change required.
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
