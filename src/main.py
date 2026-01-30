from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.database import get_db_contextmanager
from src.database.models import Base
from src.routes.movies import router as movies_router


app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Invalid input data."},
    )


@app.on_event("startup")
async def startup():
    async with get_db_contextmanager() as session:
        await session.run_sync(Base.metadata.create_all)


app.include_router(
    movies_router,
    prefix="/api/v1/theater",
)
