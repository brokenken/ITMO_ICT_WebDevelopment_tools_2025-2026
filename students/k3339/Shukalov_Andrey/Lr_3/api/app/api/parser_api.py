import os

import httpx
from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl

from app.celery_app import celery_app
from app.tasks import parse_url_task


router = APIRouter(
    prefix="/parser",
    tags=["parser"],
)

PARSER_URL = os.getenv(
    "PARSER_URL",
    "http://parser:8001",
)


class ParseRequest(BaseModel):
    url: HttpUrl


@router.post("/direct")
async def parse_direct(request: ParseRequest):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{PARSER_URL}/parse",
                json={"url": str(request.url)},
            )

            response.raise_for_status()

        return response.json()

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Parser returned error: {exc.response.text}",
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Parser service is unavailable: {exc}",
        ) from exc


@router.post(
    "/async",
    status_code=status.HTTP_202_ACCEPTED,
)
def parse_async(request: ParseRequest):
    task = parse_url_task.delay(str(request.url))

    return {
        "task_id": task.id,
        "status": "queued",
    }


@router.get("/tasks/{task_id}")
def task_status(task_id: str):
    task = AsyncResult(
        task_id,
        app=celery_app,
    )

    response = {
        "task_id": task_id,
        "status": task.status,
    }

    if task.successful():
        response["result"] = task.result

    elif task.failed():
        response["error"] = str(task.result)

    return response