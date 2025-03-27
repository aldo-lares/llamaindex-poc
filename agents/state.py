"""Initial state for the agent system."""

def get_initial_state() -> dict:
    """Return the initial state for the agent system."""
    return {
        "username": None,
        "session_token": None,
        "account_id": None,
        "account_balance": None,
    }
