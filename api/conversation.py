from fastapi import APIRouter,Request,Depends
from database.dependencies import get_db_session
from models.conversation import CreateConversationResponse,ConversationRequest
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.conversation import ConversationRepository
router=APIRouter(
  prefix="/api/conversations",
  tags=["conversations"]
)

@router.post("",
            response_model=CreateConversationResponse
             )
async def create_conversation(body:ConversationRequest, session:AsyncSession=Depends(get_db_session)):
  repo=ConversationRepository(session)
  # I KNOW HERE IS NO USER ID VALIDATION THINGS BECAUSE ITS ONLY FOR LEARNING LANGCHAIN TOPIC NOT TO PRACTICE THE AUTH SYSTEM
  conversation=await repo.create(
    user_id=body.user_id
  )
  return CreateConversationResponse(
    id=conversation.id,
    thread_id=conversation.thread_id
  )

