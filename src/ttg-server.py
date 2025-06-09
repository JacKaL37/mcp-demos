import os
import random
import signal
import atexit
import re
from typing import Dict, List, Any, Optional, Tuple

# ---------- IMPORTING PACKAGES ----------
from fastmcp import FastMCP
from dotenv import load_dotenv

# ---------- ENVIRONMENT SETUP ----------
# Load environment variables from .env file
load_dotenv()
# Get port from environment variable or use default
SERVER_PORT = int(os.environ.get("SERVER_PORT", 8090))
# Initialize the MCP server with the specified port
mcp = FastMCP("TTG Dice Server", port=SERVER_PORT)

# ---------- DICE ROLLING FUNCTIONS ----------
def parse_dice_notation(dice_notation: str) -> Tuple[int, int, int]:
    """
    Parse standard dice notation like "2d6+3" into components.
    
    Args:
        dice_notation: A string in the format "NdS+M" where:
                      N = number of dice (optional, defaults to 1)
                      S = sides on each die (required)
                      M = modifier (optional, defaults to 0)
    
    Returns:
        Tuple containing (number_of_dice, sides_per_die, modifier)
    """
    # Default values
    number_of_dice = 1
    modifier = 0
    
    # Parse the dice notation
    pattern = r'^(\d+)?d(\d+)([+-]\d+)?$'
    match = re.match(pattern, dice_notation.lower().strip())
    
    if not match:
        raise ValueError(f"Invalid dice notation: {dice_notation}. Expected format like '2d6', 'd20', or '3d8+2'")
    
    # Extract components
    if match.group(1):
        number_of_dice = int(match.group(1))
    sides_per_die = int(match.group(2))
    if match.group(3):
        modifier = int(match.group(3))
    
    return (number_of_dice, sides_per_die, modifier)

def roll_dice(number_of_dice: int, sides_per_die: int) -> List[int]:
    """
    Roll the specified number of dice with the given number of sides.
    
    Args:
        number_of_dice: Number of dice to roll
        sides_per_die: Number of sides on each die
        
    Returns:
        List of individual dice results
    """
    return [random.randint(1, sides_per_die) for _ in range(number_of_dice)]

# ---------- MCP TOOL DEFINITIONS ----------
@mcp.tool()
def roll(dice_notation: str) -> Dict[str, Any]:
    """
    Roll dice using standard dice notation (e.g., "2d6+3").
    
    Args:
        dice_notation: A string describing the dice roll, like "2d6+3" for two 6-sided dice plus 3
    
    Returns:
        Dictionary containing the roll results and details
    """
    print(f"[ttg-server] roll({dice_notation})")
    
    try:
        # Parse the dice notation
        number_of_dice, sides_per_die, modifier = parse_dice_notation(dice_notation)
        
        # Roll the dice
        individual_rolls = roll_dice(number_of_dice, sides_per_die)
        
        # Calculate the total
        subtotal = sum(individual_rolls)
        total = subtotal + modifier
        
        # Format the expression for display
        expression = f"{number_of_dice}d{sides_per_die}"
        if modifier > 0:
            expression += f"+{modifier}"
        elif modifier < 0:
            expression += f"{modifier}"  # Negative sign already included
        
        return {
            "expression": expression,
            "individual_rolls": individual_rolls,
            "subtotal": subtotal,
            "modifier": modifier,
            "total": total
        }
    except ValueError as e:
        return {
            "error": str(e)
        }

# ---------- SERVER LIFECYCLE MANAGEMENT ----------
def cleanup_handler(sig=None, frame=None):
    """Handle cleanup when the server is being shut down"""
    print("[ttg-server] Shutting down TTG dice server...")
    # Add any necessary cleanup code here

# Register signal handlers for proper cleanup
signal.signal(signal.SIGINT, cleanup_handler)
signal.signal(signal.SIGTERM, cleanup_handler)
atexit.register(cleanup_handler)

# ---------- SERVER STARTUP ----------
if __name__ == "__main__":
    print(f"[ttg-server] Starting TTG Dice Server on port {SERVER_PORT}...")
    mcp.run(transport="sse")
    print("[ttg-server] Server stopped.")