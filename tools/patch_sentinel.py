"""Patch sentinel: does the CURRENT sts2.dll still agree with our baselines?

WHY THIS EXISTS
---------------
Every number this project measures against is downstream of a base-game
extract taken on some particular day. `game_ref/` holds those extracts and is
NON-REGENERABLE in practice -- it is gitignored, it is expensive to rebuild,
and several files in it carry hand-written review layers. The game, meanwhile,
patches monthly. When MegaCrit changes a cost, a rarity, a starting deck or a
relic, our baselines do not fail; they DRIFT, silently, and every anchor
measured against them quietly becomes a claim about a game that no longer
exists.

This tool is the alarm for that. It re-extracts the same surfaces out of the
DLL that is installed right now and reports where they disagree with the
stored baselines. It fixes nothing, it rewrites nothing in `game_ref/`, and it
is not a lint: a finding here is an INPUT to a [USER]-gated pass, never an
instruction to this or any other agent (see docs/patch-sentinel.md).

WHAT IT COMPARES
----------------
  cards       game_ref/<char>.json, the extractor's own per-card records, for
              every canon pool that has a baseline. Field-for-field.
  characters  game_ref/<char>_char_facts.yaml -- StartingHp, starting-deck
              size, starting-relic count. Structural only.
  relics      .sentinel/relics.json, a snapshot this tool blesses itself,
              because no relic baseline exists anywhere in the repo. First run
              establishes it and reports nothing.
  dll         .sentinel/dll.json -- size + sha256 of the assembly the last
              bless was taken from, so "the game patched" is visible even when
              no watched field moved.

IP / REPO RULE  (.gitignore:28, csharp-build-spec.md §0.3)
----------------------------------------------------------
This file contains no base-game data and is safe to commit. It reads no card
TEXT at any point -- the extractor's records are costs, rarities, command
vocabularies and var numbers, never prose -- so a finding is a field name and
a numeric or structural delta by construction. Entry NAMES are base-game
identifiers; they print by default because the report is a local terminal
artifact, and `--redact` replaces them with stable digests for anything that
gets pasted somewhere durable. Snapshots go to `.sentinel/`, which is
gitignored like `game_ref/`.

USAGE
-----
    python tools/patch_sentinel.py              # advisory report, exit 0
    python tools/patch_sentinel.py --strict     # exit 1 if anything drifted
    python tools/patch_sentinel.py --bless      # (re)take the self-snapshots
    python tools/patch_sentinel.py --redact     # digest the entry names
    python tools/patch_sentinel.py --surfaces cards,relics

Requires ilspycmd and a local game install for a real comparison. With
neither -- a CI runner, a fresh clone -- it prints why it could not look and
exits 0. That is the intended CI behaviour: this job proves the tool runs, it
does not assert anything about a game the runner does not have.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import extract_base_game_pool as extract      # noqa: E402

GAME_REF = REPO / "game_ref"
SNAP_DIR = REPO / ".sentinel"
RELIC_SNAPSHOT = SNAP_DIR / "relics.json"
DLL_SNAPSHOT = SNAP_DIR / "dll.json"

# The five canon pools. A character is only watched if its baseline exists --
# an absent game_ref/<char>.json is "not extracted here", not a finding.
CHARACTERS = ("Ironclad", "Silent", "Defect", "Necrobinder", "Regent")
RELIC_NS = "MegaCrit.Sts2.Core.Models.Relics"
RELIC_POOL_NS = "MegaCrit.Sts2.Core.Models.RelicPools"
CHAR_NS = "MegaCrit.Sts2.Core.Models.Characters."

SURFACES = ("dll", "cards", "characters", "relics")

# --- relic reads ------------------------------------------------------------
# Same discipline as the card extractor: match SHAPES, never names, so no
# base-game table ever enters this file.
NAMESPACE_DECL = re.compile(r"\bnamespace\s+([\w.]+)\s*(?:;|\{)")
RELIC_RARITY = re.compile(r"RelicRarity\.(\w+)")
# `new DynamicVar("Lightning", 1m)` and `new PowerVar<FocusPower>(1m)` are the
# two canonical-var spellings a relic model uses; both carry the printed
# number, which is the half that moves in a balance patch.
RELIC_NAMED_VAR = re.compile(r'new DynamicVar\(\s*"(\w+)"\s*,\s*(-?[\d.]+)m')
RELIC_TYPED_VAR = re.compile(r"new (\w+)Var<(\w+)>\(\s*(-?[\d.]+)m")
RELIC_PLAIN_VAR = re.compile(r"new (\w+)Var\(\s*(-?[\d.]+)m")
POOL_MEMBER = re.compile(r"ModelDb\.Relic<(\w+)>")
CARD_MEMBER = re.compile(r"ModelDb\.Card<(\w+)>")
STARTING_HP = re.compile(r"StartingHp\s*=>\s*(\d+)")
STARTING_GOLD = re.compile(r"StartingGold\s*=>\s*(\d+)")
DECK_BLOCK = re.compile(r"StartingDeck\s*=>(.*?);", re.S)
RELICS_BLOCK = re.compile(r"StartingRelics\s*=>(.*?);", re.S)


class Finding:
    """One disagreement. `kind` is added / removed / changed / schema."""

    def __init__(self, surface: str, key: str, kind: str,
                 field: str | None = None,
                 baseline: object = None, current: object = None,
                 note: str | None = None):
        self.surface = surface
        self.key = key
        self.kind = kind
        self.field = field
        self.baseline = baseline
        self.current = current
        self.note = note

    def render(self, redact: bool = False) -> str:
        key = digest(self.key) if redact else self.key
        if self.kind == "changed":
            return (f"  upstream changed {self.surface}/{key}.{self.field}: "
                    f"baseline says {self.baseline!r}, DLL says "
                    f"{self.current!r}")
        if self.kind == "added":
            return f"  upstream ADDED {self.surface}/{key}"
        if self.kind == "removed":
            return f"  upstream REMOVED {self.surface}/{key}"
        return f"  {self.surface}/{key}: {self.note}"

    def as_dict(self, redact: bool = False) -> dict:
        return {"surface": self.surface,
                "key": digest(self.key) if redact else self.key,
                "kind": self.kind, "field": self.field,
                "baseline": self.baseline, "current": self.current,
                "note": self.note}


def digest(name: str) -> str:
    """A stable stand-in for a base-game identifier.

    Same input, same digest across runs and machines, so a redacted report can
    still be compared with the next one -- which is the only thing a report
    that leaves this machine needs the name FOR.
    """
    return "id#" + hashlib.sha1(name.encode("utf-8")).hexdigest()[:8]


# ---------------------------------------------------------------------------
# The diff core. Pure, data-in/data-out, and tested against a synthetic
# fixture -- the one part of this tool that must be right whether or not a
# game is installed.
# ---------------------------------------------------------------------------

def diff_records(surface: str,
                 baseline: dict[str, dict],
                 current: dict[str, dict],
                 fields: tuple[str, ...] | None = None) -> list[Finding]:
    """Compare two {key: record} maps and return every disagreement.

    FIELD SETS ARE COMPARED BEFORE VALUES. If the baseline was written by an
    older extractor than the one running now, the honest answer is "these
    records are not the same shape", reported once as a `schema` finding --
    and then only the fields both sides carry are compared. Diffing the
    symmetric difference instead would report every card in the pool as
    changed and bury the one that actually moved.
    """
    findings: list[Finding] = []
    for key in sorted(set(current) - set(baseline)):
        findings.append(Finding(surface, key, "added"))
    for key in sorted(set(baseline) - set(current)):
        findings.append(Finding(surface, key, "removed"))

    shared = sorted(set(baseline) & set(current))
    if not shared:
        return findings

    if fields is None:
        base_fields = {f for k in shared for f in baseline[k]}
        cur_fields = {f for k in shared for f in current[k]}
        only_base = sorted(base_fields - cur_fields)
        only_cur = sorted(cur_fields - base_fields)
        if only_base or only_cur:
            findings.append(Finding(
                surface, "<schema>", "schema",
                note=("record shape differs; comparing the "
                      f"{len(base_fields & cur_fields)} shared fields only. "
                      f"baseline-only: {only_base or 'none'}; "
                      f"DLL-only: {only_cur or 'none'}")))
        compare = tuple(sorted(base_fields & cur_fields))
    else:
        compare = fields

    for key in shared:
        b, c = baseline[key], current[key]
        for field in compare:
            if field not in b or field not in c:
                continue
            if _normalise(b[field]) != _normalise(c[field]):
                findings.append(Finding(surface, key, "changed", field,
                                        b[field], c[field]))
    return findings


def _normalise(value: object) -> object:
    """JSON round-tripping turns 3 into 3.0 and tuples into lists.

    Neither is a patch. Normalising here keeps the report free of findings
    that describe our own serialisation rather than MegaCrit's changes.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, (list, tuple)):
        return [_normalise(v) for v in value]
    if isinstance(value, dict):
        return {k: _normalise(v) for k, v in sorted(value.items())}
    return value


# ---------------------------------------------------------------------------
# Readers
# ---------------------------------------------------------------------------

def _types_in_namespace(root: Path, namespace: str) -> dict[str, str]:
    """Every decompiled type declared in one namespace, by short name."""
    out: dict[str, str] = {}
    for path in root.rglob("*.cs"):
        try:
            src = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = NAMESPACE_DECL.search(src)
        if m and m.group(1) == namespace:
            out[path.stem] = src
    return out


def parse_relic(src: str, name: str) -> dict:
    """One relic's watched surface. Numbers and vocabularies, never text."""
    rarity = RELIC_RARITY.search(src)
    vars_: dict[str, float] = {}
    for var_name, value in RELIC_NAMED_VAR.findall(src):
        vars_[var_name] = float(value)
    for kind, arg, value in RELIC_TYPED_VAR.findall(src):
        vars_[arg] = float(value)
    for kind, value in RELIC_PLAIN_VAR.findall(src):
        # DynamicVar/PowerVar are handled above with their real key; a bare
        # `new DamageVar(6m)` keys off its own type like the card extractor.
        if kind not in ("Dynamic", "Power"):
            vars_.setdefault(kind, float(value))
    return {
        "name": name,
        "rarity": rarity.group(1) if rarity else None,
        "vars": vars_,
        "cmds": sorted({f"{a}.{b}" for a, b in extract.CMD.findall(src)}),
        # Relics reach for their effects through GENERIC commands far more
        # than cards do (`PowerCmd.Apply<XPower>(...)`), and the plain-call
        # regex cannot see those -- a relic watched on `cmds` alone would have
        # most of its vocabulary invisible.
        "generic_cmds": sorted({f"{a}.{b}"
                                for a, b in extract.GENERIC_CMD.findall(src)}),
        "powers": sorted(set(extract.POWER.findall(src))),
        "orbs": sorted(set(extract.ORB.findall(src))),
        "body_lines": src.count("\n"),
    }


def read_relics(root: Path) -> dict[str, dict]:
    """Every relic model, plus which relic pools list it."""
    sources = _types_in_namespace(root, RELIC_NS)
    pools = _types_in_namespace(root, RELIC_POOL_NS)
    membership: dict[str, list[str]] = {}
    for pool_name, pool_src in pools.items():
        for relic in POOL_MEMBER.findall(pool_src):
            membership.setdefault(relic, []).append(pool_name)
    records = {}
    for name, src in sources.items():
        # RelicModel itself and any abstract base are not relics.
        if not re.search(rf"class\s+{re.escape(name)}\s*:\s*RelicModel", src):
            continue
        record = parse_relic(src, name)
        record["pools"] = sorted(membership.get(name, []))
        records[name] = record
    return records


def read_character_facts(root: Path, character: str) -> dict:
    """StartingHp / deck size / starting-relic count, structurally."""
    src = extract._read_decompiled_type(root, CHAR_NS + character)
    hp = STARTING_HP.search(src)
    gold = STARTING_GOLD.search(src)
    deck = DECK_BLOCK.search(src)
    relics = RELICS_BLOCK.search(src)
    return {
        "hp": int(hp.group(1)) if hp else None,
        "starting_gold": int(gold.group(1)) if gold else None,
        "starting_deck_size": (len(CARD_MEMBER.findall(deck.group(1)))
                               if deck else None),
        "starting_relic_count": (len(POOL_MEMBER.findall(relics.group(1)))
                                 if relics else None),
    }


def baseline_character_facts(path: Path) -> dict | None:
    """The same three numbers as this repo's hand-kept char_facts YAML.

    Deliberately a narrow read rather than a YAML load of the whole file: the
    rest of that file is TRANSLATED into tier0's vocabulary (prefixed card ids,
    hook names), and translated fields cannot be compared with the DLL without
    inventing a mapping. Counts and HP survive the translation intact, so
    counts and HP are what this watches. `starting_gold` has no baseline field
    at all and is carried on the relic-style snapshot instead.

    THREE spellings of "a starting relic", not two (2026-08-05, R105). The
    first two are relics tier0 models: a bare hook name, and a hook that
    needed a number. The third, `unmodelled_starting_relics`, is a relic tier0
    CANNOT express -- Cracked Core channels an orb, Bound Phylactery summons a
    pet, Divine Right grants Stars, and this engine has orbs, relic-summons
    and Stars nowhere. The alternative to naming them was to leave the three
    new fact sheets at zero relics and let the sentinel report a fabricated
    finding on every run, or to invent a hook nothing implements. Counting a
    named-but-unmodelled relic keeps the COUNT honest -- which is the only
    thing this surface claims -- while the sheet says out loud that the effect
    is not simulated.
    """
    try:
        import yaml
    except ImportError:                                   # pragma: no cover
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return None
    hooks = data.get("relic_hooks") or []
    effects = data.get("starting_relic_effects") or []
    unmodelled = data.get("unmodelled_starting_relics") or []
    return {
        "hp": data.get("hp"),
        "starting_deck_size": len(data.get("starting_deck") or []),
        # All three spellings are the same fact -- a starting relic that the
        # loader could express as a bare hook, one that needed a number, and
        # one tier0 cannot express at all. Summing them is what makes this
        # comparable with a DLL count of relic types.
        "starting_relic_count": len(hooks) + len(effects) + len(unmodelled),
    }


def dll_fingerprint(dll: Path) -> dict:
    # read_bytes rather than a chunked open(): the assembly is ~9 MB, and the
    # encoding gate cannot tell a binary handle from a text one (it is a source
    # scan, not a runtime check), so the shape that needs no exemption wins.
    stat = dll.stat()
    return {"path": str(dll), "size": stat.st_size,
            "sha256": hashlib.sha256(dll.read_bytes()).hexdigest()}


# ---------------------------------------------------------------------------
# Surfaces
# ---------------------------------------------------------------------------

def check_cards(root: Path) -> tuple[list[Finding], list[str]]:
    findings: list[Finding] = []
    notes: list[str] = []
    for character in CHARACTERS:
        baseline_path = GAME_REF / f"{character.lower()}.json"
        if not baseline_path.exists():
            notes.append(f"cards/{character}: no baseline in game_ref -- "
                         f"not watched")
            continue
        rows = json.loads(baseline_path.read_text(encoding="utf-8"))
        baseline = {row["name"]: row for row in rows}
        names, sources = extract.read_pool(root, character)
        # The pool's resolved token types -- see canon_role_tempo's twin call.
        tokens = set(sources) - set(names)
        current = {}
        unparsed = []
        for name in names:
            card = extract.parse_card(sources[name], name, tokens)
            if card is None:
                unparsed.append(name)
                continue
            current[name] = card
        if unparsed:
            # The extractor's own ctor regex found nothing. That is a shape
            # change in CardModel, not a balance change -- and it is the one
            # failure mode that would make the diff below understate drift.
            notes.append(f"cards/{character}: {len(unparsed)} card types the "
                         f"extractor could not parse (ctor shape changed?)")
        findings.extend(diff_records(f"cards/{character}", baseline, current))
    return findings, notes


def check_characters(root: Path) -> tuple[list[Finding], list[str]]:
    findings: list[Finding] = []
    notes: list[str] = []
    fields = ("hp", "starting_deck_size", "starting_relic_count")
    for character in CHARACTERS:
        path = GAME_REF / f"{character.lower()}_char_facts.yaml"
        if not path.exists():
            notes.append(f"characters/{character}: no char_facts baseline -- "
                         f"not watched")
            continue
        baseline = baseline_character_facts(path)
        if baseline is None:
            notes.append(f"characters/{character}: baseline unreadable "
                         f"(pyyaml missing?) -- not watched")
            continue
        current = read_character_facts(root, character)
        findings.extend(diff_records(
            f"characters/{character}",
            {character: baseline}, {character: current}, fields=fields))
    return findings, notes


def check_relics(root: Path, bless: bool) -> tuple[list[Finding], list[str]]:
    current = read_relics(root)
    if bless or not RELIC_SNAPSHOT.exists():
        SNAP_DIR.mkdir(exist_ok=True)
        RELIC_SNAPSHOT.write_text(
            json.dumps(current, indent=1, sort_keys=True), encoding="utf-8")
        verb = "re-blessed" if bless else "established"
        return [], [f"relics: snapshot {verb} from the current DLL "
                    f"({len(current)} relics) -- nothing to compare yet"]
    baseline = json.loads(RELIC_SNAPSHOT.read_text(encoding="utf-8"))
    return diff_records("relics", baseline, current), []


def check_dll(dll: Path, bless: bool) -> tuple[list[Finding], list[str]]:
    current = dll_fingerprint(dll)
    if bless or not DLL_SNAPSHOT.exists():
        SNAP_DIR.mkdir(exist_ok=True)
        DLL_SNAPSHOT.write_text(json.dumps(current, indent=1),
                                encoding="utf-8")
        return [], [f"dll: fingerprint recorded ({current['size']} bytes, "
                    f"sha256 {current['sha256'][:12]}...)"]
    baseline = json.loads(DLL_SNAPSHOT.read_text(encoding="utf-8"))
    return diff_records("dll", {"sts2.dll": baseline}, {"sts2.dll": current},
                        fields=("size", "sha256")), []


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def report(findings: list[Finding], notes: list[str], redact: bool) -> None:
    print("=" * 72)
    print("PATCH SENTINEL -- advisory. Findings are alarms for a [USER]-gated")
    print("pass; nothing here is an instruction to change anything.")
    print("=" * 72)
    for note in notes:
        print(f"  note: {note}")
    if notes:
        print()
    if not findings:
        print("  no drift: every watched field matches its baseline.")
        return
    by_surface: dict[str, list[Finding]] = {}
    for f in findings:
        by_surface.setdefault(f.surface, []).append(f)
    for surface in sorted(by_surface):
        rows = by_surface[surface]
        kinds = {}
        for f in rows:
            kinds[f.kind] = kinds.get(f.kind, 0) + 1
        summary = ", ".join(f"{n} {k}" for k, n in sorted(kinds.items()))
        print(f"\n{surface}: {len(rows)} finding(s) -- {summary}")
        for f in rows:
            print(f.render(redact))
    print(f"\n  TOTAL: {len(findings)} finding(s) across "
          f"{len(by_surface)} surface(s).")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when anything drifted (NOT for CI)")
    ap.add_argument("--bless", action="store_true",
                    help="(re)write the self-managed snapshots from this DLL")
    ap.add_argument("--redact", action="store_true",
                    help="print stable digests instead of base-game names")
    ap.add_argument("--surfaces", default=",".join(SURFACES),
                    help=f"comma-separated subset of {','.join(SURFACES)}")
    ap.add_argument("--json", default=None,
                    help="also write the findings to this path as JSON")
    args = ap.parse_args(argv)

    wanted = [s.strip() for s in args.surfaces.split(",") if s.strip()]
    unknown = [s for s in wanted if s not in SURFACES]
    if unknown:
        ap.error(f"unknown surface(s): {unknown}; known: {list(SURFACES)}")

    # CANNOT-LOOK is not a failure. A fresh clone and a CI runner have neither
    # the game nor game_ref/, and a sentinel that fails there would be turned
    # off within a week. Say why, exit 0.
    try:
        dll = extract.game_dll()
    except SystemExit as err:
        print("PATCH SENTINEL: skipped -- no local game install "
              f"({err.code})")
        return 0
    if not GAME_REF.exists():
        print("PATCH SENTINEL: skipped -- no game_ref/ baselines on this "
              "machine (they are gitignored; extract locally first)")
        return 0

    findings: list[Finding] = []
    notes: list[str] = []

    if "dll" in wanted:
        f, n = check_dll(dll, args.bless)
        findings += f
        notes += n

    needs_tree = [s for s in wanted if s in ("cards", "characters", "relics")]
    if needs_tree:
        with extract.decompiled_project(dll) as root:
            if "cards" in wanted:
                f, n = check_cards(root)
                findings += f
                notes += n
            if "characters" in wanted:
                f, n = check_characters(root)
                findings += f
                notes += n
            if "relics" in wanted:
                f, n = check_relics(root, args.bless)
                findings += f
                notes += n

    report(findings, notes, args.redact)

    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(
            json.dumps([f.as_dict(args.redact) for f in findings], indent=1),
            encoding="utf-8")

    return 1 if (args.strict and findings) else 0


if __name__ == "__main__":
    sys.exit(main())
