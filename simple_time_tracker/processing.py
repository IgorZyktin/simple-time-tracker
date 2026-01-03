"""Инструменты по работе с данными."""

from dataclasses import dataclass
from datetime import date
from datetime import datetime
from datetime import timedelta
import itertools


@dataclass
class Minute:
    """Модель минуты."""

    moment: datetime
    is_active: bool | None


class Day:
    """Данные по одному дню."""

    def __init__(self, minutes: list[Minute]) -> None:
        """Инициализировать экземпляр."""
        self.minutes = minutes

    @property
    def total_active(self) -> str:
        """Вернуть сумму активных минут."""
        return human_readable_time(
            sum(1 for each in self.minutes if each.is_active) * 60
        )

    @property
    def total_passive(self) -> str:
        """Вернуть сумму пассивных минут."""
        return human_readable_time(
            sum(
                1
                for each in self.minutes
                if not each.is_active and each.is_active is not None
            ) * 60
        )


def to_minutes(raw_starts: list[tuple[datetime, bool]]) -> list[Minute]:
    """Сформировать минуты из стартовых моментов.

    Пример выходных данных:
    [
        Minute(moment=datetime.datetime(2026, 1, 2, 0, 14), is_active=True),
        Minute(moment=datetime.datetime(2026, 1, 2, 0, 15), is_active=True),
        Minute(moment=datetime.datetime(2026, 1, 2, 0, 16), is_active=True),
        Minute(moment=datetime.datetime(2026, 1, 2, 0, 17), is_active=True),
        Minute(moment=datetime.datetime(2026, 1, 2, 0, 18), is_active=True),
        ...
    ]
    """
    minutes: list[Minute] = []

    for (l_start, l_active), (r_start, r_active) in itertools.pairwise(
        raw_starts
    ):
        moment = l_start.replace(second=0, microsecond=0)
        while moment < r_start:
            minutes.append(Minute(moment=moment, is_active=l_active))
            moment += timedelta(minutes=1)

    return minutes


def group_minutes_by_days(minutes: list[Minute]) -> dict[date, list[Minute]]:
    """Разложить минуты по датам.

    Пример выходных данных:
    {
        datetime.date(2026, 1, 2): [
            Minute(moment=datetime.datetime(2026, 1, 2, 0, 14), is_active=True),
            ...
        ],
    }
    """
    result: dict[date, list[Minute]] = {}

    for minute in minutes:
        _date = minute.moment.date()

        if _date in result:
            result[_date].append(minute)
        else:
            result[_date] = [minute]

    return result


def spread_minutes(
    by_day: dict[date, list[Minute]],
) -> dict[date, list[Minute]]:
    """Заполнить пустые минуты в сутках."""
    result: dict[date, list[Minute]] = {}

    for _date, minutes in by_day.items():
        array: list[Minute] = []

        for hour in range(24):
            for minute in range(60):
                array.append(
                    Minute(
                        moment=datetime(
                            _date.year, _date.month, _date.day, hour, minute
                        ),
                        is_active=None,
                    )
                )

        for minute in minutes:
            index = minute.moment.hour * 60 + minute.moment.minute
            array[index] = minute

        result[_date] = array

    return result


def wrap_days(by_day: dict[date, list[Minute]]) -> dict[date, Day]:
    """Обернуть данные по минутам во вспомогательный класс."""
    return {_date: Day(minutes=minutes) for _date, minutes in by_day.items()}


def human_readable_time(seconds: float) -> str:
    """Отформатировать время в человекочитаемом виде.

    >>> human_readable_time(46551387)
    '76н 6д 18ч 56м 27с'
    >>> human_readable_time(600)
    '10м'
    """
    if seconds < 1:
        return '0с'

    _weeks = 0
    _days = 0
    _hours = 0
    _minutes = 0
    _seconds = 0
    _suffixes = ('н', 'д', 'ч', 'м', 'с')

    if seconds > 0:
        _minutes, _seconds = divmod(int(round(seconds)), 60)  # noqa: RUF046
        _hours, _minutes = divmod(_minutes, 60)
        _days, _hours = divmod(_hours, 24)
        _weeks, _days = divmod(_days, 7)

    return ' '.join(
        f'{x}{_suffixes[i]}'
        for i, x in enumerate([_weeks, _days, _hours, _minutes, _seconds])
        if x
    )
