from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.genres import Genre
from services.genres import GenreService, get_genre_service

router = APIRouter()


@router.get("/",
            response_model=list[Genre],
            response_model_by_alias=False,
            summary="Cписок жанров",
            description="Получить список жанров",
            response_description="Названия и uuid жанров")
async def genres(
    genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    return await genre_service.get_all()


@router.get("/{genre_id}",
            response_model=Genre,
            response_model_by_alias=False,
            summary="Получить жанр",
            description="Получить информацию о жанре по uuid",
            response_description="Информация о жанре")
async def genre_details(
    genre_id: str, genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="genre not found")
    return genre
