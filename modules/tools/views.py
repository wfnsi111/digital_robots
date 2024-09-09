from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .crud import tools_crud
from db_mysql.session import get_db
from modules.user.views import get_current_active_user
from modules.chat.crud import chat_crud
from .schema_models import *
from openai import AsyncOpenAI
from colorama import init
from mylog.log import logger
from config.resp import resp_error_json, resp_success_json, respJsonBase
from config import error_code
from config.config import MODEL_BASE_URL
import json
import traceback

from modules.user.views import oauth2_scheme

router = APIRouter()
# router = APIRouter(dependencies=[Depends(verify_token)])    # 验证token


init(autoreset=True)

messages_history = {}

eval_tool = {}
execute_command = '立即执行'


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
    您要执行的动作为【{function_name}】:
    参数为：
    {function_args},\n
    确认执行，请输入：“{execute_command}”
    """
    return s


# def post_api(params):
#     response = requests.post(f"{base_url}/chat/completions", json=params)
#     if response.status_code == 200:
#         return response.content.decode("utf-8")
#     raise


async def run_conversation(user_id, token, **params):
    max_retry = 5
    stream = params['stream']
    client = AsyncOpenAI(
        base_url=MODEL_BASE_URL,
        api_key=token
    )
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


@router.post("/completions2", summary="工具对话", )
async def completions2(request: ChatCompletionRequest,
                       db: Session = Depends(get_db),
                       user=Depends(get_current_active_user),
                       token: str = Depends(oauth2_scheme)
                       ):
    # api_key = request.headers.get("Authorization")
    user_id = user.id
    digital_role = request.digital_role
    query = request.query
    tools = get_tools_info(user_id, db)
    model = "chatglm3-6b"
    stream = False

    if query.strip().lower() == 'clear':
        messages_history[user_id] = []
        return '你好'

    if query.strip().lower() == execute_command:
        # 用户输入执行确认命名后，返回函数参数
        tool_params = eval_tool.get(user_id, {})
        data = {
            "reply": tool_params,
            "function": True
        }
        if tool_params:
            return resp_success_json(data=data)
        else:
            return resp_error_json(error=error_code.TOOLS_NO_CHOOSE, data=data)

    messages_list = messages_history.get(user_id, [])
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
                "content": '所有信息，必须从对话中提取。不能胡乱编造。你必须每次对话调用rpa工具'
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
        tools = json.dumps(tools)
    else:
        tools = '{}'
    # 调用工具，获取对话返回值
    reply = await run_conversation(user_id, token, **params)
    chat_crud._save_msg(db, user_id, digital_role, model, tools, query, reply, '', messages_list[0]['content'])

    data = {
            "reply": reply,
            "function": False
        }
    return resp_success_json(data=data)


# @router.get("/identify", summary="确认参数")
# def identify_tool(user=Depends(get_current_active_user)):
#     user_id = user.id
#     tool_params = eval_tool.get(user_id)
#     if tool_params:
#         return tool_params
#     else:
#         # raise HTTPException(status_code=500, detail="技能参数不存在")
#         return {}
