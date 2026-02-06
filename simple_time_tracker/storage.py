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
        metric_id: str,
    ) -> None:
        """Поменять текущее состояние."""
        filename = self.path / (moment.strftime('%Y-%m') + '.csv')

        timestamp = moment.isoformat().replace(':', '-')
        with open(filename, mode='a') as file:
            file.write(f'{timestamp},{int(is_active)},{metric_id}\n')

    def get_state(
        self,
        moment: datetime,
        metric_id: str,
    ) -> tuple[bool, datetime]:
        """Вернуть текущее состояние."""
        files = [
            str(x)
            for x in os.listdir(self.path.absolute())
            if str(x).endswith('.csv')
        ]

        files.sort()

        if not files:
            return False, moment

        last_file = files[-1]

        with open(self.path / last_file) as file:
            reader = csv.reader(file)
            last_line = None

            for line in reader:  # noqa: B007
                if len(line) >= 3:
                    _, _, line_metric_id, *_ = line
                else:
                    line_metric_id = '1'

                if line_metric_id == metric_id:
                    last_line = line

            if last_line is None:
                return False, moment

            str_timestamp, str_is_active, *_ = line

            timestamp = datetime.strptime(  # noqa: DTZ007
                str_timestamp,
                '%Y-%m-%dT%H-%M-%S.%f',
            )
            return bool(int(str_is_active)), timestamp

    def gather_stats(
        self,
        now: datetime,
        metric_id: str,
        days: int,
    ) -> dict[date, processing.Day]:
        """Сформировать статистический отчёт.

        Формат данных:
         {
            <день1>: <данные по дню>,
            <день2>: <данные по дню>,
            ...
         }
        """
        raw_starts = self._gather_raw_starts(days, metric_id)
        raw_starts.append((now, None))
        minutes = processing.to_minutes(raw_starts)
        by_days = processing.group_minutes_by_days(minutes)
        spread = processing.spread_minutes(by_days)
        wrapped = processing.wrap_days(spread)
        return wrapped

    def _gather_raw_starts(self, days: int, metric_id: str) -> list[tuple[datetime, bool | None]]:
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
        files.sort()
        lines: list[tuple[datetime, bool]] = []

        for filename in files[:days]:
            with open(self.path / filename) as file:
                reader = csv.reader(file)
                for line in reader:
                    if len(line) >= 3:
                        str_timestamp, str_is_active, line_metric_id, *_ = line
                    else:
                        str_timestamp, str_is_active = line
                        line_metric_id = '1'

                    if line_metric_id == metric_id:
                        timestamp = datetime.strptime(  # noqa: DTZ007
                            str_timestamp,
                            '%Y-%m-%dT%H-%M-%S.%f',
                        )
                        is_active = bool(int(str_is_active))
                        lines.append((timestamp, is_active))

        return lines
