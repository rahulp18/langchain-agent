from fastapi import APIRouter,Request,Depends
from models.conversation import ChatResponse,ChatRequest
from database.dependencies import DbSession
from agents.dependencies import AgentServiceDep
from repositories.conversation import ConversationRepository
from sqlalchemy import text
router=APIRouter(
  prefix='/api',
  tags=['chat']
)
 
 

@router.post('/chat',response_model=ChatResponse)
async def create_chat(body:ChatRequest,agent_service:AgentServiceDep,session:DbSession):
  print(body)
  repo=ConversationRepository(session=session)
  conversation=await repo.get_by_id(conversation_id=body.conversation_id,user_id=body.user_id)
  if not conversation:
    raise RuntimeError("Invalid conversation id")
  answer=await agent_service.chat(body.message,conversation.thread_id)
  return ChatResponse(
    message=answer
  )
