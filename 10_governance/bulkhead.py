"""每个下游一块并发配额。慢的那路只占满自己的信号量。"""

import asyncio

LIMITS = {"kb": 8, "repo": 16, "ci": 4}
SEMAPHORES = {name: asyncio.Semaphore(limit) for name, limit in LIMITS.items()}


async def call(name: str, fn, *args, timeout: float = 5):
    async with SEMAPHORES[name]:
        try:
            return await asyncio.wait_for(fn(*args), timeout=timeout)
        except TimeoutError:
            return {"ok": False, "error": "upstream_timeout", "next": "稍后重试，或走已经约定好的降级"}
