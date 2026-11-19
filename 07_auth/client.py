"""携带本地签发的 token 访问受保护的 MCP Server。"""

import asyncio
from pathlib import Path

from fastmcp import Client

LOCAL = Path(__file__).resolve().parent / ".local"
URL = "http://127.0.0.1:8765/mcp"


async def list_names(token: str | None) -> list[str]:
    async with Client(URL, auth=token) as client:
        tools = await client.list_tools()
    return [tool.name for tool in tools]


async def call(token: str, name: str, arguments: dict) -> str:
    async with Client(URL, auth=token) as client:
        result = await client.call_tool(name, arguments)
    return result.content[0].text


if __name__ == "__main__":
    bearer = (LOCAL / "token.txt").read_text().strip()

    async def main() -> None:
        print("可见工具", await list_names(bearer))
        print(await call(bearer, "query_employee", {"employee_id": "E001"}))
        print(await call(bearer, "query_employee", {"employee_id": "E002"}))

    asyncio.run(main())
