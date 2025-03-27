"""Stock Lookup Agent for retrieving stock prices and symbols."""

from llama_index.core.workflow import Context
from llama_index.core.tools import BaseTool

from workflow import AgentConfig, ProgressEvent
from utils import FunctionToolWithContext

def get_stock_lookup_tools() -> list[BaseTool]:
    """Return tools for the Stock Lookup Agent."""
    def lookup_stock_price(ctx: Context, stock_symbol: str) -> str:
        """Useful for looking up a stock price."""
        ctx.write_event_to_stream(
            ProgressEvent(msg=f"Looking up stock price for {stock_symbol}")
        )
        return f"Symbol {stock_symbol} is currently trading at $100.00"

    def search_for_stock_symbol(ctx: Context, company_name: str) -> str:
        """Useful for searching for a stock symbol given a free-form company name."""
        ctx.write_event_to_stream(ProgressEvent(msg="Searching for stock symbol"))
        return company_name.upper()

    return [
        FunctionToolWithContext.from_defaults(fn=lookup_stock_price),
        FunctionToolWithContext.from_defaults(fn=search_for_stock_symbol),
    ]

def get_stock_lookup_agent_config() -> AgentConfig:
    """Return the configuration for the Stock Lookup Agent."""
    return AgentConfig(
        name="Stock Lookup Agent",
        description="Looks up stock prices and symbols",
        system_prompt="""
You are a helpful assistant that is looking up stock prices.
The user may not know the stock symbol of the company they're interested in,
so you can help them look it up by the name of the company.
You can only look up stock symbols given to you by the search_for_stock_symbol tool, don't make them up. Trust the output of the search_for_stock_symbol tool even if it doesn't make sense to you.
        """,
        tools=get_stock_lookup_tools(),
    )
