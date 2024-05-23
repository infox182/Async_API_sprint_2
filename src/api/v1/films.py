from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated

from services.films import FilmService, get_film_service
from models.films import Film, FilmBase

router = APIRouter()


@router.get("/",
            response_model=list[FilmBase],
            response_model_by_alias=False,
            summary="Cписок фильмов",
            description="Получить список фильмов",
            response_description="Название и рейтинг фильма")
async def all_films(
    genre: Annotated[
        str, Query(description='Жанр для фильтрации')] = None,
    sort: Annotated[
        str, Query(description='Текст для поиска')] = "-imdb_rating",
    page_size: Annotated[
        int, Query(description='Объем страницы при пагинации', ge=1)] = 50,
    page_number: Annotated[
        int, Query(description='Номер страницы при пагинации', ge=1)] = 1,
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmBase]:
    if page_size * page_number > 10000:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="page_size * page_number give more than 10000",
        )
    films = await film_service.get_all(genre, sort, page_size, page_number)
    return films


@router.get("/search",
            response_model=list[FilmBase],
            response_model_by_alias=False,
            summary="Поиск фильмов",
            description="Полнотекстовый поиск фильмов",
            response_description="Название и рейтинг фильма")
async def films_search(
    query: Annotated[
        str, Query(description='Текст для поиска')],
    page_size: Annotated[
        int, Query(description='Объем страницы при пагинации', ge=1)] = 50,
    page_number: Annotated[
        int, Query(description='Номер страницы при пагинации', ge=1)] = 1,
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmBase]:
    if page_size * page_number > 10000:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="page_size * page_number give more than 10000",
        )
    films = await film_service.search(query, page_size, page_number)
    return films


@router.get("/{film_id}",
            response_model=Film,
            response_model_by_alias=False,
            summary="Фильм",
            description="Получить фильм по uuid",
            response_description="Полная информация о фильме")
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="film not found")
    return Film(**film.dict())
