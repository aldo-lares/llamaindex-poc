"""Tool for listing epics."""

from llama_index.core.workflow import Context
from workflow import ProgressEvent

async def list_epics(ctx: Context) -> str:
    """Lists all available epics."""
    ctx.write_event_to_stream(ProgressEvent(msg="Listing all epics"))
    
    user_state = await ctx.get("user_state")
    epics = user_state.get("epics", [])
    
    if not epics:
        return "No epics found."
    
    result = "Available Epics:\n"
    for epic in epics:
        result += f"- {epic['id']}: {epic['title']} ({epic['status']}) - {epic['priority']} priority\n"
    
    return result
