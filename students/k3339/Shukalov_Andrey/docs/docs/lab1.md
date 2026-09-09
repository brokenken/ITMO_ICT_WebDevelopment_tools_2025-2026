# Лабораторная работа №1

## Цель

Реализовать полноценное серверное приложение на FastAPI с ORM, PostgreSQL,
CRUD-операциями, отношениями между моделями, миграциями Alembic и
пользовательской авторизацией через JWT.

В качестве варианта выбрана **программа-тайм-менеджер**. Приложение позволяет
создавать проекты и задачи, задавать задачам сроки и приоритеты, назначать теги
и учитывать затраченное время.

**Исходный код:** [ветка `lab1`](https://github.com/brokenken/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab1/students/k3339/Shukalov_Andrey/Lr_1)

## Выполнение практик 1-3

- [Практика 1.1](https://github.com/brokenken/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab1/students/k3339/Shukalov_Andrey/Lr_1/Practise_1) — базовое FastAPI-приложение, временные данные, Pydantic-модели и CRUD.
- [Практика 1.2](https://github.com/brokenken/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab1/students/k3339/Shukalov_Andrey/Lr_1/Practise_2) — подключение PostgreSQL, ORM и работа со связанными моделями.
- [Практика 1.3 — финальная версия `time-manager`](https://github.com/brokenken/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab1/students/k3339/Shukalov_Andrey/Lr_1/time-manager) — Alembic, миграции, ENV-конфигурация, структурирование проекта и дополнительное поле ассоциативной сущности.



## Модель данных

Финальная версия содержит шесть таблиц.

| Модель | Назначение | Основные связи |
|---|---|---|
| `User` | Пользователь системы | Владелец проектов, задач и тегов |
| `Project` | Проект | `Project -> Task`: one-to-many |
| `Task` | Задача | Принадлежит проекту; связана с тегами и записями времени |
| `Tag` | Тег | `Task <-> Tag`: many-to-many |
| `TaskTag` | Ассоциативная сущность задачи и тега | Поле связи `relevance` от 1 до 5 |
| `TimeEntry` | Интервал затраченного времени | `Task -> TimeEntry`: one-to-many |

### Пример моделей отношений

```python
class TaskTag(Base):
    __tablename__ = "task_tags"

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    )
    relevance: Mapped[int] = mapped_column(default=3)
```

У задачи присутствуют связи с проектом, тегами и интервалами времени:

```python
project: Mapped[Project | None] = relationship(back_populates="tasks")
tag_links: Mapped[list[TaskTag]] = relationship(...)
time_entries: Mapped[list[TimeEntry]] = relationship(...)
```

## Подключение к PostgreSQL

Подключение реализовано через SQLAlchemy:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def get_session():
    with SessionLocal() as session:
        yield session
```

Настройки загружаются с помощью `pydantic-settings` из переменных окружения:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    jwt_secret_key: str
    access_token_expire_minutes: int = 60
```

Пример локального `.env`

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/time_manager
JWT_SECRET_KEY=GENERATE_A_NEW_RANDOM_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Alembic

В проекте имеется каталог `migrations` и `alembic.ini`. В `migrations/env.py`
URL БД берётся из тех же настроек окружения, что и приложение:

```python
from app.core.config import get_settings
from app.models import Base

url = get_settings().database_url
target_metadata = Base.metadata
```

Применение миграций:

```powershell
alembic upgrade head
```

## Вложенные модели

Требование вложенного отображения отношений реализовано, в частности:

- `GET /projects/{item_id}` возвращает `ProjectDetail` со списком задач;
- `GET /tasks/{task_id}` возвращает `TaskDetail` с проектом, тегами,
  записями времени и суммарным временем.

```python
class TaskDetail(TaskRead):
    project: ProjectRead | None
    tag_links: list[TaskTagRead]
    time_entries: list[TimeEntryRead]
    total_seconds: float

class ProjectDetail(ProjectRead):
    tasks: list[TaskRead]
```

## Авторизация и пользователь

Авторизация реализована вручную на уровне приложения.

Пароль хэшируется через `pwdlib`, а JWT формируется через библиотеку JWT.
В токен записываются идентификатор пользователя, время выдачи, время истечения
и версия токена.

```python
def create_access_token(user: User) -> str:
    ...
    return jwt.encode(
        {
            "sub": str(user.id),
            "iat": now,
            "exp": now + timedelta(...),
            "ver": user.token_version,
        },
        settings.jwt_secret_key,
        algorithm="HS256",
    )
```

При смене пароля увеличивается `token_version`, поэтому ранее выданные токены
могут быть отозваны.

## Реализованные эндпоинты

### Authentication

| Метод | Endpoint | Назначение |
|---|---|---|
| POST | `/auth/register` | Регистрация пользователя |
| POST | `/auth/login` | Проверка логина/пароля и выдача JWT |

### Users

| Метод | Endpoint | Назначение |
|---|---|---|
| GET | `/users/me` | Текущий пользователь |
| PATCH | `/users/me` | Изменение профиля |
| POST | `/users/me/password` | Смена пароля и отзыв старых токенов |
| DELETE | `/users/me` | Удаление аккаунта |
| GET | `/users` | Список пользователей |
| GET | `/users/{user_id}` | Публичный профиль |

### Projects

| Метод | Endpoint | Назначение |
|---|---|---|
| POST | `/projects` | Создать проект |
| GET | `/projects` | Получить список проектов |
| GET | `/projects/{item_id}` | Получить проект со вложенными задачами |
| PATCH | `/projects/{item_id}` | Изменить проект |
| DELETE | `/projects/{item_id}` | Удалить проект |

### Tasks

| Метод | Endpoint | Назначение |
|---|---|---|
| POST | `/tasks` | Создать задачу |
| GET | `/tasks` | Список задач с фильтрами |
| GET | `/tasks/{task_id}` | Задача с проектом, тегами и временем |
| PATCH | `/tasks/{task_id}` | Изменить задачу |
| DELETE | `/tasks/{task_id}` | Удалить задачу |

`GET /tasks` поддерживает фильтры по статусу, приоритету, проекту, тегу,
просроченности и строке поиска.

### Tags

| Метод | Endpoint | Назначение |
|---|---|---|
| POST | `/tags` | Создать тег |
| GET | `/tags` | Список тегов |
| GET | `/tags/{item_id}` | Получить тег |
| PATCH | `/tags/{item_id}` | Изменить тег |
| DELETE | `/tags/{item_id}` | Удалить тег |

### Связь Task–Tag

| Метод | Endpoint | Назначение |
|---|---|---|
| POST | `/tasks/{task_id}/tags` | Добавить тег к задаче |
| GET | `/tasks/{task_id}/tags` | Список тегов задачи |
| GET | `/tasks/{task_id}/tags/{tag_id}` | Получить связь |
| PATCH | `/tasks/{task_id}/tags/{tag_id}` | Изменить `relevance` |
| DELETE | `/tasks/{task_id}/tags/{tag_id}` | Удалить связь |

### Time entries

| Метод | Endpoint | Назначение |
|---|---|---|
| POST | `/time-entries` | Создать интервал времени |
| GET | `/time-entries` | Получить интервалы |
| GET | `/time-entries/{entry_id}` | Получить интервал |
| PATCH | `/time-entries/{entry_id}` | Изменить интервал |
| DELETE | `/time-entries/{entry_id}` | Удалить интервал |

### Reports

| Метод | Endpoint | Назначение |
|---|---|---|
| GET | `/reports/time` | Итоговое время по задачам |

## Запуск

```powershell
cd students\k3339\Shukalov_Andrey\Lr_1\time-manager
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Результат

Финальное приложение удовлетворяет функциональным требованиям варианта
"Time Manager": задачи имеют описание, дедлайн, приоритет и статус, а
затраченное время хранится отдельными интервалами и агрегируется в отчёте.

Лабораторная соответствует требованиям задания, включая все три практики:
`Practise_1`, `Practise_2` и финальный `time-manager` как Практику 1.3.
