import pathlib
import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.dataclasses import dataclass
from pydantic import Field


BASE_DIR = pathlib.Path(__file__).parent.resolve()


class PgSettings(BaseSettings):
    dbname: str = Field("movies_database", alias="DB_NAME")
    user: str = Field("user", alias="DB_USER")
    password: str = Field("pass", alias="DB_PASSWORD")
    host: str = Field("127.0.0.1", alias="DB_HOST")
    port: int = Field(5432, alias="DB_PORT")

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


class EsSettings(BaseSettings):
    host: str = Field("127.0.0.1", alias="ELASTIC_HOST")
    port: int = Field(9200, alias="ELASTIC_PORT")
    scheme: str = "http"

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Settings(BaseSettings):
    scheme: str = "http"
    index_name: list = ["movies", "genres", "persons"]
    json_path: str = "state.json"
    log_path: str = "logs/main_log.log"
    sleep_time: int = 10
    max_tries: int = 7
    max_time: int = 25

    pg: PgSettings = PgSettings()
    es: EsSettings = EsSettings()

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
