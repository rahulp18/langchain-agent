from fastapi import FastAPI
from api.chat import router as chat_router
from contextlib import asynccontextmanager
from database.postgres import PostgresManager
from agents.service import AgentService
 
postgres=PostgresManager()

@asynccontextmanager
async def lifespan(app:FastAPI):
  await postgres.startup()

  app.state.postgres=postgres
  print("Application startup complete")
  app.state.agent_service=AgentService(
    checkpointer=postgres.checkpointer
  )
  yield

  await postgres.shutdown()
  print("Application shutdown complete")

app=FastAPI(
  title="Single Agent API",
  version="1.0.0",
  lifespan=lifespan
)

app.include_router(chat_router)

@app.get('/health')
def health():
  return{
    "status":"working"
  }