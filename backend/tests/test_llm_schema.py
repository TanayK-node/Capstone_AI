from app.llm.schema import inline_refs
from app.schemas.extraction import ExperimentsOut, SupportOut


def _walk(node: object) -> list[str]:
    keys: list[str] = []
    if isinstance(node, dict):
        for k, v in node.items():
            keys.append(k)
            keys += _walk(v)
    elif isinstance(node, list):
        for v in node:
            keys += _walk(v)
    return keys


def test_nested_models_are_inlined_without_refs_or_titles() -> None:
    schema = inline_refs(ExperimentsOut.model_json_schema())
    keys = _walk(schema)
    assert "$ref" not in keys and "$defs" not in keys and "title" not in keys
    dataset = schema["properties"]["datasets"]["items"]
    assert dataset["type"] == "object"
    assert {"name", "quote", "chunk_id"} <= set(dataset["properties"])


def test_enum_survives() -> None:
    schema = inline_refs(SupportOut.model_json_schema())
    verdict = schema["properties"]["verdicts"]["items"]["properties"]["verdict"]
    assert verdict["enum"] == ["yes", "partial", "no"]
