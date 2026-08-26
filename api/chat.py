from fastapi import APIRouter,Request,Depends
from models.chat import ChatRequest,ChatResponse
from agents.service import AgentService
from database.dependencies import get_db_session
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

router=APIRouter(
  prefix='/api',
  tags=['chat']
)
 
@router.get('/test-db')
async def test_database(
    session:Annotated[
      AsyncSession,
      Depends(get_db_session)
    ]
):
  result=await session.execute(
    "SELECT 1"
  )
  return {
    "database":"connected"
  }

@router.post('/chat',response_model=ChatResponse)
async def create_chat(request:Request,body:ChatRequest,session:Annotated[AsyncSession,Depends(get_db_session)]):
  agent_service=request.app.state.agent_service
  answer=await agent_service.chat(body.message,body.thread_id,session=session)
  return ChatResponse(
    message=answer
  )
