"""add comments and likes

Revision ID: 7c4d8a2f1b90
Revises: 244b20e64e63
Create Date: 2026-07-14 00:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7c4d8a2f1b90"
down_revision: Union[str, Sequence[str], None] = "244b20e64e63"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_posts_visibility_created_at",
        "posts",
        ["visibility", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_posts_owner_visibility_created_at",
        "posts",
        ["owner_id", "visibility", "created_at"],
        unique=False,
    )

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["comments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comments_id"), "comments", ["id"], unique=False)
    op.create_index(op.f("ix_comments_owner_id"), "comments", ["owner_id"], unique=False)
    op.create_index(op.f("ix_comments_parent_id"), "comments", ["parent_id"], unique=False)
    op.create_index(op.f("ix_comments_post_id"), "comments", ["post_id"], unique=False)
    op.create_index(
        "ix_comments_post_parent_created_at",
        "comments",
        ["post_id", "parent_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "likes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("target_type", sa.String(length=20), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "target_type IN ('post', 'comment', 'reply')",
            name="ck_likes_target_type",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "target_type",
            "target_id",
            "user_id",
            name="uq_likes_target_user",
        ),
    )
    op.create_index(op.f("ix_likes_id"), "likes", ["id"], unique=False)
    op.create_index(op.f("ix_likes_target_id"), "likes", ["target_id"], unique=False)
    op.create_index(op.f("ix_likes_target_type"), "likes", ["target_type"], unique=False)
    op.create_index(op.f("ix_likes_user_id"), "likes", ["user_id"], unique=False)
    op.create_index(
        "ix_likes_target_lookup",
        "likes",
        ["target_type", "target_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_likes_target_lookup", table_name="likes")
    op.drop_index(op.f("ix_likes_user_id"), table_name="likes")
    op.drop_index(op.f("ix_likes_target_type"), table_name="likes")
    op.drop_index(op.f("ix_likes_target_id"), table_name="likes")
    op.drop_index(op.f("ix_likes_id"), table_name="likes")
    op.drop_table("likes")

    op.drop_index("ix_comments_post_parent_created_at", table_name="comments")
    op.drop_index(op.f("ix_comments_post_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_parent_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_owner_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_id"), table_name="comments")
    op.drop_table("comments")

    op.drop_index("ix_posts_owner_visibility_created_at", table_name="posts")
    op.drop_index("ix_posts_visibility_created_at", table_name="posts")
