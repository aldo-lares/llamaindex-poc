"""Tool for adding tasks to epics."""

from llama_index.core.workflow import Context
from workflow import ProgressEvent

async def add_task_to_epic(
    ctx: Context, epic_id: str, task_description: str
) -> str:
    """Adds a task to an existing epic."""
    ctx.write_event_to_stream(ProgressEvent(msg=f"Adding task to epic {epic_id}"))
    
    user_state = await ctx.get("user_state")
    epics = user_state.get("epics", [])
    
    for epic in epics:
        if epic["id"] == epic_id:
            task_id = f"TASK-{len(epic['tasks']) + 1}"
            task = {
                "id": task_id,
                "description": task_description,
                "status": "To Do"
            }
            epic["tasks"].append(task)
            await ctx.set("user_state", user_state)
            return f"Added task '{task_description}' to epic {epic_id} with ID {task_id}"
    
    return f"Epic with ID {epic_id} not found."
