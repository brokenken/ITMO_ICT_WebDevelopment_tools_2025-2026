from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from psycopg import Error as PsycopgError
from requests import RequestException

from parsers.threading_parser import parse_and_save


app = FastAPI(
    title="Parser Service",
    version="1.0.0",
    description="HTTP for lab2",
)


class ParseRequest(BaseModel):
    url: HttpUrl


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/parse")
def parse(request: ParseRequest):
    try:
        result = parse_and_save(str(request.url))

        return {
            "message": "Parsing completed",
            "url": result.url,
            "title": result.title,
            "approach": result.approach,
        }

    except RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not download page: {exc}",
        ) from exc

    except PsycopgError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {exc}",
        ) from exc