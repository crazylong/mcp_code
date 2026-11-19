"""Elicitation 的客户端侧：收到 input_required 就替用户选一项，客户端自动重发原请求。"""

import asyncio

from fastmcp import Client

from elicit_server import mcp


async def choose_overwrite(message, response_type, params, context):
    """收到询问就选「覆盖」。真实产品在这里弹给用户选。"""
    del message, response_type, params, context
    return {"value": "覆盖已有文件"}


async def run_local() -> str:
    async with Client(mcp, elicitation_handler=choose_overwrite) as client:
        result = await client.call_tool("import_file", {"filename": "orders.zip"})
    return result.content[0].text


if __name__ == "__main__":
    print(asyncio.run(run_local()))
