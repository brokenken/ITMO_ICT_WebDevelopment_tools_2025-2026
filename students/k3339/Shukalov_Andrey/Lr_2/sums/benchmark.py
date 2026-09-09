import asyncio
from statistics import mean
from time import perf_counter

from sums.async_sum import calculate_sum as async_calculate_sum
from sums.multiprocessing_sum import calculate_sum as process_calculate_sum
from sums.threading_sum import calculate_sum as thread_calculate_sum

LIMIT = 10_000_000_000_000
WORKERS = 4
RUNS = 5


def measure_sync(func) -> tuple[int, float]:
    started = perf_counter()
    result = func(LIMIT, WORKERS)
    return result, perf_counter() - started


async def measure_async() -> tuple[int, float]:
    started = perf_counter()
    result = await async_calculate_sum(LIMIT, WORKERS)
    return result, perf_counter() - started


def main() -> None:
    expected = LIMIT * (LIMIT + 1) // 2
    measurements = {"threading": [], "multiprocessing": [], "asyncio": []}

    for _ in range(RUNS):
        result, elapsed = measure_sync(thread_calculate_sum)
        assert result == expected
        measurements["threading"].append(elapsed)

        result, elapsed = measure_sync(process_calculate_sum)
        assert result == expected
        measurements["multiprocessing"].append(elapsed)

        result, elapsed = asyncio.run(measure_async())
        assert result == expected
        measurements["asyncio"].append(elapsed)

    print(f"limit={LIMIT}; workers={WORKERS}; runs={RUNS}")
    for approach, values in measurements.items():
        print(
            f"{approach:15} avg={mean(values):.6f}s "
            f"min={min(values):.6f}s max={max(values):.6f}s"
        )


if __name__ == "__main__":
    main()
