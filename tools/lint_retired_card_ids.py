#!/usr/bin/env python3
"""The retired-id register is complete, consistent and alive (`EB-790`).

    python tools/lint_retired_card_ids.py
    python tools/lint_retired_card_ids.py --history   # extra: sweep git

WHY THIS EXISTS. A card id outlives the class that owned it, because the
progress save keeps a `CardStats` row and a `DiscoveredCards` entry for every
card the profile has ever seen and validates each one against `ModelDb`. A
retirement nobody recorded is a `ValidationError` in every future boot of that
profile, for a save this project has ruled it will never touch
(`live-looks-8c`, 2026-09-16). `docs/retired-card-ids.yaml` is the record and
`tools/gen_retired_card_aliases.py` is what makes it bite; this is the gate
over both.

THE FOUR CLAUSES, and each is a different way the register goes wrong.

  L1  EMITTED. The committed aliases are exactly what the register emits.
      Delegated to the generator's own `--check`, so there is one emitter and
      one comparison rather than a second opinion here.

  L2  NOT LIVE. No register id is an id a LIVE class already answers to. A
      collision would put two models under one `ModelId` in
      `ModelDb._contentById`, and the boot scan's iteration order decides
      which one the game keeps -- the live card or its tombstone. This is the
      clause that matters when a cut row comes back under its old name.

  L3  NOT GENERATED. No register id appears in any card profile's committed
      manifest. A row cannot be both retired and on a sheet; if it is, either
      the register kept a row the sheet took back, or a regen wrote a class
      and the alias for it at the same time.

  L4  RECORDED (`--history`). Every generated card class git has ever seen
      deleted, and no live class has re-used the name since, is in the
      register. This is the clause that SEEDED the file, and it is opt-in
      because CI clones shallow: `git log` on `--depth=1` sees one commit and
      would report a complete register as empty, which is worse than not
      asking. The standing guarantee is not this sweep but the write path --
      `gen_klee_cards._write_plan` appends a row in the same breath as it
      deletes the class -- and L3 is what catches that path failing.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tools import gen_retired_card_aliases as gen_aliases  # noqa: E402
from tools.retired_ids import entry_for                    # noqa: E402

CARD_ROOT = REPO / "klee-mod" / "KleeCode" / "Cards"
ALIAS_DIR = CARD_ROOT / "Retired" / "Generated"
MANIFESTS = (
    CARD_ROOT / "Generated" / "manifest.json",
    CARD_ROOT / "Furina" / "Generated" / "manifest.json",
    CARD_ROOT / "Kokomi" / "Generated" / "manifest.json",
    CARD_ROOT / "Prototype" / "Generated" / "manifest.json",
)
GENERATED_DIRS = tuple(m.parent.relative_to(REPO).as_posix() for m in MANIFESTS)
# The same pattern `tools/lint_pool_membership.py` uses, and for the same
# reason it grew the alternation: a face deriving from `ModalOptionCard` is
# every bit as live as one deriving from `CustomCardModel`.
CLASS_RE = re.compile(
    r"^\s*public\s+sealed\s+class\s+(\w+)\s*:\s*"
    r"(?:CustomCardModel|ModalOptionCard)\b", re.M)


def live_entries() -> dict[str, str]:
    """`ModelId.Entry` -> declaring file, for every live card class."""
    out: dict[str, str] = {}
    for path in sorted(CARD_ROOT.rglob("*.cs")):
        if ALIAS_DIR in path.parents:
            continue                      # the aliases are the dead half
        text = path.read_text(encoding="utf-8", errors="replace")
        for name in CLASS_RE.findall(text):
            out[entry_for(name)] = path.relative_to(REPO).as_posix()
    return out


def manifest_entries() -> dict[str, str]:
    """`ModelId.Entry` -> manifest, for every id a card profile generates."""
    out: dict[str, str] = {}
    for manifest in MANIFESTS:
        if not manifest.is_file():
            continue
        doc = json.loads(manifest.read_text(encoding="utf-8"))
        for card_id in doc.get("generated") or []:
            out["KLEEMOD-" + str(card_id).upper()] = \
                manifest.relative_to(REPO).as_posix()
    return out


def deleted_classes() -> tuple[set[str], bool]:
    """(class names git has seen deleted from a generated dir, history ok)."""
    shallow = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"],
        cwd=REPO, capture_output=True, text=True).stdout.strip() == "true"
    names: set[str] = set()
    for directory in GENERATED_DIRS:
        out = subprocess.run(
            ["git", "log", "--all", "--diff-filter=D", "--name-only",
             "--pretty=format:", "--", directory],
            cwd=REPO, capture_output=True, text=True).stdout
        names.update(Path(line.strip()).stem
                     for line in out.splitlines() if line.strip().endswith(".cs"))
    return names, not shallow


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--history", action="store_true",
                    help="also run L4, the git sweep (needs a deep clone)")
    args = ap.parse_args()

    findings: list[str] = []

    try:
        rows = gen_aliases.rows()
    except SystemExit as exc:
        print(f"FINDING: {exc}")
        return 1
    if not rows:
        # A register that scans nothing is not a gate. Every id the project has
        # ever retired is still retired; an empty file means a bad edit.
        print("FINDING: docs/retired-card-ids.yaml lists no ids. The file is "
              "append-only in practice -- a row is never removed, because the "
              "save that holds the id is never edited.")
        return 1
    ids = {str(row["id"]) for row in rows}

    # L1 -- the committed C# is what the register emits.
    generated, manifest_src = gen_aliases.plan()
    if gen_aliases._check(generated, manifest_src) != 0:
        findings.append(
            "L1: the committed retired aliases are stale against "
            "docs/retired-card-ids.yaml (see the lines above).")

    # L2 -- no retired id is an id a live class answers to.
    live = live_entries()
    for entry in sorted(ids & set(live)):
        findings.append(
            f"L2: {entry} is in the register AND declared live by "
            f"{live[entry]}. Two models cannot share a ModelId: the boot scan "
            f"would file one over the other in ModelDb._contentById and the "
            f"iteration order would decide which card the game has. Drop the "
            f"register row -- the id is not retired.")

    # L3 -- no retired id is on a sheet.
    manifests = manifest_entries()
    for entry in sorted(ids & set(manifests)):
        findings.append(
            f"L3: {entry} is in the register AND generated by "
            f"{manifests[entry]}. A row is retired or it is on a sheet, never "
            f"both.")

    # L4 -- opt-in, because a shallow clone cannot answer it.
    if args.history:
        deleted, deep = deleted_classes()
        if not deep:
            findings.append(
                "L4: --history was asked for on a SHALLOW clone; git log sees "
                "one commit, so the sweep would report every id as never "
                "deleted. Fetch the history or drop the flag.")
        else:
            missing = sorted(
                entry_for(name) for name in deleted
                if entry_for(name) not in ids
                and entry_for(name) not in live)
            for entry in missing:
                findings.append(
                    f"L4: {entry} was generated once and no live class "
                    f"answers to it now, but it is not in the register. A "
                    f"save that saw it warns at every boot. Add the row and "
                    f"run tools/gen_retired_card_aliases.py.")

    for finding in findings:
        print(f"FINDING: {finding}")
    if findings:
        return 1
    print(f"retired card ids: OK ({len(ids)} retired id(s) aliased, "
          f"{len(live)} live card class(es), none shared)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
