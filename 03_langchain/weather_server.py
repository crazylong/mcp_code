"""远程天气工具。Streamable HTTP，默认 http://127.0.0.1:8000/mcp。"""

from fastmcp import FastMCP

mcp = FastMCP("Weather")

WEATHER = {
    "北京": "晴，22~28°C，北风 3 级",
    "上海": "多云，25~30°C，东南风 2 级",
    "深圳": "阵雨，26~31°C，南风 4 级",
}


@mcp.tool
async def get_weather(location: str) -> str:
    """查询城市天气。location 用城市名，例如上海。"""
    return WEATHER.get(location, f"暂无 {location} 的天气数据")


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)
