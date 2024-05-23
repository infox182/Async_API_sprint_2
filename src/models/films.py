from models.base import MyBaseModel
from models.genres import GenreForFilm
from models.persons import Person


class FilmBase(MyBaseModel):
    title: str
    imdb_rating: float | None = None


class Film(FilmBase):
    description: str | None = None
    creation_date: str | None = None
    genres: list[GenreForFilm] = []
    actors: list[Person] = []
    writers: list[Person] = []
    directors: list[Person] = []
