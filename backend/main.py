
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from workflow.graph import run_research

from database.db import (
    initialize_database,
    save_research,
    get_research_history,
    get_research_by_id,
)


# ==================================================
# 1. Initialize FastAPI
# ==================================================

app = FastAPI(
    title="ResearchX AI API",
    description=(
        "A multi-agent AI research assistant powered by "
        "Gemini, LangGraph, MCP, Tavily, and SQLite."
    ),
    version="1.0.0",
)


# ==================================================
# 2. Initialize the database
# ==================================================

initialize_database()


# ==================================================
# 3. Define request and response models
# ==================================================

class ResearchRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="The research topic to investigate.",
    )


class ResearchResponse(BaseModel):
    id: int
    topic: str
    report: str
    created_at: str


class ResearchHistoryItem(BaseModel):
    id: int
    topic: str
    created_at: str


# ==================================================
# 4. Home endpoint
# ==================================================

@app.get("/")
def home():
    return {
        "application": "ResearchX AI",
        "message": "Welcome to the ResearchX AI API!",
        "status": "running",
    }


# ==================================================
# 5. Health check endpoint
# ==================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "ResearchX AI",
        "database": "initialized",
    }


# ==================================================
# 6. Run the research workflow
# ==================================================


@app.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest):
    topic = request.topic.strip()

    if len(topic) < 3:
        raise HTTPException(
            status_code=422,
            detail="Please enter a research topic with at least 3 characters.",
        )

    try:
        # Execute the LangGraph research workflow.
        result = run_research(topic)

        report = result.get("final_report")

        if not report:
            raise RuntimeError(
                "The research workflow did not produce a final report."
            )

        # Save the completed report in SQLite.
        research_id = save_research(
            topic=topic,
            report=report,
        )

        # Retrieve the saved record.
        saved_record = get_research_by_id(research_id)

        if saved_record is None:
            raise RuntimeError(
                "Report generated, but the database record was not found."
            )

        return ResearchResponse(
            id=saved_record["id"],
            topic=saved_record["topic"],
            report=saved_record["report"],
            created_at=saved_record["created_at"],
        )

    except HTTPException:
        raise

    except Exception as error:
        # Log the complete error in the backend terminal.
        print(
            f"\n[ResearchX AI] Research failed: "
            f"{type(error).__name__}: {error}",
            flush=True,
        )

        # Preserve a useful status code for quota-related failures.
        error_text = str(error).upper()

        if (
            "RESOURCE_EXHAUSTED" in error_text
            or "429" in error_text
            or "QUOTA" in error_text
        ):
            raise HTTPException(
                status_code=429,
                detail=(
                    "The AI provider quota has been exceeded. "
                    "Check your Gemini API quota and try again "
                    "when requests become available."
                ),
            ) from error

        raise HTTPException(
            status_code=500,
            detail=(
                "Research failed. Check the backend terminal "
                "for the full diagnostic error."
            ),
        ) from error




# ==================================================
# 7. Retrieve research history
# ==================================================

@app.get(
    "/history",
    response_model=list[ResearchHistoryItem],
)
def research_history():
    try:
        history = get_research_history(limit=50)

        return history

    except Exception as error:
        print(f"Failed to retrieve research history: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve research history.",
        ) from error


# ==================================================
# 8. Retrieve a specific saved report
# ==================================================

@app.get("/history/{research_id}")
def research_details(research_id: int):
    try:
        record = get_research_by_id(research_id)

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="Research report not found.",
            )

        return record

    except HTTPException:
        raise

    except Exception as error:
        print(f"Failed to retrieve research report: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve the research report.",
        ) from error

