import os
import random
import signal
import atexit
from typing import Dict, List, Any

# ---------- IMPORTING PACKAGES ----------
from fastmcp import FastMCP
from dotenv import load_dotenv

# ---------- ENVIRONMENT SETUP ----------
# Load environment variables from .env file
load_dotenv()
# Get port from environment variable or use default
SERVER_PORT = int(os.environ.get("SERVER_PORT", 8089))
# Initialize the MCP server with the specified port
mcp = FastMCP("Hello World Server", port=SERVER_PORT)

# ---------- DATA DEFINITIONS ----------
# Define lists of synonyms
HELLO_SYNONYMS = [
    "Hello", "Hi", "Greetings", "Hey", "Salutations", 
    "Welcome", "Howdy", "Good day", "Hiya"
]

WORLD_SYNONYMS = [
    "world", "planet", "earth", "globe", "universe",
    "everyone", "folks", "friends", "people", "community"
]

# ---------- MCP TOOL DEFINITIONS ----------
@mcp.tool()
def generate_hello_world() -> Dict[str, Any]:
    """
    Generate a random 'Hello World' phrase using synonyms.
    
    Returns:
        Dictionary containing the generated phrase and its components
    """
    print("[hello-world-server] generate_hello_world()")
    
    # Select random words from each list
    hello_word = random.choice(HELLO_SYNONYMS)
    world_word = random.choice(WORLD_SYNONYMS)
    
    # Combine into a phrase
    phrase = f"{hello_word}, {world_word}!"
    
    return {
        "phrase": phrase,
        "hello_component": hello_word,
        "world_component": world_word
    }

# ---------- SERVER LIFECYCLE MANAGEMENT ----------
def cleanup_handler(sig=None, frame=None):
    """Handle cleanup when the server is being shut down"""
    print("[hello-world-server] Shutting down hello-world server...")
    # Add any necessary cleanup code here

# Register signal handlers for proper cleanup
signal.signal(signal.SIGINT, cleanup_handler)
signal.signal(signal.SIGTERM, cleanup_handler)
atexit.register(cleanup_handler)

# ---------- SERVER STARTUP ----------
if __name__ == "__main__":
    print(f"[hello-world-server] Starting Hello World Server on port {SERVER_PORT}...")
    mcp.run(transport="sse")
    print("[hello-world-server] Server stopped.")