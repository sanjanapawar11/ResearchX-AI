
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def generate_report(
    topic: str,
    research_plan: str,
    analysis: str,
    fact_check_report: str,
) -> str:
    """
    Generate a structured research report from the agent outputs.
    """

    if not topic or not topic.strip():
        raise ValueError("Research topic cannot be empty.")

    if not research_plan.strip():
        raise ValueError("Research plan cannot be empty.")

    if not analysis.strip():
        raise ValueError("Research analysis cannot be empty.")

    if not fact_check_report.strip():
        raise ValueError("Fact-checking report cannot be empty.")

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing from .env.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.2,
    )

    prompt = f"""
You are the Report Generator Agent for ResearchX AI.

Create a professional research report using the information below.

RESEARCH TOPIC:
{topic}

RESEARCH PLAN:
{research_plan}

RESEARCH ANALYSIS:
{analysis}

FACT-CHECKING REPORT:
{fact_check_report}

REPORT STRUCTURE:

# Research Report: {topic}

## 1. Executive Summary
Summarize the main findings and important conclusions.

## 2. Introduction
Explain the topic, context, and research objectives.

## 3. Research Methodology
Explain that the report uses the supplied research plan,
web search results, analysis, and evidence assessment.
Do not claim that methods were used if they were not.

## 4. Key Findings
Present the most important findings clearly.

## 5. Detailed Analysis
Explain the findings and their significance.

## 6. Evidence and Fact-Checking
Summarize supported, contradicted, and insufficiently
supported claims. Preserve the distinctions between them.

## 7. Challenges and Opportunities
Discuss these only where the supplied evidence supports them.

## 8. Conclusion
Summarize what the available evidence establishes and
identify important uncertainties.

## 9. References
List the source URLs already present in the supplied material.
Do not invent URLs, authors, publication dates, or citations.

IMPORTANT RULES:

- Use professional, clear language.
- Do not invent facts, statistics, or quotations.
- Preserve relevant source URLs.
- Do not present uncertain claims as established facts.
- Distinguish source evidence from interpretation.
- Do not claim that every statement has been independently verified.
- If evidence is missing or conflicting, explain the limitation.
- Use Markdown formatting.
- Avoid unnecessary repetition.

Return only the completed research report.
"""

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":
    from agents.planner import create_research_plan
    from agents.analyst import analyze_research
    from agents.fact_checker import fact_check_research
    from tools.web_search import search_web

    topic = input("Enter your research topic: ").strip()

    try:
        print("\n[1/5] Creating research plan...")
        plan = create_research_plan(topic)

        print("\n[2/5] Searching the web...")
        results = search_web(topic, max_results=5)

        if not results:
            raise ValueError("No search results were returned.")

        print("\n[3/5] Analyzing research...")
        analysis = analyze_research(topic, plan, results)

        print("\n[4/5] Fact-checking claims...")
        fact_check_report = fact_check_research(
            topic,
            analysis,
            results,
        )

        print("\n[5/5] Generating final report...")
        report = generate_report(
            topic,
            plan,
            analysis,
            fact_check_report,
        )

        print("\n" + "=" * 70)
        print("RESEARCHX AI - FINAL RESEARCH REPORT")
        print("=" * 70)
        print(report)

        # Save the report to a Markdown file.
        os.makedirs("reports", exist_ok=True)

        filename = "reports/research_report.md"

        with open(filename, "w", encoding="utf-8") as file:
            file.write(report)

        print(f"\nReport saved to: {filename}")

    except Exception as error:
        print(f"\nReport generation failed: {error}")
