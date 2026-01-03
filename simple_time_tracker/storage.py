"""Вспомогательный класс для хранения данных."""

import csv
from datetime import date
from datetime import datetime
import os
from pathlib import Path

from simple_time_tracker import processing


class Storage:
    """Вспомогательный класс для хранения данных."""

    def __init__(self, path: str = './data') -> None:
        """Инициализировать экземпляр."""
        self.path = Path(path)
        self.path.mkdir(exist_ok=True)

    def set_state(
        self,
        is_active: bool,
        moment: datetime,
    ) -> None:
        """Поменять текущее состояние."""
        filename = self.path / (moment.strftime('%Y-%m') + '.csv')

        timestamp = moment.isoformat().replace(':', '-')
        with open(filename, mode='a') as file:
            file.write(f'{timestamp},{int(is_active)}\n')

    def get_state(
        self,
        moment: datetime,
    ) -> tuple[bool, datetime]:
        """Вернуть текущее состояние."""
        files = [
            str(x)
            for x in os.listdir(self.path.absolute())
            if str(x).endswith('.csv')
        ]

        if not files:
            return False, moment

        last_file = files[-1]

        with open(self.path / last_file) as file:
            reader = csv.reader(file)
            line = None

            for line in reader:  # noqa: B007
                pass

            if line is None:
                return False, moment

            str_timestamp, str_is_active = line
            timestamp = datetime.strptime(  # noqa: DTZ007
                str_timestamp,
                '%Y-%m-%dT%H-%M-%S.%f',
            )
            return bool(int(str_is_active)), timestamp

    def gather_stats(self, days: int) -> dict[date, processing.Day]:
        """Сформировать статистический отчёт.

        Формат данных:
         {
            <день1>: <данные по дню>,
            <день2>: <данные по дню>,
            ...
         }
        """
        raw_starts = self._gather_raw_starts(days)
        minutes = processing.to_minutes(raw_starts)
        by_days = processing.group_minutes_by_days(minutes)
        spread = processing.spread_minutes(by_days)
        wrapped = processing.wrap_days(spread)
        return wrapped

    def _gather_raw_starts(self, days: int) -> list[tuple[datetime, bool]]:
        """Собрать все стартовые моменты за указанное число дней.

        Пример выходных данных:
        [
            (datetime.datetime(2026, 1, 2, 0, 14, 18, 163403), True),
            (datetime.datetime(2026, 1, 2, 1, 14, 26, 30100), False),
            (datetime.datetime(2026, 1, 2, 2, 14, 33, 171775), True),
            (datetime.datetime(2026, 1, 2, 3, 14, 35, 450103), False),
            (datetime.datetime(2026, 1, 2, 4, 15, 40, 314086), True),
            ...
        ]
        """
        files = [
            str(x)
            for x in os.listdir(self.path.absolute())
            if str(x).endswith('.csv')
        ]

        lines: list[tuple[datetime, bool]] = []

        for filename in files[:days]:
            with open(self.path / filename) as file:
                reader = csv.reader(file)
                for str_timestamp, str_is_active in reader:
                    timestamp = datetime.strptime(  # noqa: DTZ007
                        str_timestamp,
                        '%Y-%m-%dT%H-%M-%S.%f',
                    )
                    is_active = bool(int(str_is_active))
                    lines.append((timestamp, is_active))

        return lines
