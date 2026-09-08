from fastapi import FastAPI

from app.api import auth, projects, reports, tags, task_tags, tasks, time_entries, users

app = FastAPI(
    title="Time Manager API",
    version="1.0.0",
    description="Лабораторная: задачи, проекты, теги и учёт затраченного времени. Вход через JWT.",
)
for module in (auth, users, projects, tasks, tags, task_tags, time_entries, reports):
    app.include_router(module.router)
