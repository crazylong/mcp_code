# MCP 示例代码

《新版MCP 从协议到生产》的可运行示例。目录编号 `01_protocol`–`11_security` 与 `blog/` 里的篇号一一对应。

版本基线：Python 3.11+、MCP 规范 `2026-07-28`、`fastmcp==4.2.2`、`langchain[mcp]>=1.5.0`、`langgraph>=1.2.23`。

在仓库根目录执行：

```bash
pip install -r mcp_code/requirements.txt
cp mcp_code/.env.sample mcp_code/.env   # 只在要跑 --ask 时需要，填模型和 key
python mcp_code/check_samples.py
```

看到 `samples ok` 就说明不依赖大模型和外部网络的部分都过了：分页与末页边界、幂等、报文与 `_meta`、Resource / Prompt、进度、MRTR elicitation、中间件注入与退款收尾、JWT 签发、存量接口 401 重登、非法游标与读越界、下游不可达、工具分组、舱壁、四道闸、描述指纹、路径校验、`ClientHold` 生命周期。

## 目录

| 目录 | 对应篇 | 里面有什么 |
|---|---|---|
| `01_protocol/` | 协议 | `messages.json` 是一次不握手的 `tools/call`；`stateless_request.py` 把它打成带 `MCP-Protocol-Version`、`Mcp-Method`、`Mcp-Name` 的 POST |
| `02_stack/` | 新栈 | `fastmcp.Client` + `MCPAdapter` + `@wrap_tool_call` |
| `03_langchain/` | 接入 LangChain | stdio 数学服务、HTTP 天气服务、`MCPAdapter` 客户端 |
| `04_server/` | 生产级 Server | 描述边界、分页、截断、幂等、`cursor.mcp.json` |
| `05_features/` | Resource / Prompt / 进度 / Elicitation | 股票分析、导入进度、MRTR 式询问 |
| `06_interceptor/` | 中间件 | 嵌套 `@wrap_tool_call`、注入 `runtime.context`、退款后收尾 |
| `07_auth/` | 认证 | 本地签发 RS256 JWT，按 scope 显隐工具，按 `sub` / `dept` 控数据范围 |
| `08_legacy/` | 存量系统 | cookie 登录、401 重登、字段和分页适配 |
| `09_deploy/` | HTTP 部署 | 无状态 `ping` 服务和一份 Nginx 配置 |
| `10_governance/` | 治理 | 工具分组、图表入口、舱壁、调用字段、`Client` 生命周期 |
| `11_security/` | 安全 | 四道闸、描述指纹、路径校验、审计字段 |

## 不调模型就能跑

都在仓库根目录执行。只列工具、不进 Agent 的命令不需要 API key。

```bash
python mcp_code/01_protocol/stateless_request.py
python mcp_code/02_stack/client.py
python mcp_code/03_langchain/agent_client.py
python mcp_code/05_features/read_context.py
python mcp_code/05_features/import_client.py
python mcp_code/05_features/elicit_client.py
python mcp_code/06_interceptor/logging_client.py
```

要连天气服务时，先另开一个终端：

```bash
python mcp_code/03_langchain/weather_server.py
python mcp_code/03_langchain/agent_client.py --with-weather
```

认证示例会把公钥和 token 写到 `07_auth/.local/`，这个目录已忽略，不要提交：

```bash
python mcp_code/07_auth/gen_token.py
python mcp_code/07_auth/server.py
python mcp_code/07_auth/client.py
```

存量订单接口默认听 `127.0.0.1:8090`：

```bash
python mcp_code/08_legacy/legacy_api.py
LEGACY_BASE=http://127.0.0.1:8090 python mcp_code/08_legacy/order_mcp.py
```

无状态 HTTP 部署示例听 `127.0.0.1:8020`，`09_deploy/nginx.conf` 是给它前面的反代用的：

```bash
python mcp_code/09_deploy/server.py
python mcp_code/01_protocol/stateless_request.py http://127.0.0.1:8020/mcp ping
```

Cursor 挂第 4 篇的仓库工具时，把 `04_server/cursor.mcp.json` 里的 `/ABS/PATH/TO/mcp` 换成仓库的绝对路径。`args` 用相对路径时，客户端的工作目录一对不上，子进程就起不来。

## 要调模型

三个示例（`02_stack/client.py`、`03_langchain/agent_client.py --ask`、`06_interceptor/logging_client.py --ask`）通过 `.env` 取配置。配置文件和模板都放在 `mcp_code/` 下：

```bash
cp mcp_code/.env.sample mcp_code/.env
```

然后填三个值：

```bash
MCP_MODEL=openai:glm-5.3
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

`MCP_MODEL` **必须带供应商前缀**（`openai:`、`anthropic:`、`ollama:`）。走任何 OpenAI 兼容接口都写 `openai:`，真实地址由 `OPENAI_BASE_URL` 决定；写成裸的 `glm-5.3` 会报 `Unable to infer model provider`。

脚本启动时自动 `load_dotenv()`，不需要手动 `export`。`.env` 已被 `.gitignore` 忽略，`.env.sample` 只有占位符。

```bash
python mcp_code/02_stack/client.py
python mcp_code/03_langchain/agent_client.py --ask "计算 (3 + 5) × 12"
python mcp_code/06_interceptor/logging_client.py --ask
```

## 端口

| 端口 | 进程 |
|---|---|
| 8000 | `03_langchain/weather_server.py` |
| 8011 | `05_features/import_server.py` |
| 8012 | `05_features/elicit_server.py` |
| 8020 | `09_deploy/server.py` |
| 8090 | `08_legacy/legacy_api.py` |
| 8765 | `07_auth/server.py`（可用 `MCP_PORT` 改） |
