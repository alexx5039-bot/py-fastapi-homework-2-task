from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import MovieModel, CountryModel, GenreModel, ActorModel, LanguageModel
from src.database.session_sqlite import get_sqlite_db
from src.schemas.movies import MoviesListResponse, MovieResponseSchema, MovieCreateSchema, MovieUpdateSchema
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/", response_model=MoviesListResponse)
async def list_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_sqlite_db),
):

    total_items_result = await db.execute(
        select(func.count(MovieModel.id))
    )
    total_items = total_items_result.scalar_one()

    if total_items == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found.",
        )

    total_pages = (total_items + per_page - 1) // per_page

    if page > total_pages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found.",
        )

    offset = (page - 1) * per_page

    result = await db.execute(
        select(MovieModel)
        .order_by(MovieModel.id.desc())
        .offset(offset)
        .limit(per_page)
    )

    movies = result.scalars().all()

    if not movies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found.",
        )

    base_url = "/theater/movies/"

    prev_page = (
        f"{base_url}?page={page - 1}&per_page={per_page}"
        if page > 1
        else None
    )

    next_page = (
        f"{base_url}?page={page + 1}&per_page={per_page}"
        if page < total_pages
        else None
    )

    return MoviesListResponse(
        movies=movies,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items,
    )


async def get_or_create(db: AsyncSession, model, **kwargs):
    result = await db.execute(select(model).filter_by(**kwargs))
    instance = result.scalar_one_or_none()

    if instance:
        return instance

    instance = model(**kwargs)
    db.add(instance)
    await db.flush()
    return instance


@router.post(
    "/",
    response_model=MovieResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_movie(
        movie_data: MovieCreateSchema,
        db: AsyncSession = Depends(get_sqlite_db),
):
    existing_movie = await db.execute(
        select(MovieModel).where(
            MovieModel.name == movie_data.name,
            MovieModel.date == movie_data.date,
        )
    )
    if existing_movie.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A movie with the name '{movie_data.name}' and release date '{movie_data.date}' already exists.",
        )

    country = await get_or_create(
        db,
        CountryModel,
        code=movie_data.country,
    )

    movie = MovieModel(
        name=movie_data.name,
        date=movie_data.date,
        score=movie_data.score,
        overview=movie_data.overview,
        status=movie_data.status,
        budget=movie_data.budget,
        revenue=movie_data.revenue,
        country=country,
    )
    db.add(movie)
    await db.flush()

    for genre_name in movie_data.genres:
        genre = await get_or_create(db, GenreModel, name=genre_name)
        movie.genres.append(genre)

    for actor_name in movie_data.actors:
        actor = await get_or_create(db, ActorModel, name=actor_name)
        movie.actors.append(actor)

    for language_name in movie_data.languages:
        language = await get_or_create(db, LanguageModel, name=language_name)
        movie.languages.append(language)

    await db.commit()
    await db.refresh(movie)

    return movie


@router.get(
    "/{movie_id}/",
    response_model=MovieResponseSchema,
)
async def get_movie_details(
    movie_id: int,
    db: AsyncSession = Depends(get_sqlite_db),
):
    result = await db.execute(
        select(MovieModel)
        .where(MovieModel.id == movie_id)
        .options(
            selectinload(MovieModel.country),
            selectinload(MovieModel.genres),
            selectinload(MovieModel.actors),
            selectinload(MovieModel.languages),
        )
    )

    movie = result.scalar_one_or_none()

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found.",
        )

    return movie


@router.delete(
    "/{movie_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_sqlite_db),
):
    result = await db.execute(
        select(MovieModel).where(MovieModel.id == movie_id)
    )
    movie = result.scalar_one_or_none()

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found.",
        )

    await db.delete(movie)
    await db.commit()


@router.patch(
    "/{movie_id}/",
    status_code=status.HTTP_200_OK,
)
async def update_movie(
    movie_id: int,
    movie_data: MovieUpdateSchema,
    db: AsyncSession = Depends(get_sqlite_db),
):
    result = await db.execute(
        select(MovieModel).where(MovieModel.id == movie_id)
    )
    movie = result.scalar_one_or_none()

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found.",
        )

    update_data = movie_data.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(movie, field, value)

        await db.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input data.",
        )

    return {"detail": "Movie updated successfully."}
