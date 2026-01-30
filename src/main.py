from fastapi import FastAPI

from src.routes import movie_router

app = FastAPI()

app.include_router(
    movie_router,
    prefix="/api/v1/theater",
)
