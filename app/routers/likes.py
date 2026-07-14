from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.databases.database import get_db
from app.schemas.post import LikeState
from app.services.post_service import toggle_like
from app.utils.oauth2 import get_current_user

router = APIRouter(
    prefix="/likes",
    tags=["Likes"],
)


@router.post(
    "/{target_type}/{target_id}/toggle",
    response_model=LikeState,
)
def toggle_target_like(
    target_type: str,
    target_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    result = toggle_like(target_type, target_id, user_id, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like target not found",
        )
    return result
