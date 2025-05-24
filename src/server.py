import random
import sqlite3
import os
import pathlib

import requests
from fastmcp import FastMCP

# Create server
mcp = FastMCP("Echo Server")

# Set up database connection
# Use absolute path based on script location
SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
DATA_DIR = SCRIPT_DIR.parent / "data"
DB_PATH = DATA_DIR / "sqlite.db"

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"[debug-server] Created data directory at {DATA_DIR}")

conn = None
try:
    print(f"[debug-server] Attempting to connect to SQLite DB at {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    print(f"[debug-server] Connected to SQLite DB at {DB_PATH}")
except Exception as e:
    print(f"[debug-server] Error connecting to database: {e}")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print(f"[debug-server] add({a}, {b})")
    return a + b


@mcp.tool()
def get_secret_word() -> str:
    print("[debug-server] get_secret_word()")
    return random.choice(["apple", "banana", "cherry"])


@mcp.tool()
def get_current_weather(city: str) -> str:
    print(f"[debug-server] get_current_weather({city})")

    endpoint = "https://wttr.in"
    response = requests.get(f"{endpoint}/{city}")
    return response.text


@mcp.tool()
def execute_sql(commands: list[str]) -> str:
    """Execute SQL commands on the database
    
    Args:
        commands: List of SQL commands to execute
        
    Returns:
        String with results of SQL commands
    """
    print(f"[debug-server] execute_sql({commands})")
    
    if not conn:
        return "Error: Database connection not established"
    
    results = []
    cursor = conn.cursor()
    
    try:
        for cmd in commands:
            cursor.execute(cmd)
            if cmd.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                column_names = [description[0] for description in cursor.description]
                results.append(f"Results for: {cmd}")
                results.append(f"Columns: {column_names}")
                results.append(f"Rows: {rows}")
            else:
                results.append(f"Executed: {cmd}")
        
        # Commit changes if any write operations were performed
        conn.commit()
        
        return "\n".join(results)
    except Exception as e:
        conn.rollback()  # Roll back any changes if an error occurred
        return f"SQL Error: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="sse")

