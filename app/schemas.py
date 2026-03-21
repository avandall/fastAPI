from pydantic import BaseModel, ConfigDict, EmailStr, conint
from datetime import datetime
from typing import Optional

class Base_Post(BaseModel):
    title: str
    content: str
    published: bool = True



    model_config = ConfigDict(from_attributes=True)

class User(BaseModel):
    email: EmailStr
    password: str
    

class UserOut(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Return_Post(Base_Post):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

class Token(BaseModel):
    token: str
    token_type: str

class TokenData(BaseModel):
    id: int | None = None

class Vote(BaseModel):
    user_id: int
    post_id: int
    dir: conint(le=1)