from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.databases.database import get_db
from app.schemas.user import UserResponse
from app.services.user_service import get_user_by_id
from app.utils.oauth2 import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    user = get_user_by_id(user_id, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user