import asyncio
import os
import shutil
import subprocess
import time
from typing import Any

from langtrace_python_sdk import langtrace
langtrace.init(api_key="91e4463648736881178851e555131b0776b03d79b6d4fe8e4eef9e5a6363f49d", host="http://localhost:3000")

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings
from agents import set_default_openai_key

from dotenv import load_dotenv

load_dotenv()
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    # # Use the `add` tool to add two numbers
    # message = "Add these numbers: 7 and 22."
    # print(f"Running: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)

    # Run the `get_weather` tool
    message = "What's the weather in Tokyo?"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # # Run the `get_secret_word` tool
    # message = "What's the secret word?"
    # print(f"\n\nRunning: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)
    
    # # Test the SQLite database tool
    # message = "Use the SQL tool a few times to explore the database and explain what you see."
    # print(f"\n\nRunning: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)

    # # Run the `get_current_time` tool
    # message = "What's the current time?"
    # print(f"\n\nRunning: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)

    # # Run the ascii word art generator tool
    # message = "Generate ASCII art for a creative phrase to roast someone, improvise one of your choosing."
    # print(f"\n\nRunning: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)


async def main():
    async with MCPServerSse(
        name="SSE Python Server",
        params={
            "url": "http://localhost:8000/sse",
        },
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="SSE Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)


if __name__ == "__main__":
    # Let's make sure the user has uv installed
    if not shutil.which("uv"):
        raise RuntimeError(
            "uv is not installed. Please install it: https://docs.astral.sh/uv/getting-started/installation/"
        )

    # We'll run the SSE server in a subprocess. Usually this would be a remote server, but for this
    # demo, we'll run it locally at http://localhost:8000/sse
    process: subprocess.Popen[Any] | None = None
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(this_dir, "..", "src", "server.py")

        print("Starting SSE server at http://localhost:8000/sse ...")

        # Run `uv run server.py` to start the SSE server
        process = subprocess.Popen(["uv", "run", server_file])
        # Give it 3 seconds to start
        time.sleep(3)

        print("SSE server started. Running example...\n\n")
    except Exception as e:
        print(f"Error starting SSE server: {e}")
        exit(1)

    try:
        asyncio.run(main())
    finally:
        if process:
            process.terminate()
