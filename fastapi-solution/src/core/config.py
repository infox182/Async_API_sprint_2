from logging import config as logging_config
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = Field("project name", alias="PROJECT_NAME")
    
    es_host: str = Field("127.0.0.1", alias="ELASTIC_HOST")
    es_port: int = Field(9200, alias="ELASTIC_PORT")

    redis_host: str = Field("127.0.0.1", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")


settings = Settings()
