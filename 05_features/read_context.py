"""不经过模型，直接读取 Resource 和 Prompt。"""

import asyncio

from fastmcp import Client

from stock_server import mcp


async def load_background(stock_name: str = "特斯拉") -> dict:
    async with Client(mcp) as client:
        methodology = await client.read_resource("research://methodology")
        overview = await client.read_resource("market://overview")
        prompt = await client.get_prompt("analysis_report", {"stock_name": stock_name})
    return {
        "methodology": methodology[0].text,
        "overview": overview[0].text,
        "prompt": prompt.messages[0].content.text,
    }


if __name__ == "__main__":
    loaded = asyncio.run(load_background())
    print(loaded["prompt"])
