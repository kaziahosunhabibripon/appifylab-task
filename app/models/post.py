from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    TIMESTAMP,
    text,
)
from sqlalchemy.orm import relationship

from app.databases.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)

    content = Column(Text, nullable=False)

    image_url = Column(String, nullable=True)

    visibility = Column(
        String,
        nullable=False,
        server_default="public"
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()")
    )

    owner = relationship(
        "User",
        back_populates="posts"
    )

    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
