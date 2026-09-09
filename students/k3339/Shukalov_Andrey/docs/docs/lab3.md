# Лабораторная работа №3

## Цель

Упаковать FastAPI-приложение, PostgreSQL и парсер в Docker, реализовать
прямой HTTP-вызов парсера из основного API и асинхронный вызов через очередь
Celery + Redis.

**Исходный код:** [ветка `lab3`](https://github.com/brokenken/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab3/students/k3339/Shukalov_Andrey/Lr_3)

Выполнены подзадачи **1, 2 и 3**
## Архитектура

```text
                         ┌─────────────────┐
Клиент ─────────────────▶│ FastAPI :8000   │
                         └───────┬─────────┘
                                 │
                    ┌────────────┴─────────────┐
                    │                          │
              direct HTTP                 async task
                    │                          │
                    ▼                          ▼
             ┌─────────────┐             ┌─────────┐
             │ Parser :8001│             │  Redis  │
             └──────┬──────┘             └────┬────┘
                    │                          │
                    │                          ▼
                    │                  ┌──────────────┐
                    │                  │Celery worker │
                    │                  └──────┬───────┘
                    │                         │ HTTP
                    │                         ▼
                    │                  ┌─────────────┐
                    └─────────────────▶│ Parser :8001│
                                       └──────┬──────┘
                                              │
                                              ▼
                                        PostgreSQL
```

## Docker Compose

Compose запускает пять сервисов:

| Сервис | Назначение | Внутренний адрес |
|---|---|---|
| `db` | PostgreSQL 17 | `db:5432` |
| `redis` | брокер и backend Celery | `redis:6379` |
| `parser` | отдельный HTTP-сервис парсера | `parser:8001` |
| `api` | основное FastAPI-приложение | `api:8000` |
| `celery_worker` | обработчик фоновых задач | — |

С хоста доступны:

- API: `http://localhost:8000`;
- Parser API: `http://localhost:8001`;
- PostgreSQL: `localhost:5434`;
- Redis: `localhost:6379`.

Внутри Docker-сети сервисы обращаются друг к другу по именам сервисов,
а не через `localhost`.

## Подзадача 1. Контейнеризация

### API Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY migrations ./migrations
COPY alembic.ini .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Parser Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common ./common
COPY parsers ./parsers
COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Parser API

Парсер ЛР2 обёрнут отдельным FastAPI-приложением.

| Метод | Endpoint | Назначение |
|---|---|---|
| GET | `/health` | Проверка доступности сервиса |
| POST | `/parse` | Выполнить `parse_and_save(url)` |

Пример запроса:

```json
{
  "url": "https://example.com/"
}
```

Пример ответа:

```json
{
  "message": "Parsing completed",
  "url": "https://example.com/",
  "title": "Example Domain",
  "approach": "threading"
}
```

## Подзадача 2. Прямой вызов из FastAPI

Основное приложение содержит:

```text
POST /parser/direct
```

Endpoint принимает URL клиента и через `httpx.AsyncClient` отправляет запрос
на `http://parser:8001/parse`, то есть в **отдельный контейнер**.

Последовательность:

```text
Client
  -> POST /parser/direct
  -> main FastAPI
  -> HTTP POST http://parser:8001/parse
  -> parser service
  -> PostgreSQL
  -> result to client
```

## Подзадача 3. Celery + Redis

Celery настроен с Redis:

```python
celery_app = Celery(
    "time_manager",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
    include=["app.tasks"],
)
```

Фоновая задача:

```python
@celery_app.task(name="parse_url")
def parse_url_task(url: str):
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            f"{PARSER_URL}/parse",
            json={"url": url},
        )
        response.raise_for_status()
        return response.json()
```

### Endpoint постановки задачи

```text
POST /parser/async
```

FastAPI выполняет:

```python
task = parse_url_task.delay(str(request.url))
```

и сразу возвращает:

```json
{
  "task_id": "...",
  "status": "queued"
}
```

Клиенту не нужно ждать HTTP-загрузки и парсинга страницы.

### Получение результата

Дополнительно реализован:

```text
GET /parser/tasks/{task_id}
```

Он возвращает состояние Celery (`PENDING`, `STARTED`, `SUCCESS`, `FAILURE`)
и, после завершения, результат.

Этот endpoint не обязателен в минимальном условии, но делает асинхронную
схему удобной для проверки.

## Запуск

```powershell
cd students\k3339\Shukalov_Andrey\Lr_3
docker compose up --build
```

Проверить контейнеры:

```powershell
docker compose ps
```

## Проверка

### 1. Parser service

Открыть:

```text
http://localhost:8001/docs
```

Проверить `GET /health`, затем `POST /parse`.

### 2. Прямой вызов

Открыть:

```text
http://localhost:8000/docs
```

Выполнить:

```text
POST /parser/direct
```

с телом:

```json
{
  "url": "https://www.python.org/"
}
```

### 3. Очередь

Выполнить:

```text
POST /parser/async
```

скопировать `task_id`, затем:

```text
GET /parser/tasks/{task_id}
```

Итоговое состояние должно стать `SUCCESS`.

### 4. Логи worker

```powershell
docker compose logs celery_worker
```

В логах должны быть сообщения о получении и успешном завершении `parse_url`.

### 5. База данных

```powershell
docker compose exec db psql -U postgres -d time_manager
```

```sql
SELECT *
FROM parsed_pages
ORDER BY parsed_at DESC;
```

