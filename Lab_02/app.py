"""Оболонка вводу-виводу: читання даних, аргументи командного рядка, друк звіту."""

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from core import (
    StockItem,
    build_inventory_pipeline,
    process_inventory,
    reduce_inventory_stats,
)

DEFAULT_DATA = Path(__file__).resolve().parent / "sample_data.json"


def load_items(path: Path) -> list[StockItem]:
    """Читає товари з JSON-файлу."""
    with path.open(encoding="utf-8") as file:
        raw = json.load(file)
    return [
        {
            "id": int(row["id"]),
            "name": str(row["name"]),
            "category": str(row["category"]),
            "price": float(row["price"]),
            "stock": int(row["stock"]),
        }
        for row in raw
    ]


def render_report(top: Sequence[StockItem], stats: dict[str, float]) -> str:
    """Текстовий звіт: Top-N та агрегація."""
    lines = [
        f"{place}. {item['name']} [{item['category']}] value={item['value']:.2f}"
        for place, item in enumerate(top, start=1)
    ]
    lines.append(f"count: {stats['count']:.0f}")
    lines.append(f"inventory_value: {stats['inventory_value']:.2f}")
    lines.append(f"avg_value: {stats['avg_value']:.2f}")
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Розбирає аргументи командного рядка."""
    parser = argparse.ArgumentParser(description="Аналіз товарів складу")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--boost-category", default="Electronics")
    parser.add_argument("--factor", type=float, default=1.1)
    parser.add_argument("--min-stock", type=int, default=1)
    return parser.parse_args(argv)


def run(argv: Sequence[str] | None = None) -> int:
    """Запускає конвеєр і друкує звіт."""
    args = parse_args(argv)
    items = load_items(args.data)
    pipeline = build_inventory_pipeline(
        args.top, args.boost_category, args.factor, args.min_stock
    )
    processed = process_inventory(args.boost_category, args.factor, args.min_stock)(
        items
    )
    print(render_report(pipeline(items), reduce_inventory_stats(processed)))
    return 0
