from sqlalchemy.orm import Session

from db_mysql.db_models import User


def get_user_by_name(db: Session, username, password):
    return db.query(User).filter(User.username == username, User.password == password, User.activate == '1').first()


def get_user_by_id(db: Session, user_id, username):
    return db.query(User).filter(User.id == user_id, User.username == username, User.activate == '1').first()
