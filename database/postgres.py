import os
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from models.user import Base
from core.config import Settings
from sqlalchemy.ext.asyncio import(
  AsyncEngine,
  AsyncSession,
  async_sessionmaker,
  create_async_engine
)
class PostgresManager:
  def __init__(self,settings:Settings)->None:
 
    self.pool=AsyncConnectionPool(
      conninfo=settings.psycopg_dsn,
      open=False,
      kwargs={
        "autocommit":True
      }
    )
    self.checkpointer=AsyncPostgresSaver(
      self.pool
    )
 
    self.engine:AsyncEngine=create_async_engine(
      settings.sqlalchemy_dsn,
      echo=settings.db_echo,
      pool_pre_ping=True
    )
    self.session_factory=async_sessionmaker(
      bind=self.engine,
      class_=AsyncSession,
      expire_on_commit=False
    )
    
  async def startup(self):
    print("Opening PostgresSQL connection pool...")
    await self.pool.open()
    print("PostgresSQL connection pool opened")
    await self.checkpointer.setup()
    print("Langgraph checkpoint tables are ready")

 
 

  async def shutdown(self):
    print("Closing PostgreSQL connection pool...")
    await self.pool.close()
    print("PostgreSQL connection pool closed")
    await self.engine.dispose()
    print("SQLAlchemy engine disposed")

  
    