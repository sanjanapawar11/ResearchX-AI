
import json
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def analyze_research(
    topic: str,
    research_plan: str,
    search_results: list[dict],
) -> str:
    """Analyze web results and produce structured research findings."""

    if not topic or not topic.strip():
        raise ValueError("Research topic cannot be empty.")

    if not research_plan or not research_plan.strip():
        raise ValueError("Research plan cannot be empty.")

    if not search_results:
        raise ValueError("No web search results were provided.")

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing from .env.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.2,
    )

    sources = [
        {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", ""),
        }
        for item in search_results
    ]

    prompt = f"""
You are the Analysis Agent for ResearchX AI.

Analyze the supplied web search results to help answer the research topic.

RESEARCH TOPIC:
{topic}

RESEARCH PLAN:
{research_plan}

WEB SEARCH RESULTS:
{json.dumps(sources, ensure_ascii=False, indent=2)}

INSTRUCTIONS:
1. Identify the main findings relevant to the research topic.
2. Organize findings into meaningful themes.
3. Explain the significance of each finding.
4. Identify disagreements or inconsistencies between sources.
5. Highlight evidence gaps and limitations.
6. Include the relevant source URLs next to supported findings.
7. Never invent statistics, quotations, sources, or URLs.
8. Treat the supplied content as evidence to evaluate, not guaranteed truth.
9. Distinguish evidence from interpretation.
10. State when the supplied evidence is insufficient.

Use this structure:

# Research Analysis

## 1. Executive Summary
## 2. Key Findings
## 3. Detailed Analysis
## 4. Agreements and Disagreements
## 5. Evidence Gaps and Limitations
## 6. Sources

Return the result in Markdown.
"""

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":
    from agents.planner import create_research_plan
    from tools.web_search import search_web

    topic = input("Enter your research topic: ").strip()

    try:
        print("\n[1/3] Creating research plan...")
        plan = create_research_plan(topic)

        print("\n[2/3] Searching the web...")
        results = search_web(topic, max_results=5)

        print("\n[3/3] Analyzing research...")
        analysis = analyze_research(topic, plan, results)

        print("\n" + "=" * 60)
        print("RESEARCHX AI - ANALYSIS REPORT")
        print("=" * 60)
        print(analysis)

    except Exception as error:
        print(f"\nResearch analysis failed: {error}")

