from datetime import datetime

from sqlmodel import Field, SQLModel


class LessonProgress(SQLModel, table=True):
    """Tracks student progress per lesson."""

    __tablename__ = "lesson_progress"

    id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="users.id")
    lesson_id: int = Field(foreign_key="lessons.id")
    completed: bool = Field(default=False)
    completed_at: datetime | None = Field(default=None)
    watch_time_seconds: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
