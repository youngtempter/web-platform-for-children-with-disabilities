"""add quiz tables, lesson progress, video fields to lessons

Revision ID: 003
Revises: 002
Create Date: 2025-03-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to lessons table
    op.add_column("lessons", sa.Column("video_url", sa.String(), nullable=True))
    op.add_column("lessons", sa.Column("subtitle_url", sa.String(), nullable=True))
    op.add_column("lessons", sa.Column("has_sign_language", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("lessons", sa.Column("duration_seconds", sa.Integer(), nullable=True))
    op.add_column("lessons", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("lessons", sa.Column("updated_at", sa.DateTime(), nullable=True))

    # Create quizzes table
    op.create_table(
        "quizzes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False, server_default=""),
        sa.Column("passing_score", sa.Integer(), nullable=False, server_default="70"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("lesson_id", name="uq_quizzes_lesson_id"),
    )
    op.create_index(op.f("ix_quizzes_lesson_id"), "quizzes", ["lesson_id"], unique=True)

    # Create questions table
    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("quiz_id", sa.Integer(), nullable=False),
        sa.Column("text_ru", sa.String(), nullable=False),
        sa.Column("text_kz", sa.String(), nullable=False, server_default=""),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_questions_quiz_id"), "questions", ["quiz_id"], unique=False)

    # Create answers table
    op.create_table(
        "answers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("text_ru", sa.String(), nullable=False),
        sa.Column("text_kz", sa.String(), nullable=False, server_default=""),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_answers_question_id"), "answers", ["question_id"], unique=False)

    # Create quiz_attempts table
    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("quiz_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("passed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_quiz_attempts_quiz_id"), "quiz_attempts", ["quiz_id"], unique=False)
    op.create_index(op.f("ix_quiz_attempts_student_id"), "quiz_attempts", ["student_id"], unique=False)

    # Create lesson_progress table
    op.create_table(
        "lesson_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("watch_time_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_lesson_progress_student_id"), "lesson_progress", ["student_id"], unique=False)
    op.create_index(op.f("ix_lesson_progress_lesson_id"), "lesson_progress", ["lesson_id"], unique=False)
    op.create_unique_constraint(
        "uq_lesson_progress_student_lesson",
        "lesson_progress",
        ["student_id", "lesson_id"],
    )


def downgrade() -> None:
    # Drop lesson_progress
    op.drop_constraint("uq_lesson_progress_student_lesson", "lesson_progress", type_="unique")
    op.drop_index(op.f("ix_lesson_progress_lesson_id"), table_name="lesson_progress")
    op.drop_index(op.f("ix_lesson_progress_student_id"), table_name="lesson_progress")
    op.drop_table("lesson_progress")

    # Drop quiz_attempts
    op.drop_index(op.f("ix_quiz_attempts_student_id"), table_name="quiz_attempts")
    op.drop_index(op.f("ix_quiz_attempts_quiz_id"), table_name="quiz_attempts")
    op.drop_table("quiz_attempts")

    # Drop answers
    op.drop_index(op.f("ix_answers_question_id"), table_name="answers")
    op.drop_table("answers")

    # Drop questions
    op.drop_index(op.f("ix_questions_quiz_id"), table_name="questions")
    op.drop_table("questions")

    # Drop quizzes
    op.drop_index(op.f("ix_quizzes_lesson_id"), table_name="quizzes")
    op.drop_table("quizzes")

    # Remove columns from lessons
    op.drop_column("lessons", "updated_at")
    op.drop_column("lessons", "created_at")
    op.drop_column("lessons", "duration_seconds")
    op.drop_column("lessons", "has_sign_language")
    op.drop_column("lessons", "subtitle_url")
    op.drop_column("lessons", "video_url")
