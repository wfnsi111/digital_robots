import os
from contextlib import contextmanager
from typing import Generator
# from contextvars import ContextVar
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.config import MYSQL_CONFIG

HOST = MYSQL_CONFIG['host']
PORT = MYSQL_CONFIG['port']
USERNAME = MYSQL_CONFIG['username']
PASSWORD = MYSQL_CONFIG['password']
DB = MYSQL_CONFIG['db']

DB_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}"

engine = create_engine(DB_URI,
                       pool_pre_ping=True,
                       # echo=True,  # 是否打印原生sql
                       pool_size=5,  # 连接池大小， 0表示无限制
                       )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 创建session
DbSession = sessionmaker(bind=engine)
db_session = DbSession()


@contextmanager
def session_maker(session=db_session):
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator:
    """
    get SQLAlchemy session to curd
    :return: SQLAlchemy Session
    """
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db:
            db.close()


def get_db_connect() -> Generator:
    """
    get SQLAlchemy connect to exec sql
    :return: SQLAlchemy connect
    """
    conn = None
    try:
        conn = engine.connect()
        yield conn
    finally:
        if conn:
            conn.close()


# db_session: ContextVar[Session] = ContextVar('db_session')


if __name__ == '__main__':
    # 逆向工程 自动生成模型文件
    tables = ["knowledges", "user", "robot_skills"]
    os.system(f'sqlacodegen --tables {",".join(tables)} {DB_URI} > db_models.py')

    # 根据模型文件 生成对应的数据库表
    # Base.metadata.create_all(engine)
