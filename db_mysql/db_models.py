# coding: utf-8
from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from sqlalchemy.dialects.mysql import ENUM, VARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Knowledge(Base):
    __tablename__ = 'knowledges'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    knowledge = Column(VARCHAR(255))
    file_name = Column(String(255))
    file_path = Column(String(255))
    file_type = Column(String(255))
    digital_role = Column(VARCHAR(255), comment='数字机器人角色')
    attribute = Column(VARCHAR(255), comment='文件属性：knowledge')
    file_status = Column(String(255))
    other = Column(VARCHAR(255))
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')


class RobotSkill(Base):
    __tablename__ = 'robot_skills'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    skill_name = Column(String(255), comment='RPA技能')
    skill_id = Column(String(255), comment='技能安装id')
    description = Column(String(255), comment='技能描述')
    params = Column(String(255), comment='参数')
    activate = Column(ENUM('1', '0'), server_default=text("'1'"), comment='1.可用， 0.不可用')
    other = Column(String(255))
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    password = Column(String(255))
    email = Column(String(255))
    telephone = Column(String(255))
    token = Column(String(255))
    activate = Column(ENUM('1', '0'), server_default=text("'1'"), comment='1.可用， 0.不可用')
    other = Column(String(255))
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
