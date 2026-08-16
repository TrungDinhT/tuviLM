"""Compatibility type for model-stringified structured tool arguments."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import BeforeValidator


def _decode_json_up_to_twice(value: object) -> object:
    """Unwrap at most two JSON string layers before normal validation."""
    for _ in range(2):
        if not isinstance(value, str):
            break
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            break
    return value


type JsonCompatible[T] = Annotated[
    T,
    BeforeValidator(_decode_json_up_to_twice),
]


__all__ = ["JsonCompatible"]
