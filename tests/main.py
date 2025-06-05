import asyncio
import os
import shutil
import subprocess
import time
import signal
from typing import Any

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings
from agents import set_default_openai_key

from dotenv import load_dotenv

load_dotenv()
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

# Port configuration - keep it consistent
BASE_PORT = 8089
MAX_PORT_ATTEMPTS = 10  # Try up to 10 ports starting from BASE_PORT

async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    # Use the `add` tool to add two numbers
    message = "Add these numbers: 7 and 22."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Run the `get_weather` tool
    message = "What's the weather in Tokyo?"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Run the `get_secret_word` tool
    message = "What's the secret word?"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)
    
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


async def main(server_port):
    async with MCPServerSse(
        name="SSE Python Server",
        params={
            "url": f"http://localhost:{server_port}/sse",
        },
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="SSE Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)


def check_port_in_use(port):
    """Check if the port is already in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def find_available_port():
    """Find an available port starting from BASE_PORT"""
    for port_offset in range(MAX_PORT_ATTEMPTS):
        port = BASE_PORT + port_offset
        if not check_port_in_use(port):
            return port

    raise RuntimeError(f"Could not find an available port after {MAX_PORT_ATTEMPTS} attempts starting from {BASE_PORT}")


if __name__ == "__main__":
    # Let's make sure the user has uv installed
    if not shutil.which("uv"):
        raise RuntimeError(
            "uv is not installed. Please install it: https://docs.astral.sh/uv/getting-started/installation/"
        )

    # Find an available port
    server_port = find_available_port()
    print(f"Using port {server_port} for the server")

    # We'll run the SSE server in a subprocess. Usually this would be a remote server, but for this
    # demo, we'll run it locally
    process: subprocess.Popen[Any] | None = None
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(this_dir, "..", "src", "server.py")

        print(f"Starting SSE server at http://localhost:{server_port}/sse ...")

        # Run `uv run server.py` to start the SSE server
        # Set environment variable to pass port configuration
        env = os.environ.copy()
        env["SERVER_PORT"] = str(server_port)
        process = subprocess.Popen(["uv", "run", server_file], env=env)

        # Give it 3 seconds to start
        time.sleep(3)

        print("SSE server started. Running example...\n\n")
    except Exception as e:
        print(f"Error starting SSE server: {e}")
        if process:
            process.terminate()
        exit(1)

    def cleanup_server(sig=None, frame=None):
        """Cleanup function to ensure server is properly terminated"""
        if process:
            print("\nShutting down SSE server...")
            process.terminate()
            try:
                # Wait for process to terminate, with timeout
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it didn't terminate gracefully
                print("Server didn't terminate gracefully, force killing...")
                process.kill()
        print("Cleanup complete.")

    # Register signal handlers for proper cleanup
    signal.signal(signal.SIGINT, cleanup_server)
    signal.signal(signal.SIGTERM, cleanup_server)

    try:
        asyncio.run(main(server_port))
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        cleanup_server()

