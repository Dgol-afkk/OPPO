import pytest
from datetime import datetime
from typing import List

from script1 import Property, FilePropertyReader, PropertyService, PropertyReader


class TestPropertyValidation:

    def test_create_valid_property(self):
        prop = Property(cost=100, owner="Test", reg_date=datetime.now())
        assert prop.cost == 100
        assert prop.owner == "Test"

    def test_invalid_cost_type(self):
        with pytest.raises(ValueError):
            Property(cost="100", owner="Test", reg_date=datetime.now())  # type: ignore

    def test_negative_cost(self):
        with pytest.raises(ValueError):
            Property(cost=-500, owner="Test", reg_date=datetime.now())

    def test_empty_owner(self):
        with pytest.raises(ValueError):
            Property(cost=100, owner="   ", reg_date=datetime.now())

    def test_invalid_date_type(self):
        with pytest.raises(TypeError):
            Property(cost=100, owner="Owner", reg_date="2022-01-01")  # type: ignore


class TestParser:

    @pytest.fixture
    def reader(self):
        return FilePropertyReader("dummy.txt")

    def test_valid_parse(self, reader):
        raw_line = 'Недвижимость: Владелец: "Иванов И.И.", Дата регистрации: 2022.01.15, Стоимость: 5000000 руб.'
        result = reader._parse_line(raw_line, 1)

        assert result is not None
        assert result.owner == "Иванов И.И."
        assert result.cost == 5000000
        assert result.reg_date == datetime(2022, 1, 15)

    def test_flexible_order(self, reader):
        raw_line = '2023.10.05 15000000 руб "Сидоров А.А."'
        result = reader._parse_line(raw_line, 1)

        assert result is not None
        assert result.owner == "Сидоров А.А."


    def test_invalid_date_format(self, reader, capsys):
        raw_line = 'Владелец: "Петров", Дата: 2022-05-20, Стоимость: 100 руб.'
        assert reader._parse_line(raw_line, 1) is None

        captured = capsys.readouterr()
        assert "[Предупреждение]" in captured.err

    def test_missing_quotes_owner(self, reader, capsys):
        raw_line = 'Владелец: Петров, Дата: 2022.05.20, Стоимость: 100'
        assert reader._parse_line(raw_line, 1) is None

        captured = capsys.readouterr()
        assert "[Предупреждение]" in captured.err

    def test_missing_data(self, reader, capsys):
        raw_line = 'Недвижимость: Дата регистрации: 2021.11.11, Стоимость: 3200000 руб.'
        assert reader._parse_line(raw_line, 1) is None

        captured = capsys.readouterr()
        assert "[Предупреждение]" in captured.err

    def test_garbage_string(self, reader, capsys):
        assert reader._parse_line("", 1) is None

        assert reader._parse_line("Просто набор слов без цифр и кавычек", 1) is None
        captured = capsys.readouterr()
        assert "[Предупреждение]" in captured.err


class MockReader(PropertyReader):
    def __init__(self, data: List[Property]):
        self._data = data

    def read(self) -> List[Property]:
        return self._data


class TestBusinessLogic:

    @pytest.fixture
    def properties_list(self):
        return [
            Property(cost=5_400_000, owner="Min Price Owner", reg_date=datetime(2020, 1, 1)),
            Property(cost=30_000_000, owner="Middle Price Owner", reg_date=datetime(2023, 6, 15)),
            Property(cost=67_000_000, owner="Max Price Owner", reg_date=datetime(2021, 12, 31)),
        ]

    @pytest.fixture
    def service(self, properties_list):
        mock_reader = MockReader(properties_list)
        svc = PropertyService(mock_reader)
        svc.load_data()
        return svc

    def test_filter_exact_min_boundary(self, service):
        result = service.filter_by_cost(5_400_000, 5_400_000)
        assert len(result) == 1
        assert result[0].owner == "Min Price Owner"
        assert result[0].cost == 5_400_000

    def test_filter_exact_max_boundary(self, service):
        result = service.filter_by_cost(60_000_000, 67_000_000)
        assert len(result) == 1
        assert result[0].owner == "Max Price Owner"
        assert result[0].cost == 67_000_000

    def test_filter_middle_range(self, service):
        result = service.filter_by_cost(10_000_000, 50_000_000)
        assert len(result) == 1
        assert result[0].owner == "Middle Price Owner"

    def test_filter_below_minimum(self, service):
        result = service.filter_by_cost(0, 5_000_000)
        assert len(result) == 0

    def test_filter_all_inclusive(self, service):
        result = service.filter_by_cost(5_000_000, 70_000_000)
        assert len(result) == 3

    def test_sorting_by_date_descending(self, service):
        sorted_list = service.get_all_sorted_by_date()

        # 1. 2023 (Middle)
        assert sorted_list[0].reg_date.year == 2023
        assert sorted_list[0].owner == "Middle Price Owner"

        # 2. 2021 (Max)
        assert sorted_list[1].reg_date.year == 2021
        assert sorted_list[1].owner == "Max Price Owner"

        # 3. 2020 (Min)
        assert sorted_list[2].reg_date.year == 2020
        assert sorted_list[2].owner == "Min Price Owner"