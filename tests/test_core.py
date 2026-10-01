"""Тести для перевірки чистого функціонального ядра (pytest)."""

from copy import deepcopy

import pytest

from core import (
    Booking,
    calculate_base_cost,
    default_status_filter,
    make_booking_processor,
    with_total,
)


@pytest.fixture
def sample_bookings() -> list[Booking]:
    return [
        {
            "id": 1,
            "nights": 3,
            "price_per_night": 1000.0,
            "room_type": "standard",
            "status": "confirmed",
        },
        {
            "id": 2,
            "nights": 10,
            "price_per_night": 2000.0,
            "room_type": "suite",
            "status": "confirmed",
        },
        {
            "id": 3,
            "nights": 4,
            "price_per_night": 1500.0,
            "room_type": "deluxe",
            "status": "cancelled",
        },
    ]


def test_calculate_base_cost() -> None:
    booking: Booking = {
        "id": 1,
        "nights": 4,
        "price_per_night": 1250.0,
        "room_type": "standard",
        "status": "confirmed",
    }
    assert calculate_base_cost(booking) == 5000.0


def test_with_total_no_mutation() -> None:
    original: Booking = {
        "id": 1,
        "nights": 2,
        "price_per_night": 500.0,
        "room_type": "standard",
        "status": "confirmed",
    }
    original_copy = deepcopy(original)

    updated = with_total(original, base_cost=1000.0, total=1020.0)

    # Вихідний об'єкт не змінився
    assert original == original_copy
    assert "total" not in original
    # Отримано новий об'єкт із правильними даними
    assert updated["total"] == 1020.0
    assert updated["base_cost"] == 1000.0
    assert updated["id"] == original["id"]


def test_referential_transparency(sample_bookings: list[Booking]) -> None:
    """Перевірка референтної прозорості: однаковий вхід дає однаковий вихід."""
    processor = make_booking_processor(
        status_filter=default_status_filter,
        apply_discount=lambda cost, b: cost * 0.9,
        apply_tax=lambda cost, b: cost * 1.05,
    )

    result_1 = processor(sample_bookings)
    result_2 = processor(sample_bookings)

    assert result_1 == result_2


def test_no_input_mutation(sample_bookings: list[Booking]) -> None:
    """Перевірка повної відсутності мутацій вихідного списку."""
    original = deepcopy(sample_bookings)
    processor = make_booking_processor(
        status_filter=default_status_filter,
        apply_discount=lambda cost, b: cost,
        apply_tax=lambda cost, b: cost,
    )

    _ = processor(sample_bookings)
    assert sample_bookings == original


def test_callable_policies_and_filtering(
    sample_bookings: list[Booking],
) -> None:
    """Перевірка правильного застосування динамічних політик."""
    # Політика: знижка 200 грн на бронювання тривалістю понад 5 ночей, збір 50 грн фіксовано
    discount_policy = lambda cost, b: cost - 200.0 if b.get("nights", 0) > 5 else cost
    tax_policy = lambda cost, b: cost + 50.0

    processor = make_booking_processor(
        status_filter=lambda b: b.get("status") == "confirmed",
        apply_discount=discount_policy,
        apply_tax=tax_policy,
    )

    res = processor(sample_bookings)

    # Тільки 2 підтверджених бронювання мають потрапити до вибірки
    assert res["count"] == 2

    # Перевірка розрахунків:
    # Booking 1: 3 ночі * 1000 = 3000 -> знижка 0 -> +50 збір = 3050.0
    # Booking 2: 10 ночей * 2000 = 20000 -> знижка 200 = 19800 -> +50 збір = 19850.0
    # Разом: 3050 + 19850 = 22900.0
    assert res["revenue"] == 22900.0
