from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, oauth2
from ..database import get_db
from ..schemas import UserLogin
from app.utils import verify

router = APIRouter(tags=["Authentication"])


@router.post("/login")
async def login(user_credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User).where(models.User.email == user_credentials.email)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Credential invalid"
        )

    if not verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Credential invalid"
        )

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"token": access_token, "token_type": "bearer"}


@router.post("/login2")
async def login2(
    user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.User).where(models.User.email == user_credentials.username)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Credential invalid"
        )

    if not verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Credential invalid"
        )

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"token": access_token, "token_type": "bearer"}