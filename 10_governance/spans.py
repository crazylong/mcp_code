"""一次工具调用要留下的字段。属性名随 GenAI 语义约定变动，接入时钉住版本。"""

from dataclasses import asdict, dataclass


@dataclass
class ToolSpan:
    trace_id: str
    tool_name: str
    duration_ms: int
    is_error: bool
    arguments_digest: str
    decision: str

    def attributes(self) -> dict:
        return asdict(self)
