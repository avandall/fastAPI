from fastapi import Depends, FastAPI,Response, status, HTTPException, APIRouter
from pydantic import BaseModel
from typing import List
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..database import get_db, Base, engine
from .. import models, schemas, oauth2


router = APIRouter(prefix="/votes", tags=["Votes"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def Vote(vote: schemas.Vote, db: Session=Depends(get_db), get_current_user: schemas.TokenData=Depends(oauth2.get_current_user)):
    query_vote = db.query(models.Vote).filter(models.Vote.user_id == get_current_user.id, models.Vote.post_id == vote.post_id)
    found_vote = query_vote.first()
    if vote.dir ==1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {get_current_user.id} has already voted on post {vote.post_id}")
        new_vote = models.Vote(post_id=vote.post_id, user_id=get_current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "vote added"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"vote does not exist")
        query_vote.delete(synchronize_session=False)
        db.commit()
        return {"message": "vote deleted"}
