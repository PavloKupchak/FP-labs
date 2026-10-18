import json
from pathlib import Path

from core import Reading, Result, process_readings_pure

RATES = {"household": 4.32, "pensioner": 4.32, "commercial": 6.5}
BENEFIT_SHARES = {"pensioner": 0.5}


def load_readings(path: Path) -> list[Reading]:
    with path.open(encoding="utf-8") as file:
        raw = json.load(file)
    return [
        {
            "id": int(r["id"]),
            "prev": float(r["prev"]),
            "curr": float(r["curr"]),
            "group": str(r["group"]),
        }
        for r in raw
    ]


def render_receipt(bill: Reading) -> str:
    return (
        f"Receipt #{bill['id']} [{bill['group']}]: "
        f"{bill['consumption']:.2f} kWh, to pay: {bill['amount']:.2f}"
    )


def render_report(result: Result) -> str:
    lines = [render_receipt(b) for b in result["bills"]]
    lines.append(f"Count: {result['count']}")
    lines.append(f"Consumption: {result['consumption']:.2f} kWh")
    lines.append(f"Total: {result['amount']:.2f}")
    return "\n".join(lines)


def run(readings: list[Reading]) -> None:
    result = process_readings_pure(
        readings,
        rates=RATES,
        benefit_shares=BENEFIT_SHARES,
        min_consumption=1.0,
    )
    print(render_report(result))


def main(path: Path) -> None:
    run(load_readings(path))


if __name__ == "__main__":
    main(Path(__file__).with_name("readings.json"))
