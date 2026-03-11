from datetime import datetime

from pydantic import BaseModel


class EnrollmentResponse(BaseModel):
    """Enrollment in API responses."""

    id: int
    student_id: int
    course_id: int
    progress: float
    created_at: datetime

    class Config:
        from_attributes = True


class EnrollmentWithCourseResponse(BaseModel):
    """Enrollment with course details for my-courses."""

    id: int
    student_id: int
    course_id: int
    progress: float
    created_at: datetime
    course_title: str
    course_level: str

    class Config:
        from_attributes = True
