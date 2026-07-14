from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.databases.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String(100), nullable=False)

    last_name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False, index=True)

    password = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    posts = relationship(
        "Post",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    comments = relationship(
        "Comment",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    likes = relationship(
        "Like",
        back_populates="user",
        cascade="all, delete-orphan"
    )
