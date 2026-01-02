"""Зависимости приложения."""

import functools

from storage import Storage


@functools.lru_cache
def get_storage() -> Storage:
    """Получить экземпляр хранилища данных."""
    return Storage()
