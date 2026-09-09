import argparse
import asyncio
from time import perf_counter

from common.sum_utils import calculate_range_sum, combine, split_range

LIMIT = 10_000_000_000_000


async def calculate_part(bounds: tuple[int, int]) -> int:
    await asyncio.sleep(0)
    return calculate_range_sum(bounds)


async def calculate_sum(limit: int = LIMIT, workers: int = 4) -> int:
    ranges = split_range(limit, workers)
    tasks = [asyncio.create_task(calculate_part(bounds)) for bounds in ranges]
    return combine(await asyncio.gather(*tasks))


async def async_main(limit: int, workers: int) -> None:
    started = perf_counter()
    result = await calculate_sum(limit, workers)
    elapsed = perf_counter() - started

    print(f"asyncio: sum={result}; seconds={elapsed:.6f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sum numbers using asyncio")
    parser.add_argument("--limit", type=int, default=LIMIT)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    asyncio.run(async_main(args.limit, args.workers))


if __name__ == "__main__":
    main()
