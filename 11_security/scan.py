"""描述投毒的静态扫描：返回命中的规则名，放不放由人决定，扫描不下结论。"""

import re

RULES = {
    # 人看到 A、模型读到 B 的那类字符
    "hidden_char": r"[\u200b-\u200f\u202a-\u202e\u2060\ufeff]|<!--",
    # 工具说明里没有正当理由出现的路径
    "sensitive_path": r"~/\.ssh|/etc/passwd|/etc/shadow|id_rsa|\.env\b|/root/",
    "outbound_url": r"https?://",
    # 说明里不该有的祈使句
    "imperative": (
        r"忽略(以上|之前|上述)|ignore (all )?(previous|above)"
        r"|调用(此|该)?工具前|before (using|calling) this tool"
    ),
}


def scan_description(text: str) -> list[str]:
    return [name for name, p in RULES.items() if re.search(p, text, re.I)]
