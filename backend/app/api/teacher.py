"""Teacher API: stats, students list."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from pydantic import BaseModel

from app.api.deps import CurrentUser, require_teacher_or_admin
from app.db.session import get_session
from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.lesson import Lesson
from app.models.lesson_progress import LessonProgress
from app.models.quiz import Quiz, QuizAttempt
from app.schemas.user import UserResponse

router = APIRouter(prefix="/teacher", tags=["teacher"])


class TeacherStats(BaseModel):
    total_courses: int
    total_lessons: int
    total_students: int
    average_progress: float


class StudentQuizStats(BaseModel):
    attempts_count: int
    passed_count: int
    best_score: int | None
    avg_score: float | None


class StudentWithProgress(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    course_id: int
    course_title: str
    progress: float
    enrolled_at: str
    quiz_stats: StudentQuizStats | None = None

    class Config:
        from_attributes = True


class TeacherStudentsResponse(BaseModel):
    students: list[StudentWithProgress]
    total: int


@router.get("/stats", response_model=TeacherStats)
def get_teacher_stats(
    current_user: CurrentUser,
    session: Session = Depends(get_session),
):
    """Get statistics for current teacher's courses."""
    require_teacher_or_admin(current_user)
    
    # Get teacher's courses
    if current_user.role == "admin":
        courses = session.exec(select(Course)).all()
    else:
        courses = session.exec(select(Course).where(Course.teacher_id == current_user.id)).all()
    
    course_ids = [c.id for c in courses]
    
    if not course_ids:
        return TeacherStats(
            total_courses=0,
            total_lessons=0,
            total_students=0,
            average_progress=0.0
        )
    
    # Count lessons
    total_lessons = session.exec(
        select(func.count(Lesson.id)).where(Lesson.course_id.in_(course_ids))
    ).one()
    
    # Count unique students enrolled in teacher's courses
    enrollments = session.exec(
        select(Enrollment).where(Enrollment.course_id.in_(course_ids))
    ).all()
    
    unique_students = set(e.student_id for e in enrollments)
    total_students = len(unique_students)
    
    # Calculate average progress
    if enrollments:
        average_progress = sum(e.progress for e in enrollments) / len(enrollments)
    else:
        average_progress = 0.0
    
    return TeacherStats(
        total_courses=len(courses),
        total_lessons=total_lessons,
        total_students=total_students,
        average_progress=round(average_progress, 1)
    )


@router.get("/students", response_model=TeacherStudentsResponse)
def get_teacher_students(
    current_user: CurrentUser,
    session: Session = Depends(get_session),
):
    """Get list of students enrolled in teacher's courses with quiz stats."""
    require_teacher_or_admin(current_user)
    
    # Get teacher's courses
    if current_user.role == "admin":
        courses = session.exec(select(Course)).all()
    else:
        courses = session.exec(select(Course).where(Course.teacher_id == current_user.id)).all()
    
    course_ids = [c.id for c in courses]
    course_map = {c.id: c.title for c in courses}
    
    if not course_ids:
        return TeacherStudentsResponse(students=[], total=0)
    
    # Get all lessons in teacher's courses
    lessons = session.exec(select(Lesson).where(Lesson.course_id.in_(course_ids))).all()
    lesson_ids = [l.id for l in lessons]
    
    # Get all quizzes for these lessons
    quizzes = session.exec(select(Quiz).where(Quiz.lesson_id.in_(lesson_ids))).all() if lesson_ids else []
    quiz_ids = [q.id for q in quizzes]
    
    # Get enrollments with student info
    enrollments = session.exec(
        select(Enrollment).where(Enrollment.course_id.in_(course_ids))
    ).all()
    
    students = []
    for enrollment in enrollments:
        student = session.get(User, enrollment.student_id)
        if not student:
            continue
        
        # Get quiz stats for this student (across all teacher's quizzes)
        quiz_stats = None
        if quiz_ids:
            attempts = session.exec(
                select(QuizAttempt).where(
                    QuizAttempt.student_id == student.id,
                    QuizAttempt.quiz_id.in_(quiz_ids)
                )
            ).all()
            
            if attempts:
                scores = [a.score for a in attempts]
                passed = [a for a in attempts if a.passed]
                quiz_stats = StudentQuizStats(
                    attempts_count=len(attempts),
                    passed_count=len(passed),
                    best_score=max(scores) if scores else None,
                    avg_score=round(sum(scores) / len(scores), 1) if scores else None,
                )
        
        students.append(StudentWithProgress(
            id=student.id,
            email=student.email,
            first_name=student.first_name,
            last_name=student.last_name,
            course_id=enrollment.course_id,
            course_title=course_map.get(enrollment.course_id, ""),
            progress=enrollment.progress,
            enrolled_at=enrollment.created_at.isoformat(),
            quiz_stats=quiz_stats,
        ))
    
    return TeacherStudentsResponse(
        students=students,
        total=len(students)
    )
