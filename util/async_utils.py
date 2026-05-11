import asyncio
import inspect
from typing import Callable, Any, Coroutine


async def run_after(delay: float, fn: Callable, *args, **kwargs) -> Any:
    await asyncio.sleep(delay)
    if inspect.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    return fn(*args, **kwargs)


async def run_every(interval: float, fn: Callable, times: int = 3, *args, **kwargs):
    for _ in range(times):
        if inspect.iscoroutinefunction(fn):
            await fn(*args, **kwargs)
        else:
            fn(*args, **kwargs)
        await asyncio.sleep(interval)


async def gather_results(*coros: Coroutine) -> list[Any]:
    return await asyncio.gather(*coros)


async def run_with_timeout(coro: Coroutine, timeout: float) -> Any:
    return await asyncio.wait_for(coro, timeout=timeout)


async def retry_async(
    fn: Callable,
    *args,
    attempts: int = 3,
    delay: float = 0.5,
    exceptions: tuple = (Exception,),
    **kwargs,
) -> Any:
    last_exc = None
    for attempt in range(1, attempts + 1):
        try:
            if inspect.iscoroutinefunction(fn):
                return await fn(*args, **kwargs)
            return fn(*args, **kwargs)
        except exceptions as e:
            last_exc = e
            if attempt < attempts:
                await asyncio.sleep(delay)
    raise last_exc


async def map_async(fn: Callable, items: list, concurrency: int = 5) -> list[Any]:
    sem = asyncio.Semaphore(concurrency)

    async def bounded(item):
        async with sem:
            if inspect.iscoroutinefunction(fn):
                return await fn(item)
            return fn(item)

    return await asyncio.gather(*[bounded(item) for item in items])


def run(coro: Coroutine) -> Any:
    return asyncio.run(coro)


if __name__ == "__main__":
    async def main():
        print("--- run_after ---")
        result = await run_after(0.1, lambda: "done after delay")
        print("result:", result)

        print("\n--- gather_results ---")
        async def fetch(n):
            await asyncio.sleep(0.05)
            return f"response_{n}"

        results = await gather_results(fetch(1), fetch(2), fetch(3))
        print("gathered:", results)

        print("\n--- run_with_timeout ---")
        try:
            await run_with_timeout(asyncio.sleep(5), timeout=0.1)
        except asyncio.TimeoutError:
            print("timed out as expected")

        print("\n--- retry_async ---")
        call_count = 0
        async def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError(f"fail #{call_count}")
            return "success"

        result = await retry_async(flaky, attempts=3, delay=0.05)
        print("retry result:", result)

        print("\n--- map_async ---")
        async def process(x):
            await asyncio.sleep(0.02)
            return x * 2

        results = await map_async(process, [1, 2, 3, 4, 5], concurrency=3)
        print("mapped:", results)

    run(main())
