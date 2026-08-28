 
 
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools.weather import build_weather_tool
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
 
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import Settings
from langgraph.checkpoint.base import BaseCheckpointSaver
 

 

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
  def __init__(self,settings:Settings,checkpointer:BaseCheckpointSaver):
    self.llm=ChatGroq(
      api_key=settings.groq_api_key.get_secret_value(),
      model=settings.llm_model,
    )
    self.agent=create_agent(
      model=self.llm,
      tools=[build_weather_tool(settings)],
      middleware=[
        handle_tool_errors
      ],
      system_prompt=(
        'You are an helpful assistant'
      ),
      checkpointer=checkpointer
    )
  async def chat(self,message:str,thread_id:str)->str:
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
     
    