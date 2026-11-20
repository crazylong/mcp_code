"""同时连接 stdio 数学服务和 HTTP 天气服务，把工具交给 Agent。

`MCPAdapter` 取代了已停止维护的 `langchain-mcp-adapters`：
它接一个 FastMCP 目标（URL、脚本路径、配置字典或现成 Client），
把远端工具变成 LangChain 的 BaseTool。

只打印工具名时不需要模型。加上 --ask 才会调用 create_agent，
模型名从环境变量 MCP_MODEL 读取，例如 openai:gpt-4.1。
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.mcp import MCPAdapter

load_dotenv()  # 自动向上找 .env（在 mcp_code/ 下），模板见 .env.sample

ROOT = Path(__file__).resolve().parent
MATH = ROOT / "math_server.py"


def connections(with_weather: bool) -> dict:
    servers = {
        "math": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [str(MATH)],
            "env": {"PYTHONIOENCODING": "utf-8"},
        }
    }
    if with_weather:
        servers["weather"] = {
            "transport": "http",
            "url": os.environ.get("WEATHER_MCP_URL", "http://127.0.0.1:8000/mcp"),
        }
    return servers


async def load_tools(with_weather: bool = False):
    async with MCPAdapter(connections(with_weather)) as adapter:
        return await adapter.list_tools()


async def ask(question: str, with_weather: bool) -> str:
    from langchain.agents import create_agent

    model = os.environ.get("MCP_MODEL")
    if not model:
        raise SystemExit("没有配置模型：复制 .env.sample 为 .env，填 MCP_MODEL 和 OPENAI_API_KEY")
    tools = await load_tools(with_weather)
    agent = create_agent(model=model, tools=tools)
    response = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
    return response["messages"][-1].content


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-weather", action="store_true")
    parser.add_argument("--ask")
    args = parser.parse_args()
    if args.ask:
        print(await ask(args.ask, args.with_weather))
        return
    tools = await load_tools(args.with_weather)
    print("工具:", [tool.name for tool in tools])


if __name__ == "__main__":
    asyncio.run(main())
