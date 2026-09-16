"""EB-208 (c): the SEED LEDGER — which seed stages which encounter.

WHY THIS EXISTS, IN ONE PARAGRAPH. A staged board cannot REQUIRE an enemy
count. `EB-202`'s reachability check takes its ceiling off the DECLARED board,
which is the only place it can take it from before a launch; `EB-208` (a) then
compares the DECLARED count against the LIVE one after staging and marks the
board UNREACHED on every slot whose predicate reads `enemy_count`. Both halves
are honest and neither of them can make a three-body board happen: the
encounter is generated from the run seed, so a turn file can wish for three
bodies and the seed can give one. The only thing that CAN is knowing a seed
that stages the encounter you want — and that is a fact about (character,
build, encounter) and nothing else, which is exactly what this file keys on.

WHAT IS BUILT HERE AND WHAT IS OWED. The ledger, its format, and the tool that
records into it from a turn that has already been staged. **The ledger ships
EMPTY and the Klee three-body seed hunt is OWED** — finding such a seed means
launching the game and staging boards until one rolls three bodies, which is
game time and is not this row's. `EB-208`'s own gate says so: (c) closes when
a turn file pins from it.

THE KEY IS THREE PARTS AND ALL THREE ARE LOAD-BEARING.

  * **character** — the encounter pool is the character's act pool.
  * **build** — the seed is a seed for THE GAME'S generator, and the mod moves
    what that generator is handed. A seed recorded against `0.2.3352+proto`
    is evidence about that package and no other; a ledger that let the build
    be omitted would quietly answer with a row from a world that has moved,
    which is the failure `EB-208` (a) was built to make visible rather than
    to reintroduce here. So `--build` is REQUIRED and is never defaulted.
  * **encounter** — a canonical key over the enemy names the board actually
    staged (`three_wurms`-shaped: sorted, counted), because that is the thing
    a turn file wants to pin and a name alone does not say how many.

NOTHING HERE LAUNCHES A GAME OR STAGES A BOARD. It reads a turn directory that
has already been staged (`observed.json` — the live board and the seed the
game used) and appends one row. A closed turn directory is read-only (R101b)
and is never written to.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

REPO = Path(__file__).resolve().parents[1]
QA_DIR = REPO / "review" / "qa"

#: The ledger. ONE file, in the tree, so a turn file's `seed:` can cite a row
#: by (character, build, encounter) and a later reader can check it.
LEDGER_PATH = Path(__file__).resolve().parent / "seeds" / "seed-ledger.json"

#: Bumped when a row grows or loses a field. A reader that does not know a
#: version refuses rather than guessing which fields it has.
SCHEMA_VERSION = 1

#: The sentence the empty ledger carries, so a reader who opens it before the
#: hunt has run finds out why it is empty rather than assuming it is broken.
EMPTY_NOTE = (
    "EMPTY BY DESIGN, NOT BROKEN. The format and the recorder are built "
    "(EB-208 (c)); the seeds are OWED. Finding one means launching the game "
    "and staging boards until the encounter rolls, which is game time. "
    "Record with: python -m understudy.seed_ledger record <turn-id> "
    "--build <package version>")


class SeedLedgerError(RuntimeError):
    """The ledger, the turn, or the row is not what it claims to be."""


# ------------------------------------------------------------ the key ------

_SLUG = re.compile(r"[^a-z0-9]+")


def _slug(name: str) -> str:
    return _SLUG.sub("_", str(name or "").strip().casefold()).strip("_")


def encounter_key(names: Iterable[str]) -> str:
    """A canonical key over the enemy names a board staged.

    Sorted and COUNTED — `fuzzy_wurm_crawler_x3`, not `fuzzy_wurm_crawler` —
    because the thing a turn file wants to pin is *three bodies*, and a key
    that dropped the count would answer a one-body seed to a three-body
    question. Sorted because the wire's order is the board's left-to-right
    and is not part of what was asked for.
    """
    counted: dict[str, int] = {}
    for name in names:
        slug = _slug(name)
        if not slug:
            continue
        counted[slug] = counted.get(slug, 0) + 1
    if not counted:
        raise SeedLedgerError("an encounter key needs at least one enemy name")
    return "+".join(f"{k}_x{counted[k]}" for k in sorted(counted))


# ---------------------------------------------------------- the turn -------

def _enemy_names(state: Mapping[str, Any]) -> list[str]:
    battle = state.get("battle")
    enemies = list((battle or {}).get("enemies") or [])
    out = []
    for e in enemies:
        if not isinstance(e, Mapping):
            continue
        name = str(e.get("name") or e.get("entity_id") or "").strip()
        if name:
            out.append(name)
    return out


def row_from_turn(turn_id: str, *, build: str,
                  qa_dir: Path | None = None,
                  why: str = "") -> dict[str, Any]:
    """One ledger row, read off a turn that has ALREADY been staged.

    `observed.json` is the file with both halves: `run_seed` is the seed the
    game actually used (`stage` records it there rather than in the blind
    `packet.md`, because a packet carrying its own seed is a packet carrying
    something the tester cannot see), and `state` is the live board the seed
    produced. Nothing is inferred from the DECLARED board: what is being
    recorded is what the seed did, not what the turn file hoped.
    """
    build = str(build or "").strip()
    if not build:
        raise SeedLedgerError(
            "a row needs the BUILD it was staged on -- a seed is a seed for "
            "the generator the package hands the game, and a row with no "
            "build answers a question about a world that has moved")
    home = (qa_dir or QA_DIR) / str(turn_id)
    path = home / "observed.json"
    if not path.is_file():
        raise SeedLedgerError(
            f"{path} does not exist; a row is recorded FROM a staged turn and "
            "this tool never stages one")
    blob = json.loads(path.read_text(encoding="utf-8"))
    state = blob.get("state")
    if not isinstance(state, Mapping):
        raise SeedLedgerError(f"{path} carries no `state`")
    seed = str(blob.get("run_seed") or "").strip()
    if not seed:
        raise SeedLedgerError(
            f"{path} records no `run_seed`, so there is no seed to pin -- a "
            "board staged on a seed nobody wrote down cannot be reached again")
    names = _enemy_names(state)
    if not names:
        raise SeedLedgerError(
            f"{path} shows no enemies; the encounter is what is keyed on and "
            "a board with none is not an encounter")
    run = state.get("run") or {}
    player = state.get("player") or {}
    return {
        "seed": seed,
        "character": _slug(player.get("character")) or "unknown",
        "build": build,
        "encounter": encounter_key(names),
        "enemies": names,
        "enemy_count": len(names),
        "act": run.get("act"),
        "floor": run.get("floor"),
        "turn_id": str(turn_id),
        "why": str(why or ""),
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


# --------------------------------------------------------- the ledger ------

def empty_ledger() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "note": EMPTY_NOTE, "rows": []}


def load(path: Path | None = None) -> dict[str, Any]:
    """The ledger, or an empty one where the file does not exist yet."""
    p = Path(path or LEDGER_PATH)
    if not p.is_file():
        return empty_ledger()
    blob = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(blob, Mapping) or not isinstance(blob.get("rows"), list):
        raise SeedLedgerError(f"{p}: a seed ledger is a mapping with a `rows` "
                             "list")
    version = blob.get("schema_version")
    if version != SCHEMA_VERSION:
        raise SeedLedgerError(
            f"{p}: schema_version {version!r} against this reader's "
            f"{SCHEMA_VERSION} -- a reader that guessed which fields a row "
            "has would answer a seed against the wrong key")
    return dict(blob)


def save(ledger: Mapping[str, Any], path: Path | None = None) -> Path:
    p = Path(path or LEDGER_PATH)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dict(ledger), indent=1) + "\n", encoding="utf-8")
    return p


def _identity(row: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return (str(row.get("character")), str(row.get("build")),
            str(row.get("encounter")), str(row.get("seed")))


def record(row: Mapping[str, Any], path: Path | None = None
           ) -> tuple[dict[str, Any], bool]:
    """Append one row. Returns `(the ledger, whether it was new)`.

    IDEMPOTENT ON THE FULL IDENTITY (character, build, encounter, seed): the
    same turn recorded twice writes one row, because a ledger that counted
    the same seed twice would read as two independent confirmations of it.
    A DIFFERENT seed for the same three-part key is a second row and is meant
    to be -- more than one seed staging an encounter is the useful case.
    """
    ledger = load(path)
    known = {_identity(r) for r in ledger["rows"]}
    if _identity(row) in known:
        return ledger, False
    ledger["rows"] = list(ledger["rows"]) + [dict(row)]
    # The note is about an EMPTY ledger and stops being true the moment one
    # row lands. Leaving it would be a banner contradicting the file it sits
    # at the top of.
    ledger["note"] = ("recorded by `python -m understudy.seed_ledger record`; "
                      "the key is (character, build, encounter) and a row is "
                      "evidence about the build it names and no other")
    save(ledger, path)
    return ledger, True


def find(*, character: str = "", build: str = "", encounter: str = "",
         enemy_count: int = 0, path: Path | None = None
         ) -> list[dict[str, Any]]:
    """Every row matching the parts that were given. All of them narrow."""
    rows = list(load(path)["rows"])
    if character:
        want = _slug(character)
        rows = [r for r in rows if str(r.get("character")) == want]
    if build:
        rows = [r for r in rows if str(r.get("build")) == str(build)]
    if encounter:
        rows = [r for r in rows if str(r.get("encounter")) == str(encounter)]
    if enemy_count:
        rows = [r for r in rows if int(r.get("enemy_count") or 0)
                == int(enemy_count)]
    return rows


def one_line(row: Mapping[str, Any]) -> str:
    return (f"{row.get('seed')}  {row.get('character')}  {row.get('build')}  "
            f"{row.get('encounter')}  (turn {row.get('turn_id')})")


# ------------------------------------------------------------- the CLI -----

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m understudy.seed_ledger",
        description=("EB-208 (c): which seed stages which encounter, keyed by "
                     "character, build and encounter. Reads a turn that has "
                     "already been staged; never stages one."))
    subs = p.add_subparsers(dest="cmd", required=True)

    rec = subs.add_parser("record", help="record one staged turn's seed")
    rec.add_argument("turn_id")
    rec.add_argument("--build", required=True,
                     help="the package version the turn was staged on, e.g. "
                          "0.2.3352+proto. REQUIRED: a seed is evidence about "
                          "one build")
    rec.add_argument("--why", default="", help="what this seed is kept for")
    rec.add_argument("--qa-dir", default="")
    rec.add_argument("--ledger", default="")

    fnd = subs.add_parser("find", help="the seeds matching a key")
    fnd.add_argument("--character", default="")
    fnd.add_argument("--build", default="")
    fnd.add_argument("--encounter", default="")
    fnd.add_argument("--enemy-count", type=int, default=0)
    fnd.add_argument("--ledger", default="")

    lst = subs.add_parser("list", help="every row")
    lst.add_argument("--ledger", default="")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    ledger_path = Path(args.ledger) if args.ledger else None
    try:
        if args.cmd == "record":
            row = row_from_turn(
                args.turn_id, build=args.build, why=args.why,
                qa_dir=Path(args.qa_dir) if args.qa_dir else None)
            _ledger, new = record(row, ledger_path)
            print(("recorded: " if new else "already recorded: ")
                  + one_line(row))
            return 0
        rows = (find(character=args.character, build=args.build,
                     encounter=args.encounter, enemy_count=args.enemy_count,
                     path=ledger_path) if args.cmd == "find"
                else load(ledger_path)["rows"])
    except (OSError, SeedLedgerError, json.JSONDecodeError) as exc:
        print(f"seed_ledger: {exc}", file=sys.stderr)
        return 2
    for row in rows:
        print("  " + one_line(row))
    if not rows:
        # SAID, NOT SILENT. An empty answer to a `find` and an empty ledger
        # are different facts and a caller about to stage a board needs to
        # know which it got.
        total = len(load(ledger_path)["rows"])
        print(f"  (no rows; the ledger holds {total})")
        print(f"  {EMPTY_NOTE}" if not total else "")
    return 0 if rows else 1


if __name__ == "__main__":                                # pragma: no cover
    raise SystemExit(main())
