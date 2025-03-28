"""Tool for estimating epic size."""

from llama_index.core.workflow import Context
from workflow import ProgressEvent

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
