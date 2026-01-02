"""Вспомогательный класс для хранения данных."""

import csv
from datetime import datetime
import os
from pathlib import Path


class Storage:
    """Вспомогательный класс для хранения данных."""

    def __init__(self, path: str = './data') -> None:
        """Инициализировать экземпляр."""
        self.path = Path(path)
        self.path.mkdir(exist_ok=True)

    def set_state(self, is_active: bool) -> None:
        """Поменять текущее состояние."""
        moment = datetime.now()  # noqa: DTZ005
        filename = self.path / (moment.strftime('%Y-%m') + '.csv')

        timestamp = moment.isoformat().replace(':', '-')
        with open(filename, mode='a') as file:
            file.write(f'{timestamp},{int(is_active)}\n')

    def get_state(self) -> tuple[bool, datetime]:
        """Вернуть текущее состояние."""
        files = [
            str(x)
            for x in os.listdir(self.path.absolute())
            if str(x).endswith('.csv')
        ]
        moment = datetime.now()  # noqa: DTZ005

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
