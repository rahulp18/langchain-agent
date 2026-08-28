from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from models.conversation import Conversation


class ConversationRepository:

  def __init__(self,session:AsyncSession):
    self.session=session

  async def create(
      self,
      user_id:int
  )->Conversation:
    conversation=Conversation(
      user_id=user_id,
      thread_id=str(uuid4())
    )
    self.session.add(conversation)
    await self.session.commit()

    await self.session.refresh(
      conversation
    )
    return conversation
  async def get_by_id(
        self,
        conversation_id: int,
        user_id: int
    ) -> Conversation | None:

      result = await self.session.execute(
          select(Conversation)
          .where(
              Conversation.id == conversation_id,
              Conversation.user_id == user_id
          )
      )

      return result.scalar_one_or_none()