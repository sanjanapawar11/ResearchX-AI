
import json
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def fact_check_research(
    topic: str,
    analysis: str,
    search_results: list[dict],
) -> str:
    """
    Evaluate research claims against collected source evidence.
    """

    if not topic or not topic.strip():
        raise ValueError("Research topic cannot be empty.")

    if not analysis or not analysis.strip():
        raise ValueError("Research analysis cannot be empty.")

    if not search_results:
        raise ValueError("No source evidence was provided.")

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing from .env.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.1,
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
You are the Fact-Checking Agent for ResearchX AI.

Your task is to assess factual claims in a research analysis
against the source content supplied below.

RESEARCH TOPIC:
{topic}

RESEARCH ANALYSIS:
{analysis}

AVAILABLE SOURCE EVIDENCE:
{json.dumps(sources, ensure_ascii=False, indent=2)}

INSTRUCTIONS:

1. Extract the important factual claims from the analysis.
2. Evaluate each claim against the available source content.
3. Assign exactly one status to each claim:
   - SUPPORTED
   - CONTRADICTED
   - INSUFFICIENT EVIDENCE
4. Explain the evidence behind each classification.
5. Include the URL of each relevant source.
6. Do not invent facts, quotations, statistics, or URLs.
7. Do not treat a source's mere mention of a topic as proof of a claim.
8. Distinguish direct evidence from indirect or ambiguous evidence.
9. If the evidence conflicts, explain the disagreement.
10. Do not claim to have independently verified a source unless
    the source's relevant content was actually examined.
11. These classifications assess the supplied evidence; they do
    not establish absolute truth.

OUTPUT FORMAT:

# ResearchX AI - Fact-Checking Report

## 1. Overall Assessment

Summarize the quality and limitations of the available evidence.

## 2. Claim-by-Claim Verification

For each important claim, provide:

- Claim:
- Status:
- Evidence:
- Supporting or conflicting source URLs:
- Explanation:

## 3. Unsupported or Uncertain Claims

List claims that need more research.

## 4. Recommendations

Suggest additional sources or searches that could improve confidence.

Return the report in Markdown.
"""

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":
    from agents.planner import create_research_plan
    from agents.analyst import analyze_research
    from tools.web_search import search_web

    topic = input("Enter your research topic: ").strip()

    try:
        print("\n[1/4] Creating research plan...")
        plan = create_research_plan(topic)

        print("\n[2/4] Searching the web...")
        results = search_web(topic, max_results=5)

        if not results:
            raise ValueError(
                "The search returned no results. Try another topic."
            )

        print("\n[3/4] Analyzing research...")
        analysis = analyze_research(topic, plan, results)

        print("\n[4/4] Fact-checking claims...")
        report = fact_check_research(topic, analysis, results)

        print("\n" + "=" * 60)
        print("RESEARCHX AI - FACT-CHECKING REPORT")
        print("=" * 60)
        print(report)

    except Exception as error:
        print(f"\nFact-checking failed: {error}")

