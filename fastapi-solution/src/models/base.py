import orjson

from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class MyBaseModel(BaseModel):
    uuid: str = Field(alias="id")

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        populate_by_name = True
