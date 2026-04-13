import secrets
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from passlib.context import CryptContext
from starlette.responses import JSONResponse

from models import User, UserInDB
from config import MODE, DOCS_USER, DOCS_PASSWORD
from docs_auth import verify_docs_access

app = FastAPI(
    title="Task 6.3 - Environment-based Docs Protection",
    # Отключаем стандартные эндпоинты документации
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# --- 1. PassLib для хеширования ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 2. In-Memory БД ---
fake_users_db = {}

# --- 3. Вспомогательные функции ---
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str) -> UserInDB | None:
    if username in fake_users_db:
        return UserInDB(**fake_users_db[username])
    return None

# --- 4. Basic Auth для основного API ---
api_security = HTTPBasic()

def auth_user(credentials: HTTPBasicCredentials = Depends(api_security)) -> UserInDB:
    user = get_user(credentials.username)
    
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user

# --- 5. Основные эндпоинты API ---
@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: User):
    if get_user(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    
    fake_users_db[user_data.username] = {
        "username": user_data.username,
        "hashed_password": get_password_hash(user_data.password)
    }
    return {"message": f"User '{user_data.username}' successfully registered"}

@app.get("/login")
async def login(current_user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {current_user.username}!"}

@app.get("/")
async def root():
    return {
        "message": f"Task 6.3 API running in {MODE} mode",
        "endpoints": {
            "POST /register": "Register new user",
            "GET /login": "Login with Basic Auth"
        }
    }

# --- 6. Управление документацией в зависимости от MODE ---

if MODE == "DEV":
    # В DEV-режиме документация защищена Basic Auth
    
    @app.get("/docs", include_in_schema=False)
    async def get_docs(username: str = Depends(verify_docs_access)):
        """Защищенная документация Swagger UI"""
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=app.title + " - Swagger UI"
        )
    
    @app.get("/openapi.json", include_in_schema=False)
    async def get_openapi_json(username: str = Depends(verify_docs_access)):
        """Защищенная OpenAPI схема"""
        return JSONResponse(
            content=get_openapi(
                title=app.title,
                version=app.version,
                routes=app.routes
            )
        )
    
    # /redoc скрыт полностью (не добавляем эндпоинт)
    
    print(f"DEV MODE: Documentation protected with Basic Auth")
    print(f"Docs credentials: {DOCS_USER} / {DOCS_PASSWORD}")

elif MODE == "PROD":
    # В PROD-режиме документация полностью отключена (возвращает 404)
    
    @app.get("/docs", include_in_schema=False)
    async def get_docs_disabled():
        raise HTTPException(status_code=404, detail="Not Found")
    
    @app.get("/openapi.json", include_in_schema=False)
    async def get_openapi_disabled():
        raise HTTPException(status_code=404, detail="Not Found")
    
    @app.get("/redoc", include_in_schema=False)
    async def get_redoc_disabled():
        raise HTTPException(status_code=404, detail="Not Found")
    
    print(f"PROD MODE: Documentation is disabled (404)")

else:
    raise ValueError(f"Invalid MODE: {MODE}. Must be DEV or PROD")