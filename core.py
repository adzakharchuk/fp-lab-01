"""Чисте ядро обробки бронювань готелю (Варіант №5)."""

from collections.abc import Callable, Iterable
from typing import TypedDict


class Booking(TypedDict, total=False):
    """Словник опису бронювання готелю."""

    id: int
    nights: int
    price_per_night: float
    room_type: str
    status: str  # наприклад, 'confirmed', 'cancelled', 'pending'
    base_cost: float
    total: float  # підсумкова вартість після розрахунку


# Визначення функціональних типів (Callable) для політик
SubtotalFn = Callable[[Booking], float]
DiscountFn = Callable[[float, Booking], float]
CityTaxFn = Callable[[float, Booking], float]
FilterFn = Callable[[Booking], bool]
BookingProcessorFn = Callable[[Iterable[Booking]], dict[str, object]]


def calculate_base_cost(booking: Booking) -> float:
    """Чиста функція: розрахунок базової вартості проживання (ночі * ціна за ніч)."""
    return round(float(booking["nights"] * booking["price_per_night"]), 2)


def with_total(booking: Booking, base_cost: float, total: float) -> Booking:
    """Чиста функція: повертає новий словник без мутації вихідного."""
    return {
        **booking,
        "base_cost": base_cost,
        "total": round(total, 2),
    }


def default_status_filter(booking: Booking) -> bool:
    """Чиста функція: фільтрація тільки підтверджених бронювань."""
    return booking.get("status") == "confirmed"


def make_booking_processor(
    status_filter: FilterFn,
    apply_discount: DiscountFn,
    apply_tax: CityTaxFn,
) -> BookingProcessorFn:
    """Функція вищого порядку (фабрика обробника) для бронювань.

    Повертає чисту функцію-обробник, конфігуровану переданими політиками.
    """

    def process(bookings: Iterable[Booking]) -> dict[str, object]:
        qualified: list[Booking] = []
        total_revenue = 0.0

        for b in bookings:
            # Ізольована перевірка критерію прийнятності
            if not status_filter(b):
                continue

            base_cost = calculate_base_cost(b)
            # Застосування варіативних політик
            discounted = apply_discount(base_cost, b)
            final_total = apply_tax(discounted, b)

            new_booking = with_total(b, base_cost=base_cost, total=final_total)
            qualified.append(new_booking)
            total_revenue += final_total

        return {
            "count": len(qualified),
            "revenue": round(total_revenue, 2),
            "bookings": qualified,
        }

    return process
