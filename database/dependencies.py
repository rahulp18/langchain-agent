from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends,Request
from sqlalchemy.ext.asyncio import AsyncSession
from database.postgres import PostgresManager

def get_postgres(request:Request)->PostgresManager:
  return request.app.state.postgres


async def get_db_session(postgres:Annotated[PostgresManager,Depends(get_postgres)])->AsyncGenerator[AsyncSession,None]:
  async with postgres.session_factory() as session:
    yield session


DbSession=Annotated[AsyncSession,Depends(get_db_session)]