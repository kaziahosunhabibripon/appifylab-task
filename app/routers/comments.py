from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.databases.database import get_db
from app.schemas.post import CommentCreate, CommentResponse
from app.services.post_service import create_reply
from app.utils.oauth2 import get_current_user

router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)


@router.post(
    "/{comment_id}/replies",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_reply(
    comment_id: int,
    reply: CommentCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    new_reply = create_reply(comment_id, reply, user_id, db)
    if new_reply is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    return new_reply
