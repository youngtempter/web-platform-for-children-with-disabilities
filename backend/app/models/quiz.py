from datetime import datetime

from sqlmodel import Field, SQLModel


class Quiz(SQLModel, table=True):
    """Quiz attached to a lesson. One lesson can have one quiz."""

    __tablename__ = "quizzes"

    id: int | None = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lessons.id", unique=True)
    title: str = Field(default="")
    passing_score: int = Field(default=70)  # percentage to pass
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Question(SQLModel, table=True):
    """Question in a quiz."""

    __tablename__ = "questions"

    id: int | None = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="quizzes.id")
    text_ru: str = Field()
    text_kz: str = Field(default="")
    order: int = Field(default=0)


class Answer(SQLModel, table=True):
    """Answer option for a question."""

    __tablename__ = "answers"

    id: int | None = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="questions.id")
    text_ru: str = Field()
    text_kz: str = Field(default="")
    is_correct: bool = Field(default=False)
    order: int = Field(default=0)


class QuizAttempt(SQLModel, table=True):
    """Student's attempt at a quiz."""

    __tablename__ = "quiz_attempts"

    id: int | None = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="quizzes.id")
    student_id: int = Field(foreign_key="users.id")
    score: int = Field(default=0)  # percentage
    passed: bool = Field(default=False)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = Field(default=None)
