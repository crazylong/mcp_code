"""股票分析：Tool 查数据，Resource 提供方法论，Prompt 规定报告格式。"""

import json

from fastmcp import FastMCP

mcp = FastMCP("股票分析系统")

STOCKS = {
    "AAPL": {"name": "苹果", "price": 198.5},
    "TSLA": {"name": "特斯拉", "price": 245.8},
    "000001": {"name": "平安银行", "price": 12.35},
}


@mcp.tool
def search_stock(keyword: str) -> str:
    """按代码或名称搜索股票。还不知道代码时用这个。"""
    found = [
        f"{code}（{info['name']}）"
        for code, info in STOCKS.items()
        if keyword.upper() in code or keyword in info["name"]
    ]
    if not found:
        return f"未找到与 {keyword} 相关的股票"
    return "找到：" + "、".join(found)


@mcp.tool
def get_quote(symbol: str) -> str:
    """读取一只股票的价格。symbol 用 search_stock 返回的代码。"""
    stock = STOCKS.get(symbol.upper())
    if stock is None:
        return json.dumps({"error": f"未找到 {symbol}"}, ensure_ascii=False)
    return json.dumps({"symbol": symbol.upper(), **stock}, ensure_ascii=False)


@mcp.resource("research://methodology", mime_type="text/markdown")
def methodology() -> str:
    """公司统一的股票分析方法。客户端读出来后放进 system prompt。"""
    return "\n".join(
        [
            "1. 基本面：营收和利润是否支撑当前估值",
            "2. 技术面：近期价格位置",
            "3. 行业对比：和同业估值并排",
            "4. 综合评级：买入、持有或卖出，并写出理由",
        ]
    )


@mcp.resource("market://overview", mime_type="application/json")
def market_overview() -> str:
    """当前热门板块。这是只读背景，不是模型要调用的工具。"""
    return json.dumps(
        [
            {"sector": "人工智能", "change": "+3.2%"},
            {"sector": "新能源汽车", "change": "+1.8%"},
        ],
        ensure_ascii=False,
    )


@mcp.prompt
def analysis_report(stock_name: str) -> str:
    """指定股票的报告骨架。客户端填好参数后交给模型遵守。"""
    return (
        f"请对 {stock_name} 按下面四节输出：\n"
        "一、基本面分析\n二、技术面分析\n三、行业对比\n四、综合评级"
    )


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8010)
