"""审计记录要能回答谁、哪个会话、哪个工具、什么参数、什么结果、哪条决策。"""

from dataclasses import asdict, dataclass


@dataclass
class AuditRecord:
    user_id: str
    session_id: str
    tool_name: str
    arguments_digest: str
    decision: str
    result_status: str
    trace_id: str

    def as_log(self) -> dict:
        return asdict(self)
