from models.base import MyBaseModel


class Genre(MyBaseModel):
    name: str
    description: str | None = None


class GenreForFilm(MyBaseModel):
    name: str
