import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, make_url
from sqlmodel import Session, create_engine


load_dotenv(Path(__file__).with_name(".env"))


def get_database_url() -> URL:
    if os.getenv("DATABASE_URL"):
        return make_url(os.environ["DATABASE_URL"])
    return URL.create(
        "postgresql+psycopg2",
        username=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "warriors_db"),
    )


engine = create_engine(
    get_database_url(),
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
