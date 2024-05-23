from uuid import UUID
from pydantic import BaseModel, Field

from datetime import datetime


class Person(BaseModel):
    id: UUID
    name: str


class Person_Vld(BaseModel):
    id: UUID
    full_name: str = Field(alias="name")

    class Config:
        allow_population_by_field_name = True


class Genre(BaseModel):
    id: UUID
    name: str
    description: str | None


class GenreForFilm(BaseModel):
    id: UUID
    name: str


class FilmWork(BaseModel):
    id: UUID
    creation_date: datetime | None
    title: str | None
    description: str | None
    imdb_rating: float | None
    genres: list[GenreForFilm]
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    directors: list[Person]
    actors: list[Person]
    writers: list[Person]
