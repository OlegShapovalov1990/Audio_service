from pydantic import BaseModel, EmailStr
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True

class AudioBase(BaseModel):
    title: str

class AudioCreate(AudioBase):
    pass

class Audio(AudioBase):
    id: int
    path: str
    owner_id: int

    class Config:
        orm_mode = True