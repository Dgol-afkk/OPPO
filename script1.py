import re
import os
from datetime import datetime
from typing import List, Optional, Tuple

DATA_FILENAME = "data.txt"


class Property:
    def __init__(self, iCost: int, sOwner: str, dtRegDate: datetime):
        if not isinstance(iCost, int) or iCost < 0:
            raise ValueError("Стоимость (iCost) должна быть положительным целым числом")

        if not isinstance(sOwner, str) or not sOwner.strip():
            raise ValueError("Владелец (sOwner) должен быть непустой строкой")

        if not isinstance(dtRegDate, datetime):
            raise TypeError("Дата (dtRegDate) должна быть объектом datetime")


        self.iCost = iCost
        self.sOwner = sOwner
        self.dtRegDate = dtRegDate

    def __str__(self) -> str:
        return (f"Недвижимость: "
                f"{self.sOwner} "
                f"{self.dtRegDate.strftime('%Y.%m.%d')} "
                f"{self.iCost} руб.")


    def __eq__(self, other):
        if not isinstance(other, Property):
            return False
        return (self.iCost == other.iCost and
                self.sOwner == other.sOwner and
                self.dtRegDate == other.dtRegDate)


def parse(line: str) -> Optional[Property]:

    patterns = {
        'owner': r'"([^"]*)"',
        'date': r'(\d{4}\.\d{2}\.\d{2})',
        'cost': r'(?<!\.)\b(\d+)\b(?!\.)'
    }

    owner_match = re.search(patterns['owner'], line)
    date_match = re.search(patterns['date'], line)
    cost_match = re.search(patterns['cost'], line)

    if owner_match and date_match and cost_match:
        try:
            date_str = date_match.group(1)
            reg_date = datetime.strptime(date_str, '%Y.%m.%d')

            return Property(
                iCost=int(cost_match.group(1)),
                sOwner=owner_match.group(1).strip(),
                dtRegDate=reg_date
            )
        except (ValueError, TypeError):
            return None

    return None

def load(filename: str) -> List[Property]:
    if not os.path.exists(filename):
        print(f"Ошибка: файл '{filename}' не найден. Убедитесь, что он существует.")
        return []

    properties = []

    with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    parsed_object = parse(line.strip())
                    if parsed_object:
                        properties.append(parsed_object)

    return properties


def filter_min_max() -> Tuple[int, int]:
    while True:
        min_price_str = input("Введите минимальную стоимость: ")
        if min_price_str.isdigit():
            min_price = int(min_price_str)
            break
        else:
            print("Ошибка: введите целое положительное число.")

    while True:
        max_price_str = input("Введите максимальную стоимость: ")
        if max_price_str.isdigit():
            max_price = int(max_price_str)
            if max_price < min_price:
                print("Ошибка: максимальная стоимость не может быть меньше минимальной.")
                continue
            break
        else:
            print("Ошибка: введите целое положительное число.")

    return min_price, max_price


def filter_by_cost(properties: List[Property], min_cost: int, max_cost: int) -> List[Property]:
    filtered_list = []
    for obj in properties:
        if min_cost <= obj.iCost <= max_cost:
            filtered_list.append(obj)
    return filtered_list


def display_properties(properties: List[Property], title: str) -> None:
    print(title)
    if not properties:
        print("В списке нет объектов, соответствующих критериям.")
    else:
        for prop in properties:
            print(prop)


def main() -> None:
    all_properties = load(DATA_FILENAME)

    if not all_properties:
        print("\nНе удалось загрузить данные или файл пуст.")
        return

    while True:
        print("\n--- Меню ---")
        print("1. Показать все объекты")
        print("2. Отфильтровать по стоимости")
        print("3. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            all_properties.sort(key=lambda prop: prop.dtRegDate, reverse=True)
            display_properties(all_properties, "\n--- Полный список ---")
        elif choice == '2':
            min_price, max_price = filter_min_max()
            filtered = filter_by_cost(all_properties, min_price, max_price)
            display_properties(filtered, f"\n--- Объекты от {min_price} до {max_price} ---")
        elif choice == '3':
            print("Выход.")
            break
        else:
            print("Неверный выбор.")


if __name__ == "__main__":
    main()