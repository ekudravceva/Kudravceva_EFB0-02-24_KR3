from passlib.context import CryptContext
from models import UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fake_users_db = {}

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str) -> UserInDB | None:
    """Получает пользователя. Использует безопасное сравнение."""
    import secrets
    for db_username in fake_users_db:
        if secrets.compare_digest(username, db_username):
            return UserInDB(**fake_users_db[db_username])
    return None

def save_user(username: str, hashed_password: str):
    fake_users_db[username] = {
        "username": username,
        "hashed_password": hashed_password
    }

def user_exists(username: str) -> bool:
    """Проверяет существование пользователя с защитой от тайминг-атак."""
    import secrets
    for db_username in fake_users_db:
        if secrets.compare_digest(username, db_username):
            return True
    return False