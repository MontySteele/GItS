#!/usr/bin/env python
"""Generate the Teyvat arm's DRESSED ANCIENTS from `ancient-faces.tsv`.

One body per (Ancient, face), per R275 (2026-09-17). The shape decision and the
decompiled facts it rests on are `docs/current/operations/codegen.md`,
"Codegen -- Teyvat dressed Ancients"; the short version is that
`AncientEventModel`'s eight subclasses are NOT sealed and every string an
Ancient shows derives from `Id.Entry`, so a dressed Ancient is a ONE-LINE
SUBCLASS -- `public sealed class DvalinMondstadt : Neow { }` -- and nothing
else. No mirror, no re-implemented clause, no copied prose.

    .venv/Scripts/python.exe tools/gen_teyvat_ancients.py           # write
    .venv/Scripts/python.exe tools/gen_teyvat_ancients.py --check   # verify
    .venv/Scripts/python.exe tools/gen_teyvat_ancients.py --refresh # rebuild
                                                                    # the index

THE EMPTY FIELD IS THE POINT OF THIS PASS. R275 ships names, and the words
come later. Every text column in the faces file may be EMPTY, and an empty
column means "keep the game's own line" -- which is not a no-op, because the
dressed entry re-keys everything. It is honoured at RUNTIME by
`TeyvatLoc.Inject`'s ALIAS pass: every live row under the base entry's prefix
is copied to the dressed entry's, and only then are the face's own rows laid
over the top. So no base-game prose enters this repo (`.gitignore:28`,
`csharp-build-spec.md` sec.0.3), every language the game ships keeps working,
and the day a face writes a line the only file that changes is the TSV.

THE BOONS ARE NEVER OURS. An Ancient's options are `RelicOption<T>()`, and
`EventOption.FromRelic` is
`eventModel.GetOptionTitle(textKey) ?? relic.Title` --- `GetIfExists`, so a
missing row falls through to the RELIC's own rows. The generator writes no
option row, ever, and the alias pass copies the base entry's option rows
verbatim where the base game has any. Either way the boon a player reads is
the game's.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
FACES = REPO / "docs" / "current" / "dossiers" / "content" / "ancient-faces.tsv"
INDEX = REPO / "tools" / "data" / "sts2_base_ancients.json"
OUT = REPO / "klee-mod" / "KleeCode" / "Teyvat" / "TeyvatAncientsGenerated.cs"
DECOMP_DEFAULT = (
    Path.home() / "AppData" / "Local" / "Temp" / "claude" / "ancients-decomp"
)

#: The six faces R273 ruled, and the act each dresses. The act number is what
#: decides which Ancients a face needs a body for; it is NOT read off the act
#: classes, because those live in the mod and this generator runs without one.
FACE_ACTS: Dict[str, int] = {
    "MONDSTADT": 1,
    "LIYUE": 1,
    "NATLAN": 2,
    "INAZUMA": 2,
    "FONTAINE": 3,
    "SUMERU": 3,
}

#: The base game's per-act Ancient pools, off `ActModel.AllAncients`
#: (`Overgrowth.cs:26`, `Underdocks.cs:22`, `Hive.cs:24`, `Glory.cs:23`).
#: IDENTIFIERS, in the base classes' own order -- the order matters because a
#: face's pool is pinned to be the same length AND the same order as its base
#: act's.
ACT_ANCIENTS: Dict[int, List[str]] = {
    1: ["NEOW"],
    2: ["OROBAS", "PAEL", "TEZCATARA"],
    3: ["NONUPEIPE", "TANX", "VAKUU"],
}

#: `ModelDb.AllSharedAncients` (`ModelDb.cs:189`) -- the Ancients that belong
#: to no act and are dealt to acts 2 and 3 at run start by
#: `RunManager.GenerateRooms` through `ActModel.SetSharedAncientSubset`. Darv
#: is the only one, and R275 makes him Alice on every face.
SHARED_ANCIENTS: List[str] = ["DARV"]

#: The acts a shared Ancient can be dealt to: `RunManager.GenerateRooms`
#: walks `State.Acts.Skip(1)`, so act 1 never sees one.
SHARED_ACTS = (2, 3)

#: The five character keys `AncientDialogueSet.CharacterDialogues` is keyed by
#: -- `AncientEventModel.CharKey<T>()` is `ModelDb.Character<T>().Id.Entry`.
#: OUR ROSTER IS NOT IN HERE and that is a finding, not an omission: Klee,
#: Kokomi and Furina miss `CharacterDialogues.TryGetValue` and fall through to
#: `AgnosticDialogues`, so the `agnostic_*` columns are the ones a Teyvat run
#: actually reads.
CHARACTER_KEYS = ("IRONCLAD", "SILENT", "DEFECT", "NECROBINDER", "REGENT")

COLUMNS = (
    "ancient",
    "face",
    "name",
    "epithet",
    "first_visit",
    "dialogue_1",
    "dialogue_2",
    "dialogue_3",
    "agnostic_1",
    "agnostic_2",
    "extra",
)

#: A dialogue cell's lines are separated by this; a per-character cell's
#: sections by `SECTION_SEP`.
LINE_SEP = "|"
SECTION_SEP = ";;"

_CAMEL = re.compile(r"(?<=[a-zA-Z0-9])(?=[A-Z])")
_NOT_SLUG = re.compile(r"[^A-Z0-9_]")


def slugify(name: str) -> str:
    """`StringHelper.Slugify` for a C# type name, which is what
    `ModelDb.GetEntry` hands `Id.Entry`. Same body as the events generator's."""
    text = _CAMEL.sub("_", name.strip())
    text = re.sub(r"\s+", "_", text.upper())
    return _NOT_SLUG.sub("", text)


def pascal(name: str) -> str:
    """A dressed display name reduced to a C# identifier. Word characters
    only, each word capitalised, digits kept -- `the Sacred Sakura` becomes
    `TheSacredSakura`. The identifier is load-bearing: `Id.Entry` is its
    slug, and from that slug the engine derives the title key, the epithet
    key, every dialogue key and every asset path."""
    words = re.findall(r"[A-Za-z0-9]+", name)
    if not words:
        raise ValueError(f"no identifier can be made from {name!r}")
    return "".join(w[0].upper() + w[1:] for w in words)


# ----------------------------------------------------------------------------
# THE INDEX
# ----------------------------------------------------------------------------


def load_index() -> Dict[str, dict]:
    if not INDEX.is_file():
        raise SystemExit(f"gen_teyvat_ancients: missing index {INDEX}")
    return json.loads(INDEX.read_text(encoding="utf-8"))


_CLASS_RE = re.compile(r"^public\s+(sealed\s+)?class\s+(\w+)\s*:\s*(\w+)", re.M)
_DIALOGUE_RE = re.compile(r"new AncientDialogue\(([^)]*)\)")
_CHARKEY_RE = re.compile(r"CharKey<(\w+)>\(\)")


def _line_count(args: str) -> int:
    """`new AncientDialogue(params string[] sfxPaths)` -- one LINE per sfx
    path (`AncientDialogue.cs`'s ctor). The paths themselves are FMOD event
    identifiers and are not recorded; only how many there are."""
    args = args.strip()
    if not args:
        return 0
    return len(re.findall(r'"', args)) // 2


def refresh_index(decomp: Path) -> int:
    """Rebuild `tools/data/sts2_base_ancients.json` from a local decompile.

    IDENTIFIERS AND SHAPES ONLY: the class name, its `Id.Entry`, whether it is
    sealed, how many lines each dialogue has, and the loc-key literals the
    class itself spells. No method body and no base-game prose is read, let
    alone written -- the same rule `gen_teyvat_events.refresh_index` follows.
    """
    events = decomp / "MegaCrit.Sts2.Core.Models.Events"
    if not events.is_dir():
        print(f"gen_teyvat_ancients: no decompile at {decomp}", file=sys.stderr)
        print('  regenerate with: ilspycmd -p -o <dir> "<GameDir>\\...\\sts2.dll"',
              file=sys.stderr)
        return 2

    names = sorted(set(sum(ACT_ANCIENTS.values(), [])) | set(SHARED_ANCIENTS))
    index: Dict[str, dict] = {}
    for entry in names:
        cls = entry.title().replace("_", "")
        path = events / f"{cls}.cs"
        if not path.is_file():
            print(f"gen_teyvat_ancients: {path.name} not in the decompile",
                  file=sys.stderr)
            return 2
        src = path.read_text(encoding="utf-8", errors="replace")
        m = _CLASS_RE.search(src)
        if not m or m.group(3) != "AncientEventModel":
            print(f"gen_teyvat_ancients: {cls} is not an AncientEventModel",
                  file=sys.stderr)
            return 2
        if m.group(1):
            # The whole shape rests on this. A sealed Ancient could not be
            # dressed by subclassing and would need the events pipeline's
            # hand-written mirror instead.
            print(f"gen_teyvat_ancients: {cls} is SEALED -- the subclass shape "
                  f"does not apply", file=sys.stderr)
            return 2

        body = src[src.index("DefineDialogues"):]
        first, rest = body.split("CharacterDialogues", 1)
        chars_src, agnostic_src = rest.split("AgnosticDialogues", 1)
        agnostic_src = agnostic_src.split("return ", 1)[0]

        per_char: Dict[str, List[int]] = {}
        current = None
        for chunk in re.split(r"(CharKey<\w+>\(\))", chars_src):
            key = _CHARKEY_RE.fullmatch(chunk)
            if key:
                current = slugify(key.group(1))
                per_char[current] = []
            elif current is not None:
                per_char[current].extend(
                    _line_count(a) for a in _DIALOGUE_RE.findall(chunk))

        index[entry] = {
            "class": cls,
            "entry": entry,
            "sealed": False,
            "base": "AncientEventModel",
            "first_visit_lines": _line_count(_DIALOGUE_RE.findall(first)[0]),
            "character_dialogues": per_char,
            "agnostic_lines": [_line_count(a)
                               for a in _DIALOGUE_RE.findall(agnostic_src)],
            # Loc-key literals the class itself spells, under its own entry.
            # These are the keys a face's `extra` column may restate.
            "extra_keys": sorted({
                lit[len(entry) + 1:]
                for lit in re.findall(r'"(' + entry + r'\.[^"]*)"', src)
            } | set(_EXTRA_KEYS.get(entry, ()))),
        }

    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n",
                     encoding="utf-8")
    print(f"gen_teyvat_ancients: index refreshed, {len(index)} Ancients")
    return 0


#: Keys that live in the shipped `ancients` loc pack but are spelled by a
#: READER rather than by the Ancient's own class, so the literal scrape cannot
#: find them. Declared by name here, checked by the pins, never valued.
_EXTRA_KEYS = {
    "NEOW": ("results.prefix", "epithet", "title", "pages.DONE.description"),
    "VAKUU": ("loss", "epithet", "title", "pages.DONE.description"),
    "DARV": ("epithet", "title", "pages.DONE.description"),
    "OROBAS": ("epithet", "title", "pages.DONE.description"),
    "PAEL": ("epithet", "title", "pages.DONE.description"),
    "TANX": ("epithet", "title", "pages.DONE.description"),
    "TEZCATARA": ("epithet", "title", "pages.DONE.description"),
    "NONUPEIPE": ("epithet", "title", "pages.DONE.description"),
}


# ----------------------------------------------------------------------------
# THE FACES FILE
# ----------------------------------------------------------------------------


class Row:
    __slots__ = ("ancient", "face", "name", "epithet", "first_visit",
                 "dialogues", "agnostics", "extra", "cls", "entry",
                 "parsed_first", "parsed_chars", "parsed_agnostics",
                 "parsed_extra")

    def __init__(self, cells: Dict[str, str]) -> None:
        self.ancient = cells["ancient"].strip().upper()
        self.face = cells["face"].strip().upper()
        self.name = cells["name"].strip()
        self.epithet = cells["epithet"].strip()
        self.first_visit = cells["first_visit"].strip()
        self.dialogues = [cells[f"dialogue_{i}"].strip() for i in (1, 2, 3)]
        self.agnostics = [cells[f"agnostic_{i}"].strip() for i in (1, 2)]
        self.extra = cells["extra"].strip()
        self.cls = ""
        self.entry = ""
        self.parsed_first: List[Tuple[bool, str]] | None = None
        self.parsed_chars: List[Dict[str, List[Tuple[bool, str]]]] = []
        self.parsed_agnostics: List[List[Tuple[bool, str]] | None] = []
        self.parsed_extra: Dict[str, str] = {}


def read_faces() -> Tuple[List[Row], List[str]]:
    if not FACES.is_file():
        return [], [f"missing faces file {FACES}"]
    rows: List[Row] = []
    refusals: List[str] = []
    header: List[str] | None = None
    for n, raw in enumerate(FACES.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        cells = raw.split("\t")
        if header is None:
            header = [c.strip() for c in cells]
            if tuple(header) != COLUMNS:
                refusals.append(
                    f"{FACES.name}: header is {header}, expected {list(COLUMNS)}")
                return [], refusals
            continue
        if len(cells) != len(COLUMNS):
            refusals.append(
                f"{FACES.name}:{n}: {len(cells)} columns, expected {len(COLUMNS)}"
                " (every column is tab-separated and an empty one is an empty"
                " cell, not a missing one)")
            continue
        rows.append(Row(dict(zip(COLUMNS, cells))))
    return rows, refusals


def expected_rows() -> List[Tuple[str, str]]:
    """Every (Ancient, face) pair R275 owes a body, in a stable order."""
    out: List[Tuple[str, str]] = []
    for face, act in FACE_ACTS.items():
        for ancient in ACT_ANCIENTS[act]:
            out.append((ancient, face))
        if act in SHARED_ACTS:
            for ancient in SHARED_ANCIENTS:
                out.append((ancient, face))
    return sorted(out)


# ----------------------------------------------------------------------------
# PARSING A TEXT CELL
# ----------------------------------------------------------------------------


def parse_lines(cell: str, where: str, expect: int,
                refusals: List[str]) -> List[Tuple[bool, str]] | None:
    """A dialogue cell: `A: the ancient speaks | C: the character answers`.

    The speaker prefix is REQUIRED because the engine derives the speaker from
    which key exists in the table (`AncientDialogue.PopulateLines` asks
    `LocString.Exists(..., ".ancient")` first), so a dressed line has to say
    which of the two keys it is writing. `A` is the Ancient, `C` the player
    character. The line COUNT is checked against the base dialogue's, because
    a dialogue's length is `new AncientDialogue(params sfxPaths)` in compiled
    C# and no loc row can add or remove one.
    """
    if not cell:
        return None
    parts = [p.strip() for p in cell.split(LINE_SEP)]
    if len(parts) != expect:
        refusals.append(f"{where}: {len(parts)} line(s), the base dialogue has "
                        f"{expect} (a loc row cannot change a dialogue's length)")
        return None
    out: List[Tuple[bool, str]] = []
    for i, part in enumerate(parts):
        m = re.match(r"^([AC])\s*:\s*(.+)$", part, re.S)
        if not m:
            refusals.append(f"{where} line {i}: no speaker prefix -- every line "
                            f"starts `A: ` (the Ancient) or `C: ` (the character)")
            return None
        out.append((m.group(1) == "A", m.group(2).strip()))
    return out


def parse_char_cell(cell: str, where: str, shape: Dict[str, List[int]],
                    index: int, refusals: List[str]
                    ) -> Dict[str, List[Tuple[bool, str]]]:
    """A per-character dialogue cell.

    Two forms. `IRONCLAD= A: … | C: … ;; SILENT= …` writes one character at a
    time; a bare cell with no `CHAR=` writes the SAME lines for every base
    character, and is refused when their line counts disagree -- which they
    often do, so the sectioned form is the usual one.

    NOTHING IN OUR ROSTER READS THESE. Klee, Kokomi and Furina are not keys in
    `CharacterDialogues`, so `GetValidDialogues` misses and falls to the
    agnostic list. These three columns exist so a face CAN dress the base
    characters, not because a Teyvat run needs them.
    """
    out: Dict[str, List[Tuple[bool, str]]] = {}
    if not cell:
        return out
    if "=" in cell.split(LINE_SEP)[0]:
        for section in cell.split(SECTION_SEP):
            section = section.strip()
            if not section:
                continue
            key, _, body = section.partition("=")
            key = key.strip().upper()
            if key not in shape:
                refusals.append(f"{where}: `{key}` is not one of the base "
                                f"character keys {sorted(shape)}")
                continue
            lines = parse_lines(body.strip(), f"{where} [{key}]",
                                shape[key][index], refusals)
            if lines:
                out[key] = lines
        return out
    counts = {key: shape[key][index] for key in shape}
    if len(set(counts.values())) != 1:
        refusals.append(f"{where}: the base characters' dialogue {index} has "
                        f"different lengths ({counts}), so this cell must name "
                        f"each character -- `IRONCLAD= … ;; SILENT= …`")
        return out
    lines = parse_lines(cell, where, next(iter(counts.values())), refusals)
    if lines:
        for key in shape:
            out[key] = list(lines)
    return out


def parse_agnostics(cells: Sequence[str], where: str, lengths: Sequence[int],
                    refusals: List[str]) -> List[List[Tuple[bool, str]] | None]:
    """The `ANY` dialogues -- THE ONES A TEYVAT RUN ACTUALLY READS.

    Two columns for a variable number of dialogues, which needs saying because
    the Ancients are not uniform: Pael, Darv, Orobas, Tanx, Tezcatara and
    Nonupeipe have two agnostic dialogues, Vakuu three and Neow five. So
    `agnostic_1` is dialogue 0 and `agnostic_2` is EVERY REMAINING dialogue,
    its sections separated by `;;` in index order. A face that writes
    `agnostic_2` at all writes all of them, and a section count that disagrees
    with the base is a refusal rather than a silent short pour.
    """
    out: List[List[Tuple[bool, str]] | None] = [None] * len(lengths)
    if not lengths:
        return out
    out[0] = parse_lines(cells[0], f"{where} agnostic_1", lengths[0], refusals)
    rest = cells[1].strip() if len(cells) > 1 else ""
    if not rest:
        return out
    sections = [s.strip() for s in rest.split(SECTION_SEP)]
    if len(sections) != len(lengths) - 1:
        refusals.append(f"{where} agnostic_2: {len(sections)} section(s), the "
                        f"base has {len(lengths) - 1} agnostic dialogue(s) after "
                        f"the first (separate them with `{SECTION_SEP}`)")
        return out
    for i, section in enumerate(sections, start=1):
        out[i] = parse_lines(section, f"{where} agnostic_{i + 1}",
                             lengths[i], refusals)
    return out


def parse_extra(cell: str, where: str, allowed: Sequence[str],
                refusals: List[str]) -> Dict[str, str]:
    """`results.prefix= … ;; loss= …` -- a flat row under the dressed entry.

    The key is the suffix under the entry, spelled exactly as the base game
    spells it, and it is checked against the index's `extra_keys` so a typo is
    a refusal rather than a row nothing reads. This is where Neow's
    `results.prefix`, Vakuu's `loss` and Orobas's locked-pool option text land.
    """
    out: Dict[str, str] = {}
    if not cell:
        return out
    for section in cell.split(SECTION_SEP):
        section = section.strip()
        if not section:
            continue
        key, sep, value = section.partition("=")
        key, value = key.strip(), value.strip()
        if not sep or not value:
            refusals.append(f"{where}: `{section}` is not `key= text`")
            continue
        if key in ("title", "epithet"):
            refusals.append(f"{where}: `{key}` has its own column -- write it "
                            f"there, so one row has one source")
            continue
        # An option key in the index is a PREFIX (`EventOption`'s textKey is
        # the key without `.title`/`.description`), so both leaves are allowed
        # under one declared key.
        stem = key[:-6] if key.endswith(".title") else (
            key[:-12] if key.endswith(".description") else key)
        if key not in allowed and stem not in allowed:
            refusals.append(f"{where}: `{key}` is not a key the base entry has "
                            f"({', '.join(allowed)})")
            continue
        out[key] = value
    return out


# ----------------------------------------------------------------------------
# C# EMISSION
# ----------------------------------------------------------------------------


def cs(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


HEADER = """// <auto-generated>
//     GENERATED by tools/gen_teyvat_ancients.py from
//     docs/current/dossiers/content/ancient-faces.tsv
//     Do not edit by hand: `python tools/gen_teyvat_ancients.py --check`
//     fails on any drift, and the next run overwrites it.
// </auto-generated>

using System;
using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Events;

namespace KleeMod.Teyvat.Ancients
{
"""


def emit(rows: List[Row], index: Dict[str, dict]) -> str:
    out: List[str] = [HEADER]

    out.append("""    /// <summary>
    /// THE DRESSED ANCIENTS -- one body per (Ancient, face), R275.
    ///
    /// EACH ONE IS A NAME AND A BASE AND NOTHING ELSE, and that is the whole
    /// design. `MegaCrit.Sts2.Core.Models.Events`'s eight Ancients are the
    /// only unsealed events in the assembly,
    /// `AncientEventModel.DefineDialogues` and `AllPossibleOptions` are
    /// inherited untouched, and every string and every asset path the engine
    /// builds for an Ancient is derived from `Id.Entry` -- which
    /// `ModelDb.GetEntry` takes from THIS class's name. So the subclass
    /// re-keys the title, the epithet and all twenty-odd dialogue lines for
    /// free, and re-keys not one mechanic.
    /// </summary>
    internal static class TeyvatDressedAncientsDoc { }
""")

    for row in rows:
        base_cls = index[row.ancient]["class"]
        out.append(
            f"    /// <summary>{row.name} -- the {row.face.title()} face's "
            f"{base_cls}. Entry <c>{row.entry}</c>.</summary>\n"
            f"    public sealed class {row.cls} : {base_cls} {{ }}\n")

    out.append("}\n")

    # ---- the loc rows -------------------------------------------------
    flat: List[Tuple[str, str]] = []
    dialogue: List[Tuple[str, str, int, int, bool, str]] = []
    for row in rows:
        shape = index[row.ancient]
        flat.append((f"{row.entry}.title", row.name))
        if row.epithet:
            flat.append((f"{row.entry}.epithet", row.epithet))
        for key, value in row.parsed_extra.items():  # type: ignore[attr-defined]
            flat.append((f"{row.entry}.{key}", value))
        for i, line in enumerate(row.parsed_first or []):  # type: ignore
            dialogue.append((row.entry, "firstVisitEver", 0, i, line[0], line[1]))
        for slot, per_char in enumerate(row.parsed_chars):  # type: ignore
            for char_key, lines in sorted(per_char.items()):
                for i, line in enumerate(lines):
                    dialogue.append((row.entry, char_key, slot, i,
                                     line[0], line[1]))
        for slot, lines in enumerate(row.parsed_agnostics):  # type: ignore
            for i, line in enumerate(lines or []):
                dialogue.append((row.entry, "ANY", slot, i, line[0], line[1]))

    out.append("""
namespace KleeMod.Teyvat
{
    /// <summary>
    /// THE DRESSED ANCIENTS' TABLES -- what the face acts, the two patches and
    /// `TeyvatAncients.RowsFor` read. Pure data over TYPES and STRINGS, so the
    /// headless suite can exercise every one of them without a `ModelDb`.
    /// </summary>
    public static class TeyvatGeneratedAncients
    {
        /// <summary>
        /// THE FACES' OWN FLAT LOC ROWS, under the DRESSED `Id.Entry`, which no
        /// base Ancient has -- so a `LocTable.MergeWith`, which is global and
        /// overwrites, cannot reach the shipped game's text. A pin asserts it.
        ///
        /// NO OPTION ROW IS EVER IN HERE. An Ancient's boons are
        /// `RelicOption&lt;T&gt;()` and `EventOption.FromRelic` is
        /// `GetOptionTitle(key) ?? relic.Title`, so an absent row falls through
        /// to the relic's own; the generator has no path that writes one.
        /// </summary>
        public static readonly IReadOnlyDictionary<string, string> Rows =
            new Dictionary<string, string>(StringComparer.Ordinal)
            {""")
    for key, value in flat:
        out.append(f"                [{cs(key)}] =\n                    {cs(value)},")
    out.append("            };\n")

    out.append("""        /// <summary>
        /// ONE DRESSED DIALOGUE LINE, BY COORDINATE -- the one place this
        /// surface is not a dictionary.
        ///
        /// A dialogue line's key carries an `r` suffix when the dialogue is in
        /// the repeating pool (`AncientDialogue.PopulateLines` derives
        /// `IsRepeating` from the key's presence), and whether a given base
        /// dialogue is repeating is a fact about the shipped loc PACK, not
        /// about any C# this repo can read. So a dressed line is carried as
        /// its coordinates and `TeyvatAncients.RowsFor` resolves the suffix
        /// against the live table at merge time. Empty today, by R275: the
        /// words are a second bill.
        /// </summary>
        public readonly record struct AncientLine(
            string DressedEntry,
            string CharEntry,
            int DialogueIndex,
            int LineIndex,
            bool AncientSpeaks,
            string Text);

        /// <inheritdoc cref="AncientLine"/>
        public static readonly IReadOnlyList<AncientLine> Lines =
            new List<AncientLine>
            {""")
    for entry, char_key, slot, line_i, is_ancient, text in dialogue:
        out.append(f"                new AncientLine({cs(entry)}, {cs(char_key)}, "
                   f"{slot}, {line_i}, "
                   f"{'true' if is_ancient else 'false'}, {cs(text)}),")
    out.append("            };\n")

    out.append("""        /// <summary>Dressed `Id.Entry` -> the base Ancient's `Id.Entry`. The
        /// picture patch's fall-back table and the loc ALIAS pass both read
        /// this, so a dressed body cannot exist in one and not the other.
        /// </summary>
        public static readonly IReadOnlyDictionary<string, string> BaseEntries =
            new Dictionary<string, string>(StringComparer.Ordinal)
            {""")
    for row in rows:
        out.append(f"                [{cs(row.entry)}] = {cs(row.ancient)},")
    out.append("            };\n")

    out.append("""        /// <summary>
        /// (face, base Ancient type) -> the dressed instance. `Dress` below is
        /// the only reader; it is a table rather than a switch so a pin can
        /// count it.
        /// </summary>
        public static readonly
            IReadOnlyDictionary<(string Face, Type BaseAncient),
                                Func<AncientEventModel>> Dressings =
            new Dictionary<(string, Type), Func<AncientEventModel>>
            {""")
    for row in rows:
        base_cls = index[row.ancient]["class"]
        out.append(f"                [({cs(row.face)}, typeof({base_cls}))] =\n"
                   f"                    () => ModelDb.AncientEvent"
                   f"<Ancients.{row.cls}>(),")
    out.append("            };\n")

    out.append("""        /// <summary>
        /// face -> every dressed entry that face can show, the act's own pool
        /// and the shared Ancients together. The pins read this; nothing at
        /// runtime does.
        /// </summary>
        public static readonly IReadOnlyDictionary<string, IReadOnlyList<string>>
            FacePools = new Dictionary<string, IReadOnlyList<string>>(
                StringComparer.Ordinal)
            {""")
    by_face: Dict[str, List[str]] = {}
    for row in rows:
        by_face.setdefault(row.face, []).append(row.entry)
    for face in FACE_ACTS:
        entries = ", ".join(cs(e) for e in by_face.get(face, []))
        out.append(f"                [{cs(face)}] = new[] {{ {entries} }},")
    out.append("            };\n")

    out.append("""        /// <summary>
        /// THE ONE RUNTIME READER. Every base Ancient in `source` is swapped
        /// for this face's dressed body; one with no dressing is passed
        /// through unchanged.
        ///
        /// IT MAPS, IT DOES NOT FILTER, and that is the whole safety argument
        /// for the pools. A face act answers `AllAncients` and
        /// `GetUnlockedAncients` by handing the BASE act's own answer through
        /// here, so the length is equal by construction, the order is the base
        /// act's order, and every epoch filter the base act applies
        /// (`Hive.GetUnlockedAncients` removes Orobas behind `OrobasEpoch`)
        /// still applies -- the dressing is downstream of it. The same call
        /// serves `SetSharedAncientSubset`, which is how Darv becomes Alice
        /// without touching `ModelDb.AllSharedAncients` or the up-front rng
        /// draws `RunManager.GenerateRooms` spends dealing him out.
        ///
        /// WITH THE ARM OFF IT IS THE IDENTITY. An undressed run reaches
        /// exactly the objects it reached before.
        /// </summary>
        public static IEnumerable<AncientEventModel> Dress(
            string face, IEnumerable<AncientEventModel> source)
        {
            if (!TeyvatFrame.Enabled || source == null)
            {
                return source;
            }

            return source.Select(a =>
                a != null
                && Dressings.TryGetValue((face, a.GetType()), out var make)
                    ? make()
                    : a);
        }
    }
}
""")
    return "\n".join(out)


# ----------------------------------------------------------------------------
# DRIVER
# ----------------------------------------------------------------------------


def build(rows: List[Row], index: Dict[str, dict]) -> Tuple[str, List[str]]:
    refusals: List[str] = []

    seen: Dict[Tuple[str, str], Row] = {}
    for row in rows:
        if row.face not in FACE_ACTS:
            refusals.append(f"{row.ancient}/{row.face}: `{row.face}` is not one "
                            f"of the six faces R273 ruled")
            continue
        if row.ancient not in index:
            refusals.append(f"{row.ancient}/{row.face}: the game has no Ancient "
                            f"`{row.ancient}`")
            continue
        key = (row.ancient, row.face)
        if key in seen:
            refusals.append(f"{row.ancient}/{row.face}: two rows for one body")
            continue
        if not row.name:
            refusals.append(f"{row.ancient}/{row.face}: no name. R275 ships "
                            f"names; every other column may be empty, this one "
                            f"may not")
            continue
        seen[key] = row

    for key in expected_rows():
        if key not in seen:
            refusals.append(f"{key[0]}/{key[1]}: R275 owes this body and the "
                            f"faces file has no row for it")

    ordered = [seen[k] for k in expected_rows() if k in seen]

    entries: Dict[str, Row] = {}
    for row in ordered:
        shape = index[row.ancient]
        row.cls = pascal(row.name) + row.face.title()
        row.entry = slugify(row.cls)
        if row.entry in entries:
            refusals.append(f"{row.ancient}/{row.face}: entry `{row.entry}` "
                            f"collides with {entries[row.entry].ancient}/"
                            f"{entries[row.entry].face}")
        if row.entry in index:
            refusals.append(f"{row.ancient}/{row.face}: entry `{row.entry}` is a "
                            f"BASE Ancient's entry -- a merged row under it "
                            f"would overwrite the shipped game's text")
        entries[row.entry] = row

        where = f"{row.ancient}/{row.face}"
        row.parsed_first = parse_lines(  # type: ignore[attr-defined]
            row.first_visit, f"{where} first_visit",
            shape["first_visit_lines"], refusals)
        row.parsed_chars = [  # type: ignore[attr-defined]
            parse_char_cell(cell, f"{where} dialogue_{i + 1}",
                            shape["character_dialogues"], i, refusals)
            for i, cell in enumerate(row.dialogues)]
        row.parsed_agnostics = parse_agnostics(  # type: ignore[attr-defined]
            row.agnostics, where, shape["agnostic_lines"], refusals)
        row.parsed_extra = parse_extra(  # type: ignore[attr-defined]
            row.extra, f"{where} extra", shape["extra_keys"], refusals)

    if refusals:
        return "", refusals
    return emit(ordered, index), []


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="verify the committed output, write nothing")
    ap.add_argument("--refresh", action="store_true",
                    help="rebuild tools/data/sts2_base_ancients.json")
    ap.add_argument("--decompile", type=Path, default=DECOMP_DEFAULT)
    args = ap.parse_args(argv)

    if args.refresh:
        return refresh_index(args.decompile)

    index = load_index()
    rows, refusals = read_faces()
    if refusals:
        for r in refusals:
            print(f"gen_teyvat_ancients: {r}", file=sys.stderr)
        return 1

    text, refusals = build(rows, index)
    if refusals:
        for r in refusals:
            print(f"gen_teyvat_ancients: {r}", file=sys.stderr)
        return 1

    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.is_file() else ""
        if current != text:
            print(f"gen_teyvat_ancients: {OUT.relative_to(REPO)} is STALE "
                  f"-- rerun without --check", file=sys.stderr)
            return 1
        print(f"gen_teyvat_ancients: {len(rows)} dressed Ancient(s), output fresh")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"gen_teyvat_ancients: wrote {OUT.relative_to(REPO)} "
          f"({len(rows)} dressed Ancient(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
