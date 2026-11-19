"""把 runtime.context 补进工具参数。没有 Agent runtime 时原样放行。

caller_id 只帮日志知道是哪次调用，不能代替服务端验 token。
在 langchain[mcp] 里，横切逻辑挂在这里，不再有适配器私有的拦截器对象。
"""

from dataclasses import dataclass

from langchain.agents.middleware import wrap_tool_call


@dataclass
class CustomerContext:
    user_id: str
    api_key: str


@wrap_tool_call
async def inject_caller(request, handler):
    runtime = request.runtime
    ctx = getattr(runtime, "context", None) if runtime is not None else None
    if ctx is None:
        return await handler(request)
    tool_call = dict(request.tool_call or {})
    args = {**(tool_call.get("args") or {}), "caller_id": ctx.user_id}
    return await handler(request.override(tool_call={**tool_call, "args": args}))


if __name__ == "__main__":
    print("中间件就绪：", inject_caller.__name__)
