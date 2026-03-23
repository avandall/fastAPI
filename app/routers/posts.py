from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(tags=["Posts"])


@router.get("/posts-root")
def posts_root():
    return {"message": "Hello World"}


@router.get("/sqlalchemy", response_model=List[schemas.Return_Post])
async def alchemy_get(
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: str = "",
):
    result = await db.execute(
        select(models.Post)
        .where(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
    )
    posts = result.scalars().all()
    print(posts)
    return posts


@router.get("/sqlalchemy/{user_id}", response_model=List[schemas.Return_Post])
async def alchemy_get_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user),
):
    result = await db.execute(
        select(models.Post).where(models.Post.owner_id == user_id)
    )
    post = result.scalars().all()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with user_id: {user_id} was not found",
        )
    return post


@router.post("/sqlalchemy", status_code=status.HTTP_201_CREATED, response_model=schemas.Return_Post)
async def post_alchemy(
    post: schemas.Base_Post,
    db: AsyncSession = Depends(get_db),
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user),
):
    new_post = models.Post(owner_id=get_current_user.id, **post.model_dump())
    try:
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)
        return new_post
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi tạo bài viết: {str(e)}")


@router.put("/sqlalchemy/{id}", response_model=schemas.Return_Post)
async def update_post_alchemy(
    id: int,
    post: schemas.Base_Post,
    db: AsyncSession = Depends(get_db),
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user),
):
    result = await db.execute(select(models.Post).where(models.Post.id == id))
    post_id = result.scalars().first()
    if not post_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
    if post_id.owner_id != get_current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    for key, value in post.model_dump().items():
        setattr(post_id, key, value)

    await db.commit()
    await db.refresh(post_id)
    return post_id


@router.delete("/sqlalchemy/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_alchemy(
    id: int,
    db: AsyncSession = Depends(get_db),
    get_current_user: schemas.TokenData = Depends(oauth2.get_current_user),
):
    result = await db.execute(select(models.Post).where(models.Post.id == id))
    post_id = result.scalars().first()
    if not post_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
    if post_id.owner_id != get_current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    await db.delete(post_id)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)