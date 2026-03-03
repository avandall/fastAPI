from fastapi import Depends, FastAPI,Response, status, HTTPException, APIRouter
from pydantic import BaseModel
from typing import List
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
import time
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..database import get_db, Base, engine
from .. import models, schemas

router = APIRouter(tags=["Posts"])

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
#GET
@router.get("/posts")
def get_posts():
    cursor.execute('SELECT * from posts')
    post = cursor.fetchall()
    print(post)
    return {"data": post}

@router.get("/sqlalchemy", response_model=List[schemas.Return_Post])
def alchemy_get(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    print(posts)
    return posts
    

@router.get("/posts/{id}")
def get_post(id:int):
    cursor.execute("SELECT * FROM posts WHERE id = %s", str(id))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return {"data": post}

@router.get("/sqlalchemy/{id}", response_model=schemas.Return_Post)
def alchemy_get_id(id:int, db: Session = Depends(get_db)):
    post_id = db.query(models.Post).filter(models.Post.id==id).first()
    if not post_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return post_id


#POST
@router.post("/posts")
def create_posts(post: List[Post]):
    data_insert = [(p.title, p.content, p.published) for p in post]
    query = 'INSERT INTO posts (title, content, published) VALUES %s RETURNING *'
    result = execute_values(cursor,query,data_insert,fetch=True)
    conn.commit()
    return {"data": result}

@router.post("/sqlalchemy", response_model=schemas.Return_Post)
def post_alchemy(post:schemas.Base_Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.model_dump())
    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi tạo bài viết: {str(e)}")


#PUT
@router.put("/posts/{id}")
def update_posts(id:int, post: Post):
    cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *", (post.title, post.content, post.published,str(id)))
    updated = cursor.fetchone()
    conn.commit()
    if updated == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return {"data": updated}
    
@router.put("/sqlalchemy/{id}", response_model=schemas.Return_Post)
def update_post_alchemy(id:int, post:schemas.Base_Post, db: Session = Depends(get_db)):
    post_id = db.query(models.Post).filter(models.Post.id==id)
    if not post_id.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    post_id.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_id.first()

#DELETE
@router.delete("/posts/{id}")
def delete_post(id: int):
    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", str(id))
    deleted = cursor.fetchone()
    conn.commit()
    if deleted == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/sqlalchemy/{id}")
def delete_post_alchemy(id: int, db: Session = Depends(get_db)):
    post_id = db.query(models.Post).filter(models.Post.id==id).first()
    if not post_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    db.delete(post_id)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)