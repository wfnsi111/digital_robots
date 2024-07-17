from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .crud import tools_crud
from db_mysql.session import get_db
from .schema_models import *
from openai import AsyncOpenAI
from colorama import init
from mylog.log import logger

import json
import traceback
import requests

router = APIRouter()

from gunicorn import bind

base_url = f"http://{bind}/v1/api"

init(autoreset=True)
client = AsyncOpenAI(
    base_url=base_url,
    api_key="xxx"
)

messages_history = {}

eval_tool = {}


def get_tools_info(user_id, db: Session = Depends(get_db)):
    # 获取工具信息
    skills = tools_crud.list_skill(db, user_id)
    skill_dict = {}
    if skills is not None:
        for skill in skills:
            try:
                skill_dict[skill.skill_name] = {
                    "name": skill.skill_name,  # 函数名字
                    "description": skill.description,  # 函数描述：大模型通过函数的描述，来选择是否调用函数
                    "parameters": json.loads(skill.params),  # 函数参数
                    "skill_id": skill.skill_id,  # 函数id
                }
            except Exception as e:
                logger.error(e)
                continue
    # return json.dumps(skill_dict)
    return skill_dict


def cum_dispatch_tool(user_id, tools, function_name, function_args):
    # 检查参数
    tools_info = tools.get(function_name)
    for param_info in tools_info['parameters']:
        param_name = param_info['name']
        if param_name not in function_args:
            raise KeyError(f"RPA动作为【{function_name}】需要一个{param_name}({param_info['description']})的参数")

    eval_tool[user_id] = {
        "skill_name": function_name,
        "skill_args": function_args,
        "skill_id": tools_info['skill_id'],
    }
    s = f"""
    请确认你要执行RPA动作为【{function_name}】:
    参数为：
    {function_args}
    """
    return s


def post_api(params):
    response = requests.post(f"{base_url}/chat/completions", json=params)
    if response.status_code == 200:
        return response.content.decode("utf-8")
    raise


async def run_conversation(user_id, **params):
    max_retry = 5
    stream = params['stream']
    response = await client.chat.completions.create(**params)
    # response = post_api(params)

    for _ in range(max_retry):
        if not stream:
            if response.choices[0].message.function_call:
                function_call = response.choices[0].message.function_call
                print(f"Function Call Response: {function_call.model_dump()}")

                function_args = json.loads(function_call.arguments)
                # tool_response = dispatch_tool(function_call.name, function_args)
                try:
                    has_exception = False
                    tool_response = cum_dispatch_tool(user_id, params['tools'], function_call.name, function_args)
                except Exception as e:
                    logger.error(e)
                    has_exception = True
                    ret = traceback.format_exc()
                    tool_response = str(ret)

                print(f"Tool Call Response: {tool_response}")

                params["messages"].append(response.choices[0].message)
                params["messages"].append(
                    {
                        "role": "function",
                        "name": function_call.name,
                        "content": tool_response,  # 调用函数返回结果
                    }
                )
                if has_exception:
                    response = client.chat.completions.create(**params)
                    return response
                return tool_response
            else:
                reply = response.choices[0].message.content
                print(f"Final Reply: \n{reply}")
                params["messages"].append(
                    {
                        "role": response.choices[0].message.role,
                        "content": reply,  # 调用函数返回结果
                    }
                )
                return reply


@router.post("/completions2", summary="工具对话")
async def completions2(request: ChatCompletionRequest, db: Session = Depends(get_db)):
    user_id = request.user_id
    digital_role = request.digital_role
    tools = get_tools_info(user_id, db)
    # tools = get_tools()
    model = "chatglm3-6b"
    stream = False
    query = request.query
    messages_list = messages_history.get(user_id, [])
    if query.strip() == 'clear':
        messages_list = []

    if not messages_list:
        descriptions = [skill['description'] for skill in tools.values()]
        descriptions_str = '【' + '】，【'.join(descriptions) + '】'
        system_chat = [
            {
                "role": "system",
                "content": f'你是一个RPA机器人，调用RPA工具执行任务，请牢记。目前的RPA工具有：{descriptions_str}'
            },
            {
                "role": "user",
                "content": '所有信息，必须从对话中提取。不能胡乱编造。'
            },
        ]
        messages_list.extend(system_chat)
        messages_history[user_id] = messages_list

    chat_message = {"role": "user", "content": query}
    # 对话历史记录
    messages_list.append(chat_message)
    params = dict(model=model, messages=messages_list, stream=stream)
    if tools:
        params["tools"] = tools

    # 调用工具，获取对话返回值
    reply = await run_conversation(user_id, **params)
    return reply


@router.get("/identify", response_model=IdentifyToolResponse, summary="确认参数")
def identify_tool(user_id: int = 1):
    tool_params = eval_tool.get(user_id)
    return tool_params
