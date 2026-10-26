
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web and return structured research results.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= max_results <= 10:
        raise ValueError("max_results must be between 1 and 10.")

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY is missing from your .env file."
        )

    client = TavilyClient(api_key=api_key)

    response = client.search(
        query=query,
        search_depth="basic",
        max_results=max_results,
        topic="general",
    )

    results = []

    for item in response.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", ""),
            "score": item.get("score", 0.0),
        })

    return results


if __name__ == "__main__":
    topic = input("Enter a research topic: ").strip()

    try:
        print("\nSearching the web...")

        results = search_web(topic)

        print("\n" + "=" * 60)
        print("RESEARCHX AI - WEB RESEARCH RESULTS")
        print("=" * 60)

        for index, result in enumerate(results, start=1):
            print(f"\nSource {index}: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Relevance score: {result['score']}")
            print(f"Content: {result['content'][:500]}")
            print("-" * 60)

        print(f"\nTotal results retrieved: {len(results)}")

    except Exception as error:
        print(f"Web research failed: {error}")

