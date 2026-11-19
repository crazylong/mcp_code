"""退款成功后结束这一轮，不让模型再补一句「还需要什么帮助」。

1.x 里没有适配器级的 Command 返回通道了。留下的是 middleware 的
`before_model` 钩子：`jump_to="end"` 直接收尾，模型不会被再调一次。
"""

from langchain.agents.middleware import AgentMiddleware, hook_config
from langchain.messages import ToolMessage


def refunded(messages) -> bool:
    """最近一条 process_refund 的工具消息是否成功。"""
    for message in reversed(messages):
        if not isinstance(message, ToolMessage):
            continue
        if (message.name or "") != "process_refund":
            continue
        return "退款成功" in str(message.content)
    return False


class StopAfterRefund(AgentMiddleware):
    """退款成功后跳到最后。放进 create_agent 的 middleware 列表即生效。"""

    @hook_config(can_jump_to=["end"])
    def before_model(self, state, runtime):
        del runtime
        if refunded(state.get("messages", [])):
            return {"jump_to": "end"}
        return None
