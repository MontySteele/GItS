"""The seam between lane C's QA gates and lane B's art/provenance ledger.

Lane B (charter section 5, `EB-148`) owns the ledger's schema, its tool, and
its tests. Lane C must not co-edit those files, and the two lanes are being
built at the same time in separate worktrees -- so this module is the ONLY
place lane C knows anything about a ledger row, and it is deliberately small.

**What lane C consumes.** Five fields, and nothing else:

    asset_id      stable id of the expected surface
    packed_path   where it must appear inside the pack, WITHOUT "res://"
                  (e.g. "furina/ui/char_icon.png")
    fallback_from character id this row is knowingly filled from, or None
    rights_tier   "private" / "public-safe" / None -- carried, never judged
    review_state  free text, carried so a report can group by it

**What lane C does NOT need and must not assume:** the ledger's own column
names, its file format, its row ordering, its source/output columns, or any
of its coverage arithmetic. Those are lane B's.

**The alignment step at merge** is therefore exactly one function:
`row_from_mapping`. It accepts several plausible key spellings today
(`packed_path` / `packed` / `pck_path`, `fallback_from` / `fallback`), which
is a bridge, not a schema. When lane B's real column names land, the alias
table below collapses to the real ones and every gate above keeps working
untouched. If a mapping carries none of the aliases for `packed_path`, the row
is returned with `packed_path=None` and the gate reports it -- it is never
guessed.

The fixture in `fixtures/ledger_rows.sample.json` is lane C's stand-in for a
real export and exists so these gates have tests before lane B lands.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .findings import Report

GATE = "ledger"

#: canonical field -> accepted incoming key spellings, most-preferred first.
ALIASES: dict[str, tuple[str, ...]] = {
    "asset_id": ("asset_id", "id", "asset"),
    "packed_path": ("packed_path", "packed", "pck_path", "resource"),
    "fallback_from": ("fallback_from", "fallback", "filled_from"),
    "rights_tier": ("rights_tier", "rights", "tier"),
    "review_state": ("review_state", "review", "state"),
}


@dataclass(frozen=True)
class LedgerRow:
    asset_id: str
    packed_path: str | None
    fallback_from: str | None = None
    rights_tier: str | None = None
    review_state: str | None = None


def _pick(mapping: dict, field: str) -> str | None:
    for key in ALIASES[field]:
        if key in mapping and mapping[key] not in (None, ""):
            return str(mapping[key])
    return None


def row_from_mapping(mapping: dict) -> LedgerRow:
    """THE alignment point with lane B. One function, five fields."""
    packed = _pick(mapping, "packed_path")
    if packed:
        packed = packed.replace("\\", "/")
        if packed.startswith("res://"):
            packed = packed[len("res://"):]
    return LedgerRow(
        asset_id=_pick(mapping, "asset_id") or "",
        packed_path=packed,
        fallback_from=_pick(mapping, "fallback_from"),
        rights_tier=_pick(mapping, "rights_tier"),
        review_state=_pick(mapping, "review_state"),
    )


def load_rows(path: Path) -> list[LedgerRow]:
    """Read a ledger export. JSON (list, or {"rows": [...]}) or TSV."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".json",):
        data = json.loads(text or "[]")
        if isinstance(data, dict):
            data = data.get("rows", [])
        return [row_from_mapping(item) for item in data]
    if path.suffix.lower() in (".yaml", ".yml"):
        import yaml

        data = yaml.safe_load(text) or []
        if isinstance(data, dict):
            data = data.get("rows", [])
        return [row_from_mapping(item) for item in data]
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        cells = line.split("\t")
        rows.append(row_from_mapping(dict(zip(header, cells))))
    return rows


def check_against_contract(
    rows: list[LedgerRow], packed: set[str], where: str
) -> Report:
    """Join the ledger's expected surfaces to what the pack actually holds."""
    report = Report(GATE)
    report.checked["ledger_rows"] = len(rows)
    if not rows:
        report.error("LG-EMPTY", where,
                     "ledger export has no rows; an empty sweep is the "
                     "failure mode, not a pass.")
        return report
    without_path = 0
    for row in rows:
        if not row.packed_path:
            without_path += 1
            report.warning(
                "LG-NO-PACKED-PATH", where,
                f"row {row.asset_id!r} carries no packed path, so this gate "
                "cannot say whether it shipped. Not guessed.",
            )
            continue
        if row.packed_path not in packed:
            report.error(
                "LG-EXPECTED-MISSING", where,
                f"ledger row {row.asset_id!r} expects res://{row.packed_path}, "
                "which the pck contract does not list. Either the art never "
                "reached the pack or the ledger row is stale.",
            )
    report.checked["rows_without_packed_path"] = without_path
    return report


def check_fallbacks(rows: list[LedgerRow], observed, where: str) -> Report:
    """Every observed build fallback must be a ledger row that admits it.

    `observed` is the list of `fallback.Fallback` records parsed from a build
    log. This is the second half of gate 3: the policy file answers "is this
    fallback allowed", the ledger answers "does the art bookkeeping KNOW about
    it". A fallback nobody's ledger records is how a character ships wearing
    another character's art with every gate green.
    """
    report = Report(GATE)
    by_path = {row.packed_path: row for row in rows if row.packed_path}
    report.checked["observed_fallbacks"] = len(observed)
    for item in observed:
        full = f"{item.into.lower()}/{item.resource}"
        row = by_path.get(full)
        if row is None:
            report.error(
                "LG-FALLBACK-UNKNOWN", where,
                f"build filled {full} from {item.source}, and the ledger has "
                "no row for that packed path at all.",
            )
        elif not row.fallback_from:
            report.error(
                "LG-FALLBACK-UNDECLARED", where,
                f"build filled {full} from {item.source}, but ledger row "
                f"{row.asset_id!r} does not record a fallback. The ledger "
                "reads as if that surface has its own art.",
            )
        elif row.fallback_from.lower() != item.source.lower():
            report.error(
                "LG-FALLBACK-MISMATCH", where,
                f"build filled {full} from {item.source}; ledger row "
                f"{row.asset_id!r} records {row.fallback_from}.",
            )
    return report
