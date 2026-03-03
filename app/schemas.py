from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


class Base_Post(BaseModel):
    title: str
    content: str
    published: bool = True

class Return_Post(Base_Post):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class User(BaseModel):
    email: EmailStr
    password: str
    

class UserOut(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)