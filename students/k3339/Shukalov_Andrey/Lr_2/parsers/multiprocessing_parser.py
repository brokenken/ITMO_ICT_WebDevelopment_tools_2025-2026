import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from time import perf_counter

import requests

from common.parser_utils import DEFAULT_URLS, ParseResult, extract_title, save_result

HEADERS = {"User-Agent": "lr2-parser/1.0"}


def parse_and_save(url: str) -> ParseResult:
    response = requests.get(url, timeout=20, headers=HEADERS)
    response.raise_for_status()

    result = ParseResult(
        url=url,
        title=extract_title(response.content),
        approach="multiprocessing",
    )
    save_result(result)
    print(result)
    return result


def run(urls: list[str] = DEFAULT_URLS, workers: int = 4) -> list[ParseResult]:
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(parse_and_save, urls))


def main() -> None:
    multiprocessing.freeze_support()

    started = perf_counter()
    results = run()
    print(
        f"multiprocessing parser: pages={len(results)}; "
        f"seconds={perf_counter() - started:.3f}"
    )


if __name__ == "__main__":
    main()
