import asyncio
from time import perf_counter

import aiohttp
import asyncpg

from common.parser_utils import (
    DEFAULT_URLS,
    ParseResult,
    create_pool,
    extract_title,
    save_result_async,
)

HEADERS = {"User-Agent": "lr2-parser/1.0"}
_session: aiohttp.ClientSession | None = None
_pool: asyncpg.Pool | None = None


async def parse_and_save(url: str) -> ParseResult:
    if _session is None or _pool is None:
        raise RuntimeError("parse_and_save() must be called from run()")

    async with _session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as response:
        response.raise_for_status()
        html = await response.text(errors="replace")

    result = ParseResult(
        url=url,
        title=extract_title(html),
        approach="asyncio",
    )
    await save_result_async(_pool, result)
    print(result)
    return result


async def run(urls: list[str] = DEFAULT_URLS) -> list[ParseResult]:
    global _session, _pool

    connector = aiohttp.TCPConnector(limit=8)
    async with aiohttp.ClientSession(headers=HEADERS, connector=connector) as session:
        pool = await create_pool()
        _session = session
        _pool = pool
        try:
            tasks = [asyncio.create_task(parse_and_save(url)) for url in urls]
            return await asyncio.gather(*tasks)
        finally:
            _session = None
            _pool = None
            await pool.close()


async def async_main() -> None:
    started = perf_counter()
    results = await run()
    print(f"asyncio parser: pages={len(results)}; seconds={perf_counter() - started:.3f}")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
