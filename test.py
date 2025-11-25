import pytest
from datetime import datetime
from script1 import parse, Property


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

