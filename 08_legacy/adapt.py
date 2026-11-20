"""老订单接口的字段和分页，收成 MCP 工具能用的形状。"""

STATUS = {1: "待支付", 2: "已发货", 3: "已完成"}
STATUS_NAME = {name: code for code, name in STATUS.items()}


def map_order(row: dict) -> dict:
    return {
        "order_id": row["ordId"],
        "status": STATUS.get(row["sts"], "未知"),
        "amount": row["amt"] / 100,
    }


def to_legacy_page(cursor: str | None, limit: int) -> dict:
    """cursor 必须是上一页给的页码字符串。非数字直接 ValueError，由工具层转成 ok: false。"""
    page_no = int(cursor or 1)
    if page_no < 1:
        page_no = 1
    return {"pageNo": page_no, "pageSize": limit}


def from_legacy_page(payload: dict, page_no: int, page_size: int) -> dict:
    """page_size 必须由调用方传入。用本页实际条数倒推，末页不满时会误判还有下一页。"""
    rows = [map_order(row) for row in payload["rows"]]
    total = payload["total"]
    more = page_no * page_size < total
    return {
        "ok": True,
        "items": rows,
        "total": total,
        "truncated": more,
        "next_cursor": str(page_no + 1) if more else None,
    }


def status_code(name: str | None) -> int | None:
    if name is None:
        return None
    code = STATUS_NAME.get(name)
    if code is None:
        raise ValueError(f"未知状态 {name}，可用：{'、'.join(STATUS_NAME)}")
    return code
