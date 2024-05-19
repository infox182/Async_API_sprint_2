from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.genre import Genre
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get("/", response_model=list[Genre], response_model_by_alias=False)
async def genres(
    genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    return await genre_service.get_all()


@router.get("/{genre_id}", response_model=Genre, response_model_by_alias=False)
async def genre_details(
    genre_id: str, genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
    return genre
