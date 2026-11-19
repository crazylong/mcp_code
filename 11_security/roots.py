"""客户端声明的 roots 只作提示；路径是否放行由本函数自己判断。"""

from pathlib import Path


def inside_roots(path: Path, roots: list[Path]) -> bool:
    resolved = path.resolve()
    for root in roots:
        base = root.resolve()
        if resolved == base or base in resolved.parents:
            return True
    return False
