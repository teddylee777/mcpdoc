"""A server for just langgraph docs from langchain-ai.github.io.

This is used as a way to test the doc functionality via MCP.
"""

# /usr/bin/env python3
import httpx
from markdownify import markdownify
from mcp.server.fastmcp import FastMCP

server = FastMCP(name="llms-txt")

# ALLOWED_PREFIX 제한 제거함
HTTPX_CLIENT = httpx.AsyncClient(follow_redirects=False)


@server.tool()
async def get_docs(url: str = "overview") -> str:
    """Get langgraph docs.

    Always fetch the `overview` prior to fetching any other URLs as it will provide a
    list of available URLs.

    Args:
        url: The URL to fetch or be "overview".
    """
    if url == "overview":
        url = "https://raw.githubusercontent.com/teddylee777/mcpdoc/refs/heads/main/resources/overview.txt"

    # URL 제한 검사 제거함
    response = await HTTPX_CLIENT.get(url)
    response.raise_for_status()
    if response.status_code == 200:
        # Convert HTML to markdown
        markdown_content = markdownify(response.text)
        return markdown_content
    else:
        return "Encountered an error while fetching the URL."


if __name__ == "__main__":
    server.run(transport="stdio")
