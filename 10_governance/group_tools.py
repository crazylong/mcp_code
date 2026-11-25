"""按前缀把工具分给不同角色。主 Agent 不挂这些业务工具。"""

from collections import defaultdict


def group_by_prefix(names: list[str], prefixes: dict[str, str]) -> dict[str, list[str]]:
    """prefixes: 前缀 -> 角色名。匹配不到的名字进入 unmatched。"""
    grouped: dict[str, list[str]] = defaultdict(list)
    for name in names:
        role = "unmatched"
        for prefix, owner in prefixes.items():
            if name.startswith(prefix):
                role = owner
                break
        grouped[role].append(name)
    return dict(grouped)


ROLES = {
    "poi_": "analysis",
    "weather_": "analysis",
    "chart_": "analysis",
    "order_": "ordering",
}
