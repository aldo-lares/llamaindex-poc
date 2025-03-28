"""tool to donvert the deep analysis of an epic into structured tasks."""

from llama_index.core.workflow import Context
from workflow import ProgressEvent
from llama_index.llms.azure_openai import AzureOpenAI
import os

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
                # Use the o1-mini model to extract tasksç
                print("Using o1-mini model to extract tasks")
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