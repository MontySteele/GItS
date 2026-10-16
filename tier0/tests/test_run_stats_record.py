"""The mod's run-stats record validates against the Worker's schema.

`klee-mod/KleeTests/RunStatsTests.cs` pins the C# trimmer's output for a
synthetic run to `klee-mod/KleeTests/Fixtures/run_stats_record_v1.json`; this
validates that same file against `telemetry-worker/schema/run-v1.json`, the
schema the Worker enforces on `POST /v1/run`. Together: what the beta sends is
what the Worker accepts.

The repo venv has no `jsonschema`, so this carries a validator for exactly the
keywords run-v1.json uses, and fails if the schema starts using one it does
not know (so a schema change cannot be skipped silently).
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "telemetry-worker" / "schema" / "run-v1.json"
RECORD = ROOT / "klee-mod" / "KleeTests" / "Fixtures" / "run_stats_record_v1.json"

KNOWN = {"$schema", "$id", "title", "description", "type", "additionalProperties",
         "required", "properties", "$defs", "$ref", "const", "enum", "pattern",
         "minLength", "maxLength", "minimum", "maximum", "minItems", "maxItems",
         "items", "anyOf"}


def _keywords(node, out: set[str]) -> set[str]:
    if isinstance(node, dict):
        for k, v in node.items():
            out.add(k)
            if k in ("properties", "$defs"):
                for sub in v.values():
                    _keywords(sub, out)
            elif isinstance(v, (dict, list)):
                _keywords(v, out)
    elif isinstance(node, list):
        for v in node:
            _keywords(v, out)
    return out


def _type_ok(value, t: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "boolean": isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "null": value is None,
    }[t]


def errors(value, schema: dict, root: dict, path: str = "$") -> list[str]:
    if "$ref" in schema:
        name = schema["$ref"].removeprefix("#/$defs/")
        return errors(value, root["$defs"][name], root, path)
    out: list[str] = []
    if "anyOf" in schema:
        if all(errors(value, s, root, path) for s in schema["anyOf"]):
            out.append(f"{path}: matches no anyOf branch")
    if "const" in schema and value != schema["const"]:
        out.append(f"{path}: != {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        out.append(f"{path}: not in {schema['enum']}")
    if "type" in schema and not _type_ok(value, schema["type"]):
        return out + [f"{path}: not {schema['type']}"]
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            out.append(f"{path}: too short")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            out.append(f"{path}: too long")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            out.append(f"{path}: {value!r} misses {schema['pattern']}")
    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            out.append(f"{path}: below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            out.append(f"{path}: above maximum")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            out.append(f"{path}: too few items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            out.append(f"{path}: too many items")
        if "items" in schema:
            for i, v in enumerate(value):
                out += errors(v, schema["items"], root, f"{path}[{i}]")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for k in schema.get("required", []):
            if k not in value:
                out.append(f"{path}: missing {k}")
        for k, v in value.items():
            if k in props:
                out += errors(v, props[k], root, f"{path}.{k}")
            elif schema.get("additionalProperties") is False:
                out.append(f"{path}: unknown field {k}")
    return out


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def test_the_validator_knows_every_keyword_the_schema_uses(schema):
    assert _keywords(schema, set()) <= KNOWN


def test_the_pinned_record_validates(schema, record):
    assert errors(record, schema, schema) == []


def test_the_pinned_record_covers_the_optional_shapes(record):
    # A card choice taken, one skipped, an Ancient, a null room, a co-op partner.
    choices = [f["card_choice"] for f in record["floors"] if "card_choice" in f]
    assert any(c["picked"] for c in choices) and any(not c["picked"] for c in choices)
    assert record["ancients"] and record["partners"]
    assert any(f["room"] is None for f in record["floors"])


@pytest.mark.parametrize("mutate", [
    lambda r: r.update(steam_id="76561198000000001"),
    lambda r: r.update(install_id="not-a-uuid"),
    lambda r: r.update(run_uuid="0b5e3c3e-6f1a-1d2b-9c4d-3a2f1e0d9c8b"),  # version 1
    lambda r: r["floors"][0].update(net_id=1),
    lambda r: r.update(character="Klee the player"),  # free text: a space
    lambda r: r.update(variant="dev"),
    lambda r: r.pop("relics"),
    lambda r: r["floors"][1]["card_choice"].update(offered=[]),
])
def test_the_validator_bites(schema, record, mutate):
    bad = copy.deepcopy(record)
    mutate(bad)
    assert errors(bad, schema, schema)


def test_no_net_id_reaches_the_record():
    text = RECORD.read_text(encoding="utf-8")
    assert "76561198" not in text
