from datetime import datetime

from pydantic import BaseModel


class LessonProgressCreate(BaseModel):
    completed: bool = False
    watch_time_seconds: int = 0


class LessonProgressResponse(BaseModel):
    id: int
    student_id: int
    lesson_id: int
    completed: bool
    completed_at: datetime | None
    watch_time_seconds: int

    class Config:
        from_attributes = True


class MarkLessonComplete(BaseModel):
    """Mark a lesson as completed."""
    watch_time_seconds: int = 0
