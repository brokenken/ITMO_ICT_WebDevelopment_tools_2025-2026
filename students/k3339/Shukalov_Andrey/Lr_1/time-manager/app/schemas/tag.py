from typing import Annotated

from pydantic import Field, StringConstraints

from app.schemas.common import PatchSchema, Schema

TagName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
Color = Annotated[str, StringConstraints(pattern=r"^#[0-9A-Fa-f]{6}$")]


class TagCreate(Schema):
    name: TagName
    color: Color = "#64748B"


class TagPatch(PatchSchema):
    name: TagName | None = None
    color: Color | None = None


class TagRead(TagCreate):
    id: int
    owner_id: int


class TaskTagCreate(Schema):
    tag_id: int = Field(gt=0)
    relevance: int = Field(default=3, ge=1, le=5)


class TaskTagPatch(Schema):
    relevance: int = Field(ge=1, le=5)


class TaskTagRead(Schema):
    task_id: int
    tag_id: int
    relevance: int
    tag: TagRead
