from sqlalchemy.orm import Session

from db_mysql.db_models import RobotSkill, ChatHistory


def list_skill(db: Session, user_id):
    return db.query(RobotSkill).filter(RobotSkill.user_id == user_id, RobotSkill.activate == '1').order_by(
        RobotSkill.update_time.desc()).all()


def _save_msg(db: Session, user_id, digital_role, model, tools, query, answer, prompt='', system=''):
    one = ChatHistory(user_id=user_id, digital_role=digital_role, model=model, tools=tools, query_content=query,
                      answer=answer, prompt=prompt, system=system)
    db.add(one)
    db.commit()
    # 使用refresh来刷新您的数据库实例（以便它包含来自数据库的任何新数据，例如生成的 ID）。
    db.refresh(one)

