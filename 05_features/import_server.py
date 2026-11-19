"""耗时导入：用进度通知把阶段推给客户端。

日志不再走协议。2026-07-28 把 `logging/setLevel` 直接移除、把协议 logging 标为 deprecated，
Server 侧的日志一律写 stderr（或 OpenTelemetry），客户端按 trace 去查。
"""

import asyncio
import logging
import sys

from fastmcp import Context, FastMCP

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(message)s")
log = logging.getLogger("import")

mcp = FastMCP("数据导入服务")
STAGES = ["解压文件", "校验字段", "写入数据库"]


@mcp.tool
async def import_orders(filename: str, ctx: Context) -> str:
    """导入订单文件。过程较长，通过进度汇报阶段。

    filename 示例：orders_2026Q3.csv
    """
    total = 100
    await ctx.report_progress(0, total, f"准备处理 {filename}")
    done = 0
    for stage in STAGES:
        await asyncio.sleep(0.05)
        done += 25
        log.info("import %s stage=%s", filename, stage)
        await ctx.report_progress(done, total, stage)
    await ctx.report_progress(total, total, "导入完成")
    return f"{filename} 导入完成"


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8011, show_banner=False)
