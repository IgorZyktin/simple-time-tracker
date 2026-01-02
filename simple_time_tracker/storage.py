"""Вспомогательный класс для хранения данных."""

from datetime import datetime
from pathlib import Path


class Storage:
    """Вспомогательный класс для хранения данных."""

    def __init__(self, path: str = '.') -> None:
        """Инициализировать экземпляр."""
        self.path = Path(path)
        self._is_active = False
        self._last_change = datetime.now()

    def set_state(self, is_active: bool) -> None:
        """Поменять текущее состояние."""
        self._is_active = is_active
        self._last_change = datetime.now()

    def get_state(self) -> tuple[bool, datetime]:
        """Вернуть текущее состояние."""
        return self._is_active, self._last_change
