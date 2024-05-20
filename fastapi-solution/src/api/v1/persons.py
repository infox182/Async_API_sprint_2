from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated

from models.person import PersonWithFilms
from models.film import FilmByPerson
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get(
    "/search",
    response_model=list[PersonWithFilms],
    response_model_by_alias=False,
    description='Поиск фильмов.'
)
async def persons(
    query: str,
    page_size: Annotated[
        int, Query(description='Pagination page size', ge=1)] = 50,
    page_number: Annotated[
        int, Query(description='Pagination page number', ge=1)] = 1,
    person_service: PersonService = Depends(get_person_service),
) -> list[PersonWithFilms]:
    if page_size * page_number > 10000:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="page_size * page_number give more than 10000",
        )
    persons = await person_service.search(query, page_size, page_number)
    return persons


@router.get(
    "/{person_id}",
    response_model=PersonWithFilms,
    response_model_by_alias=False,
    description='Получить персону по uuid.'
)
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> PersonWithFilms:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return person


@router.get(
    "/{person_id}/film",
    response_model=list[FilmByPerson],
    response_model_by_alias=False,
    description='Получить фильмы персоны.'
)
async def person_filmss(
    person_id: str,
    page_size: Annotated[
        int, Query(description='Pagination page size', ge=1)] = 50,
    page_number: Annotated[
        int, Query(description='Pagination page number', ge=1)] = 1,
    person_service: PersonService = Depends(get_person_service),
) -> list[FilmByPerson]:
    if page_size * page_number > 10000:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="page_size * page_number give more than 10000",
        )
    films = await person_service.get_films(person_id, page_size, page_number)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return films
