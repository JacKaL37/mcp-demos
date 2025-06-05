import os
import pathlib
import requests
from typing import Optional, Union, Any

from fastmcp import FastMCP
from bs4 import BeautifulSoup
import markdownify
from playwright.sync_api import sync_playwright

# Initialize the MCP server
mcp = FastMCP("Content Extractor Server")

# ---------- Helper Functions ----------

def html_to_markdown(element: BeautifulSoup) -> str:
    """Convert HTML element or tree into Markdown."""
    html_content = str(element)
    return markdownify.markdownify(html_content, heading_style="ATX")

def serialize_structure(element: BeautifulSoup) -> Any:
    """Recursively convert HTML into a JSON-friendly nested dict structure."""
    def _serialize(node):
        if node.name is None:
            text = node.string
            return text.strip() if text else ""
        children = [_serialize(child) for child in node.children if child.name or (child.string and child.string.strip())]
        return {
            "tag": node.name,
            "attributes": node.attrs,
            "content": children
        }
    return _serialize(element)

def xpath_to_css(xpath: str) -> str:
    """Convert simple XPath-like expressions to CSS selectors (basic only)."""
    import re
    css = xpath.lstrip("/")

    css = re.sub(r"\[@([a-zA-Z0-9_-]+)='([^']+)'\]", r"[\1='\2']", css)
    css = re.sub(r"([a-zA-Z0-9_-]+)\[([a-zA-Z0-9_-]+)='([^']+)'\]", r"\1#\3", css)
    css = css.replace("/", " > ")
    css = re.sub(r"\[(\d+)\]", lambda m: f":nth-of-type({m.group(1)})", css)
    return css.strip()

# ---------- MCP Tool Definition ----------

@mcp.tool()
def fetch_and_structure(
    url: str,
    element_address: Optional[str] = None,
    render: bool = False
) -> dict[str, Union[str, dict]]:
    """
    Fetch or render a webpage, convert to Markdown, and return structured data.

    Args:
        url: The URL to fetch.
        element_address: Optional XPath-like string for narrowing to an element.
        render: Use Playwright to render full JS (if True), or requests otherwise.

    Returns:
        {
            "url": ..., "element_address": ...,
            "markdown": ..., "structured_data": ...
        }
    """
    print(f"[debug-server] fetch_and_structure(url={url}, element_address={element_address}, render={render})")

    try:
        if render:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle")
                html = page.content()
                browser.close()
        else:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            html = response.text
    except Exception as e:
        return {
            "url": url,
            "element_address": element_address,
            "markdown": "",
            "structured_data": {"error": f"Failed to load page: {str(e)}"}
        }

    soup = BeautifulSoup(html, "html.parser")

    if element_address:
        css_selector = xpath_to_css(element_address)
        target = soup.select_one(css_selector)
        if not target:
            return {
                "url": url,
                "element_address": element_address,
                "markdown": "",
                "structured_data": {"error": "Element not found"}
            }
        node = target
    else:
        node = soup

    return {
        "url": url,
        "element_address": element_address,
        "markdown": html_to_markdown(node),
        "structured_data": serialize_structure(node)
    }

if __name__ == "__main__":
    mcp.run(transport="sse")