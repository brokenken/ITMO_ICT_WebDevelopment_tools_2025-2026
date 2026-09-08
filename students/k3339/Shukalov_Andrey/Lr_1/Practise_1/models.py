from enum import Enum

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class RaceType(str, Enum):
    director = 'director'
    worker = 'worker'
    junior = 'junior'


class Profession(BaseModel):
    id: int = Field(gt=0)
    title: str = Field(min_length=1)
    description: str


class Skill(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=1)
    description: str


class Warrior(BaseModel):
    id: int = Field(gt=0)
    race: RaceType
    name: str = Field(min_length=1)
    level: int = Field(ge=1)
    profession: Profession
    skills: list[Skill] | None = Field(default_factory=list)


class WarriorCreated(TypedDict):
    status: int
    data: Warrior


class Message(TypedDict):
    message: str



class ProfessionCreated(TypedDict):
    status: int
    data: Profession
