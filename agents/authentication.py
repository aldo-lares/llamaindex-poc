"""Authentication Agent for handling user login and authentication."""

from llama_index.core.workflow import Context
from llama_index.core.tools import BaseTool

from workflow import AgentConfig, ProgressEvent
from utils import FunctionToolWithContext

def get_authentication_tools() -> list[BaseTool]:
    """Return tools for the Authentication Agent."""
    async def is_authenticated(ctx: Context) -> bool:
        """Checks if the user has a session token."""
        ctx.write_event_to_stream(ProgressEvent(msg="Checking if authenticated"))
        user_state = await ctx.get("user_state")
        return user_state["session_token"] is not None

    async def store_username(ctx: Context, username: str) -> None:
        """Adds the username to the user state."""
        ctx.write_event_to_stream(ProgressEvent(msg="Recording username"))
        user_state = await ctx.get("user_state")
        user_state["username"] = username
        await ctx.set("user_state", user_state)

    async def login(ctx: Context, password: str) -> str:
        """Given a password, logs in and stores a session token in the user state."""
        user_state = await ctx.get("user_state")
        username = user_state["username"]
        ctx.write_event_to_stream(ProgressEvent(msg=f"Logging in user {username}"))
        # todo: actually check the password
        session_token = "1234567890"
        user_state["session_token"] = session_token
        user_state["account_id"] = "123"
        user_state["account_balance"] = 1000
        await ctx.set("user_state", user_state)

        return f"Logged in user {username} with session token {session_token}. They have an account with id {user_state['account_id']} and a balance of ${user_state['account_balance']}."

    return [
        FunctionToolWithContext.from_defaults(async_fn=store_username),
        FunctionToolWithContext.from_defaults(async_fn=login),
        FunctionToolWithContext.from_defaults(async_fn=is_authenticated),
    ]

def get_authentication_agent_config() -> AgentConfig:
    """Return the configuration for the Authentication Agent."""
    return AgentConfig(
        name="Authentication Agent",
        description="Handles user authentication",
        system_prompt="""
You are a helpful assistant that is authenticating a user.
Your task is to get a valid session token stored in the user state.
To do this, the user must supply you with a username and a valid password. You can ask them to supply these.
If the user supplies a username and password, call the tool "login" to log them in.
Once the user is logged in and authenticated, you can transfer them to another agent.
        """,
        tools=get_authentication_tools(),
    )
