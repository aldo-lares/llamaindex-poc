"""Account Balance Agent for checking account balances."""

from llama_index.core.workflow import Context
from llama_index.core.tools import BaseTool

from workflow import AgentConfig, ProgressEvent
from utils import FunctionToolWithContext

def get_account_balance_tools() -> list[BaseTool]:
    """Return tools for the Account Balance Agent."""
    async def is_authenticated(ctx: Context) -> bool:
        """Checks if the user has a session token."""
        ctx.write_event_to_stream(ProgressEvent(msg="Checking if authenticated"))
        user_state = await ctx.get("user_state")
        return user_state["session_token"] is not None

    async def get_account_id(ctx: Context, account_name: str) -> str:
        """Useful for looking up an account ID."""
        is_auth = await is_authenticated(ctx)
        if not is_auth:
            raise ValueError("User is not authenticated!")

        ctx.write_event_to_stream(
            ProgressEvent(msg=f"Looking up account ID for {account_name}")
        )
        user_state = await ctx.get("user_state")
        account_id = user_state["account_id"]

        return f"Account id is {account_id}"

    async def get_account_balance(ctx: Context, account_id: str) -> str:
        """Useful for looking up an account balance."""
        is_auth = await is_authenticated(ctx)
        if not is_auth:
            raise ValueError("User is not authenticated!")

        ctx.write_event_to_stream(
            ProgressEvent(msg=f"Looking up account balance for {account_id}")
        )
        user_state = await ctx.get("user_state")
        account_balance = user_state["account_balance"]

        return f"Account {account_id} has a balance of ${account_balance}"

    return [
        FunctionToolWithContext.from_defaults(async_fn=get_account_id),
        FunctionToolWithContext.from_defaults(async_fn=get_account_balance),
        FunctionToolWithContext.from_defaults(async_fn=is_authenticated),
    ]

def get_account_balance_agent_config() -> AgentConfig:
    """Return the configuration for the Account Balance Agent."""
    return AgentConfig(
        name="Account Balance Agent",
        description="Checks account balances",
        system_prompt="""
You are a helpful assistant that is looking up account balances.
The user may not know the account ID of the account they're interested in,
so you can help them look it up by the name of the account.
The user can only do this if they are authenticated, which you can check with the is_authenticated tool.
If they aren't authenticated, tell them to authenticate first and call the "RequestTransfer" tool.
If they're trying to transfer money, they have to check their account balance first, which you can help with.
        """,
        tools=get_account_balance_tools(),
    )
