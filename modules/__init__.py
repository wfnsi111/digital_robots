import platform
from fastapi import APIRouter
from .docs import docs_api
from .skills import skills_api
from .tools import tools_api
from .user import user_api
from .chat import chat_api

api_router = APIRouter()

api_router.include_router(chat_api, prefix="/chat", tags=['对话接口'])
api_router.include_router(docs_api, prefix="/docs", tags=['知识库接口'])
api_router.include_router(skills_api, prefix="/skills", tags=['技能库'])
api_router.include_router(tools_api, prefix="/tools", tags=['工具对话'])
api_router.include_router(user_api, prefix="/user", tags=['用户登录'])


__all__ = ['api_router']
