from datetime import datetime

from sqlmodel import Field, SQLModel


class SuccessPost(SQLModel, table=True):
    """Success post for community celebrations."""

    __tablename__ = "success_posts"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    content: str = Field()
    likes_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SuccessPostLike(SQLModel, table=True):
    """Track who liked which post (to prevent double-likes)."""

    __tablename__ = "success_post_likes"

    id: int | None = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="success_posts.id")
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
