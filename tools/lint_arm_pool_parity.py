#!/usr/bin/env python3
"""A prototype arm's OFFER roster must be the arm's sheet rows, in both engines.

WHY (round 10, 2026-09-04). R252 added the defence shelf -- four `proto_ko_`
rows -- to `docs/prototype-surface.yaml`, to the sim ops, to the powers, to the
codegen and to both engines' tests, and every gate was green. It did not add
them to `KleeOverhaulRoster.Slice()`, the arm's OFFER roster in the mod. The
four classes were generated and compiled into `PrototypeRoster`, so
`lint_pool_membership` was satisfied (it asks only that a class be in SOME
pool, which is a crash gate, not an offer gate); `Slice`'s only pin was a COUNT,
and a count goes red only if somebody remembers to raise it -- the same act
they had just forgotten. So the rows shipped unofferable: a live seat played
eight fights on the deployed build and was offered none of them, while the sim
offered all four the whole time.

THE INVARIANT, in one sentence: for each arm, the ids named in its roster's
`Slice()` are exactly the sheet's non-`basic` rows carrying the arm's id prefix,
in the sheet's order, and exactly the sim's mirror constant.

THREE CLAIMS, CHECKED SEPARATELY, because they fail in different places:

  (1) SHEET -> C#. Every non-`basic` sheet row with the arm's prefix is named
      in `Slice()`. This is the one the defect broke: a row exists, compiles,
      and is never offered.
  (2) C# -> SHEET. Every class `Slice()` names resolves to a sheet row with the
      arm's prefix and is not `basic`. Catches a starter row double-listed as a
      reward, and a stale class left behind by a deleted row.
  (3) C# == SIM. The ordered id list `Slice()` names equals the arm's
      `C.*_OVERHAUL_POOL_IDS`. The two lists are the two engines' answer to
      "what can this run be offered", and the roster's own docstring claims
      they are "the same ids ... in the same order"; nothing checked it.

`basic` IS THE STARTER'S MARK AND THE ONLY EXEMPTION. A `rarity: basic` row
cannot be rolled by any offer surface (the base game filters it upstream), and
under both arms the starter is a whole replacement -- so the arm's sheet rows
split cleanly in two with no curated debt list: the basics are the starter's,
everything else is the pool's. `lint_starter_pool_overlap` owns the sim-side
half of that same split.

READ OFF THE SOURCE, not off a build. The roster resolves every row through
`ModelDb.Card<T>()`, which throws until the game boots, so the C# side is
parsed: the type arguments in the `Slice()` body, mapped to sheet ids through
the `Sheet entry: id=` header each generated file carries. That is the same
seam `tools/lint_ancient_coverage.py` reads, and it is why a RENAME cannot
slip through either -- a renamed row regenerates its file with the new id and
the old type argument stops resolving.

Adding an arm means adding an ARMS row; a `*OverhaulRoster.cs` with a `Slice`
that this table does not name is a FINDING, not a skip.

Usage: python tools/lint_arm_pool_parity.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import yaml                                                   # noqa: E402

from tier0 import constants as C                              # noqa: E402

SHEET = REPO / "docs" / "prototype-surface.yaml"
CODE = REPO / "klee-mod" / "KleeCode"
ARM_DIR = CODE / "Powers" / "Prototype"
GENERATED = CODE / "Cards" / "Prototype" / "Generated"

# arm label -> (roster file, sheet id prefix, sim mirror constant).
ARMS: tuple[tuple[str, Path, str, str], ...] = (
    ("klee_overhaul",
     ARM_DIR / "KleeOverhaulRoster.cs", "proto_ko_", "KLEE_OVERHAUL_POOL_IDS"),
    ("kokomi_overhaul",
     ARM_DIR / "KokomiOverhaulRoster.cs", "proto_kk_",
     "KOKOMI_OVERHAUL_POOL_IDS"),
)
# The `*OverhaulRoster.cs` files that own no character reward pool, so have no
# `Slice` for this gate to read. The companion overhaul replaces a NATION's
# Universal roster, which is a different surface with its own gate
# (`lint_companion_shop_coverage`) and its own sheet prefix.
ROSTER_EXEMPT = {"CompanionOverhaulRoster.cs"}

SLICE_RE = re.compile(
    r"CardModel\[\]\s+Slice\s*\(\s*\)\s*=>\s*new\s+CardModel\[\]\s*\{(.*?)\n\s*\};",
    re.S)
MEMBER_RE = re.compile(r"ModelDb\.Card<(?:\w+\.)*(\w+)>\s*\(")
SHEET_ENTRY_RE = re.compile(r"^//\s+Sheet entry: id=(\S+)", re.M)
CLASS_RE = re.compile(r"public\s+sealed\s+class\s+(\w+)\s*[:{]")


def class_to_id() -> tuple[dict[str, str], list[str]]:
    """`{generated class name: sheet id}`, off each file's own header.

    The header is the emitter's own record of which row it built, so this map
    cannot drift from the sheet without the codegen gate going red first.

    ONE ROW PER FILE, BUT NOT ONE CLASS PER FILE. A choose-one row generates
    its card AND its mode faces into one file (EB-150), so the row's class is
    the one NAMED LIKE THE FILE and the rest are its faces -- which are never
    offered on their own, and a roster naming one would fail claim (2) above
    rather than resolve to the parent's id.
    """
    mapping: dict[str, str] = {}
    problems: list[str] = []
    if not GENERATED.is_dir():
        return mapping, [f"generated directory missing: "
                         f"{GENERATED.relative_to(REPO)}"]
    for path in sorted(GENERATED.glob("*.cs")):
        text = path.read_text(encoding="utf-8")
        ids = SHEET_ENTRY_RE.findall(text)
        names = CLASS_RE.findall(text)
        if not ids or not names:
            continue
        if len(ids) != 1:
            problems.append(
                f"{path.relative_to(REPO)}: {len(ids)} `Sheet entry:` headers; "
                f"this lint needs one sheet row per generated file to "
                f"attribute an id.")
            continue
        if path.stem not in names:
            problems.append(
                f"{path.relative_to(REPO)}: declares {', '.join(names)} and "
                f"none is named for the file, so which class is the sheet "
                f"row's cannot be told from the source.")
            continue
        mapping[path.stem] = ids[0]
    return mapping, problems


def sheet_rows() -> list[dict]:
    return yaml.safe_load(SHEET.read_text(encoding="utf-8")) or []


def main() -> int:
    findings: list[str] = []

    if not SHEET.is_file():
        print(f"FINDING: sheet missing: {SHEET.relative_to(REPO)}")
        return 1
    rows = sheet_rows()
    by_id = {row["id"]: row for row in rows}
    mapping, problems = class_to_id()
    findings += problems
    if not mapping:
        print("FINDING: no generated prototype card carries a "
              "`Sheet entry: id=` header -- the emitter's format or the "
              "layout changed, and this gate is reading nothing.")
        return 1

    named_rosters = {path.name for _, path, _, _ in ARMS}
    for path in sorted(ARM_DIR.glob("*OverhaulRoster.cs")):
        if path.name in named_rosters or path.name in ROSTER_EXEMPT:
            continue
        if SLICE_RE.search(path.read_text(encoding="utf-8")):
            findings.append(
                f"{path.relative_to(REPO)} has a `Slice()` this lint has no "
                f"ARMS row for -- add it (or ROSTER_EXEMPT, with the reason "
                f"it offers no character pool).")

    checked: list[str] = []
    for arm, path, prefix, constant in ARMS:
        if not path.is_file():
            findings.append(f"{arm}: roster missing: {path.relative_to(REPO)}")
            continue
        body = SLICE_RE.search(path.read_text(encoding="utf-8"))
        if body is None:
            findings.append(
                f"{arm}: no `private static CardModel[] Slice() => new "
                f"CardModel[] {{...}}` in {path.name} -- the offer roster "
                f"moved and this gate cannot see it.")
            continue

        classes = MEMBER_RE.findall(body.group(1))
        roster_ids: list[str] = []
        for name in classes:
            cid = mapping.get(name)
            if cid is None:
                findings.append(
                    f"{arm}: {path.name} offers {name}, which is not a "
                    f"generated prototype card -- no sheet row builds it, so "
                    f"the offer names something the sheet does not.")
                continue
            roster_ids.append(cid)

        # (1) and (2), by id and in the sheet's own order.
        sheet_ids = [row["id"] for row in rows
                     if row["id"].startswith(prefix)
                     and row.get("rarity") != "basic"]
        for cid in sheet_ids:
            if cid not in roster_ids:
                findings.append(
                    f"{arm}: {cid} is on the sheet, is not `rarity: basic`, "
                    f"and is not in {path.name}'s Slice() -- it compiles, it "
                    f"is in a pool, and NO OFFER SURFACE CAN EVER SHOW IT.")
        for cid in roster_ids:
            row = by_id.get(cid)
            if row is None:
                findings.append(
                    f"{arm}: {path.name} offers {cid}, which is not on the "
                    f"prototype surface at all.")
            elif not cid.startswith(prefix):
                findings.append(
                    f"{arm}: {path.name} offers {cid}, which does not carry "
                    f"this arm's `{prefix}` prefix.")
            elif row.get("rarity") == "basic":
                findings.append(
                    f"{arm}: {path.name} offers {cid}, a `rarity: basic` row "
                    f"-- a starter card the reward screen would also sell.")
        if len(set(roster_ids)) != len(roster_ids):
            duplicates = sorted({c for c in roster_ids
                                 if roster_ids.count(c) > 1})
            findings.append(
                f"{arm}: {path.name} offers {', '.join(duplicates)} more than "
                f"once, which doubles the row's offer odds.")

        # (3) the sim's mirror, ordered.
        mirror = list(getattr(C, constant, ()) or ())
        if not mirror:
            findings.append(
                f"{arm}: `C.{constant}` is empty or missing -- the sim mirror "
                f"this roster claims to match does not exist.")
        elif mirror != roster_ids:
            only_sim = [c for c in mirror if c not in roster_ids]
            only_cs = [c for c in roster_ids if c not in mirror]
            if only_sim or only_cs:
                findings.append(
                    f"{arm}: `C.{constant}` and {path.name}'s Slice() are "
                    f"different sets -- sim only: "
                    f"{', '.join(only_sim) or 'none'}; mod only: "
                    f"{', '.join(only_cs) or 'none'}. The two engines offer "
                    f"different runs.")
            else:
                findings.append(
                    f"{arm}: `C.{constant}` and {path.name}'s Slice() hold "
                    f"the same {len(mirror)} ids in DIFFERENT ORDER; the "
                    f"roster's docstring claims the same order, so one of the "
                    f"two moved.")
        # And the sheet's order, which is the order both lists claim to be in.
        if sorted(roster_ids) == sorted(sheet_ids) and roster_ids != sheet_ids:
            findings.append(
                f"{arm}: {path.name}'s Slice() holds the sheet's rows in a "
                f"different order than the sheet prints them.")

        checked.append(f"{arm}={len(roster_ids)}")

    for finding in findings:
        print(f"FINDING: {finding}")
    if findings:
        return 1
    print(f"arm pool parity: OK ({'; '.join(checked)}; sheet, mod and sim "
          f"agree by id and in order)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
