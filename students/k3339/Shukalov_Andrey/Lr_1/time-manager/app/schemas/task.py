from datetime import datetime
from typing import ClassVar

from pydantic import AwareDatetime, Field

from app.models.task import Priority, TaskStatus
from app.schemas.common import Description, PatchSchema, Schema, Title
from app.schemas.project import ProjectRead
from app.schemas.tag import TaskTagRead
from app.schemas.time_entry import TimeEntryRead


class TaskCreate(Schema):
    title: Title
    description: Description = ""
    project_id: int | None = Field(default=None, gt=0)
    deadline: AwareDatetime | None = None
    priority: Priority = Priority.medium
    status: TaskStatus = TaskStatus.todo


class TaskPatch(PatchSchema):
    nullable_fields: ClassVar[set[str]] = {"project_id", "deadline"}
    title: Title | None = None
    description: Description | None = None
    project_id: int | None = Field(default=None, gt=0)
    deadline: AwareDatetime | None = None
    priority: Priority | None = None
    status: TaskStatus | None = None


class TaskRead(TaskCreate):
    id: int
    owner_id: int
    created_at: datetime


class TaskDetail(TaskRead):
    project: ProjectRead | None
    tag_links: list[TaskTagRead]
    time_entries: list[TimeEntryRead]
    total_seconds: float


class ProjectDetail(ProjectRead):
    tasks: list[TaskRead]


class TaskTimeSummary(Schema):
    task_id: int
    title: str
    total_seconds: float


class TimeSummary(Schema):
    total_seconds: float
    tasks: list[TaskTimeSummary]
