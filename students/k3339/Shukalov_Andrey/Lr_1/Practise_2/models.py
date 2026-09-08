from enum import Enum

from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel


SQLModel.metadata.naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class RaceType(str, Enum):
    director = "director"
    worker = "worker"
    junior = "junior"


class SkillWarriorLink(SQLModel, table=True):
    __tablename__ = "skillwarriorlink"

    skill_id: int = Field(foreign_key="skill.id", primary_key=True, ondelete="CASCADE")
    warrior_id: int = Field(foreign_key="warrior.id", primary_key=True, ondelete="CASCADE")


class ProfessionBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""


class Profession(ProfessionBase, table=True):
    __tablename__ = "profession"

    id: int | None = Field(default=None, primary_key=True)
    warriors: list["Warrior"] = Relationship(
        back_populates="profession", passive_deletes="all"
    )


class SkillBase(SQLModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = ""


class Skill(SkillBase, table=True):
    __tablename__ = "skill"

    id: int | None = Field(default=None, primary_key=True)
    warriors: list["Warrior"] = Relationship(
        back_populates="skills",
        link_model=SkillWarriorLink,
        passive_deletes=True,
    )


class WarriorBase(SQLModel):
    race: RaceType
    name: str = Field(min_length=1, max_length=200)
    level: int = Field(ge=1)
    profession_id: int | None = Field(
        default=None, gt=0, foreign_key="profession.id", ondelete="SET NULL"
    )


class Warrior(WarriorBase, table=True):
    __tablename__ = "warrior"
    __table_args__ = (CheckConstraint("level >= 1", name="positive_level"),)

    id: int | None = Field(default=None, primary_key=True)
    profession: Profession | None = Relationship(back_populates="warriors")
    skills: list[Skill] = Relationship(
        back_populates="warriors",
        link_model=SkillWarriorLink,
        passive_deletes=True,
    )
