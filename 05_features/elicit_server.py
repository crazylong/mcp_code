"""同名文件导入：用 MRTR 的 guard 模式，在同一次 tools/call 里问用户要一个选择。

2026-07-28 取消了服务端主动请求，`ctx.elicit()` 只在旧协议连接上可用。
新写法是返回 `InputRequiredResult`，客户端补齐 inputResponses 后重发原请求，
Server 从 `ctx.input_responses` 读到答案继续往下走。
"""

from fastmcp import Context, FastMCP
from mcp_types import ElicitRequest, ElicitRequestFormParams, InputRequiredResult

mcp = FastMCP("文件导入服务")
EXISTING = {"orders.zip"}

SCHEMA = {
    "type": "object",
    "properties": {
        "value": {
            "type": "string",
            "title": "处理方式",
            "enum": ["覆盖已有文件", "跳过该文件", "取消导入"],
        }
    },
    "required": ["value"],
}


@mcp.tool
async def import_file(filename: str, ctx: Context) -> str | InputRequiredResult:
    """导入文件。同名文件存在时，在同一次调用里让用户选处理方式。"""
    if filename not in EXISTING:
        EXISTING.add(filename)
        return f"{filename} 导入成功"

    answers = ctx.input_responses
    if not answers:
        return InputRequiredResult(
            input_requests={
                "overwrite": ElicitRequest(
                    params=ElicitRequestFormParams(
                        message=f"文件 {filename} 已经存在，请选择处理方式",
                        requestedSchema=SCHEMA,
                    )
                )
            },
            request_state=filename,
        )

    result = answers["overwrite"]
    action = getattr(result, "action", "accept")
    if action == "cancel":
        return "导入已取消"
    if action == "decline":
        return f"{filename} 已跳过"

    choice = (getattr(result, "content", None) or {}).get("value")
    if choice == "覆盖已有文件":
        return f"{filename} 已覆盖"
    if choice == "跳过该文件":
        return f"{filename} 已跳过"
    return "导入已取消"


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8012, show_banner=False)
