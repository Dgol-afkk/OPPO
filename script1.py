import abc
import os
import re
from datetime import datetime
from typing import List, Optional, Tuple

DATA_FILENAME = "data.txt"


class Property:

    def __init__(self, cost: int, owner: str, reg_date: datetime):
        if not isinstance(cost, int) or cost < 0:
            raise ValueError("Стоимость должна быть положительным целым числом.")
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("Владелец должен быть непустой строкой.")
        if not isinstance(reg_date, datetime):
            raise TypeError("Дата должна быть объектом datetime.")

        self.cost = cost
        self.owner = owner
        self.reg_date = reg_date

    def __str__(self) -> str:
        return (f"Недвижимость: {self.owner} | "
                f"{self.reg_date.strftime('%Y.%m.%d')} | "
                f"{self.cost} руб.")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Property):
            return False
        return (self.cost == other.cost and
                self.owner == other.owner and
                self.reg_date == other.reg_date)


class PropertyReader(abc.ABC):

    @abc.abstractmethod
    def read(self) -> List[Property]:
        pass


class FilePropertyReader(PropertyReader):
    def __init__(self, filename: str):
        self._filename = filename

        self._patterns = {
            'owner': re.compile(r'"([^"]*)"'),
            'date': re.compile(r'(\d{4}\.\d{2}\.\d{2})'),
            'cost': re.compile(r'(?<!\.)\b(\d+)\b(?!\.)')
        }

    def _parse_line(self, line: str) -> Optional[Property]:
        owner_match = self._patterns['owner'].search(line)
        date_match = self._patterns['date'].search(line)
        cost_match = self._patterns['cost'].search(line)

        if owner_match and date_match and cost_match:
            try:
                date_str = date_match.group(1)
                reg_date = datetime.strptime(date_str, '%Y.%m.%d')

                return Property(
                    cost=int(cost_match.group(1)),
                    owner=owner_match.group(1).strip(),
                    reg_date=reg_date
                )
            except (ValueError, TypeError):
                return None
        return None

    def read(self) -> List[Property]:
        if not os.path.exists(self._filename):
            print(f"Ошибка: файл '{self._filename}' не найден.")
            return []

        properties = []
        try:
            with open(self._filename, 'r', encoding='utf-8') as file:
                for line in file:
                    if line.strip():
                        parsed_object = self._parse_line(line.strip())
                        if parsed_object:
                            properties.append(parsed_object)
        except IOError as e:
            print(f"Ошибка при чтении файла: {e}")
            return []

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
        return [
            p for p in self._properties
            if min_cost <= p.cost <= max_cost
        ]

    def has_data(self) -> bool:
        return len(self._properties) > 0


class ConsoleUI:

    def __init__(self, service: PropertyService):
        self._service = service

    def _get_valid_int_input(self, prompt: str) -> int:
        while True:
            value = input(prompt)
            if value.isdigit():
                return int(value)
            print("Ошибка: введите целое положительное число.")

    def _get_price_range(self) -> Tuple[int, int]:
        min_price = self._get_valid_int_input("Введите минимальную стоимость: ")

        while True:
            max_price = self._get_valid_int_input("Введите максимальную стоимость: ")
            if max_price >= min_price:
                return min_price, max_price
            print("Ошибка: максимальная стоимость не может быть меньше минимальной.")

    def _display_list(self, properties: List[Property], title: str) -> None:
        print(title)
        if not properties:
            print("Список пуст.")
        else:
            for prop in properties:
                print(prop)

    def run(self) -> None:
        self._service.load_data()

        if not self._service.has_data():
            print("Не удалось загрузить данные или список пуст.")
            return

        while True:
            print("\n--- Меню ---")
            print("1. Показать все объекты (по дате)")
            print("2. Отфильтровать по стоимости")
            print("3. Выход")
            choice = input("Выберите действие: ")

            if choice == '1':
                data = self._service.get_all_sorted_by_date()
                self._display_list(data, "\n--- Полный список ---")
            elif choice == '2':
                min_p, max_p = self._get_price_range()
                data = self._service.filter_by_cost(min_p, max_p)
                self._display_list(data, f"\n--- Объекты от {min_p} до {max_p} ---")
            elif choice == '3':
                print("Выход.")
                break
            else:
                print("Неверный выбор.")


def main() -> None:
    file_reader = FilePropertyReader(DATA_FILENAME)
    service = PropertyService(file_reader)
    app = ConsoleUI(service)
    app.run()

if __name__ == "__main__":
    main()