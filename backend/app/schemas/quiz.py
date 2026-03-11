from datetime import datetime

from pydantic import BaseModel


# --- Answer ---

class AnswerCreate(BaseModel):
    text_ru: str
    text_kz: str = ""
    is_correct: bool = False
    order: int = 0


class AnswerUpdate(BaseModel):
    text_ru: str | None = None
    text_kz: str | None = None
    is_correct: bool | None = None
    order: int | None = None


class AnswerResponse(BaseModel):
    id: int
    question_id: int
    text_ru: str
    text_kz: str
    is_correct: bool
    order: int

    class Config:
        from_attributes = True


class AnswerResponseStudent(BaseModel):
    """Answer without is_correct for students taking quiz."""
    id: int
    question_id: int
    text_ru: str
    text_kz: str
    order: int

    class Config:
        from_attributes = True


# --- Question ---

class QuestionCreate(BaseModel):
    text_ru: str
    text_kz: str = ""
    order: int = 0
    answers: list[AnswerCreate] = []


class QuestionUpdate(BaseModel):
    text_ru: str | None = None
    text_kz: str | None = None
    order: int | None = None


class QuestionResponse(BaseModel):
    id: int
    quiz_id: int
    text_ru: str
    text_kz: str
    order: int
    answers: list[AnswerResponse] = []

    class Config:
        from_attributes = True


class QuestionResponseStudent(BaseModel):
    """Question with answers without is_correct."""
    id: int
    quiz_id: int
    text_ru: str
    text_kz: str
    order: int
    answers: list[AnswerResponseStudent] = []

    class Config:
        from_attributes = True


# --- Quiz ---

class QuizCreate(BaseModel):
    title: str = ""
    passing_score: int = 70


class QuizUpdate(BaseModel):
    title: str | None = None
    passing_score: int | None = None


class QuizResponse(BaseModel):
    id: int
    lesson_id: int
    title: str
    passing_score: int
    created_at: datetime
    questions: list[QuestionResponse] = []

    class Config:
        from_attributes = True


class QuizResponseStudent(BaseModel):
    """Quiz response for students without correct answers."""
    id: int
    lesson_id: int
    title: str
    passing_score: int
    questions: list[QuestionResponseStudent] = []

    class Config:
        from_attributes = True


# --- Quiz Attempt ---

class QuizSubmit(BaseModel):
    """Student's answers to submit."""
    answers: dict[int, int]  # question_id -> selected_answer_id


class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    student_id: int
    score: int
    passed: bool
    started_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True


class QuizResultResponse(BaseModel):
    """Result after submitting quiz."""
    attempt_id: int
    score: int
    passed: bool
    total_questions: int
    correct_answers: int
