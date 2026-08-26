import os
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from models.user import Base
from sqlalchemy.ext.asyncio import(
  AsyncEngine,
  AsyncSession,
  async_sessionmaker,
  create_async_engine
)
class PostgresManager:
  def __init__(self):
    database_url=os.getenv("DATABASE_URL")

    if not database_url:
      raise RuntimeError(
        "Database URL is not present in .env"
      )
    self.pool=AsyncConnectionPool(
      conninfo=database_url,
      open=False,
      kwargs={
        "autocommit":True
      }
    )
    self.checkpointer=AsyncPostgresSaver(
      self.pool
    )
    sqlalchemy_url=database_url.replace(
      "postgres://",
      "postgres+psycopg://",
      1
    )
    self.engine:AsyncEngine=create_async_engine(
      sqlalchemy_url,
      echo=True
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

    await self.create_tables()
 

  async def shutdown(self):
    print("Closing PostgreSQL connection pool...")
    await self.pool.close()
    print("PostgreSQL connection pool closed")
    await self.engine.dispose()
    print("SQLAlchemy engine disposed")

  async def create_tables(self):
    async with self.engine.begin() as connection:
      await connection.run_sync(
        Base.metadata.create_all
      )
    