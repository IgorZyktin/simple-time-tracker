"""Точка входа."""

import uvicorn

from simple_time_tracker import app


def main():
    """Точка входа."""
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=7070,
    )


if __name__ == '__main__':
    main()
