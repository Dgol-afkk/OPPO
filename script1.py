import re
import os
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


def test_parse():
    """
    Тестирование функции parse на различных входных данных.
    """
    print("\n--- Запуск тестов для функции parse ---")

    test_cases = {
        'Корректная строка': 'Недвижимость: Владелец: "Иванов И.И.", Дата регистрации: 2022.01.15, Стоимость: 5000000 руб.',
        # Этот тест теперь вызовет ошибку, если не использовать try-except,
        # так как datetime.strptime не сможет обработать неверную дату.
        # 'Некорректная дата': 'Недвижимость: Владелец: "Петров П.П.", Дата регистрации: 2022-13-40, Стоимость: 7500000 руб.',
        'Некорректная стоимость (не число)': 'Недвижимость: Владелец: "Сидоров С.С.", Дата регистрации: 2023.05.20, Стоимость: много руб.',
        'Отсутствует владелец': 'Недвижимость: Дата регистрации: 2021.11.11, Стоимость: 3200000 руб.',
        'Пустая строка': ''
    }

    all_tests_passed = True
    for description, test_line in test_cases.items():
        result = parse(test_line)
        print(f"Тест: '{description}'")
        print(f"Вход: '{test_line}'")

        if description == 'Корректная строка':
            if result and result.owner == "Иванов И.И." and result.cost == 5000000:
                print("Результат: Успех, объект создан.")
            else:
                print("Результат: Ошибка, объект не был создан корректно.")
                all_tests_passed = False
        else:
            if result is None:
                print("Результат: Успех, функция вернула None, как и ожидалось.")
            else:
                print("Результат: Ошибка, функция должна была вернуть None.")
                all_tests_passed = False
        print("-" * 20)

    if all_tests_passed:
        print("Все тесты пройдены успешно!")
    else:
        print("Некоторые тесты не были пройдены.")
    print("--- Тестирование завершено ---\n")


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
    """
    Главная функция с меню для пользователя.
    """
    all_properties = load(DATA_FILENAME)

    if not all_properties:
        print("\nНе удалось загрузить данные или файл пуст.")
        choice = input("Хотите запустить тесты для функции parse? (y/n): ")
        if choice.lower() == 'y':
            test_parse()
        return

    while True:
        print("\n--- Меню ---")
        print("1. Показать все объекты (отсортированные по дате)")
        print("2. Отфильтровать по стоимости")
        print("3. Запустить тесты для функции parse")
        print("4. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            all_properties.sort(key=lambda prop: prop.datee, reverse=True)
            display_properties(
                all_properties,
                "\n--- Полный отсортированный список ---"
            )
        elif choice == '2':
            print("\n--- Фильтрация по стоимости ---")
            min_price, max_price = filter_min_max()
            filtered = filter_by_cost(all_properties, min_price, max_price)
            display_properties(
                filtered,
                f"\n--- Объекты стоимостью от {min_price} до {max_price} ---"
            )
        elif choice == '3':
            test_parse()
        elif choice == '4':
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Пожалуйста, введите число от 1 до 4.")


if __name__ == "__main__":
    main()