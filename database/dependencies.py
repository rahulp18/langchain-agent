from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from database.postgres import PostgresManager

async def get_db_session(postgres:PostgresManager)->AsyncGenerator[AsyncSession,None]:
  async with postgres.session_factory as session:
    yield session