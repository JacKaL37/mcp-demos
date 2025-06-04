import asyncio
import os
import shutil
import subprocess
import time
from typing import Any, Dict

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings
from agents import set_default_openai_key

from dotenv import load_dotenv

load_dotenv()
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

async def test_dnd_assistant(mcp_server: MCPServer):
    agent = Agent(
        name="DM Assistant",
        instructions="""You are a Dungeon Master's assistant for tabletop role-playing games.
        Use the available tools to help with dice rolling, character management, note-taking,
        and other DM tasks. Be creative, helpful, and keep the game flowing.""",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    # Test dice rolling
    message = "Roll 3d6+2 for a strength check."
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Test note creation
    message = "Create a note about a new magic shop called 'The Arcane Emporium' in the town of Fallcrest."
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Test character creation
    message = "Add a character named Thorne Ironheart who is a level 5 Dwarf Fighter with 45 HP."
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Test NPC generation
    message = "Generate a random Elf shopkeeper NPC for my game."
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Test initiative tracking
    message = "Roll initiative for the following participants: Thorne (modifier +3), Goblin 1 (modifier +1), Goblin 2 (modifier +1), Evil Mage (modifier +2)."
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Test encounter creation
    message = "Create an encounter called 'Goblin Ambush' with 4 goblins and a goblin boss."
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Test loot generation
    message = "Generate medium-level loot for a defeated ogre."
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Test random table
    message = "Give me a random tavern name for my next town."
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Test quest hook generation
    message = "I need a quest hook for my players' next adventure."
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Test reading notes
    message = "List all notes we've created so far."
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Test interactively working with the DM
    message = "I want to run a dungeon crawl for 4 level 3 players. Help me prepare by generating a simple encounter, some treasure, and a quest hook."
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():
    async with MCPServerSse(
        name="DND Server",
        params={
            "url": "http://localhost:8000/sse",
        },
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="DND Assistant Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await test_dnd_assistant(server)


if __name__ == "__main__":
    # Let's make sure the user has uv installed
    if not shutil.which("uv"):
        raise RuntimeError(
            "uv is not installed. Please install it: https://docs.astral.sh/uv/getting-started/installation/"
        )

    # We'll run the DND server in a subprocess
    process: subprocess.Popen[Any] | None = None
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(this_dir, "..", "src", "dnd-server.py")

        print("Starting DND MCP server at http://localhost:8000/sse ...")

        # Run `uv run dnd-server.py` to start the DND server
        process = subprocess.Popen(["uv", "run", server_file])
        # Give it 3 seconds to start
        time.sleep(3)

        print("DND server started. Running example...\n\n")
    except Exception as e:
        print(f"Error starting DND server: {e}")
        exit(1)

    try:
        asyncio.run(main())
    finally:
        if process:
            process.terminate()