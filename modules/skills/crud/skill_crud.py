from sqlalchemy.orm import Session

from db_mysql.db_models import RobotSkill

import os


def create_skill(db: Session, user_id, skill_name, skill_id, description, params, other):
    skill = RobotSkill(user_id=user_id, skill_name=skill_name, skill_id=skill_id, description=description,
                       params=params, other=other)
    db.add(skill)
    db.commit()
    # 使用refresh来刷新您的数据库实例（以便它包含来自数据库的任何新数据，例如生成的 ID）。
    db.refresh(skill)
    return skill


def list_skill(db: Session, user_id):
    return db.query(RobotSkill).filter(RobotSkill.user_id == user_id, RobotSkill.activate == '1').order_by(
        RobotSkill.update_time.desc()).all()


def delete_skill(db: Session, id):
    skill = db.query(RobotSkill).filter(RobotSkill.id == id).first()
    if skill:
        skill.activate = '0'
        db.commit()
        db.refresh(skill)
    return skill
