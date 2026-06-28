"""Web fetch tool for Claude Harness."""

import urllib.request
from typing import Literal

from .base import BaseTool, ToolResult


class WebFetchTool(BaseTool):
    """Fetch content from a URL."""

    name = "web_fetch"
    description = "Fetch content from a URL."

    def __init__(self, timeout: int = 30):
        """Initialize the web fetch tool.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    def execute(
        self,
        url: str,
        method: Literal["GET", "POST"] = "GET",
        headers: dict | None = None,
        body: str | None = None,
    ) -> ToolResult:
        """Fetch content from a URL.

        Args:
            url: URL to fetch
            method: HTTP method
            headers: Additional headers
            body: Request body

        Returns:
            Response content
        """
        try:
            headers = headers or {}
            headers["User-Agent"] = "Claude-Harness/1.0"

            req = urllib.request.Request(
                url,
                method=method,
                headers=headers,
            )

            if body:
                req.data = body.encode("utf-8")

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                content = response.read().decode("utf-8", errors="replace")

                return ToolResult(
                    success=True,
                    content=f"Status: {response.status}\n\n{content[:10000]}",
                )

        except urllib.error.HTTPError as e:
            return ToolResult(
                success=False,
                content="",
                error=f"HTTP {e.code}: {e.reason}",
            )
        except Exception as e:
            return ToolResult(success=False, content="", error=str(e))


class WebSearchTool(BaseTool):
    """Search the web."""

    name = "web_search"
    description = "Search the web for information."

    def __init__(self, timeout: int = 30):
        """Initialize the web search tool.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    def execute(self, query: str, limit: int = 5) -> ToolResult:
        """Search the web.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            Search results
        """
        # Simple web search using DuckDuckGo HTML
        try:
            import urllib.parse

            encoded_query = urllib.parse.quote(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Claude-Harness/1.0"},
            )

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                content = response.read().decode("utf-8", errors="replace")

            # Parse results
            import re

            results = re.findall(
                r'<a class="result__a" href="([^"]+)">([^<]+)</a>.*?<a class="result__snippet"[^>]*>([^<]+)</a>',
                content,
                re.DOTALL,
            )

            if not results:
                return ToolResult(success=True, content="No results found")

            output = []
            for i, (url, title, snippet) in enumerate(results[:limit], 1):
                output.append(f"{i}. {title}\n   {snippet}\n   {url}\n")

            return ToolResult(
                success=True,
                content=f"Search results for '{query}':\n\n" + "\n".join(output),
            )

        except Exception as e:
            return ToolResult(success=False, content="", error=str(e))
