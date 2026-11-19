"""一次不握手的调用：把 messages.json 里的 tools/call 直接 POST 出去。

2026-07-28 没有 initialize。每个请求自己带协议版本、客户端能力和身份，
HTTP 层还要带 MCP-Protocol-Version、Mcp-Method、Mcp-Name 三个头。

用法：
    python stateless_request.py                                  # 只打印报文与头
    python stateless_request.py http://127.0.0.1:8020/mcp ping    # 换成别的工具真发
"""

import json
import sys
import urllib.request
from pathlib import Path

MESSAGES = json.loads((Path(__file__).parent / "messages.json").read_text(encoding="utf-8"))
BASE_HEADERS = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}


def build(key: str, tool: str | None = None) -> tuple[dict, dict]:
    """按方法名拼出 HTTP 头和 JSON-RPC 正文。tool 给定时换掉工具名和参数。"""
    body = json.loads(json.dumps(MESSAGES[key]))
    if tool:
        body["params"]["name"] = tool
        body["params"]["arguments"] = {}
    headers = dict(BASE_HEADERS)
    headers["MCP-Protocol-Version"] = body["params"]["_meta"]["io.modelcontextprotocol/protocolVersion"]
    headers["Mcp-Method"] = body["method"]
    name = body["params"].get("name")
    if name:
        headers["Mcp-Name"] = name
    return headers, body


def post(url: str, key: str, tool: str | None = None) -> str:
    headers, body = build(key, tool)
    request = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST"
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8")


if __name__ == "__main__":
    TOOL = sys.argv[2] if len(sys.argv) > 2 else None
    HEADERS, BODY = build("tools_call", TOOL)
    print("HTTP 头：", json.dumps(HEADERS, ensure_ascii=False, indent=2))
    print("正文：", json.dumps(BODY, ensure_ascii=False, indent=2))
    if len(sys.argv) > 1:
        print("响应：", post(sys.argv[1], "tools_call", TOOL))
