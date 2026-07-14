from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.hash import hash_password, verify_password
from app.utils.jwt import create_access_token


def create_user(user: UserCreate, db: Session):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        return None

    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(user: UserLogin, db: Session):
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user is None:
        return None

    if not verify_password(
        user.password,
        existing_user.password
    ):
        return None

    access_token = create_access_token(
        {
            "user_id": existing_user.id
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
