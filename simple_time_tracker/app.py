"""Веб-приложение."""

from typing import Annotated

from fastapi import Depends
from fastapi import FastAPI
from fastapi import Request
from fastapi.templating import Jinja2Templates

from simple_time_tracker import dependencies as dep
from simple_time_tracker.storage import Storage

app = FastAPI()

templates = Jinja2Templates(directory='simple_time_tracker/templates')


@app.get('/')
async def status(
    storage: Annotated[Storage, Depends(dep.get_storage)],
    request: Request,
    subject: str = 'Ребёнок',
    active_name: str = 'бодрствует',
    passive_name: str = 'спит',
    active_color: str = 'rgb(154,107,115)',
    passive_color: str = 'rgb(104,128,180)',
):
    """Вернуть страницу с отображением текущего статуса."""
    is_active, start = storage.get_state()
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'subject': subject,
            'active_name': active_name,
            'passive_name': passive_name,
            'active_color': active_color,
            'passive_color': passive_color,
            'is_active': is_active,
            'start': start,
        },
    )


@app.post('/')
async def change_state(
    storage: Annotated[Storage, Depends(dep.get_storage)],
    is_active: bool,
) -> dict:
    """Изменить текущее состояние."""
    storage.set_state(is_active)
    return {'message': f'changed to {is_active}'}
