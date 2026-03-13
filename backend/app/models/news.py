from datetime import datetime

from sqlmodel import Field, SQLModel


class News(SQLModel, table=True):
    """News/announcements for the platform."""

    __tablename__ = "news"

    id: int | None = Field(default=None, primary_key=True)
    title_ru: str = Field()
    title_kz: str = Field(default="")
    content_ru: str = Field()
    content_kz: str = Field(default="")
    video_url: str | None = Field(default=None)
    image_url: str | None = Field(default=None)
    media_url: str | None = Field(default=None)
    media_type: str | None = Field(default=None)  # "youtube", "image" or None
    is_published: bool = Field(default=True)
    author_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
