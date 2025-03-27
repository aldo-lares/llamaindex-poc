"""Epic Redaction Agent for creating and managing software epics."""

from llama_index.core.workflow import Context
from llama_index.core.tools import BaseTool
from llama_index.llms.azure_openai import AzureOpenAI
import os

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
            temperature=float(os.getenv("AZURE_OPENAI_O1_MINI_TEMPERATURE", "0.2")),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            max_tokens=int(os.getenv("AZURE_OPENAI_O1_MINI_MAX_TOKENS", "4096"))
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

    async def convert_deep_analysis_to_tasks(
        ctx: Context,
        epic_id: str
    ) -> str:
        """Converts the deep analysis of an epic into structured tasks.
        
        Args:
            epic_id: The ID of the epic to process
        """
        ctx.write_event_to_stream(ProgressEvent(msg=f"Converting deep analysis to tasks for epic {epic_id}"))
        
        user_state = await ctx.get("user_state")
        tasks_added = 0
        
        for epic in user_state.get("epics", []):
            if epic["id"] == epic_id and "deep_analysis" in epic:
                # Use the o1-mini model to extract tasks
                deep_thinking_llm = AzureOpenAI(
                    engine=os.getenv("AZURE_OPENAI_O1_MINI_ENGINE"),
                    temperature=float(os.getenv("AZURE_OPENAI_O1_MINI_TEMPERATURE", "0.2")),
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
                )
                
                task_extraction_prompt = f"""
                Given this deep analysis of an epic:
                
                {epic['deep_analysis']}
                
                Extract all specific tasks that should be created, formatted as a numbered list.
                Each task should have:
                1. A clear, concise description
                2. An estimated complexity (Low, Medium, High)
                3. Any dependencies on other tasks
                
                Format each task as:
                1. Description: [task description]
                   Complexity: [complexity]
                   Dependencies: [dependencies or "None"]
                """
                
                response = await deep_thinking_llm.acomplete(task_extraction_prompt)
                task_text = response.text
                
                # Parse the output to extract tasks
                # This is a simplified parser - you might need more robust parsing
                task_blocks = task_text.split("\n\n")
                
                for block in task_blocks:
                    if "Description:" in block:
                        description = block.split("Description:")[1].split("Complexity:")[0].strip()
                        complexity_part = block.split("Complexity:")[1].split("Dependencies:")[0].strip() if "Dependencies:" in block else block.split("Complexity:")[1].strip()
                        
                        task_id = f"TASK-{len(epic['tasks']) + 1}"
                        task = {
                            "id": task_id,
                            "description": description,
                            "complexity": complexity_part,
                            "status": "To Do"
                        }
                        
                        if "Dependencies:" in block:
                            dependencies = block.split("Dependencies:")[1].strip()
                            if dependencies and dependencies.lower() != "none":
                                task["dependencies"] = dependencies
                        
                        epic["tasks"].append(task)
                        tasks_added += 1
                
                await ctx.set("user_state", user_state)
                return f"Added {tasks_added} structured tasks to epic {epic_id} from deep analysis"
                
        return f"Epic with ID {epic_id} not found or has no deep analysis"

    return [
        FunctionToolWithContext.from_defaults(async_fn=create_epic),
        FunctionToolWithContext.from_defaults(async_fn=list_epics),
        FunctionToolWithContext.from_defaults(async_fn=add_task_to_epic),
        FunctionToolWithContext.from_defaults(async_fn=update_epic_status),
        FunctionToolWithContext.from_defaults(async_fn=estimate_epic),
        FunctionToolWithContext.from_defaults(async_fn=deep_thinking_epic_definition),
        FunctionToolWithContext.from_defaults(async_fn=convert_deep_analysis_to_tasks)
    ]

def get_epic_redaction_agent_config() -> AgentConfig:
    """Return the configuration for the Epic Redaction Agent."""
    return AgentConfig(
        name="Epic Redaction Agent",
        description="Creates and manages software definition epics with deep thinking capabilities",
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

NEW CAPABILITY: You now have a deep thinking mode that uses advanced AI to perform comprehensive analysis
of epics. When a user wants to create a well-defined epic, suggest using the deep_thinking_epic_definition tool
to generate a thorough breakdown of tasks and considerations.

Valid epic statuses are: Draft, Ready, In Progress, Review, Done
Valid priorities are: Low, Medium, High, Critical
        """,
        tools=get_epic_redaction_tools(),
    )
