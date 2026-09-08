from app.models import Task
from app.schemas.project import ProjectRead
from app.schemas.tag import TaskTagRead
from app.schemas.task import TaskDetail, TaskRead
from app.schemas.time_entry import TimeEntryRead


def task_detail(item: Task) -> TaskDetail:
    return TaskDetail(
        **TaskRead.model_validate(item).model_dump(),
        project=ProjectRead.model_validate(item.project) if item.project else None,
        tag_links=[TaskTagRead.model_validate(link) for link in item.tag_links],
        time_entries=[TimeEntryRead.model_validate(entry) for entry in item.time_entries],
        total_seconds=sum(entry.duration_seconds for entry in item.time_entries),
    )
