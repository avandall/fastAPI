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

router = APIRouter(prefix="/", tags=["Users"])

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

#GET
@router.get("/", response_model=List[schemas.UserOut])
def get_users(db: Session = Depends(get_db)):
    user = db.query(models.User).all()
    return user

#POST(create user)
@router.post("/", response_model=schemas.UserOut)
def create_user(user:schemas.User, db: Session = Depends(get_db)):
    password_hash = pwd_context.hash(user.password)
    user.password = password_hash
    new_user = models.User(**user.model_dump())
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating user: {e}")

#PUT(update user)
@router.put("/{id}", response_model=schemas.UserOut)
def update_user(id:int, user:schemas.User, db:Session=Depends(get_db)):
    user_id = db.query(models.User).filter(models.User.id==id)
    if not user_id.first():
        raise HTTPException(status_code=404, detail="User not found")
    user_id.update(user.model_dump(), synchronize_session=False)
    db.commit()
    return user_id.first()

#DELETE
@router.delete("/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):
    user_id = db.query(models.User).filter(models.User.id==id).first()
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user_id)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)