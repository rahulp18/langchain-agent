from fastapi import APIRouter
from database.dependencies import DbSession
from models.user import CreateUserDto,User
from repositories.user import UserRepository
router=APIRouter(
  prefix='/api/users',
  tags=['users']
)

@router.post("",
            #  response_class=User
             )
async def create_user(body:CreateUserDto,session:DbSession):
  repo=UserRepository(session)
  print(body)
  return await repo.create_user(name=body.name,email=body.email)
