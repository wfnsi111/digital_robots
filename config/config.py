from urllib import parse
import os
import platform

DEBUG = True
# DEBUG = False

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

if platform.system().lower() == 'windows':
    embedding_model_path = "D:/PycharmProjects/text2vec-bge-large-chinese"
else:
    embedding_model_path = "/home/work/models/text2vec-bge-large-chinese"

# 向量数据库配置
CHROMA_CONFIG = {
    'doc_source': os.path.join(basedir, "docs"),  # 需要向量化的文档
    'embedding_model': embedding_model_path,  # embeding模型
    'db_source': os.path.join(basedir, "db_chroma"),  # 向量化数据库
    'chunk_size': 200,  # 块词量
    'chunk_overlap': 20,  # 交集范围
    'k': 3,  # 查询文档量
}

# mysql 配置
MYSQL_CONFIG = {
    'host': '192.168.3.56',
    'port': 3306,
    'username': 'root',
    'password': parse.quote_plus('Qfgn123@'),
    'db': 'digital_robots',
}

# Set up limit request time
DEFAULT_PING_INTERVAL = 1000

# set LLM path
# MODEL_PATH = os.environ.get('MODEL_PATH', '/home/work/chatglm3-2/chatglm3-6b')
MODEL_PATH = '/home/work/chatglm3-2/chatglm3-6b'

TOKENIZER_PATH = os.environ.get("TOKENIZER_PATH", MODEL_PATH)

# set Embedding Model path
EMBEDDING_PATH = os.environ.get('EMBEDDING_PATH', '/home/work/chatglm3-2/m3e-base')
