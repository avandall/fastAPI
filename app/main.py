from fastapi import FastAPI
from .database import engine
from . import models
from .routers import posts, users, auth


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)

