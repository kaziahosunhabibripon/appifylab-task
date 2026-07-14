from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_id(user_id: int, db: Session):
    return db.query(User).filter(User.id == user_id).first()