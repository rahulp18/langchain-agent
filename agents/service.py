import json
from collections.abc import AsyncIterator

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage

from core.config import Settings
from tools.weather import build_weather_tool
from langgraph.checkpoint.base import BaseCheckpointSaver


@wrap_tool_call
async def handle_tool_errors(request, handler):
    try:
        return await handler(request)
    except Exception as error:
        return ToolMessage(
            content=f"Tool execution failed: {error}",
            tool_call_id=request.tool_call["id"],
        )


def sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


class AgentService:

    def __init__(
        self,
        settings: Settings,
        checkpointer: BaseCheckpointSaver,
    ):
        self.llm = ChatGroq(
            api_key=settings.groq_api_key.get_secret_value(),
            model=settings.llm_model,
        )

        self.agent = create_agent(
            model=self.llm,
            tools=[
                build_weather_tool(settings),
            ],
            middleware=[
                handle_tool_errors,
            ],
            system_prompt="You are a helpful assistant",
            checkpointer=checkpointer,
        )

    async def chat(
        self,
        message: str,
        thread_id: str,
    ) -> str:

        response = await self.agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            },
            config={
                "configurable": {
                    "thread_id": thread_id,
                }
            },
        )

        return response["messages"][-1].content

    async def stream(
        self,
        message: str,
        thread_id: str,
    ) -> AsyncIterator[str]:

        try:
            # v3 returns an awaitable that resolves to the run stream,
            # so this one has to be awaited before iterating.
            run = await self.agent.astream_events(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": message,
                        }
                    ]
                },
                version="v3",
                config={
                    "configurable": {
                        "thread_id": thread_id,
                    }
                },
            )

            async with run:
                # One chat stream per LLM call. The agent loops
                # model -> tool -> model, so this yields more than once
                # whenever a tool is used.
                async for chat_stream in run.messages:

                    async for delta in chat_stream.text:
                        yield sse(
                            {
                                "type": "token",
                                "content": delta,
                            }
                        )

                    reply = await chat_stream.output

                    for tool_call in reply.tool_calls:
                        yield sse(
                            {
                                "type": "tool_call",
                                "name": tool_call["name"],
                                "args": tool_call["args"],
                            }
                        )

        except Exception as error:
            yield sse(
                {
                    "type": "error",
                    "message": f"{type(error).__name__}: {error}",
                }
            )

        yield sse({"type": "done"})
