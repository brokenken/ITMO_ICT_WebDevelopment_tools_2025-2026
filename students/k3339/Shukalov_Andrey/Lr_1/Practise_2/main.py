from typing import Annotated, TypeVar

from fastapi import Depends, FastAPI, HTTPException, Path, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import SQLModel, Session, select

from connection import get_session
from models import Profession, Skill, SkillWarriorLink, Warrior
from schemas import (
    DeleteResult,
    LinkCreate,
    LinkRead,
    ProfessionCreate,
    ProfessionCreated,
    ProfessionRead,
    ProfessionUpdate,
    SkillCreate,
    SkillCreated,
    SkillRead,
    SkillUpdate,
    WarriorCreate,
    WarriorCreated,
    WarriorRead,
    WarriorUpdate,
)


app = FastAPI(title="Практика 1.2 — Воины, профессии и умения", version="1.2.0")
SessionDep = Annotated[Session, Depends(get_session)]
PositiveId = Annotated[int, Path(gt=0)]
TableModel = TypeVar("TableModel", bound=SQLModel)


def get_or_404(
    session: Session, model: type[TableModel], object_id: int, message: str
) -> TableModel:
    record = session.get(model, object_id)
    if record is None:
        raise HTTPException(status_code=404, detail=message)
    return record


def commit_changes(session: Session) -> None:
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Конфликт данных",
        ) from None


def read_warrior(session: Session, warrior_id: int) -> Warrior:
    statement = (
        select(Warrior)
        .where(Warrior.id == warrior_id)
        .options(selectinload(Warrior.profession), selectinload(Warrior.skills))
    )
    warrior = session.exec(statement).first()
    if warrior is None:
        raise HTTPException(status_code=404, detail="Воин не найден")
    return warrior


@app.get("/", response_model=str, tags=["Главная"])
def hello() -> str:
    return "Hello, Andrey!"


@app.get("/warriors_list", response_model=list[WarriorRead], tags=["Воины"])
def warriors_list(session: SessionDep) -> list[Warrior]:
    statement = select(Warrior).order_by(Warrior.id).options(
        selectinload(Warrior.profession), selectinload(Warrior.skills)
    )
    return list(session.exec(statement).all())


@app.get("/warrior/{warrior_id}", response_model=WarriorRead, tags=["Воины"])
def warrior_get(warrior_id: PositiveId, session: SessionDep) -> Warrior:
    return read_warrior(session, warrior_id)


@app.post("/warrior", response_model=WarriorCreated, status_code=201, tags=["Воины"])
def warrior_create(warrior: WarriorCreate, session: SessionDep) -> dict:
    if warrior.profession_id is not None:
        get_or_404(session, Profession, warrior.profession_id, "Профессия не найдена")
    db_warrior = Warrior.model_validate(warrior)
    session.add(db_warrior)
    commit_changes(session)
    session.refresh(db_warrior)
    return {"status": 201, "data": read_warrior(session, db_warrior.id)}


@app.patch("/warrior/{warrior_id}", response_model=WarriorRead, tags=["Воины"])
def warrior_update(
    warrior_id: PositiveId, warrior: WarriorUpdate, session: SessionDep
) -> Warrior:
    db_warrior = get_or_404(session, Warrior, warrior_id, "Воин не найден")
    changes = warrior.model_dump(exclude_unset=True)
    if changes.get("profession_id") is not None:
        get_or_404(session, Profession, changes["profession_id"], "Профессия не найдена")
    db_warrior.sqlmodel_update(changes)
    session.add(db_warrior)
    commit_changes(session)
    session.refresh(db_warrior)
    return read_warrior(session, warrior_id)


@app.delete("/warrior/{warrior_id}", response_model=DeleteResult, tags=["Воины"])
def warrior_delete(warrior_id: PositiveId, session: SessionDep) -> dict:
    warrior = get_or_404(session, Warrior, warrior_id, "Воин не найден")
    session.delete(warrior)
    commit_changes(session)
    return {"ok": True}


@app.get("/professions_list", response_model=list[ProfessionRead], tags=["Профессии"])
def professions_list(session: SessionDep) -> list[Profession]:
    return list(session.exec(select(Profession).order_by(Profession.id)).all())


@app.get("/profession/{profession_id}", response_model=ProfessionRead, tags=["Профессии"])
def profession_get(profession_id: PositiveId, session: SessionDep) -> Profession:
    return get_or_404(session, Profession, profession_id, "Профессия не найдена")


@app.post("/profession", response_model=ProfessionCreated, status_code=201, tags=["Профессии"])
def profession_create(profession: ProfessionCreate, session: SessionDep) -> dict:
    db_profession = Profession.model_validate(profession)
    session.add(db_profession)
    commit_changes(session)
    session.refresh(db_profession)
    return {"status": 201, "data": db_profession}


@app.patch("/profession/{profession_id}", response_model=ProfessionRead, tags=["Профессии"])
def profession_update(
    profession_id: PositiveId, profession: ProfessionUpdate, session: SessionDep
) -> Profession:
    db_profession = get_or_404(session, Profession, profession_id, "Профессия не найдена")
    db_profession.sqlmodel_update(profession.model_dump(exclude_unset=True))
    session.add(db_profession)
    commit_changes(session)
    session.refresh(db_profession)
    return db_profession


@app.delete("/profession/{profession_id}", response_model=DeleteResult, tags=["Профессии"])
def profession_delete(profession_id: PositiveId, session: SessionDep) -> dict:
    profession = get_or_404(session, Profession, profession_id, "Профессия не найдена")
    session.delete(profession)
    commit_changes(session)
    return {"ok": True}


@app.get("/skills_list", response_model=list[SkillRead], tags=["Умения"])
def skills_list(session: SessionDep) -> list[Skill]:
    return list(session.exec(select(Skill).order_by(Skill.id)).all())


@app.get("/skill/{skill_id}", response_model=SkillRead, tags=["Умения"])
def skill_get(skill_id: PositiveId, session: SessionDep) -> Skill:
    return get_or_404(session, Skill, skill_id, "Умение не найдено")


@app.post("/skill", response_model=SkillCreated, status_code=201, tags=["Умения"])
def skill_create(skill: SkillCreate, session: SessionDep) -> dict:
    db_skill = Skill.model_validate(skill)
    session.add(db_skill)
    commit_changes(session)
    session.refresh(db_skill)
    return {"status": 201, "data": db_skill}


@app.patch("/skill/{skill_id}", response_model=SkillRead, tags=["Умения"])
def skill_update(skill_id: PositiveId, skill: SkillUpdate, session: SessionDep) -> Skill:
    db_skill = get_or_404(session, Skill, skill_id, "Умение не найдено")
    db_skill.sqlmodel_update(skill.model_dump(exclude_unset=True))
    session.add(db_skill)
    commit_changes(session)
    session.refresh(db_skill)
    return db_skill


@app.delete("/skill/{skill_id}", response_model=DeleteResult, tags=["Умения"])
def skill_delete(skill_id: PositiveId, session: SessionDep) -> dict:
    skill = get_or_404(session, Skill, skill_id, "Умение не найдено")
    session.delete(skill)
    commit_changes(session)
    return {"ok": True}


@app.get("/warrior-skills", response_model=list[LinkRead], tags=["Связи воинов и умений"])
def warrior_skills_list(
    session: SessionDep, warrior_id: Annotated[int | None, Query(gt=0)] = None
) -> list[SkillWarriorLink]:
    statement = select(SkillWarriorLink).order_by(
        SkillWarriorLink.warrior_id, SkillWarriorLink.skill_id
    )
    if warrior_id is not None:
        statement = statement.where(SkillWarriorLink.warrior_id == warrior_id)
    return list(session.exec(statement).all())


@app.get(
    "/warrior-skill/{warrior_id}/{skill_id}",
    response_model=LinkRead,
    tags=["Связи воинов и умений"],
)
def warrior_skill_get(
    warrior_id: PositiveId, skill_id: PositiveId, session: SessionDep
) -> SkillWarriorLink:
    link = session.get(SkillWarriorLink, {"warrior_id": warrior_id, "skill_id": skill_id})
    if link is None:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    return link


@app.post(
    "/warrior-skill", response_model=LinkRead, status_code=201, tags=["Связи воинов и умений"]
)
def warrior_skill_create(link: LinkCreate, session: SessionDep) -> SkillWarriorLink:
    get_or_404(session, Warrior, link.warrior_id, "Воин не найден")
    get_or_404(session, Skill, link.skill_id, "Умение не найдено")
    if session.get(SkillWarriorLink, link.model_dump()) is not None:
        raise HTTPException(status_code=409, detail="Это умение уже назначено воину")
    db_link = SkillWarriorLink.model_validate(link)
    session.add(db_link)
    commit_changes(session)
    session.refresh(db_link)
    return db_link


@app.delete(
    "/warrior-skill/{warrior_id}/{skill_id}",
    response_model=DeleteResult,
    tags=["Связи воинов и умений"],
)
def warrior_skill_delete(
    warrior_id: PositiveId, skill_id: PositiveId, session: SessionDep
) -> dict:
    link = session.get(SkillWarriorLink, {"warrior_id": warrior_id, "skill_id": skill_id})
    if link is None:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    session.delete(link)
    commit_changes(session)
    return {"ok": True}
