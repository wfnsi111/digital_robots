"""
定义所有API请求参数和返回值model

"""
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field
from datetime import datetime


class User(BaseModel):
    name: Optional[str] = None
    account: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    token: Optional[str] = None
    other: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    user_id: int
