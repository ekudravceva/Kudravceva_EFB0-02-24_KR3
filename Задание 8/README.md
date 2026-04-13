```markdown
# Задание 8

## Описание проделанной работы

### Задание 8.1 - Регистрация пользователя с SQLite

Реализован эндпоинт для регистрации пользователей с сохранением данных в базу SQLite.

**Функционал:**
- Создание таблицы `users` с полями: `id`, `username`, `password`
- POST-эндпоинт `/register` для регистрации нового пользователя

### Задание 8.2 - CRUD операции для Todo

Реализованы все базовые CRUD операции для управления списком дел (Todo).

**Функционал:**
- **Create** - `POST /todos` - создание новой задачи
- **Read** - `GET /todos/{id}` - получение задачи по ID
- **Update** - `PUT /todos/{id}` - обновление задачи
- **Delete** - `DELETE /todos/{id}` - удаление задачи

**Модель Todo:**
- `id` - уникальный идентификатор (автоинкремент)
- `title` - заголовок задачи
- `description` - описание задачи
- `completed` - статус выполнения (по умолчанию false)

## Инструкция по запуску

### 1. Создание виртуального окружения

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Установка зависимостей

```bash
pip install fastapi uvicorn
```

### 3. Создание таблиц в базе данных

```bash
python init_users_db.py
python init_todos_db.py
```

### 4. Запуск сервера

```bash
uvicorn main:app --reload --port 8000
```