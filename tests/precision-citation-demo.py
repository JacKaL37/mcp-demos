import asyncio
import os
import shutil
import subprocess
import time
from typing import Any

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings
from agents import set_default_openai_key

from dotenv import load_dotenv

load_dotenv()
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

async def run(mcp_server: MCPServerSse):
    agent = Agent(
        name="Assistant",
        instructions=(
            "You can use the fetch_and_structure tool to retrieve page content.\n"
            "- Always pass the 'url'.\n"
            "- Use 'element_address' (XPath-like) to target a specific element if needed.\n"
            "- Set 'render' to True only if the content doesn't appear in static HTML."
        ),
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    # Fetch full page, no rendering
    msg_full = "Fetch 'https://example.com' and return its main content."
    print(f"\nRunning full-page fetch:\n{msg_full}")
    result = await Runner.run(starting_agent=agent, input=msg_full)
    print("=== Result ===")
    print(result.final_output)

    # Fetch a specific element with rendering enabled
    msg_render = (
        "Fetch 'https://example.com' with render=True and element_address='//div[@id=\"content\"]'. "
        "Return the Markdown and structure for that element."
    )
    print(f"\nRunning element fetch with render:\n{msg_render}")
    result = await Runner.run(starting_agent=agent, input=msg_render)
    print("=== Result ===")
    print(result.final_output)

async def main():
    async with MCPServerSse(
        name="BeautifulSoup+Playwright Server",
        params={"url": "http://localhost:8000/sse"},
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="MCP Rendered Web Demo", trace_id=trace_id):
            print(f"Trace view: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)

if __name__ == "__main__":
    if not shutil.which("uv"):
        raise RuntimeError("Please install `uv`: https://docs.astral.sh/uv/")

    process: subprocess.Popen[Any] | None = None
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(this_dir, "server.py")
        print("Starting SSE server at http://localhost:8000/sse ...")
        process = subprocess.Popen(["uv", "run", server_file])
        time.sleep(3)
    except Exception as e:
        print(f"Error starting SSE server: {e}")
        exit(1)

    try:
        asyncio.run(main())
    finally:
        if process:
            process.terminate()
