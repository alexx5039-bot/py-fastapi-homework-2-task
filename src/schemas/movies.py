
from datetime import date, datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, validator, Field


class MovieListItem(BaseModel):
    id: int
    name: str
    date: date
    score: float
    overview: str

    class Config:
        from_attributes = True


class MoviesListResponse(BaseModel):
    movies: List[MovieListItem]
    prev_page: Optional[str]
    next_page: Optional[str]
    total_pages: int
    total_items: int


class MovieCreateSchema(BaseModel):
    name: str = Field(max_length=255)
    date: date
    score: float = Field(ge=0, le=100)
    overview: str
    status: str
    budget: float = Field(ge=0)
    revenue: float = Field(ge=0)
    country: str
    genres: List[str]
    actors: List[str]
    languages: List[str]

    @validator("date")
    def validate_date_not_too_far(cls, value: date):
        if value > (datetime.utcnow().date() + timedelta(days=365)):
            raise ValueError("Release date cannot be more than one year in the future.")
        return value


class IdNameSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CountrySchema(BaseModel):
    id: int
    code: str
    name: str | None

    class Config:
        from_attributes = True


class MovieResponseSchema(BaseModel):
    id: int
    name: str
    date: date
    score: float
    overview: str
    status: str
    budget: float
    revenue: float
    country: CountrySchema
    genres: list[IdNameSchema]
    actors: list[IdNameSchema]
    languages: list[IdNameSchema]

    class Config:
        from_attributes = True


class MovieUpdateSchema(BaseModel):
    name: Optional[str] = None
    date: Optional[date] = None
    score: Optional[float] = Field(default=None, ge=0, le=100)
    overview: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[float] = Field(default=None, ge=0)
    revenue: Optional[float] = Field(default=None, ge=0)
