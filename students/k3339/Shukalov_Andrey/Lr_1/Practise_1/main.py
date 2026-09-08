from fastapi import FastAPI, HTTPException

from models import Message, Profession, ProfessionCreated, Warrior, WarriorCreated

app = FastAPI()

temp_bd = [
    {
        "id": 1,
        "race": "director",
        "name": "Мартынов Дмитрий",
        "level": 12,
        "profession": {
            "id": 1,
            "title": "Влиятельный человек",
            "description": "Эксперт по всем вопросам"
        },
        "skills": [
            {
                "id": 1,
                "name": "Купле-продажа компрессоров",
                "description": ""
            },
            {
                "id": 2,
                "name": "Оценка имущества",
                "description": ""
            }
        ]
    },
    {
        "id": 2,
        "race": "worker",
        "name": "Андрей Косякин",
        "level": 12,
        "profession": {
            "id": 2,
            "title": "Дельфист-гребец",
            "description": "Уважаемый сотрудник"
        },
        "skills": []
    }
]

temp_professions = [
    {
        "id": 1,
        "title": "Влиятельный человек",
        "description": "Эксперт по всем вопросам"
    },
    {
        "id": 2,
        "title": "Дельфист-гребец",
        "description": "Уважаемый сотрудник"
    }
]


@app.get('/warriors_list', response_model=list[Warrior], tags=['Воины'])
def warriors_list() -> list[dict]:
    return temp_bd


@app.get('/warrior/{warrior_id}', response_model=Warrior, tags=['Воины'])
def warrior_get(warrior_id: int) -> dict:
    for warrior in temp_bd:
        if warrior['id'] == warrior_id:
            return warrior
    raise HTTPException(status_code=404, detail='Воин не найден')


@app.post('/warrior', response_model=WarriorCreated, status_code=201, tags=['Воины'])
def warrior_create(warrior: Warrior) -> WarriorCreated:
    for saved_warrior in temp_bd:
        if saved_warrior['id'] == warrior.id:
            raise HTTPException(status_code=409, detail='Воин с таким id уже существует')

    temp_bd.append(warrior.model_dump(mode='json'))
    return {'status': 201, 'data': warrior}


@app.put('/warrior/{warrior_id}', response_model=Warrior, tags=['Воины'])
def warrior_update(warrior_id: int, warrior: Warrior) -> Warrior:
    if warrior.id != warrior_id:
        raise HTTPException(status_code=400, detail='id в пути и теле должны совпадать')

    for i, saved_warrior in enumerate(temp_bd):
        if saved_warrior['id'] == warrior_id:
            temp_bd[i] = warrior.model_dump(mode='json')
            return warrior
    raise HTTPException(status_code=404, detail='Воин не найден')


@app.delete('/warrior/{warrior_id}', response_model=Message, tags=['Воины'])
def warrior_delete(warrior_id: int) -> Message:
    for i, warrior in enumerate(temp_bd):
        if warrior['id'] == warrior_id:
            temp_bd.pop(i)
            return {'message': 'Воин удалён'}
    raise HTTPException(status_code=404, detail='Воин не найден')



@app.get('/professions_list', response_model=list[Profession], tags=['Профессии'])
def professions_list() -> list[dict]:
    return temp_professions


@app.get('/profession/{profession_id}', response_model=Profession, tags=['Профессии'])
def profession_get(profession_id: int) -> dict:
    for profession in temp_professions:
        if profession['id'] == profession_id:
            return profession
    raise HTTPException(status_code=404, detail='Профессия не найдена')


@app.post('/profession', response_model=ProfessionCreated, status_code=201, tags=['Профессии'])
def profession_create(profession: Profession) -> ProfessionCreated:
    for saved_profession in temp_professions:
        if saved_profession['id'] == profession.id:
            raise HTTPException(status_code=409, detail='Профессия с таким id уже существует')

    temp_professions.append(profession.model_dump(mode='json'))
    return {'status': 201, 'data': profession}


@app.put('/profession/{profession_id}', response_model=Profession, tags=['Профессии'])
def profession_update(profession_id: int, profession: Profession) -> Profession:
    if profession.id != profession_id:
        raise HTTPException(status_code=400, detail='id в пути и теле должны совпадать')

    for i, saved_profession in enumerate(temp_professions):
        if saved_profession['id'] == profession_id:
            temp_professions[i] = profession.model_dump(mode='json')
            return profession
    raise HTTPException(status_code=404, detail='Профессия не найдена')


@app.delete('/profession/{profession_id}', response_model=Message, tags=['Профессии'])
def profession_delete(profession_id: int) -> Message:
    for i, profession in enumerate(temp_professions):
        if profession['id'] == profession_id:
            temp_professions.pop(i)
            return {'message': 'Профессия удалена'}
    raise HTTPException(status_code=404, detail='Профессия не найдена')
