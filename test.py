import pytest
from datetime import datetime
from script1 import parse, Property, filter_by_cost

class TestParser:

    def test_valid_parse(self):
        raw_line = 'Недвижимость: Владелец: "Иванов И.И.", Дата регистрации: 2022.01.15, Стоимость: 5000000 руб.'
        result = parse(raw_line)

        assert result is not None
        assert result.sOwner == "Иванов И.И."
        assert result.iCost == 5000000
        assert result.dtRegDate == datetime(2022, 1, 15)

    def test_invalid_date_format(self):
        raw_line = 'Недвижимость: Владелец: "Петров", Дата: 2022-99-99, Стоимость: 100 руб.'
        assert parse(raw_line) is None

    def test_missing_data(self):
        raw_line = 'Недвижимость: Дата регистрации: 2021.11.11, Стоимость: 3200000 руб.'
        assert parse(raw_line) is None

    def test_garbage_string(self):
        assert parse("") is None
        assert parse("Просто набор слов") is None

class TestPropertyValidation:

    def test_create_valid_property(self):
        prop = Property(iCost=100, sOwner="Test", dtRegDate=datetime.now())
        assert prop.iCost == 100

    def test_invalid_cost_type(self):
        with pytest.raises(ValueError):
            Property(iCost="100", sOwner="Test", dtRegDate=datetime.now())

    def test_negative_cost(self):
        with pytest.raises(ValueError):
            Property(iCost=-500, sOwner="Test", dtRegDate=datetime.now())

    def test_empty_owner(self):
        with pytest.raises(ValueError):
            Property(iCost=100, sOwner="   ", dtRegDate=datetime.now())


class TestBusinessLogic:

    @pytest.fixture
    def properties_list(self):
        return [
            Property(iCost=5_400_000, sOwner="Min Price Owner", dtRegDate=datetime(2020, 1, 1)),
            Property(iCost=30_000_000, sOwner="Middle Price Owner", dtRegDate=datetime(2023, 6, 15)),
            Property(iCost=67_000_000, sOwner="Max Price Owner", dtRegDate=datetime(2021, 12, 31)),
        ]

    def test_filter_exact_min_boundary(self, properties_list):
        result = filter_by_cost(properties_list, 5_400_000, 5_400_000)
        assert len(result) == 1
        assert result[0].sOwner == "Min Price Owner"
        assert result[0].iCost == 5_400_000

    def test_filter_exact_max_boundary(self, properties_list):
        result = filter_by_cost(properties_list, 60_000_000, 67_000_000)

        assert len(result) == 1
        assert result[0].sOwner == "Max Price Owner"
        assert result[0].iCost == 67_000_000

    def test_filter_middle_range(self, properties_list):
        result = filter_by_cost(properties_list, 10_000_000, 50_000_000)

        assert len(result) == 1
        assert result[0].sOwner == "Middle Price Owner"

    def test_filter_below_minimum(self, properties_list):
        result = filter_by_cost(properties_list, 0, 5_000_000)
        assert len(result) == 0

    def test_filter_all_inclusive(self, properties_list):
        result = filter_by_cost(properties_list, 5_000_000, 70_000_000)
        assert len(result) == 3

    def test_sorting_by_date_descending(self, properties_list):
        properties_list.sort(key=lambda prop: prop.dtRegDate, reverse=True)

        assert properties_list[0].dtRegDate.year == 2023
        assert properties_list[0].sOwner == "Middle Price Owner"
        assert properties_list[1].dtRegDate.year == 2021
        assert properties_list[1].sOwner == "Max Price Owner"
        assert properties_list[2].dtRegDate.year == 2020
        assert properties_list[2].sOwner == "Min Price Owner"