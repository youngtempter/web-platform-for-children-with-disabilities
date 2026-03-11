from sqlmodel import Session, create_engine, SQLModel
from app.config import settings
from app.models.user import User  # noqa: F401
from app.models.course import Course  # noqa: F401
from app.models.lesson import Lesson  # noqa: F401
from app.models.enrollment import Enrollment  # noqa: F401 - needed for SQLModel to discover models

_connect_args = {}
if "sqlite" in settings.database_url:
    _connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args=_connect_args,
)


def create_db_and_tables():
    """Создать таблицы (для SQLite при первом запуске)."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency that yields a database session."""
    with Session(engine) as session:
        yield session
