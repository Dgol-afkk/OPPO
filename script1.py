import re
from datetime import datetime
from typing import List, Optional, Tuple

DATA_FILENAME = "data.txt"


class Property:

    def __init__(self, cost: int, owner: str, datee: datetime):
        self.cost = cost
        self.owner = owner
        self.datee = datee

    def __str__(self) -> str:

        return (f"Недвижимость: "
                f"{self.owner} "
                f"{self.datee.strftime('%Y.%m.%d')} "
                f"{self.cost} руб.")


def parse(line: str) -> Optional[Property]:

    patterns = {
        'owner': r'"([^"]*)"',
        'date': r'(\d{4}\.\d{2}\.\d{2})',
        'cost': r'(\d+)'
    }

    owner_match = re.search(patterns['owner'], line)
    date_match = re.search(patterns['date'], line)
    cost_match = re.search(patterns['cost'], line)

    if owner_match and date_match and cost_match:
            date_str = date_match.group(1)
            reg_date = datetime.strptime(date_str, '%Y.%m.%d')
            return Property(
                owner=owner_match.group(1).strip(),
                datee=reg_date,
                cost=int(cost_match.group(1))
            )

    return None


def load(filename: str) -> List[Property]:

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

    while True:
        max_price_str = input("Введите максимальную стоимость: ")
        if max_price_str.isdigit():
            max_price = int(max_price_str)
            break



    return min_price, max_price


def filter_by_cost(properties: List[Property], min_cost: int, max_cost: int) -> List[Property]:
    filtered_list = []
    for obj in properties:
        if min_cost <= obj.cost <= max_cost:
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

    all = load(DATA_FILENAME)

    all.sort(key=lambda prop: prop.datee, reverse=True)
    display_properties(
        all,
        "\n--- Полный отсортированный список ---"
    )
    print("\n--- Фильтрация по стоимости ---")
    min_price, max_price = filter_min_max()
    filtered = filter_by_cost(all, min_price, max_price)
    display_properties(
        filtered,
        "\n--- Отфильтрованный по стоимости список ---"
    )



if __name__ == "__main__":
    main()