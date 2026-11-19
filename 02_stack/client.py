"""最小 Client：一个 Client 拿工具，一个 middleware 做审计，最后交给 Agent。

这就是新栈的全部接线：
- 传输和协议交给 fastmcp.Client
- 工具与 Agent 之间的转换交给 MCPAdapter
- 横切逻辑交给 LangChain 的 middleware
"""

import asyncio
import os
import sys
from pathlib import Path

from langchain.agents.middleware import wrap_tool_call
from langchain.mcp import MCPAdapter

SERVER = Path(__file__).resolve().parent / "server.py"


@wrap_tool_call
async def audit(request, handler):
    """记一行工具名，再放行。真实项目在这里取 runtime.context 和审计字段。"""
    name = request.tool_call.get("name")
    print(f"调用 {name}", file=sys.stderr)
    return await handler(request)


async def load_tools():
    async with MCPAdapter(SERVER) as adapter:
        return await adapter.list_tools()


async def main() -> None:
    tools = await load_tools()
    print("工具:", [tool.name for tool in tools])

    model = os.environ.get("MCP_MODEL")
    if not model:
        print("设置 MCP_MODEL 后可跑完整 Agent，例如 openai:gpt-4.1")
        return

    from langchain.agents import create_agent

    agent = create_agent(model=model, tools=tools, middleware=[audit])
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "查一下 ORD-001 再退款"}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
