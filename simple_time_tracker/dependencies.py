"""Зависимости приложения."""

import functools

from simple_time_tracker.storage import Storage


@functools.lru_cache
def get_storage() -> Storage:
    """Получить экземпляр хранилища данных."""
    return Storage()
