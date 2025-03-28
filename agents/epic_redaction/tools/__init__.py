"""Tools for the Epic Redaction Agent."""

from llama_index.core.tools import BaseTool
from utils import FunctionToolWithContext

from .create_epic import create_epic
from .list_epics import list_epics
from .add_task import add_task_to_epic
from .update_status import update_epic_status
from .estimate import estimate_epic
from .deep_thinking import deep_thinking_epic_definition
from .convert_analysis import convert_deep_analysis_to_tasks

def get_epic_redaction_tools() -> list[BaseTool]:
    """Return tools for the Epic Redaction Agent."""
    return [
        FunctionToolWithContext.from_defaults(async_fn=create_epic),
        FunctionToolWithContext.from_defaults(async_fn=list_epics),
        FunctionToolWithContext.from_defaults(async_fn=add_task_to_epic),
        FunctionToolWithContext.from_defaults(async_fn=update_epic_status),
        FunctionToolWithContext.from_defaults(async_fn=estimate_epic),
        FunctionToolWithContext.from_defaults(async_fn=deep_thinking_epic_definition),
        FunctionToolWithContext.from_defaults(async_fn=convert_deep_analysis_to_tasks)
    ]
