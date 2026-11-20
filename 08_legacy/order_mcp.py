"""MCP 工具只暴露订单号、状态和金额。cookie 留在这个进程里。"""

import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastmcp import FastMCP

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adapt import from_legacy_page, status_code, to_legacy_page

mcp = FastMCP("legacy-orders")
BASE = os.environ.get("LEGACY_BASE", "http://127.0.0.1:8090")
COOKIE = ""
TIMEOUT = float(os.environ.get("LEGACY_TIMEOUT", "3"))


class UpstreamTimeout(RuntimeError):
    """老接口没在超时内回来。抛给工具层转成可纠正的错误。"""


def login() -> None:
    global COOKIE
    request = Request(
        f"{BASE}/login",
        data=json.dumps({"username": os.environ.get("LEGACY_USER", "order-bot")}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=TIMEOUT) as response:
        COOKIE = response.headers.get("Set-Cookie", "").split(";", 1)[0]


def legacy_get(path: str) -> dict:
    """带会话的只读查询；401 时重新登录并重放一次，不用于写操作。"""
    try:
        if not COOKIE:
            login()
        for attempt in range(2):
            request = Request(f"{BASE}{path}", headers={"Cookie": COOKIE})
            try:
                with urlopen(request, timeout=TIMEOUT) as response:
                    return json.loads(response.read())
            except HTTPError as exc:
                if exc.code == 401 and attempt == 0:
                    login()
                    continue
                raise
    except HTTPError:
        # 业务上的 4xx/5xx 往上抛，别被下面的超时分支吞掉
        raise
    except (TimeoutError, URLError) as exc:
        raise UpstreamTimeout(str(exc)) from exc
    raise RuntimeError("unreachable")


@mcp.tool
def query_orders(status: str | None = None, cursor: str | None = None, limit: int = 2) -> dict:
    """按状态查询订单。

    什么时候用：用户要看某一类订单，例如已发货。
    什么时候不用：要改订单状态。这个工具只查询。
    status 用中文：待支付、已发货、已完成。不传则查全部。
    cursor 传上一页返回的 next_cursor，自己不要编。
    返回 ok、items、total、truncated、next_cursor。
    """
    try:
        page = to_legacy_page(cursor, limit)
    except ValueError:
        return {
            "ok": False,
            "error": "bad_cursor",
            "message": f"cursor 必须是上一页返回的页码，收到 {cursor!r}",
            "next": "不传 cursor 从头查，或原样传回 next_cursor",
        }

    query = f"/api/orders?pageNo={page['pageNo']}&pageSize={page['pageSize']}"
    code = status_code(status)
    if code is not None:
        query += f"&sts={code}"

    try:
        payload = legacy_get(query)
    except UpstreamTimeout:
        return {
            "ok": False,
            "error": "upstream_timeout",
            "message": f"订单服务 {TIMEOUT:g} 秒内没有返回",
            "next": "稍后重试一次；连续超时就别再试，转人工",
        }

    if payload.get("code") != 0:
        return {"ok": False, "error": "upstream", "message": "订单服务拒绝了这次查询", "next": "稍后重试"}
    return from_legacy_page(payload["data"], page["pageNo"], page["pageSize"])


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
