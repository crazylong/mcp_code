"""接收进度。本地直接连 Server 对象，不需要先起 HTTP。

日志不在协议里了，所以这里只挂 progress_handler；Server 的日志在它自己的 stderr。
"""

import asyncio

from fastmcp import Client

from import_server import mcp


async def on_progress(progress: float, total: float | None, message: str | None) -> None:
    if total:
        print(f"进度 {progress:.0f}/{total:.0f} {message or ''}")
    else:
        print(f"进度 {progress} {message or ''}")


async def run_local() -> tuple[str, list[str]]:
    seen: list[str] = []

    async def remember(progress: float, total: float | None, message: str | None) -> None:
        seen.append(message or "")
        await on_progress(progress, total, message)

    async with Client(mcp, progress_handler=remember) as client:
        result = await client.call_tool("import_orders", {"filename": "orders.zip"})
    return result.content[0].text, seen


if __name__ == "__main__":
    text, progress = asyncio.run(run_local())
    print(text)
    print(progress)
