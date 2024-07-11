import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from jwt.exceptions import PyJWTError
from datetime import datetime, timedelta

"""
pip
passlib[bcrypt]
pyjwt
"""
# 密码加密相关配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 用于生成和验证 Token 的密钥
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 模拟用户数据库
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": "$2b$12$yvR/JwDilUSUJq3hG9Ev9uIQ5fP38/6aOe7d57sSm3Af2tRUIJzKK",  # 密码是 "password"
        "password": "123456",  # 密码是 "password"
    }
}

USER_TOKEN = {
    'admin': 'xxxx'
}


async def verify_token(request: Request, token: str = Header(...)):
    path: str = request.get('path')

    if path.startswith('/token'):
        pass
    else:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user: str = payload.get("sub")
            if user is None:
                raise HTTPException(status_code=403, detail="Invalid token")
            if token != USER_TOKEN[user]:
                raise HTTPException(status_code=403, detail="Invalid token")
        except PyJWTError:
            raise HTTPException(status_code=403, detail="Invalid token")

# 添加全局token验证，
app = FastAPI(dependencies=[Depends(verify_token)])

# OAuth2密码认证模式，用于验证用户身份
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 获取用户信息的函数
def get_user(user: str):
    if user in fake_users_db:
        user_dict = fake_users_db[user]
        return user_dict


# 验证用户密码的函数
def verify_password(plain_password, hashed_password):
    # return pwd_context.verify(plain_password, hashed_password)
    return plain_password.strip() == '123456'


# 验证用户信息的函数
def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


# 创建 Token 的函数
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 登录接口
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # 过期时间
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    USER_TOKEN[user["username"]] = access_token
    return {"access_token": access_token, "token_type": "bearer"}


# 测试，需要验证 Token
@app.get("/test")
async def protected_route():
    return {"test": 'ok'}


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8888, workers=1)
