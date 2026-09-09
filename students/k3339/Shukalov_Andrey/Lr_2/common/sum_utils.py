from collections.abc import Iterable


def split_range(limit: int, workers: int) -> list[tuple[int, int]]:
    if limit < 1:
        raise ValueError("limit must be positive")
    if workers < 1:
        raise ValueError("workers must be positive")
    workers = min(workers, limit)
    base_size, remainder = divmod(limit, workers)
    ranges: list[tuple[int, int]] = []
    start = 1
    for worker_index in range(workers):
        size = base_size + (1 if worker_index < remainder else 0)
        end = start + size - 1
        ranges.append((start, end))
        start = end + 1
    return ranges


def calculate_range_sum(bounds: tuple[int, int]) -> int:
    start, end = bounds
    count = end - start + 1
    return (start + end) * count // 2


def combine(parts: Iterable[int]) -> int:
    return sum(parts)
