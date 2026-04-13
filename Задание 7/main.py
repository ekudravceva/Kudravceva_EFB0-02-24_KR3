from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import secrets
import traceback  

from models import (
    UserRegister, UserResponse, Token, 
    ResourceCreate, ResourceUpdate, ResourceResponse
)
from auth import get_password_hash, verify_password, create_access_token, decode_token
from database import fake_users_db, resources_db, resource_id_counter

app = FastAPI(title="RBAC API")
security = HTTPBearer()

#вспомогательные функции
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    payload = decode_token(token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = fake_users_db.get(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return {"username": username, "role": user["role"]}

def require_role(allowed_roles: List[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker

# аутентификация
@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    try:
        print(f"Attempting to register: {user.username}, role: {user.role}")  # Отладка
        
        if user.role not in ["admin", "user", "guest"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid role. Choose: admin, user, guest"
            )
        
        # Проверка существования пользователя
        for existing_user in fake_users_db:
            if secrets.compare_digest(existing_user, user.username):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already exists"
                )
        
        hashed_password = get_password_hash(user.password)
        fake_users_db[user.username] = {
            "username": user.username,
            "hashed_password": hashed_password,
            "role": user.role
        }
        
        return UserResponse(username=user.username, role=user.role)
    
    except HTTPException:
        raise
    except Exception as e:
        # отладка
        print(f"Error in register: {str(e)}")  
        print(traceback.format_exc())  
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/login", response_model=Token)
async def login(user: UserRegister):
    try:
        print(f"Login attempt: {user.username}")  # отладка
        
        db_user = fake_users_db.get(user.username)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not verify_password(user.password, db_user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization failed"
            )
        
        access_token = create_access_token(data={"sub": user.username})
        return Token(access_token=access_token, token_type="bearer")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in login: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# эндпоинты
@app.get("/resources", response_model=List[ResourceResponse])
async def get_all_resources(current_user: dict = Depends(require_role(["admin", "user", "guest"]))):
    return resources_db

@app.get("/resources/{resource_id}", response_model=ResourceResponse)
async def get_resource(resource_id: int, current_user: dict = Depends(require_role(["admin", "user", "guest"]))):
    for resource in resources_db:
        if resource["id"] == resource_id:
            return resource
    raise HTTPException(status_code=404, detail="Resource not found")

@app.post("/resources", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource: ResourceCreate,
    current_user: dict = Depends(require_role(["admin", "user"]))
):
    new_resource = {
        "id": resource_id_counter.get_and_increment(),
        "title": resource.title,
        "description": resource.description,
        "completed": False,
        "owner": current_user["username"]
    }
    resources_db.append(new_resource)
    return new_resource

@app.put("/resources/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    resource_update: ResourceUpdate,
    current_user: dict = Depends(require_role(["admin", "user"]))
):
    for idx, resource in enumerate(resources_db):
        if resource["id"] == resource_id:
            if current_user["role"] == "admin" or resource["owner"] == current_user["username"]:
                resources_db[idx]["title"] = resource_update.title
                resources_db[idx]["description"] = resource_update.description
                resources_db[idx]["completed"] = resource_update.completed
                return resources_db[idx]
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update your own resources"
                )
    raise HTTPException(status_code=404, detail="Resource not found")

@app.delete("/resources/{resource_id}")
async def delete_resource(resource_id: int, current_user: dict = Depends(require_role(["admin", "user"]))):
    for idx, resource in enumerate(resources_db):
        if resource["id"] == resource_id:
            if current_user["role"] == "admin" or resource["owner"] == current_user["username"]:
                resources_db.pop(idx)
                return {"message": "Resource deleted successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only delete your own resources"
                )
    raise HTTPException(status_code=404, detail="Resource not found")

# эндпоинты админа

@app.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(current_user: dict = Depends(require_role(["admin"]))):
    return [{"username": u["username"], "role": u["role"]} for u in fake_users_db.values()]

@app.delete("/admin/users/{username}")
async def delete_user(username: str, current_user: dict = Depends(require_role(["admin"]))):
    if username == current_user["username"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    if username not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    global resources_db
    resources_db = [r for r in resources_db if r["owner"] != username]
    
    del fake_users_db[username]
    return {"message": f"User {username} deleted"}