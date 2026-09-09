from pydantic import AwareDatetime, Field, model_validator

from app.schemas.common import Description, PatchSchema, Schema


class TimeEntryCreate(Schema):
    task_id: int = Field(gt=0)
    started_at: AwareDatetime
    ended_at: AwareDatetime
    note: Description = ""

    @model_validator(mode="after")
    def valid_interval(self) -> "TimeEntryCreate":
        if self.ended_at <= self.started_at:
            raise ValueError("ended_at must be after started_at")
        return self


class TimeEntryPatch(PatchSchema):
    started_at: AwareDatetime | None = None
    ended_at: AwareDatetime | None = None
    note: Description | None = None


class TimeEntryRead(TimeEntryCreate):
    id: int
    duration_seconds: float
