import json

from fastapi import APIRouter, Depends

from modules.user.views import get_current_active_user
from config.config import MODEL_BASE_URL, TOKEN
from modules import knowledge_func
from openai import AsyncOpenAI
from .crud import chat_crud
from .schema_models import *
from sqlalchemy.orm import Session
from db_mysql.session import get_db
from mylog.log import logger

router = APIRouter()

client = AsyncOpenAI(
    base_url=MODEL_BASE_URL,
    api_key=TOKEN
)


def get_knowledge_info(messages, k, digital_role, user_id):
    prompt = messages[-1].content
    filter = {
        "$and": [
            {'digital_role': digital_role},
            {'attribute': 'knowledge'},
            {'user_id': user_id},
        ]
    }
    knowledge_info = knowledge_func.similarity_search(prompt, k, filter)
    if not knowledge_info:
        return []
    knowledge_info = '[' + ']\n['.join(knowledge_info) + ']'

    messages[-1].content = f"""
            根据以下已知信息,回答问题。
            找到答案就仅使用已知信息数据回答问题，找不到答案就用自己的知识回答问题。不允许在答案中添加编造成分。
            重点：请不要复述问题，也不要复述已知信息，不要加入分析逻辑，直接告诉答案。
            答案请使用中文。

            已知信息:
            ------------------------------------------------------------------------------
                {knowledge_info}
            ------------------------------------------------------------------------------
            问题:
            *************************
                {prompt}
            *************************
            """
    return knowledge_info


@router.post("/completions", response_model=ChatCompletionResponse, summary='对话接口')
async def create_chat_completion(request: ChatCompletionRequest, user=Depends(get_current_active_user),
                                 db: Session = Depends(get_db)):
    messages = request.messages
    query = messages[-1].content
    knowledge_info = ''

    if request.digital_role not in ('General Robot', 'RPA Robot'):
        knowledge_info = get_knowledge_info(messages, request.k, request.digital_role, user.id)

        # 保留10条聊天记录
        if len(messages) > 20:
            messages = messages[:10] + messages[-11:]

    if request.model == 'glm-4':
        params = dict(
            model="glm-4",
            messages=messages,
            stream=request.stream,
            max_tokens=256,
            temperature=0.4,
            presence_penalty=1.2,
            top_p=0.8,
        )
    else:
        # chatglm3-6b
        params = dict(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens or 8192,
            stream=request.stream,
            tools=request.tools,
        )

    response = await client.chat.completions.create(**params)

    # 存放聊天记录
    tools = request.tools
    try:
        tools = json.dumps(tools)
    except Exception as e:
        logger.error(tools)
        logger.error(e)
    answer = response.choices[0].message.content
    try:
        chat_crud._save_msg(db, user.id, request.digital_role, request.model, tools, query, answer, knowledge_info)
    except Exception as e:
        logger.error(e)

    return response
