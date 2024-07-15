from sqlalchemy.orm import Session

from db_mysql.db_models import RobotSkill

import os


def list_skill(db: Session, user_id):
    return db.query(RobotSkill).filter(RobotSkill.user_id == user_id, RobotSkill.activate == '1').order_by(
        RobotSkill.update_time.desc()).all()


