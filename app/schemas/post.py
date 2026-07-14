from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse


class PostCreate(BaseModel):
    content: str = ""
    visibility: str = Field(default="public", pattern="^(public|private)$")
    image_url: str | None = None


class PostUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1)
    visibility: str | None = Field(default=None, pattern="^(public|private)$")
    image_url: str | None = None


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)


class LikeState(BaseModel):
    target_type: str
    target_id: int
    liked: bool
    likes_count: int
    liked_by: list[UserResponse]


class CommentResponse(BaseModel):
    id: int
    content: str
    post_id: int
    parent_id: int | None = None
    created_at: datetime
    owner: UserResponse
    likes_count: int = 0
    liked_by: list[UserResponse] = Field(default_factory=list)
    is_liked: bool = False
    replies: list["CommentResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PostResponse(BaseModel):
    id: int
    content: str
    image_url: str | None = None
    visibility: str
    created_at: datetime
    owner: UserResponse
    likes_count: int = 0
    liked_by: list[UserResponse] = Field(default_factory=list)
    is_liked: bool = False
    comments: list[CommentResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


CommentResponse.model_rebuild()
