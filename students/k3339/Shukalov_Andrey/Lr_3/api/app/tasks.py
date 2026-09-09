import os

import httpx

from app.celery_app import celery_app


PARSER_URL = os.getenv(
    "PARSER_URL",
    "http://parser:8001",
)


@celery_app.task(name="parse_url")
def parse_url_task(url: str):
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            f"{PARSER_URL}/parse",
            json={"url": url},
        )

        response.raise_for_status()

        return response.json()