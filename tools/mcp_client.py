
import asyncio
import json
import sys

from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERVER_PATH = PROJECT_ROOT / "mcp_server" / "server.py"


async def search_with_mcp(
    query: str,
    max_results: int = 5,
) -> dict:
    """
    Call the ResearchX MCP search tool through an MCP client.
    """

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
        env=None,
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                "search_web",
                arguments={
                    "query": query,
                    "max_results": max_results,
                },
            )

            if result.isError:
                raise RuntimeError("MCP search tool returned an error.")

            output = []

            for content in result.content:
                if content.type == "text":
                    output.append(content.text)

            if not output:
                raise RuntimeError("The MCP tool returned no content.")

            try:
                return json.loads("\n".join(output))
            except json.JSONDecodeError:
                return {"result": "\n".join(output)}


if __name__ == "__main__":
    topic = input("Enter a research topic: ").strip()

    try:
        response = asyncio.run(search_with_mcp(topic))

        print("\n" + "=" * 60)
        print("RESEARCHX AI - MCP SEARCH RESULTS")
        print("=" * 60)

        print(json.dumps(response, indent=2, ensure_ascii=False))

    except Exception as error:
        print(f"MCP client failed: {error}")

