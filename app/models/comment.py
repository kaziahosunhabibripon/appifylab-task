from sqlalchemy import Column, ForeignKey, Integer, Text, TIMESTAMP, text
from sqlalchemy.orm import relationship

from app.databases.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id = Column(
        Integer,
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    owner = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    parent = relationship(
        "Comment",
        remote_side=[id],
        back_populates="replies",
    )
    replies = relationship(
        "Comment",
        back_populates="parent",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
