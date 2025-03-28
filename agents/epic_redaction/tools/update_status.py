"""Tool for updating epic status."""

from llama_index.core.workflow import Context
from workflow import ProgressEvent

async def update_epic_status(
    ctx: Context, epic_id: str, new_status: str
) -> str:
    """Updates the status of an epic."""
    ctx.write_event_to_stream(ProgressEvent(msg=f"Updating status of epic {epic_id} to {new_status}"))
    
    user_state = await ctx.get("user_state")
    epics = user_state.get("epics", [])
    
    valid_statuses = ["Draft", "Ready", "In Progress", "Review", "Done"]
    if new_status not in valid_statuses:
        return f"Invalid status. Please choose from: {', '.join(valid_statuses)}"
    
    for epic in epics:
        if epic["id"] == epic_id:
            epic["status"] = new_status
            await ctx.set("user_state", user_state)
            return f"Updated status of epic {epic_id} to {new_status}"
    
    return f"Epic with ID {epic_id} not found."
