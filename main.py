import uvicorn
import torch
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sse_starlette.sse import EventSourceResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html
)
from modules import api_router
from mylog.log import logger
from datetime import datetime
from config.config import CHROMA_CONFIG
from gunicorn_conf import bind


def clear_docs():
    # 清理本地知识库文档
    folder_path = CHROMA_CONFIG['doc_source']
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            os.unlink(file_path)
        except Exception as e:
            logger.error(f'Failed to delete {file_path}. Reason: {e}')


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('=====================================================================================')
    logger.info(f'start server: {bind} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    yield
    logger.info(f'end server: {bind} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    # 释放内存，gpu
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

    # 清理本地知识库文档
    clear_docs()


# Set up limit request time
EventSourceResponse.DEFAULT_PING_INTERVAL = 1000

app = FastAPI(lifespan=lifespan, title="数字机器人  API文档", docs_url=None, redoc_url=None)
# 启动app时会自动将CDN更换为响应速度较快的那个
# monkey_patch_for_docs_ui(app)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 指定主路由
app.include_router(api_router, prefix='/v1/api')


# 重写docs文档
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


if __name__ == "__main__":
    import platform
    if platform.system().lower() == "windows":
        # uvicorn.run('main:app', host="0.0.0.0", port=8888)
        uvicorn.run('main:app', host="192.168.3.28", port=8888, reload=True)
    else:
        HOST = bind.split(":")[0]
        uvicorn.run('main:app', host=HOST, port=8888)
