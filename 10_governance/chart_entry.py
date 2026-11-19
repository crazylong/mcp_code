"""26 个图表工具收成一个入口。类型白名单留在代码里，不留给模型自由发挥。"""

CHARTS = {
    "bar": lambda config: {"mark": "bar", "x": config["x"], "y": config["y"]},
    "column": lambda config: {"mark": "column", "x": config["x"], "y": config["y"]},
    "line": lambda config: {"mark": "line", "x": config["x"], "y": config["y"]},
}


def generate_visualization(chart_type: str, chart_config: dict) -> dict:
    """按 chart_type 路由。未知类型直接拒绝，不把近似名字交给模型猜。"""
    renderer = CHARTS.get(chart_type)
    if renderer is None:
        known = "、".join(sorted(CHARTS))
        return {"ok": False, "error": "unknown_chart", "message": f"只支持 {known}"}
    if "x" not in chart_config or "y" not in chart_config:
        return {"ok": False, "error": "invalid_config", "message": "chart_config 需要 x 和 y"}
    return {"ok": True, "spec": renderer(chart_config)}
