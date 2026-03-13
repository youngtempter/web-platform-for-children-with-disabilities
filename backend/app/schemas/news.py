from datetime import datetime

from pydantic import BaseModel


class NewsCreate(BaseModel):
    """Request body for creating news."""

    title_ru: str
    title_kz: str = ""
    content_ru: str
    content_kz: str = ""
    video_url: str | None = None
    image_url: str | None = None
    media_url: str | None = None
    media_type: str | None = None
    is_published: bool = True


class NewsUpdate(BaseModel):
    """Request body for updating news."""

    title_ru: str | None = None
    title_kz: str | None = None
    content_ru: str | None = None
    content_kz: str | None = None
    video_url: str | None = None
    image_url: str | None = None
    media_url: str | None = None
    media_type: str | None = None
    is_published: bool | None = None


class NewsResponse(BaseModel):
    """News in API responses."""

    id: int
    title_ru: str
    title_kz: str
    content_ru: str
    content_kz: str
    video_url: str | None
    image_url: str | None
    media_url: str | None
    media_type: str | None
    is_published: bool
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    """List of news with pagination info."""

    news: list[NewsResponse]
    total: int
