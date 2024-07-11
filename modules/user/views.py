from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from modules.docs.crud import docs_crud
from db_mysql.session import get_db
from pydantic import BaseModel

router = APIRouter()


class User(BaseModel):
    username: str


@router.post("/login", summary="用户登录", tags=['用户'])
async def login(request: User, db: Session = Depends(get_db)):
    username = docs_crud.getByUsername(db=db, username=request.username)
    print(username)
    return {'message': '登录成功', 'data': username}
