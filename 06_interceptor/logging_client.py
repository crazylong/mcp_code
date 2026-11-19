"""横切逻辑挂在 LangChain middleware 上，不在 MCP 协议里。

middleware 列表的顺序就是嵌套顺序：第一个在最外层。
只有真跑 create_agent 时它们才会被调用，所以这里先验证工具名单和挂载顺序。
"""

import asyncio
import sys
from pathlib import Path

from langchain.agents.middleware import wrap_tool_call
from langchain.mcp import MCPAdapter

ORDER = Path(__file__).resolve().parent / "order_server.py"


@wrap_tool_call
async def outer(request, handler):
    print("外层 before", request.tool_call.get("name"), file=sys.stderr)
    result = await handler(request)
    print("外层 after", file=sys.stderr)
    return result


@wrap_tool_call
async def inner(request, handler):
    print("内层 before", request.tool_call.get("name"), file=sys.stderr)
    result = await handler(request)
    print("内层 after", file=sys.stderr)
    return result


MIDDLEWARE = [outer, inner]


async def load_tools():
    async with MCPAdapter(ORDER) as adapter:
        return await adapter.list_tools()


async def call_query() -> str:
    from langchain.agents import create_agent

    tools = await load_tools()
    agent = create_agent(model="openai:gpt-4.1", tools=tools, middleware=MIDDLEWARE)
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "查一下 ORD-001"}]}
    )
    return result["messages"][-1].content


async def main() -> None:
    tools = await load_tools()
    print("工具:", [tool.name for tool in tools])
    print("中间件:", [fn.__name__ for fn in MIDDLEWARE])
    if len(sys.argv) > 1 and sys.argv[1] == "--ask":
        print(await call_query())


if __name__ == "__main__":
    asyncio.run(main())
