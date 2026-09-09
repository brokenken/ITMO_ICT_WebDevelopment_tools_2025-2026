from fastapi import FastAPI

from app.api import (
    auth,
    parser_api,
    projects,
    reports,
    tags,
    task_tags,
    tasks,
    time_entries,
    users,
)


app = FastAPI(
    title="Time Manager API",
    version="1.0.0",
    description=("Main API"),
)


for module in (
    auth,
    users,
    projects,
    tasks,
    tags,
    task_tags,
    time_entries,
    reports,
    parser_api,
):
    app.include_router(module.router)