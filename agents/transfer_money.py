"""Transfer Money Agent for handling money transfers between accounts."""

from llama_index.core.workflow import Context
from llama_index.core.tools import BaseTool

from workflow import AgentConfig, ProgressEvent
from utils import FunctionToolWithContext

def get_transfer_money_tools() -> list[BaseTool]:
    """Return tools for the Transfer Money Agent."""
    async def is_authenticated(ctx: Context) -> bool:
        """Checks if the user has a session token."""
        ctx.write_event_to_stream(ProgressEvent(msg="Checking if authenticated"))
        user_state = await ctx.get("user_state")
        return user_state["session_token"] is not None

    async def transfer_money(
        ctx: Context, from_account_id: str, to_account_id: str, amount: int
    ) -> str:
        """Useful for transferring money between accounts."""
        is_auth = await is_authenticated(ctx)
        if not is_auth:
            raise ValueError("User is not authenticated!")

        ctx.write_event_to_stream(
            ProgressEvent(
                msg=f"Transferring {amount} from {from_account_id} to account {to_account_id}"
            )
        )
        return f"Transferred {amount} to account {to_account_id}"

    async def balance_sufficient(ctx: Context, account_id: str, amount: int) -> bool:
        """Useful for checking if an account has enough money to transfer."""
        is_auth = await is_authenticated(ctx)
        if not is_auth:
            raise ValueError("User is not authenticated!")

        ctx.write_event_to_stream(
            ProgressEvent(msg="Checking if balance is sufficient")
        )
        user_state = await ctx.get("user_state")
        return user_state["account_balance"] >= amount

    async def has_balance(ctx: Context) -> bool:
        """Useful for checking if an account has a balance."""
        is_auth = await is_authenticated(ctx)
        if not is_auth:
            raise ValueError("User is not authenticated!")

        ctx.write_event_to_stream(
            ProgressEvent(msg="Checking if account has a balance")
        )
        user_state = await ctx.get("user_state")
        return (
            user_state["account_balance"] is not None
            and user_state["account_balance"] > 0
        )

    return [
        FunctionToolWithContext.from_defaults(async_fn=transfer_money),
        FunctionToolWithContext.from_defaults(async_fn=balance_sufficient),
        FunctionToolWithContext.from_defaults(async_fn=has_balance),
        FunctionToolWithContext.from_defaults(async_fn=is_authenticated),
    ]

def get_transfer_money_agent_config() -> AgentConfig:
    """Return the configuration for the Transfer Money Agent."""
    return AgentConfig(
        name="Transfer Money Agent",
        description="Handles money transfers between accounts",
        system_prompt="""
You are a helpful assistant that transfers money between accounts.
The user can only do this if they are authenticated, which you can check with the is_authenticated tool.
If they aren't authenticated, tell them to authenticate first and call the "RequestTransfer" tool.
        """,
        tools=get_transfer_money_tools(),
        tools_requiring_human_confirmation=["transfer_money"],
    )
