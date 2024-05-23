import abc
import json
import os
from typing import Any, Dict


class BaseStorage(abc.ABC):

    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""

    @abc.abstractmethod
    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""


class JsonFileStorage(BaseStorage):

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        if not os.path.exists(file_path):
            with open(self.file_path, "w") as f:
                json.dump({}, f)

    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""
        new_state = self.retrieve_state()
        new_state.update(state)
        with open(self.file_path, "w") as f:
            json.dump(new_state, f)

    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""
        with open(self.file_path, "r") as f:
            return json.load(f)


class State:

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа."""
        state = {key: value}
        self.storage.save_state(state)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу."""
        state = self.storage.retrieve_state()
        return state.get(key)
