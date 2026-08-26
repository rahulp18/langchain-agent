from fastapi import APIRouter,Request,Depends
from database.dependencies import get_db_session
from models.conversation import CreateConversationResponse
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.conversation import ConversationRepository
router=APIRouter(
  prefix="/api/conversations",
  tags=["conversations"]
)

@router.post("",
            response_model=CreateConversationResponse
             )
async def create_conversation(session:AsyncSession=Depends(get_db_session)):
  repo=ConversationRepository(session)

  conversation=await repo.create(
    user_id=1
  )
  return CreateConversationResponse(
    id=conversation.id,
    thread_id=conversation.thread_id
  )

