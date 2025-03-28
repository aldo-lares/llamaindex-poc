"""Agent configuration module."""

from .epic_redaction import get_epic_redaction_agent_config
from .concrete_info import get_concrete_info_agent_config
from .state import get_initial_state

def get_agent_configs():
    """Return a list of all agent configurations."""
    return [
        get_epic_redaction_agent_config(),
        get_concrete_info_agent_config(),
    ]

__all__ = [
    "get_agent_configs",
    "get_initial_state",
    "get_epic_redaction_agent_config",
    "get_concrete_info_agent_config",
]
