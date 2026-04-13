import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from config import MODE, DOCS_USER, DOCS_PASSWORD

# Basic Auth для документации
docs_security = HTTPBasic()

def verify_docs_access(credentials: HTTPBasicCredentials = Depends(docs_security)):
    """
    Проверяет доступ к документации в DEV режиме.
    Использует secrets.compare_digest для защиты от тайминг-атак.
    """
    # Безопасное сравнение имени пользователя
    username_correct = secrets.compare_digest(
        credentials.username.encode('utf-8'),
        DOCS_USER.encode('utf-8')
    )
    
    # Безопасное сравнение пароля
    password_correct = secrets.compare_digest(
        credentials.password.encode('utf-8'),
        DOCS_PASSWORD.encode('utf-8')
    )
    
    if not (username_correct and password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username