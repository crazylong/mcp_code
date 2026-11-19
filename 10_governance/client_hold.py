"""把一个 fastmcp.Client 的生命周期拉到应用级。

无状态协议下没有会话要复用，省的是 TCP/TLS 建连和每次 tools/list 的往返。
注意：`Client` 是异步上下文管理器，`open()` 与 `close()` 必须在**同一个 task** 里调用，
否则 anyio 会抛 "Attempted to exit cancel scope in a different task"。
跨 task 的场景（FastAPI lifespan、LangGraph 不同节点）请用一个常驻 worker task 持有它。
"""

from fastmcp import Client


class ClientHold:
    def __init__(self, target, headers: dict[str, str] | None = None):
        self.target = target
        self.headers = headers
        self.client: Client | None = None
        self._ctx = None

    async def open(self) -> Client:
        kwargs = {"headers": self.headers} if self.headers else {}
        self._ctx = Client(self.target, **kwargs)
        self.client = await self._ctx.__aenter__()
        return self.client

    async def close(self) -> None:
        if self._ctx is not None:
            await self._ctx.__aexit__(None, None, None)
        self.client = None
        self._ctx = None

    async def call(self, name: str, arguments: dict):
        if self.client is None:
            raise RuntimeError("先 open()")
        return await self.client.call_tool(name, arguments)
