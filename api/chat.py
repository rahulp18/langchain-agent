from fastapi import APIRouter,HTTPException
from models.conversation import ChatResponse,ChatRequest
from database.dependencies import DbSession
from agents.dependencies import AgentServiceDep
from repositories.conversation import ConversationRepository
from fastapi.responses import StreamingResponse

router=APIRouter(
  prefix='/api/chat',
  tags=['chat']
)



@router.post('',response_model=ChatResponse)
async def create_chat(body:ChatRequest,agent_service:AgentServiceDep,session:DbSession):
  repo=ConversationRepository(session=session)
  conversation=await repo.get_by_id(conversation_id=body.conversation_id,user_id=body.user_id)
  if not conversation:
    raise HTTPException(status_code=404,detail="Invalid conversation id")
  answer=await agent_service.chat(body.message,conversation.thread_id)
  return ChatResponse(
    message=answer
  )


@router.post('/stream')
async def stream_chat(body:ChatRequest,agent_service:AgentServiceDep,session:DbSession):
   repo=ConversationRepository(session=session)
   conversation=await repo.get_by_id(conversation_id=body.conversation_id,user_id=body.user_id)
   if not conversation:
      raise HTTPException(status_code=404,detail="Invalid conversation id")

   return StreamingResponse(
    agent_service.stream(body.message,conversation.thread_id),
    media_type="text/event-stream",
    headers={
      "Cache-Control":"no-cache",
      "Connection":"keep-alive",
      # stops nginx from buffering the whole response
      "X-Accel-Buffering":"no",
    }
  )
