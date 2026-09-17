from __future__ import annotations

import functools
import inspect
import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Callable

logger = logging.getLogger(__name__)

_TYPE_MAP: dict[type, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


def _python_type_to_json(tp: type) -> str:
    return _TYPE_MAP.get(tp, "string")


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    func: Callable


@dataclass
class ToolCall:
    tool_name: str
    args: dict[str, Any]
    result: str
    success: bool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self._traces: list[ToolCall] = []

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool
        logger.info("已注册工具: %s", tool.name)

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def get_schemas(self) -> list[dict[str, Any]]:
        return [
            {"name": t.name, "description": t.description, "parameters": t.parameters}
            for t in self._tools.values()
        ]

    def list_names(self) -> list[str]:
        return list(self._tools.keys())

    def _record(self, trace: ToolCall) -> None:
        self._traces.append(trace)
        logger.info(
            "工具调用: %s | 参数: %s | 成功: %s | 结果: %s",
            trace.tool_name, trace.args, trace.success, trace.result[:100],
        )

    def get_traces(self) -> list[ToolCall]:
        return list(self._traces)

    def clear_traces(self) -> None:
        self._traces.clear()


registry = ToolRegistry()


def tool(func: Callable) -> Callable:
    sig = inspect.signature(func)
    properties: dict[str, Any] = {}
    required: list[str] = []

    for name, param in sig.parameters.items():
        param_type = _python_type_to_json(param.annotation if param.annotation is not inspect.Parameter.empty else str)
        properties[name] = {"type": param_type, "description": f"{name}参数"}
        if param.default is inspect.Parameter.empty:
            required.append(name)

    description = (inspect.getdoc(func) or "").strip()

    @functools.wraps(func)
    def traced_func(*args: Any, **kwargs: Any) -> Any:
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        trace_args = dict(bound.arguments)

        try:
            result = func(*args, **kwargs)
            registry._record(ToolCall(
                tool_name=func.__name__,
                args=trace_args,
                result=str(result),
                success=True,
            ))
            return result
        except Exception as e:
            registry._record(ToolCall(
                tool_name=func.__name__,
                args=trace_args,
                result=str(e),
                success=False,
            ))
            raise

    tool_obj = Tool(
        name=func.__name__,
        description=description,
        parameters={
            "type": "object",
            "properties": properties,
            "required": required,
        },
        func=traced_func,
    )
    registry.register(tool_obj)
    return func


def parse_llm_output(text: str) -> dict[str, Any]:
    tool_call_match = re.search(r"<tool_call>(.*?)</tool_call>", text, re.DOTALL)
    if tool_call_match:
        try:
            call_data = json.loads(tool_call_match.group(1).strip())
            return {
                "type": "tool_call",
                "tool": call_data["tool"],
                "args": call_data.get("args", {}),
            }
        except (json.JSONDecodeError, KeyError):
            logger.warning("工具调用解析失败，视为普通回复")
            return {"type": "answer", "content": text}

    return {"type": "answer", "content": text}
