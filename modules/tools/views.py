import sys

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .crud import tools_crud
from db_mysql.session import get_db
from .schema_models import *
import json
import traceback
from openai import OpenAI
from colorama import init, Fore
from loguru import logger
from .tool_register import dispatch_tool, get_tools

router = APIRouter()

init(autoreset=True)
client = OpenAI(
    # base_url="http://127.0.0.1:8000/v1",
    base_url="http://192.168.1.56:8888/v1/api",
    api_key="xxx"
)

messages_history = {}

eval_tool = {}


def get_tools_info(user_id, db: Session = Depends(get_db)):
    skills = tools_crud.list_skill(db, user_id)
    skill_dict = {}
    if skills is not None:
        for skill in skills:
            try:
                skill_dict[skill.skill_name] = {
                    "name": skill.skill_name,  # 函数名字
                    "description": skill.description,  # 函数描述：大模型通过函数的描述，来选择是否调用函数
                    "parameters": json.loads(skill.params)
                }
            except Exception as e:
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
        "function_name": function_name,
        "function_args": function_args
    }
    s = f"""
    请确认你要执行RPA动作为【{function_name}】:
    参数为：
    {function_args}

    """
    return s


def run_conversation(user_id, **params):
    max_retry = 5
    stream = params['stream']
    response = client.chat.completions.create(**params)
    # response = post_api(params)

    for _ in range(max_retry):
        if not stream:
            if response.choices[0].message.function_call:
                function_call = response.choices[0].message.function_call
                logger.info(f"Function Call Response: {function_call.model_dump()}")

                function_args = json.loads(function_call.arguments)
                # tool_response = dispatch_tool(function_call.name, function_args)
                try:
                    has_exception = False
                    tool_response = cum_dispatch_tool(user_id, params['tools'], function_call.name, function_args)
                except:
                    has_exception = True
                    ret = traceback.format_exc()
                    tool_response = str(ret)

                logger.info(f"Tool Call Response: {tool_response}")

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
                logger.info(f"Final Reply: \n{reply}")
                params["messages"].append(
                    {
                        "role": response.choices[0].message.role,
                        "content": response.choices[0].message.content,  # 调用函数返回结果
                    }
                )
                return params["messages"]


@router.post("/completions2", summary="工具对话")
async def completions2(request: ChatCompletionRequest, db: Session = Depends(get_db)):
    user_id = request.user_id
    digital_role = request.digital_role
    tools = get_tools_info(user_id, db)
    # tools = get_tools()
    model = "chatglm3"
    stream = False
    query = request.query
    messages_list = messages_history.get(user_id, [])
    if query.strip() == 'clear':
        messages_list = []

    if not messages_list:
        system_chat = [
            {
                "role": "system",
                "content": '你是一个RPA机器人，调用RPA工具执行任务，请牢记。目前的RPA工具有：【发送邮件】，【打开网页】'
            },
            {
                "role": "user",
                "content": '所有信息，必须从role为user的角色中提取。不能胡乱编造。'
            },
        ]
        messages_list.extend(system_chat)
        messages_history[user_id] = messages_list

    chat_message = {"role": "user", "content": query}
    messages_list.append(chat_message)
    params = dict(model=model, messages=messages_list, stream=stream, dialogue=digital_role)
    if tools:
        params["tools"] = tools

    reply = run_conversation(user_id, **params)
    return reply


@router.get("/identify", summary="确认参数")
def identify_tool(user_id: int = 1):
    tool_params = eval_tool.get(user_id)
    return tool_params
