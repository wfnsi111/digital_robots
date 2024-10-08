import json

from openai import OpenAI
from colorama import init, Fore
from loguru import logger
import requests
from tool_register import get_tools, dispatch_tool

base_url = "http://192.168.1.56:8888/v1/api"
init(autoreset=True)
client = OpenAI(
    # base_url="http://127.0.0.1:8000/v1",
    base_url=base_url,
    api_key="xxx"
)

tools = get_tools()


def post_api(params):
    response = requests.post(f"{base_url}/chat/completions", json=params)
    if response.status_code == 200:
        return response.content.decode("utf-8")
    raise


def run_conversation(messages: list, stream=False, tools=None, max_retry=5):
    params = dict(model="chatglm3", messages=messages, stream=stream)
    if tools:
        params["tools"] = tools
    # response = client.chat.completions.create(**params)
    response = post_api(params)

    for _ in range(max_retry):
        if not stream:
            if response.choices[0].message.function_call:
                function_call = response.choices[0].message.function_call
                logger.info(f"Function Call Response: {function_call.model_dump()}")

                function_args = json.loads(function_call.arguments)
                tool_response = dispatch_tool(function_call.name, function_args)
                logger.info(f"Tool Call Response: {tool_response}")

                params["messages"].append(response.choices[0].message)
                params["messages"].append(
                    {
                        "role": "function",
                        "name": function_call.name,
                        "content": tool_response,  # 调用函数返回结果
                    }
                )
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
        else:
            output = ""
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(Fore.BLUE + content, end="", flush=True)
                output += content
                print(chunk.choices[0].finish_reason)

                if chunk.choices[0].finish_reason == "stop":
                    return

                elif chunk.choices[0].finish_reason == "function_call":
                    print("\n")

                    function_call = chunk.choices[0].delta.function_call
                    logger.info(f"Function Call Response: {function_call.model_dump()}")

                    function_args = json.loads(function_call.arguments)
                    tool_response = dispatch_tool(function_call.name, function_args)
                    logger.info(f"Tool Call Response: {tool_response}")

                    params["messages"].append(
                        {
                            "role": "assistant",
                            "content": output
                        }
                    )
                    params["messages"].append(
                        {
                            "role": "function",
                            "name": function_call.name,
                            "content": tool_response,
                        }
                    )

                    break

        response = client.chat.completions.create(**params)


if __name__ == "__main__":
    query = "成都天气如何"
    # run_conversation(query, stream=True)

    logger.info("\n=========== next conversation ===========")
    messages_list = [{"role": "assistant",
                      "content": '你是一个RPA机器人，调用RPA工具执行任务，请牢记。目前的RPA工具有：【发送邮件】，【打开网页】.'}]
    while True:
        query = input("请输入：")

        chat_message = {"role": "user", "content": query}

        messages_list.append(chat_message)
        res = run_conversation(messages_list, tools=tools, stream=False)
        # messages_list.extend(res)
