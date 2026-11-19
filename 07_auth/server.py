"""资源服务器：验 JWT，按 scope 暴露工具，数据范围从 token 取。"""

import os
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.auth import require_scopes
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token

LOCAL = Path(__file__).resolve().parent / ".local"

EMPLOYEES = {
    "E001": {"name": "张三", "department": "技术部"},
    "E002": {"name": "李四", "department": "财务部"},
}
BUDGETS = {
    "技术部": {"total": 500, "used": 320},
    "财务部": {"total": 150, "used": 90},
}


def load_verifier() -> JWTVerifier:
    public_key = Path(os.environ.get("MCP_PUBLIC_KEY_FILE", LOCAL / "public.pem")).read_text()
    return JWTVerifier(
        public_key=public_key,
        issuer=os.environ.get("MCP_ISSUER", "https://auth.example.com"),
        audience=os.environ.get("MCP_AUDIENCE", "http://127.0.0.1:8765/mcp"),
    )


mcp = FastMCP("Internal Tools", auth=load_verifier())


def caller() -> dict:
    token = get_access_token()
    if token is None:
        raise PermissionError("unauthenticated")
    return {"sub": token.claims["sub"], "dept": token.claims.get("dept"), "scopes": token.scopes}


@mcp.tool(auth=require_scopes("employee:read"))
def query_employee(employee_id: str) -> str:
    """查询员工。只能查 token 主体自己的档案，查不到和不是本人用同一句回复。"""
    who = caller()
    row = EMPLOYEES.get(employee_id)
    if row is None or employee_id != who["sub"]:
        return "未找到该员工"
    return f"{row['name']}，{row['department']}"


@mcp.tool(auth=require_scopes("budget:read"))
def query_department_budget(department: str) -> str:
    """查询部门预算。部门以 token 里的 dept 为准，参数里的部门名对不上就拒绝。"""
    who = caller()
    if department != who["dept"]:
        return "未找到该部门预算"
    budget = BUDGETS.get(department)
    if budget is None:
        return "未找到该部门预算"
    return f"总额 {budget['total']} 万，已用 {budget['used']} 万"


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=int(os.environ.get("MCP_PORT", "8765")))
