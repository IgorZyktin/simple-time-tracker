"""Точка входа."""

import os

import uvicorn

from simple_time_tracker.app import app


def main():
    """Точка входа."""
    uvicorn.run(
        app,
        host='0.0.0.0' if os.name != 'nt' else '127.0.0.1',
        port=7070,
    )


if __name__ == '__main__':
    main()
