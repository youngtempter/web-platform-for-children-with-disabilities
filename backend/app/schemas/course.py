from datetime import datetime

from pydantic import BaseModel


class CourseCreate(BaseModel):
    """Request body for creating a course."""

    title: str
    description: str = ""
    level: str = "beginner"


class CourseUpdate(BaseModel):
    """Request body for updating a course."""

    title: str | None = None
    description: str | None = None
    level: str | None = None


class CourseResponse(BaseModel):
    """Course in API responses."""

    id: int
    title: str
    description: str
    level: str
    teacher_id: int
    created_at: datetime

    class Config:
        from_attributes = True
