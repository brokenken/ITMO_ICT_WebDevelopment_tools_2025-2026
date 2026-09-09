# Лабораторная работа №2

## Цель

Исследовать различия между `threading`, `multiprocessing` и `asyncio` в Python
на двух задачах:

1. вычисление суммы чисел от 1 до `10^13`;
2. параллельный HTTP-парсинг нескольких страниц с сохранением результатов
   в PostgreSQL.

**Исходный код:** [ветка `lab2`](https://github.com/brokenken/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab2/students/k3339/Shukalov_Andrey/Lr_2)

## Задача 1. Вычисление суммы

Во всех трёх реализациях диапазон `1..10^13` делится на несколько максимально
равных диапазонов функцией `split_range()`.

```python
def split_range(limit: int, workers: int) -> list[tuple[int, int]]:
    workers = min(workers, limit)
    base_size, remainder = divmod(limit, workers)

    ranges = []
    start = 1

    for worker_index in range(workers):
        size = base_size + (1 if worker_index < remainder else 0)
        end = start + size - 1
        ranges.append((start, end))
        start = end + 1

    return ranges
```

Сумма каждого диапазона вычисляется арифметической формулой:

```python
def calculate_range_sum(bounds: tuple[int, int]) -> int:
    start, end = bounds
    count = end - start + 1
    return (start + end) * count // 2
```

Это позволяет выполнить требование для `10^13` за реалистичное время.

### Threading

Файл: `sums/threading_sum.py`.

Используется `ThreadPoolExecutor`. Каждый поток получает отдельный диапазон.

```python
def calculate_sum(limit=LIMIT, workers=4):
    ranges = split_range(limit, workers)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        partial_results = executor.map(calculate_range_sum, ranges)
        return combine(partial_results)
```

Особенности:

- потоки работают внутри одного процесса;
- память общая;
- создание потоков дешевле процессов;
- для CPU-bound Python-кода ускорение ограничено GIL;
- для I/O-bound задач потоки подходят значительно лучше.

### Multiprocessing

Файл: `sums/multiprocessing_sum.py`.

Используется `ProcessPoolExecutor`.

```python
def calculate_sum(limit=LIMIT, workers=4):
    ranges = split_range(limit, workers)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        partial_results = executor.map(calculate_range_sum, ranges)
        return combine(partial_results)
```

Особенности:

- каждый worker является отдельным процессом;
- процессы имеют отдельные интерпретаторы и могут выполнять Python-код
  параллельно на разных ядрах;
- создание процессов и передача данных дороже, чем у потоков.

### Asyncio

Файл: `sums/async_sum.py`.

```python
async def calculate_sum(limit=LIMIT, workers=4):
    ranges = split_range(limit, workers)
    tasks = [
        asyncio.create_task(calculate_part(bounds))
        for bounds in ranges
    ]
    return combine(await asyncio.gather(*tasks))
```

Особенности:

- `asyncio` использует кооперативную многозадачность;
- задачи выполняются в одном event loop;
- сам по себе `asyncio` не превращает CPU-bound код в параллельный;
- наибольшая польза достигается для операций ожидания I/O.

## Замеры задачи 1

Запуск:

```powershell
python -m sums.benchmark
```

Скрипт делает 5 запусков каждого подхода и выводит `avg`, `min` и `max`.

Замеры выполнены на одном компьютере. Для задачи суммы был предоставлен
один итоговый запуск каждого подхода, поэтому в таблице указано фактическое
время этого запуска.

| Подход | Среднее, с |
|---|---:|
| Threading | 0.001084 |
| Multiprocessing | 0.136542 |
| Asyncio | 0.000345 |

### Анализ

Для текущей реализации каждая подзадача вычисляется формулой практически
мгновенно. Поэтому обычно наиболее заметны расходы на создание worker'ов:
`multiprocessing` может оказаться дороже потоков и asyncio. Это не означает,
что процессы хуже для CPU-bound задач - достаточно тяжёлом независимом
CPU-вычислении они позволяют обойти ограничение GIL.


## Задача 2. Параллельный парсер

Список содержит несколько URL. Каждый `parse_and_save(url)`:

1. выполняет HTTP-запрос;
2. получает HTML;
3. извлекает содержимое `<title>`;
4. сохраняет URL, title и тип подхода в PostgreSQL;
5. выводит результат.

### Схема таблицы

```sql
CREATE TABLE IF NOT EXISTS parsed_pages (
    id BIGSERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    approach VARCHAR(32) NOT NULL
        CHECK (approach IN ('threading', 'multiprocessing', 'asyncio')),
    parsed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Локальный `.env`:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=time_manager
DB_USER=postgres
DB_PASSWORD=YOUR_PASSWORD
```

Сам `.env` в Git не добавляется.

### Threading parser

Файл: `parsers/threading_parser.py`.

```python
def parse_and_save(url: str) -> ParseResult:
    response = requests.get(url, timeout=20, headers=HEADERS)
    response.raise_for_status()

    result = ParseResult(
        url=url,
        title=extract_title(response.content),
        approach="threading",
    )
    save_result(result)
    print(result)
    return result
```

Несколько URL обрабатываются `ThreadPoolExecutor`. Для сетевых операций
потоки эффективны, поскольку во время ожидания ответа другие потоки могут
продолжать работу.

### Multiprocessing parser

Файл: `parsers/multiprocessing_parser.py`.

Логика `parse_and_save` аналогична threading-варианту, но задачи выполняются
через `ProcessPoolExecutor`. Такой вариант работает, однако для сетевого I/O
дополнительные процессы обычно создают лишние накладные расходы.

### Async parser

Файл: `parsers/async_parser.py`.

Асинхронный вариант использует:

- `aiohttp.ClientSession` для HTTP;
- `asyncio.create_task()` для конкурентного запуска URL;
- `asyncpg.Pool` для асинхронной записи в PostgreSQL.

```python
tasks = [
    asyncio.create_task(parse_and_save(url))
    for url in urls
]
return await asyncio.gather(*tasks)
```

Для большого количества независимых HTTP-запросов это наиболее естественная
модель из трёх рассматриваемых.

## Запуск парсеров

Из корня `Lr_2`:

```powershell
python -m parsers.threading_parser
python -m parsers.multiprocessing_parser
python -m parsers.async_parser
```

Каждая программа сама выводит полное время выполнения.

## Замеры задачи 2

Каждый парсер запускался три раза. Среднее арифметическое:
`threading = 1.248 с`, `multiprocessing = 1.590 с`, `asyncio = 0.359 с`.

| Подход | URL | Запуск 1, с | Запуск 2, с | Запуск 3, с | Среднее, с |
|---|---:|---:|---:|---:|---:|
| Threading | 8 | 1.135 | 1.291 | 1.319 | **1.248** |
| Multiprocessing | 8 | 1.690 | 1.586 | 1.495 | **1.590** |
| Asyncio | 8 | 0.304 | 0.467 | 0.306 | **0.359** |

### Анализ результатов

Парсинг веб-страниц является преимущественно I/O-bound задачей. Пока программа
ожидает сетевой ответ, CPU почти не занят. Поэтому:

- `asyncio` обычно масштабируется хорошо без создания множества threads;
- `threading` также хорошо подходит для небольшого/среднего количества URL;
- `multiprocessing` способен выполнять задачу, но его главное преимущество
  относится к тяжёлому коду, а не к ожиданию HTTP.

По фактическим измерениям быстрее всего оказался `asyncio` (в среднем
0.359 с), затем `threading` (1.248 с), а самым медленным —
`multiprocessing` (1.590 с). Для сетевого I/O такой результат ожидаем:
асинхронная модель эффективно использует время ожидания HTTP-ответов,
а отдельные процессы добавляют лишние накладные расходы.

## Проверка записей в БД

```sql
SELECT id, url, title, approach, parsed_at
FROM parsed_pages
ORDER BY parsed_at DESC;
```

