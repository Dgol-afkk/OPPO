import abc
import os
import re
import sys
from datetime import datetime
from typing import List, Optional, Tuple

DATA_FILENAME = "data.txt"


class Property:

    def __init__(self, cost: int, owner: str, reg_date: datetime):
        self._validate(cost, owner, reg_date)
        self.cost = cost
        self.owner = owner
        self.reg_date = reg_date

    def _validate(self, cost: int, owner: str, reg_date: datetime):
        if not isinstance(cost, int) or cost < 0:
            raise ValueError("Стоимость должна быть положительным целым числом.")
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("Владелец должен быть непустой строкой.")
        if not isinstance(reg_date, datetime):
            raise TypeError("Дата должна быть объектом datetime.")

    def __str__(self) -> str:
        return (f"{self.owner:<30} | "
                f"{self.reg_date.strftime('%d.%m.%Y')} | "
                f"{self.cost:>12,} руб.".replace(',', ' '))

    def __repr__(self):
        return f"Property(cost={self.cost}, owner='{self.owner}', reg_date={self.reg_date})"


class PropertyReader(abc.ABC):

    @abc.abstractmethod
    def read(self) -> List[Property]:
        pass


class FilePropertyReader(PropertyReader):

    def __init__(self, filename: str):
        self._filename = filename

        self._patterns = {
            'owner': re.compile(r'"([^"]+)"'),
            'date': re.compile(r'\b(\d{4}\.\d{2}\.\d{2})\b'),
            'cost': re.compile(r'(?<!\.)\b(\d+)\b(?!\.)')
        }

    def _parse_line(self, line: str, line_num: int) -> Optional[Property]:

        owner_match = self._patterns['owner'].search(line)
        date_match = self._patterns['date'].search(line)
        cost_match = self._patterns['cost'].search(line)

        if not (owner_match and date_match and cost_match):
            print(f"[Предупреждение] Строка {line_num}: Неполные данные -> {line.strip()}", file=sys.stderr)
            return None

        try:
            date_str = date_match.group(1)
            reg_date = datetime.strptime(date_str, '%Y.%m.%d')

            cost = int(cost_match.group(1))
            owner = owner_match.group(1).strip()

            return Property(cost=cost, owner=owner, reg_date=reg_date)

        except ValueError as e:
            print(f"[Ошибка данных] Строка {line_num}: {e} -> {line.strip()}", file=sys.stderr)
            return None

    def read(self) -> List[Property]:
        if not os.path.exists(self._filename):
            raise FileNotFoundError(f"Файл '{self._filename}' не найден.")

        properties = []
        try:
            with open(self._filename, 'r', encoding='utf-8') as file:
                for idx, line in enumerate(file, start=1):
                    if line.strip():  # Пропускаем пустые строки
                        prop = self._parse_line(line, idx)
                        if prop:
                            properties.append(prop)
        except IOError as e:
            raise IOError(f"Ошибка ввода-вывода: {e}")

        return properties


class PropertyService:

    def __init__(self, reader: PropertyReader):
        self._reader = reader
        self._properties: List[Property] = []

    def load_data(self) -> None:
        self._properties = self._reader.read()

    def get_all_sorted_by_date(self) -> List[Property]:
        return sorted(self._properties, key=lambda p: p.reg_date, reverse=True)

    def filter_by_cost(self, min_cost: int, max_cost: int) -> List[Property]:
        return [p for p in self._properties if min_cost <= p.cost <= max_cost]

    def has_data(self) -> bool:
        return len(self._properties) > 0


class ConsoleUI:

    def __init__(self, service: PropertyService):
        self._service = service

    def _get_valid_int(self, prompt: str) -> int:
        while True:
            val = input(prompt).strip()
            val_clean = val.replace(" ", "")
            if val_clean.isdigit():
                return int(val_clean)
            print("Пожалуйста, введите целое неотрицательное число.")

    def run(self):
        try:
            self._service.load_data()
            if not self._service.has_data():
                print("Файл был прочитан, но валидных записей не найдено.")
                return
            else:
                print("Данные успешно загружены.")
        except FileNotFoundError:
            print(f"Критическая ошибка: Файл '{DATA_FILENAME}' не найден рядом со скриптом.")
            return
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return

        while True:
            print("1. Показать все записи (по дате)")
            print("2. Фильтр по стоимости")
            print("3. Выход")

            choice = input("Ваш выбор: ").strip()

            if choice == '1':
                items = self._service.get_all_sorted_by_date()
                print("\n--- Все записи ---")
                for item in items:
                    print(item)

            elif choice == '2':
                min_p = self._get_valid_int("Минимальная цена: ")
                max_p = self._get_valid_int("Максимальная цена: ")

                if max_p < min_p:
                    print("Ошибка: Максимальная цена меньше минимальной.")
                    continue

                items = self._service.filter_by_cost(min_p, max_p)
                print(f"\n--- Найдено записей: {len(items)} ---")
                for item in items:
                    print(item)

            elif choice == '3':
                print("Работа завершена.")
                break
            else:
                print("Неверный пункт меню.")


def main():
    reader = FilePropertyReader(DATA_FILENAME)
    service = PropertyService(reader)
    app = ConsoleUI(service)
    app.run()


if __name__ == "__main__":
    main()