"""Демонстрація лінивих потоків і конвеєра сенсорних даних."""

import sys
from itertools import islice, starmap

from streams import (
    drop,
    fib_stream,
    moving_average,
    naturals,
    prefix_sums,
    process_sensor,
    simulated_sensor,
    sliding_window,
    summarize_batches,
    take,
)


def main() -> None:
    """Показує перші елементи, віконні суми, рухоме середнє та конвеєр датчика."""
    print(f"fib: {take(10, fib_stream())}")
    print(f"fib skip 5 take 8: {take(8, drop(5, fib_stream()))}")
    sums = islice(starmap(lambda *w: sum(w), sliding_window(naturals(1), 3)), 10)
    print(f"window sums: {list(sums)}")
    print(f"moving average: {take(4, moving_average(naturals(1), 3))}")
    print(f"prefix sums: {take(5, prefix_sums(naturals(1)))}")

    batches = process_sensor(
        simulated_sensor(seed=1),
        noise_level=2.0,
        alarm_level=12.0,
        batch_size=3,
    )
    for batch in summarize_batches(batches):
        print(
            f"batch: min={batch.minimum:.2f} max={batch.maximum:.2f} "
            f"avg={batch.average:.2f}"
        )

    eager = list(range(100_000))
    lazy = (x for x in range(100_000))
    print(f"memory: list={sys.getsizeof(eager)}B generator={sys.getsizeof(lazy)}B")


if __name__ == "__main__":
    main()
