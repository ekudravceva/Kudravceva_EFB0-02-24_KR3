import secrets
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from passlib.context import CryptContext
from starlette.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from models import User, UserInDB, Token, LoginRequest
from config import MODE, DOCS_USER, DOCS_PASSWORD, ACCESS_TOKEN_EXPIRE_MINUTES
from jwt_auth import authenticate_user, create_access_token, verify_token
from docs_auth import verify_docs_access
from database import get_password_hash, verify_password, get_user, save_user, user_exists

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Task 6",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

api_security = HTTPBasic()

def auth_user(credentials: HTTPBasicCredentials = Depends(api_security)) -> UserInDB:
    username = credentials.username
    password = credentials.password
    
    if not user_exists(username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    user = get_user(username)
    
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user

@app.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
async def register(request: Request, user_data: User):
    if get_user(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    save_user(user_data.username, get_password_hash(user_data.password))
    
    return {"message": "New user created"}

@app.get("/login_basic")
async def login_basic(current_user: UserInDB = Depends(auth_user)):
    return {"message": f"You got my secret, welcome"}

@app.get("/")
async def root():
    return {
        "message": f"Task 6.5 API running in {MODE} mode",
        "endpoints": {
            "POST /register": "Register new user (1/min)",
            "POST /login": "Login and get JWT token (5/min)",
            "GET /protected_resource": "JWT protected resource",
            "GET /login_basic": "Basic Auth login"
        }
    }

if MODE == "DEV":
    
    @app.get("/docs", include_in_schema=False)
    async def get_docs(username: str = Depends(verify_docs_access)):
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=app.title + " - Swagger UI"
        )
    
    @app.get("/openapi.json", include_in_schema=False)
    async def get_openapi_json(username: str = Depends(verify_docs_access)):
        return JSONResponse(
            content=get_openapi(
                title=app.title,
                version=app.version,
                routes=app.routes
            )
        )
    
    print(f"DEV MODE: Documentation protected with Basic Auth")
    print(f"Docs credentials: {DOCS_USER} / {DOCS_PASSWORD}")

elif MODE == "PROD":
    
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


@app.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest):
    """
    Вход пользователя, возвращает JWT токен.
    Лимит: 5 запросов в минуту.
    """
    if not user_exists(login_data.username):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not authenticate_user(login_data.username, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_data.username}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

@app.get("/protected_resource")
async def protected_resource(username: str = Depends(verify_token)):
    return {"message": "Access granted"}