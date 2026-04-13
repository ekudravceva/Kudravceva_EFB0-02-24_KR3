from passlib.context import CryptContext
from models import UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {}

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str) -> UserInDB | None:
    if username in fake_users_db:
        return UserInDB(**fake_users_db[username])
    return None

def save_user(username: str, hashed_password: str):
    fake_users_db[username] = {
        "username": username,
        "hashed_password": hashed_password
    }