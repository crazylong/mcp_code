"""四道闸。前一道没过，就不做后面的判断。"""

from dataclasses import dataclass


@dataclass
class Decision:
    gate: str
    effect: str
    reason: str


def authorize(
    *,
    authenticated: bool,
    scopes: set[str],
    required_scope: str,
    role_tools: set[str],
    tool_name: str,
    tenant_allows: bool,
    resource_owner: str,
    caller_id: str,
    amount: float,
    confirm_limit: float,
    approve_limit: float,
) -> Decision:
    if not authenticated:
        return Decision("identity", "deny", "没有通过签名、issuer、audience 或过期检查")
    if required_scope not in scopes or tool_name not in role_tools:
        return Decision("visibility", "deny", "scope 或角色工具集里没有这个工具")
    if not tenant_allows:
        return Decision("policy", "deny", "当前租户或环境不允许")
    # 先确认这条记录是不是调用者自己的，再谈金额。归属没定就别进入审批分支。
    if resource_owner != caller_id:
        return Decision("recheck", "deny", "资源不属于 token 里的调用者")
    if amount > approve_limit:
        return Decision("policy", "approve", "超过审批阈值")
    if amount > confirm_limit:
        return Decision("policy", "confirm", "额度内写操作，先回显参数")
    return Decision("recheck", "allow", "只读或阈值内，带调用者过滤执行")
