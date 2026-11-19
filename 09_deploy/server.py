"""无状态 HTTP：每个请求自带协议版本与能力，前面可以放普通负载均衡。"""

from fastmcp import FastMCP

mcp = FastMCP("deploy-demo")


@mcp.tool
def ping() -> str:
    """健康检查。确认端点、认证和反代都通了再挂业务工具。"""
    return "ok"


if __name__ == "__main__":
    # 8020：第 3 篇的天气服务占 8000，这里避开。
    # stateless_http 让每个请求独立，不再要求会话粘滞；协议版本由每个请求自带。
    mcp.run(transport="http", host="127.0.0.1", port=8020, stateless_http=True, show_banner=False)
