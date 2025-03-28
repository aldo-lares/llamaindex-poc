"""Tool for deep thinking about epic definitions."""

from llama_index.core.workflow import Context
from llama_index.llms.azure_openai import AzureOpenAI
import os
from workflow import ProgressEvent

async def deep_thinking_epic_definition(
    ctx: Context,
    epic_title: str,
    business_context: str,
    user_needs: str = "",
    constraints: str = "",
    success_criteria: str = ""
) -> str:
    """Performs deep analysis of an epic to define comprehensive tasks and requirements.
    
    Args:
        epic_title: The title of the epic to analyze
        business_context: The business context and goals for this epic
        user_needs: The user needs this epic addresses (optional)
        constraints: Technical or business constraints to consider (optional)
        success_criteria: How success will be measured (optional)
    """
    ctx.write_event_to_stream(ProgressEvent(msg=f"Performing deep thinking for epic: {epic_title}"))
    
    # First, configure and use the o1-mini model for deep thinking
    deep_thinking_llm = AzureOpenAI(
        engine=os.getenv("AZURE_OPENAI_O1_MINI_ENGINE"),
        temperature=float(os.getenv("AZURE_OPENAI_O1_MINI_TEMPERATURE", 0.2)),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        max_tokens=int(os.getenv("AZURE_OPENAI_O1_MINI_MAX_TOKENS", 4096))
    )
    
    # Prepare a comprehensive prompt for deep thinking
    deep_thinking_prompt = f"""
    # Deep Analysis of Epic: {epic_title}
    
    ## Business Context
    {business_context}
    
    ## User Needs
    {user_needs}
    
    ## Constraints
    {constraints}
    
    ## Success Criteria
    {success_criteria}
    
    Perform a deep analysis of this epic by:
    1. Breaking down high-level requirements into detailed technical tasks
    2. Identifying dependencies between tasks
    3. Estimating complexity for each task
    4. Highlighting potential risks or challenges
    5. Suggesting implementation approaches
    6. Recommending success metrics and testing strategies
    
    Structure your response as:
    - Epic Summary
    - Key Tasks (detailed breakdown with complexity estimates)
    - Dependencies
    - Technical Approach
    - Risk Assessment
    - Success Metrics
    """
    
    # Call the deep thinking model
    response = await deep_thinking_llm.acomplete(deep_thinking_prompt)
    deep_analysis = response.text
    
    # Store the deep analysis in the user state
    user_state = await ctx.get("user_state")
    
    # Find the epic or create a new one
    epic_found = False
    for epic in user_state.get("epics", []):
        if epic["title"] == epic_title:
            epic["deep_analysis"] = deep_analysis
            epic_found = True
            break
    
    if not epic_found:
        # Create a new epic with the deep analysis
        epic_id = f"EPIC-{len(user_state.get('epics', [])) + 1}"
        epic = {
            "id": epic_id,
            "title": epic_title,
            "description": business_context,
            "deep_analysis": deep_analysis,
            "priority": "Medium",  # Default values
            "status": "Draft",
            "tasks": []
        }
        
        if "epics" not in user_state:
            user_state["epics"] = []
        user_state["epics"].append(epic)
    
    await ctx.set("user_state", user_state)
    
    # Extract tasks from the deep analysis to add as actual tasks
    # This is a simplified implementation - in a real system, you might want to parse
    # the deep analysis more thoroughly
    tasks_section = deep_analysis.split("Key Tasks")[1].split("Dependencies")[0] if "Key Tasks" in deep_analysis and "Dependencies" in deep_analysis else ""
    tasks = [line.strip() for line in tasks_section.split("\n") if line.strip() and not line.strip().startswith('-')]
    
    # Add extracted tasks to the epic
    for task_desc in tasks:
        if task_desc and len(task_desc) > 5:  # Simple validation
            for epic in user_state.get("epics", []):
                if epic["title"] == epic_title:
                    task_id = f"TASK-{len(epic['tasks']) + 1}"
                    task = {
                        "id": task_id,
                        "description": task_desc,
                        "status": "To Do"
                    }
                    epic["tasks"].append(task)
    
    await ctx.set("user_state", user_state)
    
    return f"Completed deep thinking analysis for epic '{epic_title}'. Generated {len(tasks)} tasks from the analysis."
