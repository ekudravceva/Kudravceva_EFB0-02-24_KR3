from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    password: str
    role: str  # "admin", "user", "guest"

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    role: str

class UserResponse(BaseModel):
    username: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ResourceCreate(BaseModel):
    title: str
    description: str

class ResourceUpdate(BaseModel):
    title: str
    description: str
    completed: bool

class ResourceResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    owner: str