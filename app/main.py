from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import posts, users, auth



models.Base.metadata.create_all(bind=engine)
origins = ["*"]  # Allow all origins, you can specify your frontend URL here
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)

