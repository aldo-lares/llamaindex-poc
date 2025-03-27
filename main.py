import asyncio
import os
from dotenv import load_dotenv

from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.azure_openai import AzureOpenAI

from workflow import (
    ConciergeAgent,
    ProgressEvent,
    ToolRequestEvent,
    ToolApprovedEvent,
)

# Import agent-related functions from the new agents module
from agents import (
    get_initial_state,
    get_agent_configs
)


async def main():
    """Main function to run the workflow."""
    # Load environment variables from .env file
    load_dotenv()

    from colorama import Fore, Style

    
    # Check if O1-mini configuration exists
    if os.getenv("AZURE_OPENAI_O1_MINI_ENGINE"):
        print(f"O1-MINI Configuration found ({os.getenv('AZURE_OPENAI_O1_MINI_ENGINE')}). Deep thinking capabilities enabled.")
    else:
        print(f"WARNING: O1-MINI Configuration not found. Deep thinking will use standard model: {os.getenv('AZURE_OPENAI_ENGINE')}")
    
    # Initialize primary LLM
    llm = AzureOpenAI(
        engine=os.getenv("AZURE_OPENAI_ENGINE"),
        temperature=float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.4")),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )
    
    memory = ChatMemoryBuffer.from_defaults(llm=llm)
    initial_state = get_initial_state()
    agent_configs = get_agent_configs()
    workflow = ConciergeAgent(timeout=None)

    # Interactive chat loop
    handler = workflow.run(
        user_msg="Hello!",
        agent_configs=agent_configs,
        llm=llm,
        chat_history=[],
        initial_state=initial_state,
    )

    while True:
        async for event in handler.stream_events():
            if isinstance(event, ToolRequestEvent):
                print(
                    Fore.GREEN
                    + "SYSTEM >> I need approval for the following tool call:"
                    + Style.RESET_ALL
                )
                print(event.tool_name)
                print(event.tool_kwargs)
                
                # Special handling for deep thinking operations
                if event.tool_name == "deep_thinking_epic_definition":
                    print(Fore.YELLOW + "\nThis is a deep thinking operation using the o1-mini model." + Style.RESET_ALL)
                    print(Fore.YELLOW + "It will perform extensive analysis on the epic requirements." + Style.RESET_ALL)
                print()

                approved = input("Do you approve? (y/n): ")
                if "y" in approved.lower():
                    handler.ctx.send_event(
                        ToolApprovedEvent(
                            tool_id=event.tool_id,
                            tool_name=event.tool_name,
                            tool_kwargs=event.tool_kwargs,
                            approved=True,
                        )
                    )
                else:
                    reason = input("Why not? (reason): ")
                    handler.ctx.send_event(
                        ToolApprovedEvent(
                            tool_name=event.tool_name,
                            tool_id=event.tool_id,
                            tool_kwargs=event.tool_kwargs,
                            approved=False,
                            response=reason,
                        )
                    )
            elif isinstance(event, ProgressEvent):
                # Special handling for deep thinking progress events
                if "deep thinking" in event.msg.lower():
                    print(Fore.MAGENTA + f"DEEP THINKING >> {event.msg}" + Style.RESET_ALL)
                else:
                    print(Fore.GREEN + f"SYSTEM >> {event.msg}" + Style.RESET_ALL)

        result = await handler
        print(Fore.BLUE + f"AGENT >> {result['response']}" + Style.RESET_ALL)

        # update the memory with only the new chat history
        for i, msg in enumerate(result["chat_history"]):
            if i >= len(memory.get()):
                memory.put(msg)

        user_msg = input("USER >> ")
        if user_msg.strip().lower() in ["exit", "quit", "bye"]:
            break

        # pass in the existing context and continue the conversation
        handler = workflow.run(
            ctx=handler.ctx,
            user_msg=user_msg,
            agent_configs=agent_configs,
            llm=llm,
            chat_history=memory.get(),
            initial_state=initial_state,
        )


if __name__ == "__main__":
    asyncio.run(main())
