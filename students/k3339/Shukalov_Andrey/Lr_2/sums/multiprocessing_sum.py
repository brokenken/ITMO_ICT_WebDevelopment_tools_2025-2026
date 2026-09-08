import argparse
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from time import perf_counter

from common.sum_utils import calculate_range_sum, combine, split_range

LIMIT = 10_000_000_000_000


def calculate_sum(limit: int = LIMIT, workers: int = 4) -> int:
    ranges = split_range(limit, workers)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        partial_results = executor.map(calculate_range_sum, ranges)
        return combine(partial_results)


def main() -> None:
    multiprocessing.freeze_support()

    parser = argparse.ArgumentParser(description="Sum numbers using processes")
    parser.add_argument("--limit", type=int, default=LIMIT)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    started = perf_counter()
    result = calculate_sum(args.limit, args.workers)
    elapsed = perf_counter() - started

    print(f"multiprocessing: sum={result}; seconds={elapsed:.6f}")


if __name__ == "__main__":
    main()
