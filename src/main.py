from fastapi import FastAPI

from src.routes import movie_router
from src.database.session_sqlite import sqlite_engine, Base


app = FastAPI(
    title="Movies homework",
    description="Description of project",
)

api_version_prefix = "/api/v1"


@app.on_event("startup")
async def startup():
    async with sqlite_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(
    movie_router,
    prefix=f"{api_version_prefix}/theater",
    tags=["theater"],
)
