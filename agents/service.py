import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools.weather import search_weather
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sqlalchemy.ext.asyncio import AsyncSession
load_dotenv()

 

@wrap_tool_call
async def handle_tool_errors(request,handler):
  try:
    return await handler(request)
  except Exception as error:
    return ToolMessage(
            content=f"Tool execution failed: {error}",
            tool_call_id=request.tool_call["id"],
    )



class AgentService:
  def __init__(self,checkpointer):
    self.llm=ChatGroq(
      api_key=os.getenv("GROQ_API_KEY"),
      model="openai/gpt-oss-120b",
    )
    self.agent=create_agent(
      model=self.llm,
      tools=[search_weather],
      middleware=[
        handle_tool_errors
      ],
      system_prompt=(
        'You are an helpful assistant'
      ),
      checkpointer=checkpointer
    )
  async def chat(self,message:str,thread_id:str,session:AsyncSession)->str:
    response=await self.agent.ainvoke({
      'messages':[
        {
          "role":"user",
          "content":message
        }
      ]
    },
   config={
     "configurable":{
       "thread_id":thread_id
     }
   }
    )
    return  response["messages"][-1].content
     
    