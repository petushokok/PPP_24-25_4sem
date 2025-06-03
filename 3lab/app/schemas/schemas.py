from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):  
    id: int
    email: EmailStr
    access_token: str
    token_type: str

class UserBase(BaseModel):
    email: EmailStr

class UserMe(UserBase):
    id: int
    created_at: datetime | None = None 

class TokenData(UserBase):
    sub: str | None = None


