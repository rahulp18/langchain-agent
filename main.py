from fastapi import FastAPI
from api.chat import router as chat_router
from api.conversation import router as conversation_router
from api.user import router as user_router
from contextlib import asynccontextmanager
from database.postgres import PostgresManager
from agents.service import AgentService
from core.config import get_settings
 

@asynccontextmanager
async def lifespan(app:FastAPI):

  settings=get_settings()
 
  postgres=PostgresManager(settings)
  await postgres.startup()

  app.state.postgres=postgres
  app.state.settings=settings
  app.state.agent_service=AgentService(
    settings,
    checkpointer=postgres.checkpointer
  )
  try:
    yield
  finally:
    await postgres.shutdown()

 

app=FastAPI(
  title="Single Agent API",
  version="1.0.0",
  lifespan=lifespan
)

app.include_router(chat_router)
app.include_router(conversation_router)
app.include_router(user_router)

@app.get('/health')
def health():
  return{
    "status":"working"
  }