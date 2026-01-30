import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.config.settings import get_settings
from src.database.session_sqlite import (
    reset_sqlite_database,
    get_sqlite_db_contextmanager,
)
from src.database.populate import CSVDatabaseSeeder
from src.main import app


@pytest_asyncio.fixture(scope="function", autouse=True)
async def reset_db():
    """Reset the SQLite database before each test."""
    await reset_sqlite_database()


@pytest_asyncio.fixture(scope="function")
async def client():
    """Provide an asynchronous test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_client:
        yield async_client


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Provide an async database session for database interactions."""
    async with get_sqlite_db_contextmanager() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def seed_database(db_session):
    """Seed the database with test data if it is empty."""
    settings = get_settings()
    seeder = CSVDatabaseSeeder(
        csv_file_path=settings.PATH_TO_MOVIES_CSV,
        db_session=db_session,
    )

    if not await seeder.is_db_populated():
        await seeder.seed()

    yield db_session
