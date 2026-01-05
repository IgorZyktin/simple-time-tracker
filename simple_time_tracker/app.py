"""Веб-приложение."""

from datetime import datetime
import logging
from typing import Annotated
from typing import Literal

from fastapi import Depends
from fastapi import FastAPI
from fastapi import Request
from fastapi.templating import Jinja2Templates

from simple_time_tracker import dependencies as dep
from simple_time_tracker.storage import Storage

app = FastAPI()
templates = Jinja2Templates(directory='simple_time_tracker/templates')
LOG = logging.getLogger(__name__)


@app.get('/simple-time-tracker')
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
    moment = datetime.now()  # noqa: DTZ005
    is_active, start = storage.get_state(moment)
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


@app.post('/simple-time-tracker')
async def change_state(
    storage: Annotated[Storage, Depends(dep.get_storage)],
    is_active: bool,
) -> dict:
    """Изменить текущее состояние."""
    moment = datetime.now()  # noqa: DTZ005
    previous_is_active, start = storage.get_state(moment)

    if is_active == previous_is_active:
        return {'message': f'no difference from {is_active}'}

    storage.set_state(is_active, moment)
    LOG.info('[%s] Setting is_active to %s', moment, is_active)
    return {'message': f'changed to {is_active}'}


@app.get('/stats')
async def stats(
    storage: Annotated[Storage, Depends(dep.get_storage)],
    request: Request,
    subject: str = 'Ребёнок',
    active_name: str = 'бодрствует',
    passive_name: str = 'спит',
    active_color: str = 'rgb(252,3,3)',
    passive_color: str = 'rgb(3,182,252)',
    unknown_color: str = 'rgb(119,119,119)',
    highlight: Literal['active', 'passive'] = 'passive',
    days: int = 7,
):
    """Вывести статистику."""
    month_map = {
        1: 'января',
        2: 'февраля',
        3: 'марта',
        4: 'апреля',
        5: 'мая',
        6: 'июня',
        7: 'июля',
        8: 'августа',
        9: 'сентября',
        10: 'октября',
        11: 'ноября',
        12: 'декабря',
    }

    _stats = storage.gather_stats(days=days)
    return templates.TemplateResponse(
        request=request,
        name='stats.html',
        context={
            'stats': _stats,
            'subject': subject,
            'active_name': active_name,
            'passive_name': passive_name,
            'active_color': active_color,
            'passive_color': passive_color,
            'unknown_color': unknown_color,
            'highlight': highlight,
            'days': days,
            'month_map': month_map,
        },
    )
