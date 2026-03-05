from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..schemas import UserLogin
from ..database import get_db
from .. import models, oauth2
from app.utils import hash, verify
from typing import Annotated

router = APIRouter(tags=['Authentication'])

@router.post("/login")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email==user_credentials.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential invalid")
    
    if not verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential invalid")
    
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"token": access_token, "token_type": "bearer"}

@router.post("/login2")
def login2(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email==user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential invalid")
    
    if not verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential invalid")
    
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"token": access_token, "token_type": "bearer"}
