from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.databases.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.auth_service import create_user, login_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    new_user = create_user(user, db)

    if new_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    return new_user


@router.post(
    "/login",
    response_model=Token
)
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    token = login_user(user, db)

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return token    