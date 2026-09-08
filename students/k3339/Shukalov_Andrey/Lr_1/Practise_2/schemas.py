from pydantic import ConfigDict, field_validator
from sqlmodel import Field, SQLModel

from models import ProfessionBase, RaceType, SkillBase, WarriorBase


class ProfessionCreate(ProfessionBase):
    model_config = ConfigDict(extra="forbid")


class ProfessionRead(ProfessionBase):
    id: int


class ProfessionUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None

    @field_validator("title", "description")
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise ValueError("Поле можно пропустить, но нельзя передать null")
        return value


class SkillCreate(SkillBase):
    model_config = ConfigDict(extra="forbid")


class SkillRead(SkillBase):
    id: int


class SkillUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None

    @field_validator("name", "description")
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise ValueError("Поле можно пропустить, но нельзя передать null")
        return value


class WarriorCreate(WarriorBase):
    model_config = ConfigDict(extra="forbid")


class WarriorUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")
    race: RaceType | None = None
    name: str | None = Field(default=None, min_length=1, max_length=200)
    level: int | None = Field(default=None, ge=1)
    profession_id: int | None = Field(default=None, gt=0)

    @field_validator("race", "name", "level")
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise ValueError("Поле можно пропустить, но нельзя передать null")
        return value


class WarriorRead(WarriorBase):
    id: int
    profession: ProfessionRead | None = None
    skills: list[SkillRead] = Field(default_factory=list)


class ProfessionCreated(SQLModel):
    status: int = 201
    data: ProfessionRead


class SkillCreated(SQLModel):
    status: int = 201
    data: SkillRead


class WarriorCreated(SQLModel):
    status: int = 201
    data: WarriorRead


class LinkCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")
    warrior_id: int = Field(gt=0)
    skill_id: int = Field(gt=0)


class LinkRead(LinkCreate):
    pass


class DeleteResult(SQLModel):
    ok: bool = True
