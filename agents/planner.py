
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def create_research_plan(topic: str) -> str:
    """
    Generate a structured research plan for a given topic.
    """

    if not topic or not topic.strip():
        raise ValueError("Research topic cannot be empty.")

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing from .env")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.2,
    )

    prompt = f"""
    You are the Research Planner Agent in ResearchX AI.

    Your responsibility is to prepare a clear research plan.

    Research topic:
    {topic}

    Generate the following sections:

    1. Research Objective
    2. Key Research Areas
    3. Research Questions
    4. Information Required
    5. Suggested Report Structure

    Requirements:
    - Be specific and organized.
    - Include 4 to 6 research areas.
    - Include 4 to 6 research questions.
    - Do not invent research findings or citations.
    - Return only the research plan.
    """

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":
    topic = input("Enter your research topic: ")

    try:
        plan = create_research_plan(topic)

        print("\n" + "=" * 50)
        print("RESEARCHX AI - RESEARCH PLAN")
        print("=" * 50)
        print(plan)

    except Exception as error:
        print(f"Error creating research plan: {error}")

