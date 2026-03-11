from datetime import datetime

from sqlmodel import Field, SQLModel


class Enrollment(SQLModel, table=True):
    """Student enrollment in a course."""

    __tablename__ = "enrollments"

    id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="users.id")
    course_id: int = Field(foreign_key="courses.id")
    progress: float = Field(default=0.0)  # 0.0 to 100.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
