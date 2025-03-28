"""Tools for the Concrete Fabrication Information Agent."""

from llama_index.core.tools import BaseTool
from utils import FunctionToolWithContext

from .get_fabrication_info import get_fabrication_info
from .get_mixing_ratios import get_mixing_ratios
from .get_curing_info import get_curing_info

def get_concrete_info_tools() -> list[BaseTool]:
    """Return tools for the Concrete Fabrication Information Agent."""
    return [
        FunctionToolWithContext.from_defaults(async_fn=get_fabrication_info),
        FunctionToolWithContext.from_defaults(async_fn=get_mixing_ratios),
        FunctionToolWithContext.from_defaults(async_fn=get_curing_info)
    ]
