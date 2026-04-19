from collections.abc import Callable
from typing import Any

from pydantic import BaseModel


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]


ToolHandler = Callable[..., dict[str, Any]]
