from core import Reading, Result, process_readings_pure


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
        rates={"household": 4.32, "pensioner": 4.32, "commercial": 6.5},
        benefit_shares={"pensioner": 0.5},
        min_consumption=1.0,
    )
    print(render_report(result))


if __name__ == "__main__":
    sample: list[Reading] = [
        {"id": 1, "prev": 100.0, "curr": 250.0, "group": "household"},
        {"id": 2, "prev": 0.0, "curr": 200.0, "group": "pensioner"},
        {"id": 3, "prev": 500.0, "curr": 400.0, "group": "commercial"},
        {"id": 4, "prev": 10.0, "curr": 10.0, "group": "household"},
        {"id": 5, "prev": 1000.0, "curr": 1300.0, "group": "commercial"},
    ]
    run(sample)
