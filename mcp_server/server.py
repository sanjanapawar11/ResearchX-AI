
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv()

mcp = FastMCP("ResearchX-Web-Research")


@mcp.tool()
def search_web(query: str, max_results: int = 5) -> dict:
    """
    Search the web for research information.

    Args:
        query: The topic or question to search for.
        max_results: Number of results to return, between 1 and 10.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= max_results <= 10:
        raise ValueError("max_results must be between 1 and 10.")

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError("TAVILY_API_KEY is missing from .env.")

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

    return {
        "query": query,
        "total_results": len(results),
        "results": results,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")

