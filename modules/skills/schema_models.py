"""
定义所有API请求参数和返回值model

"""
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field
from datetime import datetime


class SkillModelParam(BaseModel):
    name: str  # 参数名
    description: str  # 参数描述
    type: str = 'str'  # 参数类型
    required: bool  # 是否必须


class SkillModel(BaseModel):
    id: Optional[int] = None
    skill_name: str  # RPA技能
    skill_id: str  # 技能安装id
    description: str  # 技能描述
    params: str  # 参数
    other: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class CreateSkillResponse(BaseModel):
    pass


class DeleteSkillRequest(BaseModel):
    id: int
