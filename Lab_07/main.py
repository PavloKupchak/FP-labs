"""Демонстрація конвеєра бронювань та поліморфного завантаження."""

from pathlib import Path

from core import high_season, low_season, top_bookings
from models import Box

DATA_DIR = Path(__file__).resolve().parent


def main() -> None:
    """Показує Top-N бронювань із JSON, CSV та відкритого файлу."""
    json_path = DATA_DIR / "sample_data.json"
    csv_path = DATA_DIR / "sample_data.csv"

    from_json = top_bookings(json_path, top=3, tariff=high_season)
    from_csv = top_bookings(str(csv_path), top=3, tariff=high_season)
    with csv_path.open(encoding="utf-8") as file:
        from_file = top_bookings(file, top=3, tariff=high_season)

    print("Top-3 (high season):")
    for booking in from_json:
        print(f"  {booking.guest}: {booking.total_price} ({booking.room_type})")
    print(f"json == csv == file: {from_json == from_csv == from_file}")

    cheaper = top_bookings(json_path, top=2, tariff=low_season, min_nights=4)
    print(f"Top-2 (low season, 4+ nights): {[b.guest for b in cheaper]}")

    boxes = sorted([Box(2, 3, 4), Box(1, 2, 3), Box(3, 3, 3)])
    print(f"boxes: {boxes}")
    print(f"max box: {max(boxes)}")


if __name__ == "__main__":
    main()
