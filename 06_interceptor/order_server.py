"""订单工具。caller_id 只是拦截器演示用的参数，服务端权限不能信它。"""

from fastmcp import FastMCP

mcp = FastMCP("OrderService")

ORDERS = {
    "ORD-001": {"product": "无线耳机", "status": "已签收", "amount": 299.0},
    "ORD-002": {"product": "机械键盘", "status": "配送中", "amount": 599.0},
}


@mcp.tool
async def query_order(order_id: str, caller_id: str = "") -> str:
    """查询订单。caller_id 由客户端拦截器写入，只用于日志，不作为权限依据。"""
    order = ORDERS.get(order_id)
    if order is None:
        return f"未找到订单 {order_id}"
    actor = caller_id or "未知"
    return f"订单 {order_id}：{order['product']}，{order['status']}，{order['amount']} 元（记录人 {actor}）"


@mcp.tool
async def process_refund(order_id: str) -> str:
    """退款。只有已签收的订单可以退；已退过的单重复调用返回第一次的结果。"""
    order = ORDERS.get(order_id)
    if order is None:
        return f"退款失败：未找到 {order_id}"
    if order["status"] == "已退款":
        return f"退款成功：{order_id}，{order['amount']} 元（重放，未重复退款）"
    if order["status"] != "已签收":
        return f"退款失败：当前状态是 {order['status']}"
    order["status"] = "已退款"
    return f"退款成功：{order_id}，{order['amount']} 元"


if __name__ == "__main__":
    # 给 Client / MCPAdapter 当子进程用。远程部署改成 transport="http"。
    mcp.run(transport="stdio", show_banner=False)
