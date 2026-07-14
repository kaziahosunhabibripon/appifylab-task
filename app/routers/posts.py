from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.databases.database import get_db
from app.schemas.post import (
    CommentCreate,
    CommentResponse,
    PostCreate,
    PostResponse,
    PostUpdate,
)
from app.services.post_service import (
    create_comment,
    create_post,
    delete_post,
    get_feed,
    get_post,
    update_post,
)
from app.utils.file_upload import save_upload_file
from app.utils.oauth2 import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


async def _parse_post_create(request: Request) -> PostCreate:
    content_type = request.headers.get("content-type", "")

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        image = form.get("image")
        image_url = form.get("image_url")
        if isinstance(image, StarletteUploadFile):
            image_url = save_upload_file(image)

        content = str(form.get("content") or "").strip()
        if not content and not image_url:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Post must include text or an image",
            )

        return PostCreate(
            content=content,
            visibility=str(form.get("visibility") or "public"),
            image_url=str(image_url) if image_url else None,
        )

    payload = await request.json()
    post = PostCreate.model_validate(payload)
    if not post.content.strip() and not post.image_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Post must include text or an image",
        )
    return post


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_new_post(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    post = await _parse_post_create(request)
    return create_post(post, user_id, db)


@router.get("", response_model=list[PostResponse])
def feed(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    return get_feed(user_id, db, limit=limit, offset=offset)


@router.get("/{post_id}", response_model=PostResponse)
def post_details(
    post_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    post = get_post(post_id, user_id, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return post


@router.patch("/{post_id}", response_model=PostResponse)
def edit_post(
    post_id: int,
    post_update: PostUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    post = update_post(post_id, post_update, user_id, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or not owned by you",
        )
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_post(
    post_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    deleted = delete_post(post_id, user_id, db)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or not owned by you",
        )


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    post_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    new_comment = create_comment(post_id, comment, user_id, db)
    if new_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return new_comment
