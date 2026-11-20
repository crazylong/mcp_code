"""把一个 fastmcp.Client 的生命周期拉到应用级。

无状态协议下没有会话要复用，省的是 TCP/TLS 建连和每次 `tools/list` 的往返。

两条约束：
1. `Client` 是异步上下文管理器，`open()` 与 `close()` 必须在**同一个 task** 里调用，
   否则 anyio 会抛 "Attempted to exit cancel scope in a different task"。
2. `Client` 没有 `headers` 参数。请求头属于传输层（`StreamableHttpTransport(url, headers=...)`），
   Bearer token 用 `auth=` 传。
"""

import contextlib

from fastmcp import Client


class ClientHold:
    def __init__(self, target, auth: str | None = None):
        self.target = target
        self.auth = auth
        self.client: Client | None = None
        self._ctx: contextlib.AbstractAsyncContextManager | None = None

    async def open(self) -> Client:
        self._ctx = Client(self.target, **({"auth": self.auth} if self.auth else {}))
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
