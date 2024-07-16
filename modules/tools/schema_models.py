"""
定义所有API请求参数和返回值model

"""
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field
from datetime import datetime


class ChatCompletionRequest(BaseModel):
    user_id: int = 1
    query: str
    digital_role: Optional[str] = 'RPA Robot'


class IdentifyToolResponse(BaseModel):
    skill_name: str
    skill_args: dict
    skill_id: str
