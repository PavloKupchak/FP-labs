from collections.abc import Iterator

import pytest

from streams import (
    BatchStat,
    drop_noise,
    process_sensor,
    sensor_stream,
    simulated_sensor,
    summarize,
    summarize_batches,
    take,
    until_alarm,
)


def test_drop_noise_removes_only_leading_noise() -> None:
    readings = [0.1, 0.5, 3.0, 0.2, 4.0]
    assert list(drop_noise(readings, 1.0)) == [3.0, 0.2, 4.0]


def test_until_alarm_stops_at_threshold() -> None:
    assert list(until_alarm([1.0, 5.0, 9.0, 3.0], 9.0)) == [1.0, 5.0]
    assert list(until_alarm([10.0, 1.0], 9.0)) == []


def test_pipeline_batches() -> None:
    readings = [0.1, 0.2, 3.0, 4.0, 5.0, 6.0, 7.0, 20.0, 1.0]
    batches = list(
        process_sensor(readings, noise_level=1.0, alarm_level=10.0, batch_size=2)
    )
    assert batches == [(3.0, 4.0), (5.0, 6.0), (7.0,)]


def test_pipeline_empty_and_all_noise() -> None:
    kwargs = {"noise_level": 1.0, "alarm_level": 10.0, "batch_size": 2}
    assert list(process_sensor([], **kwargs)) == []  # type: ignore[arg-type]
    assert list(process_sensor([0.1, 0.2], **kwargs)) == []  # type: ignore[arg-type]


def test_invalid_batch_size() -> None:
    with pytest.raises(ValueError):
        process_sensor([1.0], noise_level=0.0, alarm_level=5.0, batch_size=0)


def test_sensor_stream_uses_injected_provider() -> None:
    values = iter([1.0, 2.0, 3.0, 4.0])
    stream = sensor_stream(lambda: next(values))
    assert take(3, stream) == [1.0, 2.0, 3.0]


def test_pipeline_is_lazy_on_infinite_source() -> None:
    counter: list[float] = []

    def source() -> Iterator[float]:
        for value in [0.1, 0.2, 0.3, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]:
            counter.append(value)
            yield value

    batches = process_sensor(source(), noise_level=1.0, alarm_level=50.0, batch_size=2)
    assert next(batches) == (5.0, 6.0)
    assert len(counter) == 5


def test_simulated_sensor_is_deterministic_and_pipeline_terminates() -> None:
    first = take(20, simulated_sensor(seed=3))
    second = take(20, simulated_sensor(seed=3))
    assert first == second
    batches = list(
        process_sensor(
            simulated_sensor(seed=3), noise_level=2.0, alarm_level=12.0, batch_size=3
        )
    )
    assert batches
    assert all(value < 12.0 for batch in batches for value in batch)
    assert all(value >= 2.0 for value in batches[0])


def test_summaries() -> None:
    assert summarize((1.0, 3.0, 5.0)) == BatchStat(1.0, 5.0, 3.0)
    stats = list(summarize_batches([(1.0, 2.0), (4.0,)]))
    assert stats == [BatchStat(1.0, 2.0, 1.5), BatchStat(4.0, 4.0, 4.0)]
