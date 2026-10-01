"""Оболонка введення/виведення (I/O) для запуску обробки бронювань."""

from core import (
    Booking,
    CityTaxFn,
    DiscountFn,
    FilterFn,
    make_booking_processor,
)


def render_report(result: dict[str, object]) -> None:
    """Ізольована функція відображення звіту (I/O)."""
    print("=" * 60)
    print("             ЗВІТ ОБРОБКИ БРОНЮВАНЬ ГОТЕЛЮ")
    print("=" * 60)
    print(f"Кількість підтверджених бронювань : {result['count']}")
    print(f"Загальна виручка готелю          : {result['revenue']:.2f} грн")
    print("-" * 60)
    print("Деталізація бронювань:")

    bookings = result.get("bookings", [])
    if isinstance(bookings, list):
        for b in bookings:
            print(
                f"  ID: {b['id']} | Номер: {b['room_type']:<8} | "
                f"Ночей: {b['nights']} | Базова: {b['base_cost']:>8.2f} грн | "
                f"Разом: {b['total']:>8.2f} грн"
            )
    print("=" * 60)


def main() -> None:
    # Тестовий набір даних
    sample_bookings: list[Booking] = [
        {
            "id": 101,
            "nights": 5,
            "price_per_night": 1200.0,
            "room_type": "standard",
            "status": "confirmed",
        },
        {
            "id": 102,
            "nights": 2,
            "price_per_night": 2500.0,
            "room_type": "suite",
            "status": "cancelled",
        },
        {
            "id": 103,
            "nights": 8,
            "price_per_night": 1500.0,
            "room_type": "deluxe",
            "status": "confirmed",
        },
        {
            "id": 104,
            "nights": 1,
            "price_per_night": 1000.0,
            "room_type": "standard",
            "status": "pending",
        },
        {
            "id": 105,
            "nights": 12,
            "price_per_night": 3000.0,
            "room_type": "suite",
            "status": "confirmed",
        },
    ]

    # Функціональні політики Варіанта №5:
    # 1. Фільтрація: тільки підтверджені
    is_confirmed: FilterFn = lambda b: b.get("status") == "confirmed"

    # 2. Сезонна/тривала знижка: 15% при тривалості понад 7 ночей, інакше 0%
    seasonal_discount: DiscountFn = lambda cost, b: (
        cost * 0.85 if b.get("nights", 0) >= 7 else cost
    )

    # 3. Туристичний збір: 5% для люксів/делюксів, 2% для стандарту
    tourist_tax: CityTaxFn = lambda cost, b: cost * (
        1.05 if b.get("room_type") in ("suite", "deluxe") else 1.02
    )

    # Збирання конфігурованого процесора через функцію вищого порядку
    processor = make_booking_processor(
        status_filter=is_confirmed,
        apply_discount=seasonal_discount,
        apply_tax=tourist_tax,
    )

    # Виконання чистих обчислень
    result = processor(sample_bookings)

    # Відображення звіту (I/O)
    render_report(result)


if __name__ == "__main__":
    main()
