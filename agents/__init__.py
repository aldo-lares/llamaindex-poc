"""Agent configuration module."""

from .epic_redaction import get_epic_redaction_agent_config
from .stock_lookup import get_stock_lookup_agent_config
from .authentication import get_authentication_agent_config
from .account_balance import get_account_balance_agent_config
from .transfer_money import get_transfer_money_agent_config
from .state import get_initial_state

def get_agent_configs():
    """Return a list of all agent configurations."""
    return [
        get_epic_redaction_agent_config(),
        # Uncomment to enable additional agents
        # get_stock_lookup_agent_config(),
        # get_authentication_agent_config(),
        # get_account_balance_agent_config(),
        # get_transfer_money_agent_config(),
    ]

__all__ = [
    "get_agent_configs",
    "get_initial_state",
    "get_epic_redaction_agent_config",
    "get_stock_lookup_agent_config",
    "get_authentication_agent_config",
    "get_account_balance_agent_config",
    "get_transfer_money_agent_config",
]
