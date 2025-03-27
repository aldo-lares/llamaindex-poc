"""Epic Redaction Agent for creating and managing software epics."""

from llama_index.core.workflow import Context
from llama_index.core.tools import BaseTool

from workflow import AgentConfig, ProgressEvent
from utils import FunctionToolWithContext

def get_epic_redaction_tools() -> list[BaseTool]:
    """Return tools for the Epic Redaction Agent."""
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

    async def estimate_epic(
        ctx: Context, 
        epic_id: str,
        estimation_method: str = "story_points",
        complexity_factor: float = 1.0,
        uncertainty_level: str = "medium"
    ) -> str:
        """Estimates the size/effort required for an epic based on its definition and tasks.
        
        Args:
            epic_id: The ID of the epic to estimate.
            estimation_method: The method to use for estimation (story_points, hours, days).
            complexity_factor: A multiplier for the base estimate (1.0 is standard).
            uncertainty_level: How uncertain the estimate is (low, medium, high).
        """
        ctx.write_event_to_stream(ProgressEvent(msg=f"Estimating epic {epic_id}"))
        
        user_state = await ctx.get("user_state")
        epics = user_state.get("epics", [])
        
        # Find the epic
        epic = None
        for e in epics:
            if e["id"] == epic_id:
                epic = e
                break
                
        if epic is None:
            return f"Epic with ID {epic_id} not found."
        
        # Calculate base estimate based on description length, number of tasks, and priority
        base_estimate = 0
        
        # Factor in description complexity - longer descriptions often mean more complex work
        description_length = len(epic["description"])
        base_estimate += min(10, description_length / 50)  # Cap at 10 points for description
        
        # Factor in number of tasks
        task_count = len(epic["tasks"])
        base_estimate += task_count * 2  # 2 points per task
        
        # Factor in priority - higher priority often means more critical/complex work
        priority_factor = {
            "Low": 0.8,
            "Medium": 1.0,
            "High": 1.2,
            "Critical": 1.5
        }.get(epic["priority"], 1.0)
        
        # Apply complexity and priority factors
        final_estimate = base_estimate * complexity_factor * priority_factor
        
        # Apply uncertainty ranges
        uncertainty_ranges = {
            "low": (0.9, 1.1),
            "medium": (0.7, 1.3),
            "high": (0.5, 2.0)
        }
        
        low_range, high_range = uncertainty_ranges.get(uncertainty_level.lower(), (0.7, 1.3))
        low_estimate = round(final_estimate * low_range)
        high_estimate = round(final_estimate * high_range)
        final_estimate = round(final_estimate)
        
        # Convert to appropriate units based on estimation method
        if estimation_method == "hours":
            unit = "hours"
            # Convert story points to hours (assuming 1 point = 4 hours)
            low_estimate *= 4
            high_estimate *= 4
            final_estimate *= 4
        elif estimation_method == "days":
            unit = "days"
            # Convert story points to days (assuming 1 point = 0.5 days)
            low_estimate *= 0.5
            high_estimate *= 0.5
            final_estimate *= 0.5
        else:  # Default to story points
            unit = "story points"
        
        # Store the estimate in the epic
        epic["estimated_size"] = f"{final_estimate} {unit} (range: {low_estimate}-{high_estimate})"
        await ctx.set("user_state", user_state)
        
        return f"Epic '{epic['title']}' estimated at {final_estimate} {unit} with a range of {low_estimate}-{high_estimate} {unit} ({uncertainty_level} uncertainty)"

    return [
        FunctionToolWithContext.from_defaults(async_fn=create_epic),
        FunctionToolWithContext.from_defaults(async_fn=list_epics),
        FunctionToolWithContext.from_defaults(async_fn=add_task_to_epic),
        FunctionToolWithContext.from_defaults(async_fn=update_epic_status),
        FunctionToolWithContext.from_defaults(async_fn=estimate_epic)
    ]

def get_epic_redaction_agent_config() -> AgentConfig:
    """Return the configuration for the Epic Redaction Agent."""
    return AgentConfig(
        name="Epic Redaction Agent",
        description="Creates and manages software definition epics",
        system_prompt="""
You are an expert software product manager specializing in creating and managing software epics.
You help users define clear, well-structured software epics and break them down into manageable tasks.

When creating epics:
1. Extract key information from the user's request
2. Create a descriptive title that captures the essence of the epic
3. Write a detailed description including context, goals and business value
4. Set an appropriate priority
5. Help break down the epic into smaller tasks
6. Estimate the size of epics based on their complexity, description, and tasks

You can also help with maintaining existing epics, updating their status, and listing the available epics.
Always suggest to the user that they should list epics first if they want to refer to an existing epic.

For estimation, you can provide estimates in story points, hours, or days, and adjust for complexity
and uncertainty factors. This helps with sprint planning and resource allocation.

Valid epic statuses are: Draft, Ready, In Progress, Review, Done
Valid priorities are: Low, Medium, High, Critical
        """,
        tools=get_epic_redaction_tools(),
    )
