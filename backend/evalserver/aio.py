import asyncio
from typing import Coroutine
from typing import Optional
from typing import TypeVar

T = TypeVar("T")


async def wait_or_default(
    coro: Coroutine[None, None, T],
    timeout: float,
    default: Optional[T] = None,
    should_cancel: bool = True,
) -> Optional[T]:
    task = asyncio.Task(coro)
    try:
        return await asyncio.wait_for(task, timeout)
    except asyncio.TimeoutError:
        if should_cancel:
            task.cancel()
        return default
