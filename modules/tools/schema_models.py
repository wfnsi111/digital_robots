"""
定义所有API请求参数和返回值model

"""
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field
from datetime import datetime


class ChatCompletionRequest(BaseModel):
    query: str
    digital_role: Optional[str] = 'RPA Robot'


class IdentifyToolResponse(BaseModel):
    skill_name: str
    skill_args: dict
    skill_id: str
