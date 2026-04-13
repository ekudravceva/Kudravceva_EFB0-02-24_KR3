import secrets
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from passlib.context import CryptContext
from starlette.responses import JSONResponse

from models import User, UserInDB, Token, LoginRequest
from config import MODE, DOCS_USER, DOCS_PASSWORD, ACCESS_TOKEN_EXPIRE_MINUTES
from jwt_auth import authenticate_user, create_access_token, verify_token
from datetime import timedelta
from docs_auth import verify_docs_access
from database import get_password_hash, verify_password, get_user, save_user

app = FastAPI(
    title="Task 6",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

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

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: User):
    if get_user(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    save_user(user_data.username, get_password_hash(user_data.password))
    
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
    
    # /redoc скрыт полностью
    
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


@app.post("/token")
async def login_for_access_token(login_data: LoginRequest):
    """
    Эндпоинт для получения JWT токена.
    Аналог /login из задания 6.4.
    """
    if not authenticate_user(login_data.username, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_data.username}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

@app.get("/protected_resource")
async def protected_resource(username: str = Depends(verify_token)):
    """
    Защищенный ресурс, доступный только с валидным JWT токеном.
    """
    return {"message": f"Access granted to protected resource for user: {username}"}