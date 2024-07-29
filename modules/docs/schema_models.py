"""
定义所有API请求参数和返回值model

"""
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field
from datetime import datetime
from fastapi import File, UploadFile


# 知识库
class AddDocumentsRequest(BaseModel):
    digital_role: str
    attribute: Optional[str] = 'docs'
    files: List[UploadFile] = File(...)


class AddDocumentsResponse(BaseModel):
    result: str = "ok"


class DocumentsModel(BaseModel):
    id: int
    file_name: str
    update_time: datetime
    status: str


class ListDocumentsRequest(BaseModel):
    digital_role: Optional[str] = None


class ListDocumentsResponse(BaseModel):
    documents: List[DocumentsModel]


class DeleteDocumentsRequest(BaseModel):
    doc_id: int
    filename: str
    digital_role: str


class DeleteDocumentsResponse(BaseModel):
    result: str = "ok"


class QueryDocumentsRequest(BaseModel):
    prompt: str  # 查询提示词
    k: Optional[int] = 3  # 查询文档量
    digital_role: Optional[str] = 'hr robot'  # 数字机器人角色
