"""一个按生产要求写的仓库工具 Server。

描述写清使用边界，参数有上下界，错误带 next，
搜索结果分页，单文件按行截断，写操作用 request_id 去重。
日志走 stderr。
"""

import logging
import sys
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(message)s")
log = logging.getLogger("repo-tools")

mcp = FastMCP("repo-tools")

CORPUS = {
    "src/Http.java": [
        "public class Http {",
        "  int timeout = 3000;",
        "  void send() { log(\"timeout\"); }",
        "}",
    ],
    "src/OrderService.java": [
        "public class OrderService {",
        "  Order find(String id) { return db.find(id); }",
        "}",
    ],
}

NOTES: dict[str, dict] = {}


def page(items: list, cursor: str | None, limit: int) -> dict:
    start = int(cursor or 0)
    chunk = items[start : start + limit]
    more = start + limit < len(items)
    return {
        "items": chunk,
        "total": len(items),
        "truncated": more,
        "next_cursor": str(start + limit) if more else None,
    }


def clip(lines: list[str], offset: int, max_lines: int) -> dict:
    chunk = lines[offset : offset + max_lines]
    more = offset + max_lines < len(lines)
    return {
        "content": "\n".join(chunk),
        "truncated": more,
        "total_lines": len(lines),
        "next": f"用 offset={offset + max_lines} 继续读" if more else None,
    }


@mcp.tool
def repo_search(
    repo: Annotated[str, Field(description="owner/name，例如 acme/order", pattern=r"^[\w.-]+/[\w.-]+$")],
    query: Annotated[str, Field(min_length=2, description="标识符或报错文案")],
    limit: Annotated[int, Field(ge=1, le=50, description="返回条数")] = 20,
    cursor: Annotated[str | None, Field(description="上一页的 next_cursor")] = None,
) -> dict:
    """在指定仓库里按关键词检索代码。

    什么时候用：定位某个符号、配置项或报错文案在哪个文件。
    什么时候不用：已经知道路径，用 read_file；要改代码时不要用这个工具。
    返回：ok、items、total、truncated、next_cursor。truncated 为 true 表示后面还有。
    """
    log.info("repo_search repo=%s query_len=%s", repo, len(query))
    if repo != "acme/order":
        return {
            "ok": False,
            "error": "no_permission",
            "message": f"当前凭证不能读 {repo}",
            "next": "确认凭证是否包含该仓库的读权限，或改用 acme/order",
        }
    hits = []
    for path, lines in CORPUS.items():
        for number, line in enumerate(lines, start=1):
            if query.lower() in line.lower():
                hits.append({"path": path, "line": number, "snippet": line.strip()})
    try:
        body = page(hits, cursor, limit)
    except ValueError:
        return {
            "ok": False,
            "error": "bad_cursor",
            "message": f"cursor 必须是上一页返回的 next_cursor，收到 {cursor!r}",
            "next": "不传 cursor 从头查，或原样传回 next_cursor",
        }
    body["ok"] = True
    return body


@mcp.tool
def read_file(
    path: Annotated[str, Field(description="仓库内相对路径")],
    offset: Annotated[int, Field(ge=0)] = 0,
    max_lines: Annotated[int, Field(ge=1, le=200)] = 200,
) -> dict:
    """读取一个文件的一段内容。

    什么时候用：已经知道路径，要看具体实现。
    什么时候不用：还不知道文件在哪，先用 repo_search。
    文件很长时只返回 max_lines 行，并用 truncated 说明这不是全文。
    """
    lines = CORPUS.get(path)
    if lines is None:
        return {
            "ok": False,
            "error": "not_found",
            "message": f"仓库里没有 {path}",
            "next": "先用 repo_search 确认路径",
        }
    if offset >= len(lines):
        return {
            "ok": False,
            "error": "eof",
            "message": f"{path} 只有 {len(lines)} 行，offset={offset} 已经在文件末尾之后",
            "next": "用 offset=0 从头读，或把 offset 调到 total_lines 以内",
        }
    body = clip(lines, offset, max_lines)
    body.update({"ok": True, "path": path, "lines": f"{offset + 1}-{offset + body['content'].count(chr(10)) + 1}"})
    return body


@mcp.tool
def note_finding(
    path: str,
    summary: Annotated[str, Field(min_length=1, max_length=200)],
    request_id: Annotated[str, Field(min_length=8, description="调用方生成的幂等键")],
) -> dict:
    """记录一条代码审查结论。相同 request_id 重复调用返回第一次的结果。"""
    previous = NOTES.get(request_id)
    if previous is not None:
        return {**previous, "replayed": True}
    saved = {"ok": True, "path": path, "summary": summary, "request_id": request_id, "replayed": False}
    NOTES[request_id] = saved
    log.info("note_finding request_id=%s path=%s", request_id, path)
    return saved


if __name__ == "__main__":
    mcp.run(transport="stdio")
