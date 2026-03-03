from fastapi import Depends, FastAPI, Path, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
from typing import Annotated, Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
import time
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .database import get_db, Base, engine
from . import models, schemas
from .routers import posts, users

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(posts.router)
app.include_router(users.router)

my_posts = [{"message":"Food","content":"I like pizza", "id":1},{"message":"Drink","content":"I like sting", "id":2}]

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    

while True:
    try:
        conn = psycopg2.connect(host='localhost', database = 'learnFastAPI', user='postgres', password='avandall1999', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connected !!!")
        break
    except Exception as e:
        print('Connection failed !')
        print('Error:', e)
        time.sleep(3)

