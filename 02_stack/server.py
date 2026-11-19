"""最小 Server：两个工具，一个只读一个写。描述写清什么时候不用。"""

from fastmcp import FastMCP

mcp = FastMCP("mini-orders")

ORDERS = {
    "ORD-001": {"product": "无线耳机", "amount": 299.0, "refunded": False},
    "ORD-002": {"product": "机械键盘", "amount": 599.0, "refunded": False},
}


@mcp.tool
def query_order(order_id: str) -> dict:
    """查一张订单。

    什么时候用：用户给了一个订单号，要看商品和金额。
    什么时候不用：要退钱，用 refund_order。
    """
    order = ORDERS.get(order_id)
    if order is None:
        return {"ok": False, "error": "not_found", "next": "确认订单号，例如 ORD-001"}
    return {"ok": True, **order, "order_id": order_id}


@mcp.tool
def refund_order(order_id: str) -> dict:
    """给一张订单退款。写操作，重复调用返回第一次的结果。

    什么时候用：用户明确要求退款，且知道订单号。
    什么时候不用：只是想查订单状态。
    """
    order = ORDERS.get(order_id)
    if order is None:
        return {"ok": False, "error": "not_found", "next": "先 query_order 确认订单"}
    if order["refunded"]:
        return {"ok": True, "order_id": order_id, "replayed": True}
    order["refunded"] = True
    return {"ok": True, "order_id": order_id, "amount": order["amount"], "replayed": False}


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
