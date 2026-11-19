"""工具定义的指纹存在调用方，不存在 Server。"""

import hashlib
import json


def fingerprint(tool: dict) -> str:
    # 线上报文是 camelCase（inputSchema），SDK v2 的 Python 属性叫 input_schema，两个都收。
    payload = {
        "name": tool["name"].strip(),
        "description": " ".join(tool.get("description", "").split()),
        "schema": tool.get("inputSchema") or tool.get("input_schema") or {},
        "annotations": tool.get("annotations") or {},
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def check(tool: dict, allow: dict[str, str]) -> None:
    expected = allow.get(tool["name"])
    actual = fingerprint(tool)
    if expected != actual:
        raise RuntimeError(f"工具定义已变更，拒绝加载：{tool['name']}")
