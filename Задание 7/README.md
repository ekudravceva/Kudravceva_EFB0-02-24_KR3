# Задание 7.1

## Описание проекта

Реализация системы управления доступом на основе ролей (Role-Based Access Control). Приложение поддерживает аутентификацию через JWT токены и разграничение прав доступа для трех ролей.

## Роли и права доступа

admin - Полный доступ ко всем ресурсам и управление пользователями 
user - Чтение всех ресурсов, создание/обновление/удаление только своих ресурсов 
guest - Только чтение (без права создания/изменения/удаления) 

## Установка и запуск

### 1. Создание виртуального окружения

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Запуск приложения

```bash
uvicorn main:app --reload --port 8000
```

После запуска приложение будет доступно по адресу: `http://localhost:8000`

### 4. Документация API

- Swagger UI: `http://localhost:8000/docs`

## API Эндпоинты

### Аутентификация

- POST - `/register` - Регистрация нового пользователя (Все)
- POST - `/login` - Вход и получение JWT токена (Все) 

### Ресурсы (CRUD)

- GET - `/resources` - Получить список всех ресурсов (admin, user, guest)
- GET - `/resources/{id}` - Получить ресурс по ID (admin, user, guest)
- POST - `/resources` - Создать новый ресурс (admin, user)
- PUT - `/resources/{id}` - Обновить ресурс (admin (любой ресурс), user (только свой))
- DELETE - `/resources/{id}` - Удалить ресурс (admin (любой ресурс), user (только свой))

## Защищенные ресурсы

- GET - `/protected_resource` - Тестовый защищенный ресурс (admin, user)

### Администрирование

- GET - `/admin/users` - Получить список всех пользователей (Только admin)
- DELETE - `/admin/users/{username}` - Удалить пользователя (Только admin)