import secrets
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext

from models import User, UserInDB

app = FastAPI(title="Task 6")

# настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db: dict[str, dict] = {}

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str) -> UserInDB | None:
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None

# Стартовый пользователь для удобства тестирования
@app.on_event("startup")
async def create_test_user():
    if not fake_users_db:
        hashed = get_password_hash("secret123")
        fake_users_db["admin"] = {
            "username": "admin",
            "hashed_password": hashed
        }
        print("Created test user: admin / secret123")

security = HTTPBasic()

def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInDB:
    username = credentials.username
    password = credentials.password

    user = get_user(username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not verify_password(password, user.hashed_password):
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

    hashed_password = get_password_hash(user_data.password)
    fake_users_db[user_data.username] = {
        "username": user_data.username,
        "hashed_password": hashed_password
    }

    return {"message": f"User '{user_data.username}' successfully registered"}

@app.get("/login")
async def login(current_user: UserInDB = Depends(auth_user)):
    """
    Защищенный ресурс, доступный только при правильном логине/пароле.
    """
    return {"message": f"Welcome, {current_user.username}!"}

@app.get("/")
async def root():
    return {"message": "Task 6"}