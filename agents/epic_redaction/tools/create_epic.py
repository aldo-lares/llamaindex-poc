"""Tool for creating epics."""

from llama_index.core.workflow import Context
from workflow import ProgressEvent

async def create_epic(
    ctx: Context, 
    title: str, 
    description: str, 
    priority: str = "Medium",
    estimated_size: str = "Unknown"
) -> str:
    """Creates a new software epic with the given details."""
    ctx.write_event_to_stream(ProgressEvent(msg=f"Creating new epic: {title}"))
    
    # In a real implementation, this would store the epic in a database
    user_state = await ctx.get("user_state")
    
    # Initialize epics list if it doesn't exist
    if "epics" not in user_state:
        user_state["epics"] = []
        
    # Create a new epic with a unique ID
    epic_id = f"EPIC-{len(user_state['epics']) + 1}"
    epic = {
        "id": epic_id,
        "title": title,
        "description": description,
        "priority": priority,
        "estimated_size": estimated_size,
        "status": "Draft",
        "tasks": []
    }
    
    user_state["epics"].append(epic)
    await ctx.set("user_state", user_state)
    
    return f"Created new epic '{title}' with ID {epic_id}"
