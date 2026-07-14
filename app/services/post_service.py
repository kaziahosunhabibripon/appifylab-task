from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, selectinload

from app.models.comment import Comment
from app.models.like import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.post import CommentCreate, PostCreate, PostUpdate


def _user_response(user: User) -> dict:
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
    }


def _liked_by(target_type: str, target_id: int, db: Session) -> list[dict]:
    users = (
        db.query(User)
        .join(Like, Like.user_id == User.id)
        .filter(Like.target_type == target_type, Like.target_id == target_id)
        .order_by(Like.created_at.asc())
        .all()
    )
    return [_user_response(user) for user in users]


def _likes_count(target_type: str, target_id: int, db: Session) -> int:
    return (
        db.query(Like)
        .filter(Like.target_type == target_type, Like.target_id == target_id)
        .count()
    )


def _is_liked(target_type: str, target_id: int, user_id: int, db: Session) -> bool:
    return (
        db.query(Like)
        .filter(
            Like.target_type == target_type,
            Like.target_id == target_id,
            Like.user_id == user_id,
        )
        .first()
        is not None
    )


def _comment_target_type(comment: Comment) -> str:
    return "reply" if comment.parent_id else "comment"


def _serialize_comment(comment: Comment, user_id: int, db: Session) -> dict:
    target_type = _comment_target_type(comment)
    return {
        "id": comment.id,
        "content": comment.content,
        "post_id": comment.post_id,
        "parent_id": comment.parent_id,
        "created_at": comment.created_at,
        "owner": _user_response(comment.owner),
        "likes_count": _likes_count(target_type, comment.id, db),
        "liked_by": _liked_by(target_type, comment.id, db),
        "is_liked": _is_liked(target_type, comment.id, user_id, db),
        "replies": [
            _serialize_comment(reply, user_id, db)
            for reply in sorted(
                comment.replies,
                key=lambda reply_item: reply_item.created_at,
            )
        ],
    }


def _serialize_post(post: Post, user_id: int, db: Session) -> dict:
    top_level_comments = [
        comment for comment in post.comments if comment.parent_id is None
    ]

    return {
        "id": post.id,
        "content": post.content,
        "image_url": post.image_url,
        "visibility": post.visibility,
        "created_at": post.created_at,
        "owner": _user_response(post.owner),
        "likes_count": _likes_count("post", post.id, db),
        "liked_by": _liked_by("post", post.id, db),
        "is_liked": _is_liked("post", post.id, user_id, db),
        "comments": [
            _serialize_comment(comment, user_id, db)
            for comment in sorted(
                top_level_comments,
                key=lambda comment_item: comment_item.created_at,
            )
        ],
    }


def _visible_posts_query(user_id: int, db: Session):
    return (
        db.query(Post)
        .options(
            selectinload(Post.owner),
            selectinload(Post.comments).selectinload(Comment.owner),
            selectinload(Post.comments).selectinload(Comment.replies),
        )
        .filter(or_(Post.visibility == "public", Post.owner_id == user_id))
    )


def get_visible_post(post_id: int, user_id: int, db: Session) -> Post | None:
    return _visible_posts_query(user_id, db).filter(Post.id == post_id).first()


def create_post(post: PostCreate, user_id: int, db: Session):
    new_post = Post(
        content=post.content,
        image_url=post.image_url,
        visibility=post.visibility,
        owner_id=user_id,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return get_post(new_post.id, user_id, db)


def get_feed(user_id: int, db: Session, limit: int = 20, offset: int = 0):
    limit = min(max(limit, 1), 100)
    offset = max(offset, 0)
    posts = (
        _visible_posts_query(user_id, db)
        .order_by(Post.created_at.desc(), Post.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_serialize_post(post, user_id, db) for post in posts]


def get_post(post_id: int, user_id: int, db: Session):
    post = get_visible_post(post_id, user_id, db)
    if post is None:
        return None
    return _serialize_post(post, user_id, db)


def update_post(post_id: int, post_update: PostUpdate, user_id: int, db: Session):
    post = db.query(Post).filter(Post.id == post_id, Post.owner_id == user_id).first()
    if post is None:
        return None

    update_data = post_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    db.commit()
    return get_post(post.id, user_id, db)


def delete_post(post_id: int, user_id: int, db: Session) -> bool:
    post = db.query(Post).filter(Post.id == post_id, Post.owner_id == user_id).first()
    if post is None:
        return False

    db.delete(post)
    db.commit()
    return True


def create_comment(
    post_id: int,
    comment: CommentCreate,
    user_id: int,
    db: Session,
    parent_id: int | None = None,
):
    post = get_visible_post(post_id, user_id, db)
    if post is None:
        return None

    parent = None
    if parent_id is not None:
        parent = (
            db.query(Comment)
            .filter(Comment.id == parent_id, Comment.post_id == post_id)
            .first()
        )
        if parent is None:
            return None

    new_comment = Comment(
        content=comment.content,
        post_id=post_id,
        owner_id=user_id,
        parent_id=parent.id if parent else None,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return _serialize_comment(new_comment, user_id, db)


def create_reply(comment_id: int, reply: CommentCreate, user_id: int, db: Session):
    parent = (
        db.query(Comment)
        .join(Post, Post.id == Comment.post_id)
        .options(selectinload(Comment.owner), selectinload(Comment.replies))
        .filter(
            Comment.id == comment_id,
            or_(Post.visibility == "public", Post.owner_id == user_id),
        )
        .first()
    )
    if parent is None:
        return None

    new_reply = Comment(
        content=reply.content,
        post_id=parent.post_id,
        owner_id=user_id,
        parent_id=parent.id,
    )

    db.add(new_reply)
    db.commit()
    db.refresh(new_reply)

    return _serialize_comment(new_reply, user_id, db)


def _get_like_target(target_type: str, target_id: int, user_id: int, db: Session):
    if target_type == "post":
        return get_visible_post(target_id, user_id, db)

    if target_type not in {"comment", "reply"}:
        return None

    comment = (
        db.query(Comment)
        .join(Post, Post.id == Comment.post_id)
        .options(selectinload(Comment.owner), selectinload(Comment.replies))
        .filter(
            Comment.id == target_id,
            or_(Post.visibility == "public", Post.owner_id == user_id),
        )
        .first()
    )

    if comment is None:
        return None

    if target_type == "comment" and comment.parent_id is not None:
        return None

    if target_type == "reply" and comment.parent_id is None:
        return None

    return comment


def toggle_like(target_type: str, target_id: int, user_id: int, db: Session):
    target = _get_like_target(target_type, target_id, user_id, db)
    if target is None:
        return None

    existing_like = (
        db.query(Like)
        .filter(
            Like.target_type == target_type,
            Like.target_id == target_id,
            Like.user_id == user_id,
        )
        .first()
    )

    liked = existing_like is None
    if existing_like:
        db.delete(existing_like)
    else:
        db.add(
            Like(
                target_type=target_type,
                target_id=target_id,
                user_id=user_id,
            )
        )

    db.commit()

    return {
        "target_type": target_type,
        "target_id": target_id,
        "liked": liked,
        "likes_count": _likes_count(target_type, target_id, db),
        "liked_by": _liked_by(target_type, target_id, db),
    }
