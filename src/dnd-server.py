import random
import os
import pathlib
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

from fastmcp import FastMCP

# Create DND server
mcp = FastMCP("DND Server")

# Set up data directory for storing notes, characters, etc.
SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
DND_DATA_DIR = SCRIPT_DIR.parent / "dnd_data"
NOTES_DIR = DND_DATA_DIR / "notes"
CHARACTERS_FILE = DND_DATA_DIR / "characters.json"
ENCOUNTERS_FILE = DND_DATA_DIR / "encounters.json"

# Create necessary directories if they don't exist
if not os.path.exists(DND_DATA_DIR):
    os.makedirs(DND_DATA_DIR)
    print(f"[dnd-server] Created DND data directory at {DND_DATA_DIR}")

if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR)
    print(f"[dnd-server] Created notes directory at {NOTES_DIR}")

# Initialize empty characters file if it doesn't exist
if not os.path.exists(CHARACTERS_FILE):
    with open(CHARACTERS_FILE, 'w') as f:
        json.dump([], f)
    print(f"[dnd-server] Created empty characters file at {CHARACTERS_FILE}")

# Initialize empty encounters file if it doesn't exist
if not os.path.exists(ENCOUNTERS_FILE):
    with open(ENCOUNTERS_FILE, 'w') as f:
        json.dump([], f)
    print(f"[dnd-server] Created empty encounters file at {ENCOUNTERS_FILE}")

# Dice rolling tool
@mcp.tool()
def roll_dice(dice_notation: str) -> Dict[str, Any]:
    """Roll dice using standard dice notation (e.g., '2d6', '1d20+5', '3d8-2')
    
    Args:
        dice_notation: Standard dice notation (e.g., '2d6', '1d20+5', '3d8-2')
        
    Returns:
        Dictionary containing roll results
    """
    print(f"[dnd-server] roll_dice({dice_notation})")
    
    # Parse the dice notation
    # Support for NdM+K or NdM-K format
    dice_pattern = re.compile(r'(\d+)d(\d+)([+-]\d+)?')
    match = dice_pattern.match(dice_notation)
    
    if not match:
        return {"error": f"Invalid dice notation: {dice_notation}. Use format like '2d6', '1d20+5', '3d8-2'"}
    
    num_dice = int(match.group(1))
    dice_sides = int(match.group(2))
    modifier_str = match.group(3) or "+0"
    modifier = int(modifier_str)
    
    # Roll the dice
    individual_rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
    total = sum(individual_rolls) + modifier
    
    return {
        "notation": dice_notation,
        "rolls": individual_rolls,
        "modifier": modifier,
        "total": total
    }

# Note management tools
@mcp.tool()
def create_note(title: str, content: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Create a new note with title, content, and optional tags
    
    Args:
        title: Title of the note
        content: Content of the note
        tags: Optional list of tags for categorizing the note
        
    Returns:
        Dictionary with information about the created note
    """
    print(f"[dnd-server] create_note({title}, {content[:20]}..., {tags})")
    
    if tags is None:
        tags = []
    
    # Create a filename from the title
    filename = re.sub(r'[^\w\s-]', '', title.lower())
    filename = re.sub(r'[\s-]+', '_', filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{filename}.md"
    
    # Prepare the note content with metadata
    metadata = f"""---
title: {title}
created: {datetime.now().isoformat()}
tags: {', '.join(tags)}
---

{content}
"""
    
    # Save the note
    note_path = NOTES_DIR / filename
    with open(note_path, 'w') as f:
        f.write(metadata)
    
    return {
        "status": "success",
        "title": title,
        "file": str(note_path),
        "tags": tags
    }

@mcp.tool()
def list_notes(tag: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all notes or filter by tag
    
    Args:
        tag: Optional tag to filter notes by
        
    Returns:
        List of note metadata
    """
    print(f"[dnd-server] list_notes(tag={tag})")
    
    notes = []
    
    for note_file in NOTES_DIR.glob("*.md"):
        with open(note_file, 'r') as f:
            content = f.read()
            
        # Extract metadata from note
        metadata = {}
        if content.startswith("---"):
            # Extract the metadata section
            meta_section = content.split("---")[1]
            for line in meta_section.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()
        
        # Filter by tag if provided
        if tag is not None:
            note_tags = metadata.get("tags", "").split(", ")
            if tag not in note_tags:
                continue
        
        notes.append({
            "title": metadata.get("title", note_file.stem),
            "created": metadata.get("created", "Unknown"),
            "tags": metadata.get("tags", "").split(", "),
            "file": str(note_file)
        })
    
    return notes

@mcp.tool()
def read_note(title_or_filename: str) -> Dict[str, Any]:
    """Read a note by title or filename
    
    Args:
        title_or_filename: Title or filename of the note to read
        
    Returns:
        Dictionary with note content and metadata
    """
    print(f"[dnd-server] read_note({title_or_filename})")
    
    # Try to find the note by filename or title
    note_file = None
    for file in NOTES_DIR.glob("*.md"):
        # Check if the filename matches
        if title_or_filename in str(file):
            note_file = file
            break
        
        # Check if the title in the metadata matches
        with open(file, 'r') as f:
            content = f.read()
            
        if content.startswith("---"):
            meta_section = content.split("---")[1]
            for line in meta_section.strip().split("\n"):
                if line.startswith("title:") and title_or_filename in line:
                    note_file = file
                    break
    
    if note_file is None:
        return {"error": f"Note not found: {title_or_filename}"}
    
    with open(note_file, 'r') as f:
        content = f.read()
    
    # Parse metadata
    metadata = {}
    note_content = content
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            meta_section = parts[1]
            note_content = parts[2].strip()
            
            for line in meta_section.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()
    
    return {
        "title": metadata.get("title", note_file.stem),
        "created": metadata.get("created", "Unknown"),
        "tags": metadata.get("tags", "").split(", "),
        "content": note_content,
        "file": str(note_file)
    }

# Character management tools
@mcp.tool()
def add_character(name: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Add or update a character with the given data
    
    Args:
        name: Character name
        character_data: Character attributes and statistics
        
    Returns:
        Dictionary with status and character info
    """
    print(f"[dnd-server] add_character({name}, {character_data})")
    
    # Load existing characters
    with open(CHARACTERS_FILE, 'r') as f:
        characters = json.load(f)
    
    # Check if character already exists
    for i, char in enumerate(characters):
        if char.get("name") == name:
            # Update existing character
            characters[i] = {
                "name": name,
                **character_data,
                "last_updated": datetime.now().isoformat()
            }
            break
    else:
        # Add new character
        characters.append({
            "name": name,
            **character_data,
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        })
    
    # Save updated characters
    with open(CHARACTERS_FILE, 'w') as f:
        json.dump(characters, f, indent=2)
    
    return {
        "status": "success",
        "name": name,
        "action": "added" if len(characters) == 1 else "updated"
    }

@mcp.tool()
def get_character(name: str) -> Dict[str, Any]:
    """Get character details by name
    
    Args:
        name: Character name
        
    Returns:
        Dictionary with character data
    """
    print(f"[dnd-server] get_character({name})")
    
    # Load characters
    with open(CHARACTERS_FILE, 'r') as f:
        characters = json.load(f)
    
    # Find character by name
    for char in characters:
        if char.get("name") == name:
            return char
    
    return {"error": f"Character not found: {name}"}

@mcp.tool()
def list_characters() -> List[Dict[str, Any]]:
    """List all characters
    
    Returns:
        List of characters with basic info
    """
    print("[dnd-server] list_characters()")
    
    # Load characters
    with open(CHARACTERS_FILE, 'r') as f:
        characters = json.load(f)
    
    # Return basic character info
    return [{
        "name": char.get("name"),
        "class": char.get("class", "Unknown"),
        "level": char.get("level", 1),
        "race": char.get("race", "Unknown")
    } for char in characters]

# Encounter management tools
@mcp.tool()
def create_encounter(name: str, monsters: List[Dict[str, Any]], description: str = "") -> Dict[str, Any]:
    """Create a new encounter with monsters and description
    
    Args:
        name: Encounter name
        monsters: List of monsters with their stats
        description: Optional description of the encounter
        
    Returns:
        Dictionary with encounter info
    """
    print(f"[dnd-server] create_encounter({name}, {monsters}, {description[:20]}...)")
    
    # Load existing encounters
    with open(ENCOUNTERS_FILE, 'r') as f:
        encounters = json.load(f)
    
    # Create new encounter
    encounter = {
        "name": name,
        "monsters": monsters,
        "description": description,
        "created": datetime.now().isoformat()
    }
    
    # Add to encounters
    encounters.append(encounter)
    
    # Save updated encounters
    with open(ENCOUNTERS_FILE, 'w') as f:
        json.dump(encounters, f, indent=2)
    
    return {
        "status": "success",
        "name": name,
        "monster_count": len(monsters)
    }

@mcp.tool()
def list_encounters() -> List[Dict[str, Any]]:
    """List all encounters
    
    Returns:
        List of encounters with basic info
    """
    print("[dnd-server] list_encounters()")
    
    # Load encounters
    with open(ENCOUNTERS_FILE, 'r') as f:
        encounters = json.load(f)
    
    # Return basic encounter info
    return [{
        "name": enc.get("name"),
        "monster_count": len(enc.get("monsters", [])),
        "created": enc.get("created")
    } for enc in encounters]

@mcp.tool()
def get_encounter(name: str) -> Dict[str, Any]:
    """Get encounter details by name
    
    Args:
        name: Encounter name
        
    Returns:
        Dictionary with encounter data
    """
    print(f"[dnd-server] get_encounter({name})")
    
    # Load encounters
    with open(ENCOUNTERS_FILE, 'r') as f:
        encounters = json.load(f)
    
    # Find encounter by name
    for enc in encounters:
        if enc.get("name") == name:
            return enc
    
    return {"error": f"Encounter not found: {name}"}

# Initiative tracker
@mcp.tool()
def roll_initiative(participants: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Roll initiative for a list of participants
    
    Args:
        participants: List of participants with name and modifier
                     [{name: "Goblin 1", modifier: 2}, {name: "Wizard", modifier: 3}]
        
    Returns:
        Ordered list of participants with initiative rolls
    """
    print(f"[dnd-server] roll_initiative({participants})")
    
    initiative_order = []
    
    for participant in participants:
        name = participant.get("name", "Unknown")
        modifier = participant.get("modifier", 0)
        
        # Roll d20 + modifier
        roll = random.randint(1, 20)
        total = roll + modifier
        
        initiative_order.append({
            "name": name,
            "roll": roll,
            "modifier": modifier,
            "total": total
        })
    
    # Sort by total initiative (highest first)
    initiative_order.sort(key=lambda x: x["total"], reverse=True)
    
    return {
        "initiative_order": initiative_order
    }

# Random generators
@mcp.tool()
def generate_random_npc(race: Optional[str] = None, occupation: Optional[str] = None) -> Dict[str, Any]:
    """Generate a random NPC
    
    Args:
        race: Optional race for the NPC
        occupation: Optional occupation for the NPC
        
    Returns:
        Dictionary with NPC details
    """
    print(f"[dnd-server] generate_random_npc(race={race}, occupation={occupation})")
    
    races = ["Human", "Elf", "Dwarf", "Halfling", "Gnome", "Half-Elf", "Half-Orc", "Dragonborn", "Tiefling"]
    occupations = ["Shopkeeper", "Blacksmith", "Guard", "Farmer", "Innkeeper", "Priest", "Noble", "Beggar", "Merchant", "Scholar"]
    traits = ["Friendly", "Suspicious", "Grumpy", "Cheerful", "Nervous", "Confident", "Shy", "Arrogant", "Humble", "Eccentric"]
    
    # Use provided race/occupation or choose randomly
    npc_race = race if race else random.choice(races)
    npc_occupation = occupation if occupation else random.choice(occupations)
    
    # Generate name based on race
    first_names = {
        "Human": ["John", "Mary", "William", "Sarah", "James", "Elizabeth"],
        "Elf": ["Legolas", "Arwen", "Elrond", "Galadriel", "Thranduil", "Tauriel"],
        "Dwarf": ["Gimli", "Thorin", "Balin", "Dwalin", "Gloin", "Durin"],
        "Halfling": ["Frodo", "Bilbo", "Sam", "Pippin", "Merry", "Rosie"],
        # Default for other races
        "default": ["Varis", "Thorn", "Lyra", "Krag", "Elwyn", "Dorian"]
    }
    
    last_names = {
        "Human": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller"],
        "Elf": ["Greenleaf", "Evenstar", "Starseeker", "Moonshadow", "Sunstrider"],
        "Dwarf": ["Ironforge", "Stonebeard", "Goldhand", "Hammerfall", "Battleaxe"],
        "Halfling": ["Baggins", "Gamgee", "Brandybuck", "Took", "Underhill"],
        # Default for other races
        "default": ["Blackwood", "Silverhand", "Stormborn", "Fireheart", "Nightwalker"]
    }
    
    name_list = first_names.get(npc_race, first_names["default"])
    first_name = random.choice(name_list)
    
    last_name_list = last_names.get(npc_race, last_names["default"])
    last_name = random.choice(last_name_list)
    
    return {
        "name": f"{first_name} {last_name}",
        "race": npc_race,
        "occupation": npc_occupation,
        "trait": random.choice(traits),
        "strength": random.randint(8, 16),
        "dexterity": random.randint(8, 16),
        "constitution": random.randint(8, 16),
        "intelligence": random.randint(8, 16),
        "wisdom": random.randint(8, 16),
        "charisma": random.randint(8, 16)
    }

@mcp.tool()
def generate_loot(treasure_level: str = "medium") -> Dict[str, Any]:
    """Generate random loot based on treasure level
    
    Args:
        treasure_level: Level of treasure (low, medium, high, legendary)
        
    Returns:
        Dictionary with generated loot
    """
    print(f"[dnd-server] generate_loot(treasure_level={treasure_level})")
    
    gold = 0
    items = []
    
    # Gold based on treasure level
    if treasure_level == "low":
        gold = random.randint(5, 50)
    elif treasure_level == "medium":
        gold = random.randint(50, 200)
    elif treasure_level == "high":
        gold = random.randint(200, 1000)
    elif treasure_level == "legendary":
        gold = random.randint(1000, 5000)
    else:
        return {"error": "Invalid treasure level. Use 'low', 'medium', 'high', or 'legendary'"}
    
    # Items based on treasure level
    common_items = ["Potion of Healing", "Torch", "Rope", "Bedroll", "Rations", "Waterskin"]
    uncommon_items = ["Potion of Greater Healing", "Scroll of Magic Missile", "Silver dagger", "Fine clothing"]
    rare_items = ["Potion of Superior Healing", "Scroll of Fireball", "Bag of Holding", "Boots of Elvenkind"]
    very_rare_items = ["Potion of Supreme Healing", "Wand of Fireballs", "Ring of Protection", "Cloak of Displacement"]
    legendary_items = ["Staff of Power", "Holy Avenger", "Vorpal Sword", "Ring of Three Wishes"]
    
    # Add items based on treasure level
    if treasure_level == "low":
        for _ in range(random.randint(0, 2)):
            items.append(random.choice(common_items))
    elif treasure_level == "medium":
        for _ in range(random.randint(1, 3)):
            items.append(random.choice(common_items + uncommon_items))
    elif treasure_level == "high":
        for _ in range(random.randint(2, 4)):
            items.append(random.choice(uncommon_items + rare_items))
        items.append(random.choice(very_rare_items))
    elif treasure_level == "legendary":
        for _ in range(random.randint(2, 4)):
            items.append(random.choice(rare_items + very_rare_items))
        items.append(random.choice(legendary_items))
    
    return {
        "gold": gold,
        "items": items
    }

# Random table roller
@mcp.tool()
def roll_on_table(table_name: str) -> Dict[str, Any]:
    """Roll on a random table
    
    Args:
        table_name: Name of the table to roll on
        
    Returns:
        Dictionary with roll result
    """
    print(f"[dnd-server] roll_on_table({table_name})")
    
    tables = {
        "tavern_name": [
            "The Prancing Pony", "The Green Dragon", "The Drunken Sailor",
            "The Silver Tankard", "The Laughing Bard", "The Rusty Nail",
            "The Sleeping Giant", "The Golden Cup", "The Salty Dog",
            "The Dragon's Breath", "The Gilded Rose", "The Howling Wolf"
        ],
        "quest_hook": [
            "A mysterious stranger offers a job with good pay and few questions.",
            "A child's pet has gone missing in a dangerous area.",
            "Strange lights have been seen in an abandoned tower.",
            "A merchant's caravan was attacked, and valuable cargo stolen.",
            "Townsfolk have been disappearing in the night.",
            "An ancient tomb has been discovered outside of town.",
            "A noble is looking for bodyguards for an upcoming journey.",
            "A wizard needs rare ingredients from a monster-infested forest.",
            "A prophetic dream suggests doom unless a specific artifact is found.",
            "Rival adventurers seek the same treasure - it's a race!",
            "A festival needs protection from rumored saboteurs.",
            "A magical experiment has gone wrong with strange effects."
        ],
        "magic_item_quirk": [
            "It always feels slightly warm to the touch.",
            "It makes a quiet whispering sound when used.",
            "It glows faintly in the presence of magic.",
            "Small animals are afraid of it.",
            "It smells faintly of cinnamon.",
            "It floats gently when dropped.",
            "It appears slightly translucent in bright light.",
            "It attracts small insects when unused for a day.",
            "Its color slowly shifts through the rainbow over the course of a week.",
            "It makes its bearer slightly more eloquent when speaking.",
            "It tastes sweet if licked (though few would try this).",
            "It appears in dreams of those who sleep near it."
        ],
        "random_encounter": [
            "A merchant caravan looking for protection.",
            "Bandits lying in wait to ambush travelers.",
            "A wounded traveler needing assistance.",
            "A strange circle of mushrooms with magical properties.",
            "A patrol of local guards checking for trouble.",
            "A wild animal hunting for food.",
            "A lost child from a nearby village.",
            "A traveling bard looking for stories and company.",
            "A minor elemental creature that escaped from another plane.",
            "An overturned wagon with cargo spilled across the road.",
            "A group of pilgrims heading to a sacred site.",
            "A bounty hunter looking for a specific criminal."
        ]
    }
    
    if table_name not in tables:
        return {
            "error": f"Table not found: {table_name}",
            "available_tables": list(tables.keys())
        }
    
    result = random.choice(tables[table_name])
    
    return {
        "table": table_name,
        "result": result
    }

if __name__ == "__main__":
    print("[dnd-server] Starting DND MCP Server...")
    mcp.run(transport="sse")