# Grades API

REST API для загрузки и анализа успеваемости студентов. Реализовано на FastAPI с использованием PostgreSQL.

## Требования

- Docker и Docker Compose
- Python 3.12+ (для локальной разработки)

## Быстрый старт

```bash
make up
```

или

```bash
docker compose up --build -d
```

После запуска сервис будет доступен на http://localhost:8000

Интерактивная документация: http://localhost:8000/docs

## API Endpoints

### POST /upload-grades

Загрузка CSV файла с оценками студентов.

**Формат CSV:**
- Разделитель: `;`
- Заголовки: `Дата;Номер группы;ФИО;Оценка`
- Формат даты: `DD.MM.YYYY`
- Оценки: от 2 до 5

**Пример ответа:**
```json
{
  "status": "ok",
  "records_loaded": 2000,
  "students": 40
}
```

### GET /students/more-than-3-twos

Возвращает список студентов, у которых оценка 2 встречается больше 3 раз.

**Пример ответа:**
```json
[
  {"full_name": "Иванов Иван", "count_twos": 5}
]
```

### GET /students/less-than-5-twos

Возвращает список студентов, у которых оценка 2 встречается меньше 5 раз.

### GET /health

Проверка работоспособности сервиса.

## Тестирование

```bash
make itest
```

## Структура проекта

```
grades-api/
├── app/              # Исходный код приложения
│   ├── main.py       # FastAPI приложение и эндпоинты
│   ├── db.py         # Подключение к БД
│   ├── schemas.py    # Pydantic схемы
│   ├── validators.py # Валидация CSV данных
│   └── settings.py   # Настройки подключения
├── sql/              # SQL миграции
│   └── 001_create_tables.sql
├── tests/            # Тесты
│   └── test_api.py
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Фичи

- Использование чистого SQL (asyncpg) без ORM
- Валидация входных данных
- Обработка ошибок с детальными сообщениями
- Транзакции для целостности данных
- Индексы для оптимизации запросов
