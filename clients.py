import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


async def main() -> None:
    client = MultiServerMCPClient({
        "paytm": {
            "url": "http://127.0.0.1:8000/sse",
            "transport": "sse",
        }
    })
    print("Fetching MCP tools...")
    tools = await client.get_tools()
    print(f"Loaded {len(tools)} tool(s).")

    llm = ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0
    )
    system_prompt = (
        "You are Paytm MCP Assistant, a helpful chatbot that can call Paytm tools "
        "via a local Model Context Protocol (MCP) server at http://127.0.0.1:8000/sse. "
        "Be concise, ask clarifying questions when needed, and call tools only when useful. "
        "If asked about data source, explain you use the local MCP server and its tools, "
        "not any external Paytm cloud API."
    )
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        name="paytm_assistant",
    )
    messages = []
    print("Type your question and press Enter. Press Ctrl+C to exit.")
    try:
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break
            if not user_input:
                continue
            user_message = HumanMessage(content=user_input)
            latest_chunk = None
            stream_method = getattr(agent, "astream", None)
            if callable(stream_method):
                async for chunk in stream_method(
                    {"messages": messages + [user_message]},
                    stream_mode="values",
                ):
                    latest_chunk = chunk
                    latest_message = chunk["messages"][-1]
                    tool_calls = getattr(latest_message, "tool_calls", None) or []
                    if tool_calls:
                        for call in tool_calls:
                            tool_name = call.get("name")
                            tool_args = call.get("args") or {}
                            print(f"Calling tool: {tool_name} with args: {tool_args}")
            else:
                for chunk in agent.stream(
                    {"messages": messages + [user_message]},
                    stream_mode="values",
                ):
                    latest_chunk = chunk
                    latest_message = chunk["messages"][-1]
                    tool_calls = getattr(latest_message, "tool_calls", None) or []
                    if tool_calls:
                        for call in tool_calls:
                            tool_name = call.get("name")
                            tool_args = call.get("args") or {}
                            print(f"Calling tool: {tool_name} with args: {tool_args}")

            if latest_chunk is None:
                continue

            messages = latest_chunk["messages"]
            last_message = messages[-1]
            if isinstance(last_message, AIMessage) and last_message.content:
                print(last_message.content)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nExiting.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass