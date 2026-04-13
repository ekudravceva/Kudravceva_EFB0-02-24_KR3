# Task 6 

## Установка и запуск

1. Создать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```
2. Установить зависимости:

```bash
pip install -r requirements.txt
```
3. Настроить .env при необходимости

4. Запустить приложение:

``` bash
uvicorn main:app --reload
```