#!/usr/bin/env python3
"""Art coverage + provenance LEDGER, joined across every expected visual surface.

Charter label EB-148 (surplus-dispatch-3, tooling lane B). This is NOT a
replacement for `tools/art_coverage.py`: that tool answers ONE question well
("which card portraits are missing") and this one joins its universe to the
five surfaces it never sees -- power badges, relic icons, character-select UI,
combat models, salon/summon sprites -- and to the provenance columns nobody
could previously query at all.

WHAT A LEDGER ROW IS
--------------------
One EXPECTED SURFACE: something the shipped mod will try to load at runtime.
Expectations are DERIVED, never listed here:

  cards  the canonical YAML sheets plus every `Art.CardPortrait("<id>")`
         literal in the mod source -- the same two universes art_coverage
         bills, so the two tools reconcile by construction. The report ends
         with that reconciliation, and
         `test_card_universe_matches_art_coverage_on_this_repo` pins it.
  pck    every `"<character>/<sub>/<name>.<ext>"` literal in the mod source.
         That is a superset of the `KleePck.Path(...)` call sites: the salon
         member bridge and the Bake-Kurage docket sprite pass their relative
         paths through other helpers, and a ledger that only knew about
         KleePck.Path could not see them.
  scene  every `res://<character>/...` reference inside a packed TEXT
         resource -- the git-tracked scenes under klee-mod/pck-src and the
         here-string scenes/materials authored by tools/build_pck.ps1. This
         universe is not optional: `select_bg.png`, `selection_splash.png`
         and `transition_wipe.png` are referenced by NOTHING in C#, only by
         those scenes, so without it the ledger calls three shipped surfaces
         stale and misses the combat layer sprites entirely.

Each row then carries the join the charter asked for:

  source          where the pixels came from (art/SOURCES.tsv URL, a generator
                  script, an authored text resource, or NOTHING)
  rendered_output the ImageGen path the pipeline writes, and whether it exists
  packed_path     res://... for pck surfaces (checked against the pck build
                  contract), images/cards/<id>.png for loose card portraits
  fallback        none | active | unintended, against the fallback lists
                  declared in tools/build_pck.ps1
  rights_tier     private-placeholder | public-safe | unclassified, read from
                  declared evidence only -- this tool ASSIGNS NOTHING
  review_state    the art_lint / art_coverage curated registries

RIGHTS TIERS ARE READ, NOT DECIDED
----------------------------------
`docs/art-asset-manifest.md:79-81` defines the two tiers the repo already
uses: Tier F (found/official/fan) is private builds only, Tier O
(original/commissioned) is the only tier that ships publicly. This tool maps
those letters onto the charter's two CATEGORIES and reports the evidence
string beside every row:

    F -> private-placeholder      O -> public-safe      anything else -> unclassified

Evidence is taken, in order, from (1) the `tier` column of the row in
art/SOURCES.tsv for that output, (2) a `Tier X` declaration in the module
docstring of the generator that owns the out-path (art_lint.GENERATOR_OWNED),
(3) nothing -- in which case the row is `unclassified` and says why. An
unclassified row is a QUESTION FOR [USER], never a default of either category.

The two coverages are reported SEPARATELY and are never summed into one
"coverage" number: a build that is 100% covered by private placeholders is 0%
ready to ship publicly, and one number cannot say both.

CHECKS
------
    MISSING-PACKED       the mod asks for a pck resource that the build
                         contract does not contain
    MISSING-RENDER       an expected surface has no rendered output on disk
    STALE-ROW            an art/SOURCES.tsv provenance row points at a
                         rendered output that no longer exists
    STALE-OUTPUT         a rendered file that no expected surface claims
    ACTIVE-FALLBACK      a character's own art is absent for a path
                         build_pck.ps1 declares a fallback for, so the build
                         WILL ship another character's bytes at that path
                         (reported, not a defect -- it is the sanctioned
                         mechanism)
    UNINTENDED-FALLBACK  another character's bytes reach a path NOBODY
                         declared a fallback for -- proved by byte identity
                         across two characters' rendered outputs, or by a
                         build log line for an undeclared path, or by a build
                         log line that fired even though the character HAS its
                         own art (the C4 `-Exclude` defect: a green build that
                         shipped the wrong character's face)
    RIGHTS-INHERITANCE   a generator declares Tier O for an out-path while
                         reading a Tier F input, so the declaration cannot be
                         true as written

EVERYTHING IS ROOTED
--------------------
`--root` is REQUIRED and every read is relative to it -- sheets, mod source,
build script, curated registries, SOURCES.tsv, the pck contract and the art
tree alike. The lane B worktree has no art at all (ImageGen/ and art/raw/ are
gitignored), so a tool that could only read its own checkout could not be run
or tested. The tests build small synthetic roots; the real run points at the
art-bearing checkout.

The curated registries (art_lint.GENERATOR_OWNED and friends, and
art_coverage.KNOWN_STALE) are read out of `<root>/tools/*.py` by AST literal
evaluation rather than by import. They are DATA that differs per checkout, and
parsing them beats importing a module whose own module-level paths would then
point at the wrong root.

Usage:
    python tools/art_ledger.py --root <checkout>
    python tools/art_ledger.py --root <checkout> --json ledger.json
    python tools/art_ledger.py --root <checkout> --build-log deploy.log
    python tools/art_ledger.py --root <checkout> --strict     # defects => exit 1
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from fnmatch import fnmatch
from pathlib import Path

import yaml

SCHEMA_VERSION = "art-ledger-v1"

# --------------------------------------------------------------------------
# Expected-surface universes. Paths are repo-relative and joined onto --root.
# --------------------------------------------------------------------------

# (sheet, output dir, owner). Mirrors tools/art_coverage.SHEETS deliberately:
# the two tools must bill the same card universe or --reconcile is a lie.
CARD_SHEETS = [
    ("docs/klee-cards.yaml", "ImageGen/images/cards/klee", "klee"),
    ("docs/furina-cards.yaml", "ImageGen/images/cards/furina", "furina"),
    ("docs/kokomi-cards.yaml", "ImageGen/images/cards/kokomi", "kokomi"),
    ("docs/inazuma-companions.yaml", "ImageGen/images/cards/companions", "companions"),
    ("docs/mondstadt-companions.yaml", "ImageGen/images/cards/companions", "companions"),
    ("docs/fontaine-companions.yaml", "ImageGen/images/cards/companions", "companions"),
]
TOKENS_SHEET = "tier0/content/cards/tokens.yaml"
TOKENS_DIR = "ImageGen/images/cards/furina"

MOD_SRC = "klee-mod/KleeCode"
SOURCES_TSV = "art/SOURCES.tsv"
PLAN_TSV = "art/plan.tsv"
BUILD_PCK = "tools/build_pck.ps1"
PCK_SRC = "klee-mod/pck-src"
PCK_CONTRACT = "klee-mod/assets/klee.pck.contract.txt"
ART_LINT = "tools/art_lint.py"
ART_COVERAGE = "tools/art_coverage.py"

# The ONE way a card asks for a portrait at runtime (klee-mod/KleeCode/KleeArt.cs).
ART_KEY_RE = re.compile(r"Art\.CardPortrait\(\"([a-z0-9_]+)\"\)")

# Every pck-relative resource literal in the mod source. Deliberately wider
# than `KleePck.Path("...")`: TurnEndAttribution.cs and Vfx/SalonVisualsBridge.cs
# hold their relative paths in constants and dictionaries and hand them to
# other helpers, so a KleePck.Path-only regex under-bills the salon members,
# the salon glyphs and the Bake-Kurage docket sprite.
PCK_KEY_RE = re.compile(
    r"\"((?:klee|furina|kokomi|shared)/[a-z0-9_/]+\.(?:png|tscn|tres))\"")

# A pck path built by CONCATENATION, e.g.
#   "klee/powers/aura_" + aura.Element.ToString().ToLowerInvariant() + ".png"
# (klee-mod/KleeCode/Powers/KleePowerIcons.cs:120). The set such a site demands
# CANNOT be enumerated by reading strings, so the ledger does not pretend to:
# it attributes every file already sitting under the prefix to the call site
# and says out loud that the universe is unknown. Without this the six aura
# badges read as stale outputs AND as packed-but-unexpected -- two wrong
# answers about art that is shipping and working.
PCK_PREFIX_RE = re.compile(
    r"\"((?:klee|furina|kokomi|shared)/[a-z0-9_]+/[a-z0-9_]*)\"\s*\+")

# res:// references inside packed TEXT resources (.tscn/.tres). Restricted to
# our own namespaces: a scene legitimately points at base-game resources
# (`res://scenes/vfx/card_trail_ironclad.tscn`) and those are not our bill.
RES_REF_RE = re.compile(
    r"res://((?:klee|furina|kokomi|shared)/[A-Za-z0-9_/]+\.(?:png|tscn|tres))")

# PowerShell here-strings. Only their BODIES are scanned for res:// refs --
# build_pck.ps1's own comments quote resource paths while explaining a defect
# ("the contract said res://furina/salon/member_usher.png whether or not that
# file existed"), and a comment is not an expectation.
HEREDOC_RE = re.compile(r"@['\"]\r?\n(.*?)\r?\n['\"]@", re.S)

# `WriteAllText((Join-Path $work 'klee\ui\char_select_bg_klee.tscn'), @'...'@)`
# -- a text resource the build script authors straight into the pack. It is a
# packed resource with no ImageGen source, and nothing else in the repo names
# it, so without this rule the scenes the build writes are invisible.
AUTHORED_WRITE_RE = re.compile(
    r"Join-Path\s+\$work\s+'((?:klee|furina|kokomi|shared)\\[^']+\.(?:tscn|tres))'")

# C# comment lines. `KleePck.cs` documents its own contract with the example
# `"klee/ui/foo.png" -> "res://klee/ui/foo.png"`, which the literal regex
# happily reads as a demand for a resource that does not and should not exist.
CS_COMMENT_RE = re.compile(r"^\s*(?://|/\*|\*)")

CHARACTERS = ("klee", "furina", "kokomi")

# Non-art resources the pck builder writes into the pack itself: the build-id
# stamp (tools/build_pck.ps1:744) and the localization JSON tables
# (tools/build_pck.ps1:583). Neither is a visual surface, so neither belongs
# on an art bill -- in either direction.
BUILD_ARTIFACTS = ("klee/build_id.tres", "klee/localization/")

# res:// -> ImageGen source, derived from the copy blocks in build_pck.ps1.
# Ordered: the first matching rule wins, so the layers rules must precede the
# plain per-character rules. Guarded against rot by
# test_pck_source_map_rules_are_still_in_the_build_script.
PCK_SOURCE_RULES = [
    ("klee/model/layers/", "ImageGen/images/model/layers/combat/"),
    ("furina/model/layers/", "ImageGen/images/furina/model/layers/combat/"),
    ("furina/salon/", "ImageGen/images/furina/salon/"),
    ("kokomi/summon/", "ImageGen/images/kokomi/summon/"),
    ("klee/ui/", "ImageGen/images/ui/"),
    ("klee/powers/", "ImageGen/images/powers/"),
    ("klee/relics/", "ImageGen/images/relics/"),
    ("klee/model/", "ImageGen/images/model/"),
    ("furina/ui/", "ImageGen/images/furina/ui/"),
    ("furina/powers/", "ImageGen/images/furina/powers/"),
    ("furina/relics/", "ImageGen/images/furina/relics/"),
    ("furina/model/", "ImageGen/images/furina/model/"),
    ("kokomi/ui/", "ImageGen/images/kokomi/ui/"),
    ("kokomi/powers/", "ImageGen/images/kokomi/powers/"),
    ("kokomi/relics/", "ImageGen/images/kokomi/relics/"),
    ("kokomi/model/", "ImageGen/images/kokomi/model/"),
]

# Substrings that must still be present in build_pck.ps1 for the four
# non-obvious rules above to be true. The other twelve are the two generic
# `foreach ($d in 'ui','powers','relics','model')` loops.
PCK_SOURCE_RULE_EVIDENCE = {
    "klee/model/layers/": r"model\layers\combat",
    "furina/model/layers/": r"furina\model\layers\combat",
    "furina/salon/": r"furina\salon",
    "kokomi/summon/": r"kokomi\summon",
}

# docs/art-asset-manifest.md:79-81. The tier letters are the repo's; the
# CATEGORY names are the charter's. Nothing here is a judgement about any
# individual asset.
TIER_CATEGORY = {
    "F": "private-placeholder",
    "O": "public-safe",
}
RIGHTS_CATEGORIES = ("private-placeholder", "public-safe", "unclassified")

TIER_DECL_RE = re.compile(r"\bTier ([A-Z])\b")

# Fallback declarations in build_pck.ps1: a `foreach ($relative in @(...))`
# list immediately followed by `Copy-<Character>Fallback $relative`.
FALLBACK_BLOCK_RE = re.compile(
    r"foreach\s*\(\s*\$relative\s+in\s+@\((?P<list>[^)]*)\)\)\s*\{\s*"
    r"Copy-(?P<char>\w+)Fallback",
    re.S)
# Anchored on `$fallback =`, NOT on the first Join-Path in the function: the
# first one builds the TARGET path (`$work\furina\...`), so an unanchored
# match reports every character as falling back to itself.
FALLBACK_SOURCE_RE = re.compile(
    r"function\s+Copy-(?P<char>\w+)Fallback.*?\$fallback\s*=\s*Join-Path\s*\(\s*"
    r"Join-Path\s+\$work\s+'(?P<from>\w+)'\s*\)\s*\$relative",
    re.S)
# "Furina fallback: ui\transition_wipe.png <- Klee"
BUILD_LOG_FALLBACK_RE = re.compile(
    r"^(?P<char>\w+) fallback:\s*(?P<rel>\S+)\s*<-\s*(?P<from>\w+)\s*$")

PS_STRING_RE = re.compile(r"'([^']*)'")


# --------------------------------------------------------------------------
# Curated-registry reading (AST, not import)
# --------------------------------------------------------------------------

def _literal(node):
    """literal_eval, plus the `frozenset({...})` calls the registries use."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id in ("frozenset", "set") and len(node.args) == 1:
        return frozenset(_literal(node.args[0]))
    if isinstance(node, ast.Set):
        return {_literal(e) for e in node.elts}
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_literal(e) for e in node.elts]
    if isinstance(node, ast.Dict):
        return {_literal(k): _literal(v) for k, v in zip(node.keys, node.values)}
    return ast.literal_eval(node)


def module_constants(path: Path, names) -> dict:
    """Top-level constant assignments from a python file, without importing it.

    The registries are per-checkout DATA (which pairs are allowlisted, which
    out-paths a generator owns). Importing would bind them to this tool's own
    repo root instead of --root, and would run module-level code besides.
    """
    out = {}
    if not path.is_file():
        return out
    tree = ast.parse(path.read_text(encoding="utf-8"))
    wanted = set(names)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in wanted:
                try:
                    out[target.id] = _literal(node.value)
                except (ValueError, TypeError, SyntaxError):
                    pass
    return out


# --------------------------------------------------------------------------
# Row + ledger
# --------------------------------------------------------------------------

@dataclass
class Row:
    surface_id: str          # stable key, e.g. "card:klee:kaboom"
    kind: str                # card | ui | power | relic | model | salon |
                             # summon | material | scene | vfx | other
    owner: str               # klee | furina | kokomi | companions | shared
    expected_by: str         # file:line of the thing that asks for it
    source: str              # provenance, or "" when there is none
    source_evidence: str
    rendered_output: str     # repo-relative ImageGen path, or ""
    rendered_present: bool
    packed_path: str         # res://... or images/cards/<id>.png
    packed_present: bool
    fallback: str            # none | active:<from> | unintended:<from>
    rights_tier: str         # one of RIGHTS_CATEGORIES
    rights_evidence: str
    review_state: str        # none | pending-red-pen | approved-exception | ...
    status: str              # covered | missing | fallback | defect
    notes: list = field(default_factory=list)


@dataclass
class Finding:
    check: str
    surface_id: str
    detail: str


class Ledger:
    def __init__(self, root: Path, build_log: Path | None = None):
        self.root = root
        self.build_log = build_log
        self.rows: list[Row] = []
        self.findings: list[Finding] = []
        self.stale_outputs: list[tuple[str, str]] = []   # (path, reason|"")
        self.packed_unexpected: list[str] = []
        self._build()

    # -- small readers ----------------------------------------------------

    def _p(self, rel: str) -> Path:
        return self.root / rel

    def _text(self, rel: str) -> str:
        p = self._p(rel)
        return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""

    def _sheet_rows(self, rel: str):
        p = self._p(rel)
        if not p.is_file():
            return []
        rows = yaml.safe_load(p.read_text(encoding="utf-8")) or []
        return [r for r in rows if isinstance(r, dict) and "id" in r]

    # -- provenance -------------------------------------------------------

    def _read_sources(self) -> dict:
        """rendered path (posix, repo-relative) -> (source_url, tier, line no)."""
        out = {}
        p = self._p(SOURCES_TSV)
        if not p.is_file():
            return out
        with p.open(encoding="utf-8", newline="") as fh:
            for lineno, parts in enumerate(csv.reader(fh, delimiter="\t"), start=1):
                if len(parts) < 3 or parts[0] == "filename":
                    continue
                out[parts[0].replace("\\", "/")] = (parts[1], parts[2], lineno)
        return out

    def _read_plan(self) -> dict:
        """out-path -> (asset_id, wiki_title, register, rank, pick, line no).

        Only EFFECTIVE picks (auto rows and shortlist rank 1) are kept: a dead
        shortlist rank is not the provenance of anything that shipped.
        """
        out = {}
        p = self._p(PLAN_TSV)
        if not p.is_file():
            return out
        for lineno, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            f = line.split("\t")
            if len(f) < 12:
                continue
            asset_id, outp, _w, _h, _mode, _focus, pick, rank = f[:8]
            title, register = f[9], f[11]
            if pick != "auto" and rank != "1":
                continue
            out[outp.replace("\\", "/")] = (asset_id, title, register, rank,
                                            pick, lineno)
        return out

    def _generator_tiers(self, generator_owned: dict) -> dict:
        """out-path -> (category, evidence, generator, derives_from_tier_f)."""
        sources = self._sources
        out = {}
        cache: dict[str, tuple] = {}
        for outp, gen in generator_owned.items():
            if gen not in cache:
                gp = self._p(f"tools/{gen}")
                doc = ""
                if gp.is_file():
                    try:
                        doc = ast.get_docstring(
                            ast.parse(gp.read_text(encoding="utf-8"))) or ""
                    except SyntaxError:
                        doc = ""
                m = TIER_DECL_RE.search(doc)
                letter = m.group(1) if m else ""
                body = gp.read_text(encoding="utf-8") if gp.is_file() else ""
                # Does the generator read anything the ledger already knows is
                # Tier F? A derived output cannot be cleaner than its input.
                derived_f = any(
                    tier == "F" and Path(path).name in body
                    for path, (_u, tier, _n) in sources.items())
                cache[gen] = (letter, derived_f)
            letter, derived_f = cache[gen]
            if letter:
                cat = TIER_CATEGORY.get(letter, "unclassified")
                ev = f"tools/{gen} docstring declares Tier {letter}"
            else:
                cat = "unclassified"
                ev = f"tools/{gen} declares no tier"
            out[outp.replace("\\", "/")] = (cat, ev, gen, derived_f)
        return out

    # -- build script -----------------------------------------------------

    def _read_fallbacks(self) -> dict:
        """character -> {relative path (posix): source character}."""
        text = self._text(BUILD_PCK)
        sources = {m.group("char").lower(): m.group("from").lower()
                   for m in FALLBACK_SOURCE_RE.finditer(text)}
        out: dict[str, dict[str, str]] = {}
        for m in FALLBACK_BLOCK_RE.finditer(text):
            char = m.group("char").lower()
            rels = {s.replace("\\", "/") for s in PS_STRING_RE.findall(m.group("list"))}
            out.setdefault(char, {}).update(
                {r: sources.get(char, "klee") for r in rels})
        return out

    def _read_contract(self) -> set:
        packed = set()
        for line in self._text(PCK_CONTRACT).splitlines():
            if line.startswith("resource=res://"):
                packed.add(line[len("resource=res://"):].strip())
        return packed

    def _read_build_log(self):
        """[(character, relative, source character)] from a real build log."""
        if not self.build_log or not Path(self.build_log).is_file():
            return []
        out = []
        text = Path(self.build_log).read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            m = BUILD_LOG_FALLBACK_RE.match(line.strip())
            if m:
                out.append((m.group("char").lower(),
                            m.group("rel").replace("\\", "/"),
                            m.group("from").lower()))
        return out

    # -- expectations -----------------------------------------------------

    def _mod_files(self):
        src = self._p(MOD_SRC)
        return sorted(src.rglob("*.cs")) if src.is_dir() else []

    def _card_expectations(self):
        """[(id, owner, outdir, expected_by)] over the two card universes."""
        rows = []
        seen = set()
        for sheet, outdir, owner in CARD_SHEETS:
            for r in self._sheet_rows(sheet):
                if r["id"] in seen:
                    continue
                seen.add(r["id"])
                rows.append((r["id"], owner, outdir, sheet))
        for r in self._sheet_rows(TOKENS_SHEET):
            if r.get("rarity") == "token" and r["id"] not in seen:
                seen.add(r["id"])
                rows.append((r["id"], "furina", TOKENS_DIR, TOKENS_SHEET))
        # Cards that ship in C# with no sheet row at all. Deploy stages every
        # character's card dir into one flat images/cards, so any of the four
        # dirs is a legal home; the ledger records whichever one holds it.
        card_dirs = [d for _s, d, _o in CARD_SHEETS] + [TOKENS_DIR]
        card_dirs = list(dict.fromkeys(card_dirs))
        for path in self._mod_files():
            text = path.read_text(encoding="utf-8", errors="replace")
            for lineno, line in enumerate(text.splitlines(), 1):
                if CS_COMMENT_RE.match(line):
                    continue
                for m in ART_KEY_RE.finditer(line):
                    cid = m.group(1)
                    if cid in seen:
                        continue
                    seen.add(cid)
                    home = next(
                        (d for d in card_dirs if (self._p(d) / f"{cid}.png").is_file()),
                        card_dirs[0])
                    rel = path.relative_to(self.root).as_posix()
                    rows.append((cid, "shared", home, f"{rel}:{lineno}"))
        return rows

    def _pck_expectations(self):
        """relative res:// path -> "file:line" of the first thing asking for it.

        Three sources, in priority order: the mod source (C# literals), the
        git-tracked scene sources under klee-mod/pck-src, and the here-string
        scenes and materials authored inside tools/build_pck.ps1.
        """
        out = {}
        for path in self._mod_files():
            text = path.read_text(encoding="utf-8", errors="replace")
            for lineno, line in enumerate(text.splitlines(), 1):
                if CS_COMMENT_RE.match(line):
                    continue
                for m in PCK_KEY_RE.finditer(line):
                    rel = path.relative_to(self.root).as_posix()
                    out.setdefault(m.group(1), f"{rel}:{lineno}")

        src = self._p(PCK_SRC)
        if src.is_dir():
            for path in sorted(src.rglob("*")):
                if path.suffix not in (".tscn", ".tres"):
                    continue
                rel = path.relative_to(self.root).as_posix()
                # The scene FILE itself is a packed resource, at its path
                # relative to pck-src (build_pck overlays the tree verbatim).
                own = path.relative_to(src).as_posix()
                out.setdefault(own, rel)
                text = path.read_text(encoding="utf-8", errors="replace")
                for lineno, line in enumerate(text.splitlines(), 1):
                    for m in RES_REF_RE.finditer(line):
                        out.setdefault(m.group(1), f"{rel}:{lineno}")

        build = self._text(BUILD_PCK)
        # Text resources the build script AUTHORS into the pack: each is a
        # packed resource in its own right, named by the path it is written to.
        for m in AUTHORED_WRITE_RE.finditer(build):
            rel = m.group(1).replace("\\", "/")
            if any(rel.startswith(a) for a in BUILD_ARTIFACTS):
                continue
            lineno = build.count("\n", 0, m.start()) + 1
            out.setdefault(rel, f"{BUILD_PCK}:{lineno}")
        for block in HEREDOC_RE.finditer(build):
            lineno = build.count("\n", 0, block.start(1)) + 1
            for offset, line in enumerate(block.group(1).splitlines()):
                for m in RES_REF_RE.finditer(line):
                    out.setdefault(m.group(1), f"{BUILD_PCK}:{lineno + offset}")

        # Computed paths: attribute whatever is already under each prefix, and
        # record the prefix so the report can say the universe is unknown.
        for prefix, site in self._pck_prefixes().items():
            for rel in self._files_under_prefix(prefix):
                out.setdefault(rel, f"{site} [computed]")
        return out

    def _pck_prefixes(self):
        """concatenation prefix -> "file:line" of the site that builds it."""
        out = {}
        for path in self._mod_files():
            text = path.read_text(encoding="utf-8", errors="replace")
            for lineno, line in enumerate(text.splitlines(), 1):
                if CS_COMMENT_RE.match(line):
                    continue
                for m in PCK_PREFIX_RE.finditer(line):
                    rel = path.relative_to(self.root).as_posix()
                    out.setdefault(m.group(1), f"{rel}:{lineno}")
        return out

    def _files_under_prefix(self, prefix: str):
        """Packed resources and rendered files whose path starts with `prefix`."""
        found = {p for p in self._packed if p.startswith(prefix)}
        dirpart, _, stem = prefix.rpartition("/")
        probe = self._imagegen_for(f"{dirpart}/probe.png")
        if probe:
            d = self._p(Path(probe).parent.as_posix())
            if d.is_dir():
                found.update(f"{dirpart}/{f.name}" for f in d.glob(f"{stem}*.png"))
        return sorted(found)

    # -- classification helpers ------------------------------------------

    @staticmethod
    def _kind_for(relative: str) -> str:
        parts = relative.split("/")
        sub = parts[1] if len(parts) > 2 else parts[0]
        if relative.endswith(".tres"):
            return "material"
        if relative.endswith(".tscn"):
            return "vfx" if sub == "vfx" else "scene"
        return {"ui": "ui", "powers": "power", "relics": "relic",
                "model": "model", "salon": "salon", "summon": "summon"}.get(
                    sub, "other")

    def _imagegen_for(self, relative: str) -> str:
        """Where the pipeline renders the pixels for a packed resource.

        PNGs only. A .tscn/.tres is AUTHORED text -- it has no ImageGen
        source, and mapping it to one manufactures a missing render for every
        scene in the pack.
        """
        if not relative.endswith(".png"):
            return ""
        for prefix, target in PCK_SOURCE_RULES:
            if relative.startswith(prefix):
                return target + relative[len(prefix):]
        return ""

    def _pck_exclude_globs(self):
        """The `$pckExclude` patterns build_pck.ps1 filters out of the copy.

        A file the build DELIBERATELY leaves out (the cached governing render
        each still generator caches beside its outputs) is a working file, not
        a stale output. Read from the script so the two cannot drift.
        """
        globs = []
        for m in re.finditer(r"\$pckExclude\s*=\s*'([^']+)'", self._text(BUILD_PCK)):
            globs.append(m.group(1))
        return globs

    def _review_state(self, key: str) -> str:
        for name, label in (("PENDING_UNDERSIZE", "pending-red-pen:undersize"),
                            ("PENDING_BANNED_FAMILY", "pending-red-pen:banned-family"),
                            ("KNOWN_UNDERSIZED", "approved:undersize")):
            if key in self._lint_reg.get(name, set()):
                return label
        for name, label in (("PENDING_RED_PEN", "pending-red-pen:duplicate-source"),
                            ("KNOWN_IDENTICAL", "known-identical")):
            for pair in self._lint_reg.get(name, set()):
                if key in pair:
                    return label
        return "none"

    def _rights_for(self, rendered: str):
        """(category, evidence). Reads declared evidence only; assigns nothing."""
        if rendered and rendered in self._sources:
            url, tier, lineno = self._sources[rendered]
            cat = TIER_CATEGORY.get(tier.strip().upper(), "unclassified")
            return cat, f"{SOURCES_TSV}:{lineno} tier={tier}"
        if rendered and rendered in self._gen_tiers:
            cat, ev, _gen, _df = self._gen_tiers[rendered]
            return cat, ev
        return "unclassified", "no SOURCES.tsv row and no generator declaration"

    def _source_for(self, rendered: str):
        """(source, evidence) for a rendered output."""
        if rendered in self._gen_tiers:
            _c, _e, gen, _d = self._gen_tiers[rendered]
            return f"generator:tools/{gen}", f"{ART_LINT} GENERATOR_OWNED"
        if rendered in self._sources:
            url, _tier, lineno = self._sources[rendered]
            plan = self._plan.get(rendered)
            if plan:
                return (f"wiki:{plan[1]}",
                        f"{PLAN_TSV}:{plan[5]}; {SOURCES_TSV}:{lineno}")
            return f"url:{url}", f"{SOURCES_TSV}:{lineno}"
        plan = self._plan.get(rendered)
        if plan:
            return f"wiki:{plan[1]}", f"{PLAN_TSV}:{plan[5]}"
        return "", ""

    # -- build ------------------------------------------------------------

    def _build(self):
        self._sources = self._read_sources()
        self._plan = self._read_plan()
        self._lint_reg = module_constants(
            self._p(ART_LINT),
            ("GENERATOR_OWNED", "PENDING_UNDERSIZE", "KNOWN_UNDERSIZED",
             "PENDING_BANNED_FAMILY", "PENDING_RED_PEN", "KNOWN_IDENTICAL",
             "APPROVED_FAMILY_EXCEPTIONS"))
        self._known_stale = module_constants(
            self._p(ART_COVERAGE), ("KNOWN_STALE",)).get("KNOWN_STALE", {})
        self._gen_tiers = self._generator_tiers(
            self._lint_reg.get("GENERATOR_OWNED", {}))
        self._fallbacks = self._read_fallbacks()
        self._packed = self._read_contract()
        self._log_fallbacks = self._read_build_log()

        self._build_card_rows()
        self._build_pck_rows()
        self._check_stale_sources()
        self._check_stale_outputs()
        self._check_unintended_fallbacks()
        self._check_rights_inheritance()
        self._check_packed_unexpected()

    def _build_card_rows(self):
        for cid, owner, outdir, expected_by in self._card_expectations():
            rendered = f"{outdir}/{cid}.png"
            present = self._p(rendered).is_file()
            source, source_ev = self._source_for(rendered)
            tier, tier_ev = self._rights_for(rendered)
            row = Row(
                surface_id=f"card:{owner}:{cid}",
                kind="card",
                owner=owner,
                expected_by=expected_by,
                source=source,
                source_evidence=source_ev,
                rendered_output=rendered,
                rendered_present=present,
                # Card portraits are LOOSE PNGs staged next to the dll, never
                # in the pck (klee-mod/KleeCode/KleeArt.cs SCOPE note;
                # klee-mod/build/deploy.ps1 stages images\cards).
                packed_path=f"images/cards/{cid}.png",
                packed_present=present,
                fallback="none",
                rights_tier=tier,
                rights_evidence=tier_ev,
                review_state=self._review_state(cid),
                status="covered" if present else "missing",
            )
            if not present:
                self.findings.append(Finding(
                    "MISSING-RENDER", row.surface_id,
                    f"no rendered output at {rendered}"))
            self.rows.append(row)

    def _build_pck_rows(self):
        for relative, expected_by in sorted(self._pck_expectations().items()):
            owner = relative.split("/", 1)[0]
            kind = self._kind_for(relative)
            rendered = self._imagegen_for(relative)
            rendered_present = bool(rendered) and self._p(rendered).is_file()
            packed_present = relative in self._packed
            notes = []

            if rendered:
                source, source_ev = self._source_for(rendered)
                tier, tier_ev = self._rights_for(rendered)
            else:
                # Authored text resource: a .tscn/.tres either overlaid from
                # the git-tracked pck-src tree or written as a heredoc by the
                # build script. Both are repo-authored text, so both are
                # evidence of origin -- but neither declares a tier, and this
                # tool does not invent one.
                pck_src_file = f"{PCK_SRC}/{relative}"
                if self._p(pck_src_file).is_file():
                    source, source_ev = f"authored:{pck_src_file}", pck_src_file
                elif f'res://{relative}' in self._text(BUILD_PCK) or \
                        relative.rsplit("/", 1)[-1] in self._text(BUILD_PCK):
                    source, source_ev = f"authored:{BUILD_PCK}", BUILD_PCK
                else:
                    source, source_ev = "", ""
                tier, tier_ev = "unclassified", "authored text resource; no tier declared"

            fallback = "none"
            rel_in_char = relative.split("/", 1)[1] if "/" in relative else relative
            declared = self._fallbacks.get(owner, {}).get(rel_in_char)
            if declared and rendered and not rendered_present:
                fallback = f"active:{declared}"
                notes.append(
                    f"build_pck.ps1 declares a fallback for this path; "
                    f"{owner} has no art at {rendered}, so the build ships "
                    f"{declared}'s bytes here")
                self.findings.append(Finding(
                    "ACTIVE-FALLBACK", f"pck:{relative}",
                    f"{owner} falls back to {declared} for {rel_in_char}"))

            if not packed_present:
                status = "defect"
                # A path whose only requester is the boot-telemetry probe list
                # is PROBED, not demanded -- KleeSceneTelemetry deliberately
                # lists resources it expects to be missing so the log says so.
                # Different weight, same visibility.
                probe = " [requested only by the diagnostics probe list]" \
                    if "/Diagnostics/" in expected_by else ""
                self.findings.append(Finding(
                    "MISSING-PACKED", f"pck:{relative}",
                    f"asked for at {expected_by}; not in {PCK_CONTRACT}{probe}"))
            elif fallback.startswith("active"):
                status = "fallback"
            elif rendered and not rendered_present:
                status = "missing"
                self.findings.append(Finding(
                    "MISSING-RENDER", f"pck:{relative}",
                    f"packed, but no rendered source at {rendered}"))
            else:
                status = "covered"

            self.rows.append(Row(
                surface_id=f"pck:{relative}",
                kind=kind,
                owner=owner,
                expected_by=expected_by,
                source=source,
                source_evidence=source_ev,
                rendered_output=rendered,
                rendered_present=rendered_present,
                packed_path=f"res://{relative}",
                packed_present=packed_present,
                fallback=fallback,
                rights_tier=tier,
                rights_evidence=tier_ev,
                review_state=self._review_state(Path(relative).stem),
                status=status,
                notes=notes,
            ))

    # -- checks -----------------------------------------------------------

    def _check_stale_sources(self):
        """STALE-ROW: a provenance row whose rendered output is gone.

        Scoped to ImageGen outputs. `art/candidates/**` rows are shortlist
        working files -- gitignored and routinely pruned -- so their absence is
        housekeeping, not a stale ledger row.
        """
        for path, (_url, _tier, lineno) in sorted(self._sources.items()):
            if not path.startswith("ImageGen/"):
                continue
            if self._p(path).is_file():
                continue
            self.findings.append(Finding(
                "STALE-ROW", f"sources:{path}",
                f"{SOURCES_TSV}:{lineno} claims provenance for {path}, "
                f"which does not exist under this root"))

    def _check_stale_outputs(self):
        """STALE-OUTPUT: a rendered file no expected surface claims."""
        expected = {r.rendered_output for r in self.rows if r.rendered_output}
        dirs = {Path(r.rendered_output).parent.as_posix()
                for r in self.rows if r.rendered_output}
        excludes = self._pck_exclude_globs()
        for d in sorted(dirs):
            p = self._p(d)
            if not p.is_dir():
                continue
            for f in sorted(p.glob("*.png")):
                rel = f.relative_to(self.root).as_posix()
                if rel in expected:
                    continue
                if any(fnmatch(f.name, g) for g in excludes):
                    self.stale_outputs.append((
                        rel, f"working file: {BUILD_PCK} excludes it from the "
                             f"pck copy via $pckExclude"))
                    continue
                reason = self._known_stale.get(f.stem, "")
                self.stale_outputs.append((rel, reason))
                if not reason:
                    self.findings.append(Finding(
                        "STALE-OUTPUT", f"file:{rel}",
                        "no expected surface claims this file and it carries "
                        "no KNOWN_STALE reason"))

    def _check_unintended_fallbacks(self):
        """UNINTENDED-FALLBACK, three shapes -- see the module docstring."""
        # (a)+(b): against a real build log, if one was supplied.
        by_rel = {(r.owner, r.rendered_output): r for r in self.rows}
        for char, rel, src in self._log_fallbacks:
            declared = self._fallbacks.get(char, {})
            if rel not in declared:
                self.findings.append(Finding(
                    "UNINTENDED-FALLBACK", f"pck:{char}/{rel}",
                    f"build log shows {char} falling back to {src} for "
                    f"{rel}, which {BUILD_PCK} does not declare"))
                continue
            rendered = self._imagegen_for(f"{char}/{rel}")
            if rendered and self._p(rendered).is_file():
                self.findings.append(Finding(
                    "UNINTENDED-FALLBACK", f"pck:{char}/{rel}",
                    f"build log shows {char} falling back to {src} for {rel} "
                    f"even though {rendered} exists -- the copy block that "
                    f"should have staged it did not run"))

        # (c): byte identity across characters.
        #
        # A DECLARED fallback does NOT excuse this. When a declared fallback is
        # genuinely active the character has no rendered file at all, so its
        # row never reaches this loop. Reaching it means the character HAS its
        # own art and that art is another character's bytes -- which is the C4
        # defect (the copy block skipped and the fallback filled in over the
        # top), not the sanctioned mechanism. The declaration is reported in
        # the detail so a reader can tell the two apart.
        digests: dict[str, list[Row]] = {}
        for row in self.rows:
            if row.kind == "card" or not row.rendered_present:
                continue
            p = self._p(row.rendered_output)
            if not p.is_file():
                continue
            digests.setdefault(
                hashlib.sha256(p.read_bytes()).hexdigest(), []).append(row)
        for rows in digests.values():
            if len({r.owner for r in rows}) < 2:
                continue
            for row in rows:
                rel_in_char = row.surface_id.split(":", 1)[1].split("/", 1)[1]
                declared = self._fallbacks.get(row.owner, {}).get(rel_in_char)
                note = (f"; {BUILD_PCK} declares a {declared} fallback for this "
                        f"path, but it cannot be the cause -- an active "
                        f"fallback means NO rendered file, and this one exists"
                        ) if declared else \
                       f"; no fallback is declared for {row.owner}/{rel_in_char}"
                others = sorted(r.surface_id for r in rows
                                if r.owner != row.owner)
                self.findings.append(Finding(
                    "UNINTENDED-FALLBACK", row.surface_id,
                    f"rendered bytes are identical to {', '.join(others)} "
                    f"across characters{note}"))

    def _check_rights_inheritance(self):
        for outp, (cat, ev, gen, derived_f) in sorted(self._gen_tiers.items()):
            if cat == "public-safe" and derived_f:
                self.findings.append(Finding(
                    "RIGHTS-INHERITANCE", f"file:{outp}",
                    f"{ev}, but tools/{gen} reads a file that art/SOURCES.tsv "
                    f"records as Tier F -- a derived output cannot be cleaner "
                    f"than its input"))

    def _check_packed_unexpected(self):
        expected = {r.packed_path[len("res://"):]
                    for r in self.rows if r.packed_path.startswith("res://")}
        self.packed_unexpected = sorted(
            p for p in self._packed - expected
            if not any(p.startswith(a) for a in BUILD_ARTIFACTS))

    # -- summaries --------------------------------------------------------

    def rights_coverage(self):
        """{category: {kind: (covered, expected)}} -- never summed together."""
        out: dict[str, dict[str, list[int]]] = {}
        for row in self.rows:
            bucket = out.setdefault(row.rights_tier, {})
            cell = bucket.setdefault(row.kind, [0, 0])
            cell[1] += 1
            if row.status == "covered":
                cell[0] += 1
        return out

    def card_totals(self):
        cards = [r for r in self.rows if r.kind == "card"]
        covered = sum(1 for r in cards if r.rendered_present)
        return len(cards), covered, len(cards) - covered

    def to_dict(self):
        return {
            "schema": SCHEMA_VERSION,
            "root": str(self.root),
            "rows": [asdict(r) for r in self.rows],
            "findings": [asdict(f) for f in self.findings],
            "stale_outputs": [{"path": p, "known_reason": r}
                              for p, r in self.stale_outputs],
            "packed_not_expected": self.packed_unexpected,
        }


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

DEFECT_CHECKS = ("MISSING-PACKED", "STALE-ROW", "STALE-OUTPUT",
                 "UNINTENDED-FALLBACK", "RIGHTS-INHERITANCE")


def report(ledger: Ledger, out=sys.stdout) -> None:
    w = out.write
    w("=" * 72 + "\n")
    w(f"ART LEDGER  ({SCHEMA_VERSION})\n")
    w(f"root: {ledger.root}\n")
    w("=" * 72 + "\n")

    kinds = {}
    for row in ledger.rows:
        cell = kinds.setdefault(row.kind, {"expected": 0, "covered": 0,
                                           "missing": 0, "fallback": 0,
                                           "defect": 0})
        cell["expected"] += 1
        cell[row.status] += 1
    w("\nEXPECTED SURFACES BY KIND\n")
    w(f"  {'kind':10s} {'expected':>8s} {'covered':>8s} {'missing':>8s} "
      f"{'fallback':>9s} {'defect':>7s}\n")
    for kind in sorted(kinds):
        c = kinds[kind]
        w(f"  {kind:10s} {c['expected']:8d} {c['covered']:8d} "
          f"{c['missing']:8d} {c['fallback']:9d} {c['defect']:7d}\n")
    tot = {k: sum(c[k] for c in kinds.values())
           for k in ("expected", "covered", "missing", "fallback", "defect")}
    w(f"  {'TOTAL':10s} {tot['expected']:8d} {tot['covered']:8d} "
      f"{tot['missing']:8d} {tot['fallback']:9d} {tot['defect']:7d}\n")

    w("\n" + "-" * 72 + "\n")
    w("RIGHTS COVERAGE -- REPORTED SEPARATELY, NEVER SUMMED\n")
    w("  Tier categories are read from declared evidence "
      "(docs/art-asset-manifest.md:79-81).\n")
    w("  This tool assigns no rights tier to anything.\n")
    w("-" * 72 + "\n")
    cov = ledger.rights_coverage()
    for cat in RIGHTS_CATEGORIES:
        bucket = cov.get(cat, {})
        total_e = sum(v[1] for v in bucket.values())
        total_c = sum(v[0] for v in bucket.values())
        w(f"\n  {cat}: {total_c} covered of {total_e} expected\n")
        if not bucket:
            w("    (no rows)\n")
        for kind in sorted(bucket):
            c, e = bucket[kind]
            w(f"    {kind:10s} {c:4d} / {e:4d}\n")
    unc = cov.get("unclassified", {})
    if unc:
        w("\n  UNCLASSIFIED is a question for [USER], not a default of either\n"
          "  category: these surfaces carry no SOURCES.tsv tier and no\n"
          "  generator tier declaration.\n")

    prefixes = ledger._pck_prefixes()
    if prefixes:
        w("\n" + "-" * 72 + "\n")
        w("COMPUTED PATHS -- THE LEDGER CANNOT ENUMERATE THESE\n")
        w("-" * 72 + "\n")
        w("  These call sites build a resource path by concatenation, so the\n"
          "  set they demand is not readable from the source. Every file\n"
          "  already sitting under the prefix is billed to the site; a member\n"
          "  of the set with NO file is invisible to this tool and to every\n"
          "  other string-reading gate in the repo.\n")
        for prefix in sorted(prefixes):
            found = ledger._files_under_prefix(prefix)
            w(f"\n  {prefix}*  ({prefixes[prefix]})\n")
            w(f"    {len(found)} file(s) attributed: "
              f"{', '.join(Path(f).name for f in found) or '(none)'}\n")

    w("\n" + "-" * 72 + "\n")
    w("FALLBACKS DECLARED IN tools/build_pck.ps1\n")
    w("-" * 72 + "\n")
    if not ledger._fallbacks:
        w("  (none parsed)\n")
    for char in sorted(ledger._fallbacks):
        rels = ledger._fallbacks[char]
        srcs = sorted(set(rels.values()))
        w(f"  {char}: {len(rels)} path(s) fall back to {', '.join(srcs)}\n")
    active = [f for f in ledger.findings if f.check == "ACTIVE-FALLBACK"]
    w(f"\n  ACTIVE right now: {len(active)}\n")
    for f in active:
        w(f"    {f.surface_id}: {f.detail}\n")

    w("\n" + "-" * 72 + "\n")
    w("FINDINGS\n")
    w("-" * 72 + "\n")
    by_check: dict[str, list[Finding]] = {}
    for f in ledger.findings:
        by_check.setdefault(f.check, []).append(f)
    for check in ("MISSING-PACKED", "UNINTENDED-FALLBACK", "RIGHTS-INHERITANCE",
                  "STALE-ROW", "STALE-OUTPUT", "MISSING-RENDER"):
        items = by_check.get(check, [])
        w(f"\n{check} -- {len(items)}\n")
        for f in items[:40]:
            w(f"  {f.surface_id}: {f.detail}\n")
        if len(items) > 40:
            w(f"  ... and {len(items) - 40} more (use --json for all)\n")

    known = [(p, r) for p, r in ledger.stale_outputs if r]
    if known:
        w(f"\nKNOWN-STALE files (recorded reason, NOT coverage) -- {len(known)}\n")
        for p, r in known:
            w(f"  {p}: {r[:110]}\n")

    if ledger.packed_unexpected:
        w(f"\nPACKED BUT NOT EXPECTED -- {len(ledger.packed_unexpected)}\n")
        w("  In the pck contract, but no mod-source literal asks for them.\n"
          "  Scene sub-resources and overlay files land here legitimately;\n"
          "  this is an inventory line, not a defect.\n")
        for p in ledger.packed_unexpected[:40]:
            w(f"  res://{p}\n")
        if len(ledger.packed_unexpected) > 40:
            w(f"  ... and {len(ledger.packed_unexpected) - 40} more\n")

    expected, covered, missing = ledger.card_totals()
    w("\n" + "=" * 72 + "\n")
    w("RECONCILIATION to tools/art_coverage.py\n")
    w(f"  card-sized outputs expected: {expected}   "
      f"covered: {covered}   missing: {missing}\n")
    w("  (art_coverage bills the same two card universes; these three numbers\n"
      "   must match its TOTAL block exactly.)\n")
    w("=" * 72 + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True, type=Path,
                    help="checkout to read (sheets, mod source, art tree). "
                         "REQUIRED: the art tree is gitignored, so the "
                         "art-bearing checkout is often not this one.")
    ap.add_argument("--json", type=Path, help="write the machine-readable ledger here")
    ap.add_argument("--build-log", type=Path,
                    help="a build_pck.ps1 log to reconcile fallbacks against")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when any defect-class finding is present")
    args = ap.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        print(f"art_ledger: --root {root} is not a directory", file=sys.stderr)
        return 2

    ledger = Ledger(root, build_log=args.build_log)
    report(ledger)

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(ledger.to_dict(), indent=2),
                             encoding="utf-8")
        print(f"\nwrote {args.json}")

    defects = [f for f in ledger.findings if f.check in DEFECT_CHECKS]
    if args.strict and defects:
        print(f"\nFAIL (--strict): {len(defects)} defect-class finding(s).",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
