"""Internal utilities."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def resolve_body(model_cls: type[T], body: T | None, kwargs: dict[str, Any]) -> T | None:
    """Resolve dual-input pattern: accept either a model instance or kwargs.

    Raises TypeError if both are provided.
    Returns None if neither is provided and the body is optional.
    """
    if body is not None and kwargs:
        raise TypeError(
            f"Pass either a {model_cls.__name__} instance or keyword arguments, not both."
        )
    if body is not None:
        return body
    if kwargs:
        return model_cls.model_validate(kwargs)
    return None
