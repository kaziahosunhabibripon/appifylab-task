from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import relationship

from app.databases.database import Base


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    target_type = Column(String(20), nullable=False, index=True)
    target_id = Column(Integer, nullable=False, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    user = relationship("User", back_populates="likes")

    __table_args__ = (
        UniqueConstraint(
            "target_type",
            "target_id",
            "user_id",
            name="uq_likes_target_user",
        ),
        CheckConstraint(
            "target_type IN ('post', 'comment', 'reply')",
            name="ck_likes_target_type",
        ),
    )
