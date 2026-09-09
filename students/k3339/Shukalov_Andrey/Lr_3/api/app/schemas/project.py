from datetime import datetime

from app.schemas.common import Description, PatchSchema, Schema, Title


class ProjectCreate(Schema):
    title: Title
    description: Description = ""


class ProjectPatch(PatchSchema):
    title: Title | None = None
    description: Description | None = None


class ProjectRead(ProjectCreate):
    id: int
    owner_id: int
    created_at: datetime
