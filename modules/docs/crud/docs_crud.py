from sqlalchemy.orm import Session

from db_mysql.db_models import User, Knowledge

import os


def getByUsername(db: Session, *, username: str):
    """
    根据用户名查询用户
    :param db:
    :param username:
    :return:
    """
    return db.query(User).filter(User.username == username).first()


def upload_docs(db: Session, file_list, digital_role, attribute, user_id, file_status):
    for file_path in file_list:
        file_name = os.path.split(file_path)[-1]
        one = Knowledge(file_name=file_name, file_path=file_path, digital_role=digital_role, attribute=attribute,
                        user_id=user_id, file_status=file_status)
        db.add(one)
        db.commit()
        # 使用refresh来刷新您的数据库实例（以便它包含来自数据库的任何新数据，例如生成的 ID）。
        db.refresh(one)


def list_docs(db: Session, user_id, digital_role):
    return db.query(Knowledge).filter(Knowledge.user_id == user_id, Knowledge.digital_role == digital_role).order_by(
        Knowledge.update_time.desc()).all()


def delete_docs(db: Session, doc_id):
    one = db.query(Knowledge).filter(Knowledge.id == doc_id).first()
    if one:
        db.delete(one)
        db.commit()
        return 'ok'
