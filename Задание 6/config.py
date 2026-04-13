import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Режим работы приложения
MODE = os.getenv("MODE", "DEV").upper()

# Учетные данные для документации (только для DEV)
DOCS_USER = os.getenv("DOCS_USER", "admin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "docs123")

# Проверка допустимых значений MODE
if MODE not in ["DEV", "PROD"]:
    raise ValueError(f"Invalid MODE: {MODE}. Must be DEV or PROD")