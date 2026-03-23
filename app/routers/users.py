from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/", response_model=List[schemas.UserOut])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User))
    user = result.scalars().all()
    return user


@router.post("/", response_model=schemas.UserOut)
async def create_user(user: schemas.User, db: AsyncSession = Depends(get_db)):
    password_hash = pwd_context.hash(user.password)
    userdict = user.model_dump()
    userdict["password"] = password_hash
    new_user = models.User(**userdict)
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating user: {e}")


@router.put("/{id}", response_model=schemas.UserOut)
async def update_user(id: int, user: schemas.User, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == id))
    user_id = result.scalars().first()
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user.model_dump().items():
        setattr(user_id, key, value)

    await db.commit()
    await db.refresh(user_id)
    return user_id


@router.delete("/{id}")
async def delete_user(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == id))
    user_id = result.scalars().first()
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user_id)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)