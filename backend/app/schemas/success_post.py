from datetime import datetime

from pydantic import BaseModel


class SuccessPostCreate(BaseModel):
    """Request body for creating a success post."""

    content: str


class SuccessPostResponse(BaseModel):
    """Success post in API responses."""

    id: int
    user_id: int
    author_name: str
    content: str
    likes_count: int
    liked_by_me: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SuccessPostListResponse(BaseModel):
    """List of success posts."""

    posts: list[SuccessPostResponse]
    total: int
