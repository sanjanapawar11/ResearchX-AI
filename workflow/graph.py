
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from agents.planner import create_research_plan
from tools.mcp_client import search_with_mcp
import asyncio
from agents.analyst import analyze_research
from agents.fact_checker import fact_check_research
from agents.report_generator import generate_report


# --------------------------------------------------
# 1. Shared workflow state
# --------------------------------------------------

class ResearchState(TypedDict, total=False):
    topic: str
    research_plan: str
    search_results: list[dict]
    analysis: str
    fact_check_report: str
    final_report: str
    error: str


# --------------------------------------------------
# 2. Planner node
# --------------------------------------------------

def planner_node(state: ResearchState) -> dict:
    try:
        topic = state.get("topic", "").strip()

        if not topic:
            raise ValueError("Research topic is missing.")

        plan = create_research_plan(topic)

        if not plan:
            raise ValueError("Planner returned an empty research plan.")

        return {"research_plan": plan}

    except Exception as error:
        return {"error": f"Planner failed: {error}"}


# --------------------------------------------------
# 3. Web research node
# --------------------------------------------------


def research_node(state: ResearchState) -> dict:
    """Retrieve web research results through the MCP client."""

    try:
        response = asyncio.run(
            search_with_mcp(
                query=state["topic"],
                max_results=5,
            )
        )

        results = response.get("results", [])

        if not results:
            return {
                "error": "MCP web research returned no results."
            }

        return {
            "search_results": results
        }

    except Exception as error:
        return {
            "error": f"MCP web research failed: {error}"
        }




# --------------------------------------------------
# 4. Analysis node
# --------------------------------------------------

def analysis_node(state: ResearchState) -> dict:
    try:
        if state.get("error"):
            return {}

        research_plan = state.get("research_plan")
        search_results = state.get("search_results")

        if not research_plan:
            raise ValueError("Research plan is missing.")

        if not search_results:
            raise ValueError("Search results are missing.")

        analysis = analyze_research(
            topic=state["topic"],
            research_plan=research_plan,
            search_results=search_results,
        )

        if not analysis:
            raise ValueError("Analysis agent returned an empty result.")

        return {"analysis": analysis}

    except Exception as error:
        return {"error": f"Analysis failed: {error}"}


# --------------------------------------------------
# 5. Fact-checking node
# --------------------------------------------------

def fact_check_node(state: ResearchState) -> dict:
    try:
        if state.get("error"):
            return {}

        analysis = state.get("analysis")
        search_results = state.get("search_results")

        if not analysis:
            raise ValueError("Analysis is missing.")

        if not search_results:
            raise ValueError("Search results are missing.")

        report = fact_check_research(
            topic=state["topic"],
            analysis=analysis,
            search_results=search_results,
        )

        if not report:
            raise ValueError("Fact-checker returned an empty report.")

        return {"fact_check_report": report}

    except Exception as error:
        return {"error": f"Fact-checking failed: {error}"}


# --------------------------------------------------
# 6. Report generation node
# --------------------------------------------------

def report_node(state: ResearchState) -> dict:
    try:
        if state.get("error"):
            return {}

        topic = state.get("topic")
        research_plan = state.get("research_plan")
        analysis = state.get("analysis")
        fact_check_report = state.get("fact_check_report")

        missing = []

        if not topic:
            missing.append("topic")

        if not research_plan:
            missing.append("research_plan")

        if not analysis:
            missing.append("analysis")

        if not fact_check_report:
            missing.append("fact_check_report")

        if missing:
            raise ValueError(
                "Missing required workflow data: "
                + ", ".join(missing)
            )

        report = generate_report(
            topic=topic,
            research_plan=research_plan,
            analysis=analysis,
            fact_check_report=fact_check_report,
        )

        if not report:
            raise ValueError("Report generator returned an empty report.")

        return {"final_report": report}

    except Exception as error:
        return {"error": f"Report generation failed: {error}"}


# --------------------------------------------------
# 7. Conditional routing
# --------------------------------------------------

def route_after_planner(state: ResearchState) -> str:
    return "end" if state.get("error") else "research"


def route_after_research(state: ResearchState) -> str:
    return "end" if state.get("error") else "analysis"


def route_after_analysis(state: ResearchState) -> str:
    return "end" if state.get("error") else "fact_check"


def route_after_fact_check(state: ResearchState) -> str:
    return "end" if state.get("error") else "report"


def route_after_report(state: ResearchState) -> str:
    return "end"


# --------------------------------------------------
# 8. Build the LangGraph workflow
# --------------------------------------------------

builder = StateGraph(ResearchState)

builder.add_node("planner", planner_node)
builder.add_node("research", research_node)
builder.add_node("analysis", analysis_node)
builder.add_node("fact_check", fact_check_node)
builder.add_node("report", report_node)

builder.add_edge(START, "planner")

builder.add_conditional_edges(
    "planner",
    route_after_planner,
    {
        "research": "research",
        "end": END,
    },
)

builder.add_conditional_edges(
    "research",
    route_after_research,
    {
        "analysis": "analysis",
        "end": END,
    },
)

builder.add_conditional_edges(
    "analysis",
    route_after_analysis,
    {
        "fact_check": "fact_check",
        "end": END,
    },
)

builder.add_conditional_edges(
    "fact_check",
    route_after_fact_check,
    {
        "report": "report",
        "end": END,
    },
)

builder.add_conditional_edges(
    "report",
    route_after_report,
    {
        "end": END,
    },
)

research_graph = builder.compile()


# --------------------------------------------------
# 9. Public workflow function
# --------------------------------------------------

def run_research(topic: str) -> ResearchState:
    if not topic or not topic.strip():
        raise ValueError("Research topic cannot be empty.")

    initial_state: ResearchState = {
        "topic": topic.strip()
    }

    result = research_graph.invoke(initial_state)

    if result.get("error"):
        raise RuntimeError(result["error"])

    if not result.get("final_report"):
        raise RuntimeError(
            "Workflow finished without producing a final report."
        )

    return result


# --------------------------------------------------
# 10. Run from the terminal
# --------------------------------------------------

if __name__ == "__main__":
    topic = input("Enter a research topic: ").strip()

    try:
        result = run_research(topic)

        print("\n" + "=" * 70)
        print("RESEARCHX AI - FINAL RESEARCH REPORT")
        print("=" * 70)

        print(result["final_report"])

        import os

        os.makedirs("reports", exist_ok=True)

        with open(
            "reports/research_report.md",
            "w",
            encoding="utf-8",
        ) as file:
            file.write(result["final_report"])

        print("\nReport saved to reports/research_report.md")

    except Exception as error:
        print(f"\nResearch workflow failed: {error}")

