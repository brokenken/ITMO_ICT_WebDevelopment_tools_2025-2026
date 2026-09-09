import os
from dataclasses import dataclass

import asyncpg
import psycopg
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

DEFAULT_URLS = [
    "https://example.com/",
    "https://www.python.org/",
    "https://docs.python.org/3/",
    "https://www.postgresql.org/",
    "https://www.djangoproject.com/",
    "https://fastapi.tiangolo.com/",
    "https://aiohttp.readthedocs.io/en/stable/",
    "https://pypi.org/",
]


@dataclass(frozen=True)
class ParseResult:
    url: str
    title: str
    approach: str


def extract_title(html: str | bytes) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title is None:
        return "No title"
    return soup.title.get_text(" ", strip=True) or "No title"


def db_config() -> dict[str, str | int]:
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5434")),
        "dbname": os.getenv("DB_NAME", "lr2_db"),
        "user": os.getenv("DB_USER", "lr2"),
        "password": os.getenv("DB_PASSWORD", "lr2"),
    }


def save_result(result: ParseResult) -> None:
    """Save a result using a separate connection, safe for threads/processes."""
    with psycopg.connect(**db_config()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO parsed_pages (url, title, approach)
                VALUES (%s, %s, %s)
                """,
                (result.url, result.title, result.approach),
            )


async def create_pool() -> asyncpg.Pool:
    config = db_config()
    return await asyncpg.create_pool(
        host=str(config["host"]),
        port=int(config["port"]),
        database=str(config["dbname"]),
        user=str(config["user"]),
        password=str(config["password"]),
        min_size=1,
        max_size=8,
    )


async def save_result_async(pool: asyncpg.Pool, result: ParseResult) -> None:
    async with pool.acquire() as connection:
        await connection.execute(
            """
            INSERT INTO parsed_pages (url, title, approach)
            VALUES ($1, $2, $3)
            """,
            result.url,
            result.title,
            result.approach,
        )
