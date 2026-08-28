from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import ForeignKey,String,DateTime
from sqlalchemy.orm import Mapped,mapped_column

from models.user import Base

class Conversation(Base):
  __tablename__='conversations'

  id:Mapped[int]=mapped_column(
    primary_key=True
  )
  title:Mapped[str|None]=mapped_column()
  user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

  thread_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

  created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
  )

class CreateConversationResponse(BaseModel):
  id:int
  thread_id:str

class ChatRequest(BaseModel):
  conversation_id:int
  user_id:str
  message:str

class ChatResponse(BaseModel):
  message:str

class ConversationRequest(BaseModel):
  user_id:str