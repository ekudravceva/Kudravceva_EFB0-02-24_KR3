from pydantic import BaseModel

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

User = UserCreate