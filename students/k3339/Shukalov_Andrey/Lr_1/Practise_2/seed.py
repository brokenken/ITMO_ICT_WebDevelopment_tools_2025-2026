from sqlmodel import Session, select

from connection import engine
from models import Profession, RaceType, Skill, Warrior


def seed_database() -> bool:
    with Session(engine) as session:
        for model in (Profession, Skill, Warrior):
            if session.exec(select(model).limit(1)).first() is not None:
                print("База не пуста: демонстрационные данные не добавлены.")
                return False

        director = Profession(title="Влиятельный человек", description="Эксперт по всем вопросам")
        worker = Profession(title="Дельфист-гребец", description="Уважаемый сотрудник")
        trade = Skill(name="Купле-продажа компрессоров", description="")
        valuation = Skill(name="Оценка имущества", description="")
        first = Warrior(
            race=RaceType.director,
            name="Мартынов Дмитрий",
            level=12,
            profession=director,
            skills=[trade, valuation],
        )
        second = Warrior(
            race=RaceType.worker,
            name="Андрей Косякин",
            level=12,
            profession=worker,
        )
        session.add_all([first, second])
        session.commit()
        for record in (director, worker, trade, valuation, first, second):
            session.refresh(record)
        print("Созданы 2 профессии, 2 умения, 2 воина и 2 связи.")
        print(f"Воины: {first.id}, {second.id}; профессии: {director.id}, {worker.id}; умения: {trade.id}, {valuation.id}")
        return True


if __name__ == "__main__":
    seed_database()
