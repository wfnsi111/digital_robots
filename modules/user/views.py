from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session
from modules.user.crud import user_crud
from db_mysql.session import get_db
from .schema_models import *

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/api/user/login")

access_token_test = 'gfgrtrelllfkdfjalenzzz'


async def verify_token(token: str = Depends(oauth2_scheme)):
    # todo 验证 token
    if access_token_test not in token:
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def create_access_token(user):
    # todo 创建 token
    return user.username + access_token_test + str(user.id)


async def fake_decode_token(db, token):
    # 解析token， 查询user
    username, user_id = token.split(access_token_test)
    user = user_crud.get_user_by_id(db, user_id, username)
    return user


async def get_current_active_user(token: str = Depends(oauth2_scheme),
                                  db: Session = Depends(get_db)):
    await verify_token(token)  # 验证token
    user = await fake_decode_token(db, token)  # 获取用户
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # return user
    if user.activate == '0':
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


@router.post("/login", summary="用户登录")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    username = username.strip()
    password = password.strip()
    user = user_crud.get_user_by_name(db=db, username=username, password=password)
    if not user:
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect account")
        return {
            "code": 400,
            "msg": "无效的账户",
            "data": ""
        }
    access_token = await create_access_token(user)
    return {
        "code": 200,
        "msg": "success",
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "user_id": user.id,
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "username": user.username,
            "user_id": user.id,
        }
    }


"""
请求头token 格式：Authorization: Bearer + 空格 + token
#Authorization: Bearer testgfgrtrelllfkdfjalenzzz1313131


# 通过依赖注入获取用户信息
@router.get("/test", summary="测试")
def test(user=Depends(get_current_active_user)):
    return user
"""

