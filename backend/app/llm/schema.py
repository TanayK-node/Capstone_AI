"""Make Pydantic JSON schemas acceptable to provider structured-output modes.

Pydantic puts nested models under "$defs" and points at them with "$ref"; it also adds
"title" and "default" keys. Gemini's structured output supports only a subset of JSON
Schema, so we inline references and drop decoration it does not need.
"""

from __future__ import annotations

from typing import Any

_DROP = {"title", "default", "$defs", "examples"}


def inline_refs(schema: dict[str, Any]) -> dict[str, Any]:
    defs: dict[str, Any] = schema.get("$defs", {})

    def walk(node: Any, seen: tuple[str, ...]) -> Any:
        if isinstance(node, dict):
            if "$ref" in node:
                name = node["$ref"].rsplit("/", 1)[-1]
                if name in seen:
                    raise ValueError(f"recursive schema reference {name!r} cannot be inlined")
                merged = {**defs[name], **{k: v for k, v in node.items() if k != "$ref"}}
                return walk(merged, (*seen, name))
            return {k: walk(v, seen) for k, v in node.items() if k not in _DROP}
        if isinstance(node, list):
            return [walk(v, seen) for v in node]
        return node

    result: dict[str, Any] = walk(schema, ())
    return result
