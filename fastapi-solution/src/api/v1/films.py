from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from services.film import FilmService, get_film_service
from models.film import Film, FilmBase

router = APIRouter()


@router.get("/", response_model=list[FilmBase], response_model_by_alias=False)
async def all_films(
    genre: str | None = None,
    sort: str = "-imdb_rating",
    page_size: int = 50,
    page_number: int = 1,
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmBase]:
    if page_size * page_number > 10000:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="page_size * page_number give more than 10000",
        )
    films = await film_service.get_all(genre, sort, page_size, page_number)
    return films


@router.get("/search", response_model=list[FilmBase], response_model_by_alias=False)
async def films_search(
    query: str,
    page_size: int = 50,
    page_number: int = 1,
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmBase]:
    if page_size * page_number > 10000:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="page_size * page_number give more than 10000",
        )
    films = await film_service.search(query, page_size, page_number)
    return films


@router.get("/{film_id}", response_model=Film, response_model_by_alias=False)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return Film(**film.dict())
