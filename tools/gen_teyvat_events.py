#!/usr/bin/env python3
"""Generate the Teyvat arm's DRESSED EVENTS from the curated event faces.

WHAT THIS IS
------------
Six curated face files under `docs/current/dossiers/content/event-faces/` hold,
per nation, a dressed title/scene/option set for each base event of the zone
that nation stands in. This turns those into:

  * one C# class per (base event, face) under
    `klee-mod/KleeCode/Teyvat/Events/<Face>/` -- a one-line subclass of the
    base event's hand-written MIRROR, with no body at all;
  * the loc rows for every key those classes ask for, as a `TeyvatLoc`
    partial;
  * the `(dressing, base event type) -> dressed model` rows the
    `PullNextEvent` postfix substitutes through.

The C# SHAPE decision, and the decompile facts it rests on, are written up in
`docs/current/operations/codegen.md` under "Codegen -- Teyvat dressed events".
The short version: every base event class is `sealed` and hardcodes its own loc
keys as string literals, so a dressed event CANNOT subclass its base; what it
CAN subclass is a hand-written abstract mirror of it, and then `Id.Entry`,
`OptionKey`, `Title` and `InitialDescription` all re-derive from the dressed
class NAME for free. That is why the generated file is one line of C#.

WHAT IS NOT GENERATED
---------------------
The mirrors. A base event with no mirror in `MIRRORS` below is reported and
skipped -- that report is the engineering queue for this surface. Mirroring an
event is hand work by design: it re-implements the base game's clauses and is
read against the decompile, which no generator can do on taste.

THE INDEX
---------
`tools/data/sts2_base_events.json` carries the structural facts both this
generator and the headless pins need: per base event the class name, the
`Id.Entry`, its option key names in order, its other page keys, whether an
option can kill, and the frozen harvest's option count. IDENTIFIERS ONLY --
no method bodies, no base-game prose -- so the repo's decompiled-material rule
(`.gitignore:28`, `csharp-build-spec.md` sec.0.3) is not bent, and `--check`
never needs a decompile.

Usage
-----
    python tools/gen_teyvat_events.py             # write the active faces
    python tools/gen_teyvat_events.py --check     # fail if output would change
    python tools/gen_teyvat_events.py --refresh   # rebuild the base-event index
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parent.parent

INDEX_PATH = REPO / "tools" / "data" / "sts2_base_events.json"
FACE_DIR = REPO / "docs" / "current" / "dossiers" / "content" / "event-faces"
HARVEST = REPO / "docs" / "sts2-events-harvest.txt"
EVENTS_ROOT = REPO / "klee-mod" / "KleeCode" / "Teyvat" / "Events"
GENERATED_CS = REPO / "klee-mod" / "KleeCode" / "Teyvat" / "TeyvatEventsGenerated.cs"

#: The decompiled namespace the index is refreshed from. Not in the repo; see
#: `tools/extract_base_game_pool.py` for the ilspycmd line that produces it.
DECOMP_DEFAULT = (
    Path.home() / "AppData" / "Local" / "Temp" / "claude" / "teyvat-decomp"
    / "MegaCrit.Sts2.Core.Models.Events"
)


# ---------------------------------------------------------------------------
# The face -> dressing map.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FaceSpec:
    """One curated face, and the dressing act it lands in.

    `act` is the dressing's `Id.Entry` -- the same constant
    `KleeMod.Teyvat.TeyvatFrame` holds, and the key the `PullNextEvent`
    substitution table is looked up by. `folder` is both the output directory
    and the C# namespace leaf.

    `active` is how acts 2 and 3 wait: their faces are curated and listed here,
    but their sibling ACTS do not exist (`TeyvatFrame` publishes two dressings,
    at index 0), so generating their events would mint classes no run can
    reach and a substitution table keyed on an act id nothing answers to.
    Turning one on is this flag plus the act.
    """

    key: str
    file: str
    act: str
    folder: str
    active: bool = True


FACES: Tuple[FaceSpec, ...] = (
    FaceSpec("overgrowth-mondstadt", "overgrowth-mondstadt-2026-09-14.md",
             "MONDSTADT", "Mondstadt"),
    FaceSpec("underdocks-liyue", "underdocks-liyue-2026-09-14.md",
             "LIYUE", "Liyue"),
    # Acts 2 and 3, curated and waiting on their acts.
    FaceSpec("glory-sumeru", "glory-sumeru-2026-09-14.md",
             "SUMERU", "Sumeru", active=False),
    FaceSpec("glory-fontaine", "glory-fontaine-2026-09-14.md",
             "FONTAINE", "Fontaine", active=False),
    FaceSpec("hive-inazuma", "hive-inazuma-2026-09-14.md",
             "INAZUMA", "Inazuma", active=False),
    FaceSpec("hive-natlan", "hive-natlan-2026-09-14.md",
             "NATLAN", "Natlan", active=False),
)


#: Base event class -> the hand-written abstract mirror that re-implements it.
#: THE HAND-WORK LEDGER. Everything absent from here is reported by the
#: generator as needing a mirror; adding one is a C# file under
#: `Teyvat/Events/Mirrors/` plus a row here, and every face that names the
#: event generates on the next run with no further work.
MIRRORS: Dict[str, str] = {
    "RoomFullOfCheese": "RoomFullOfCheeseMirror",
    "TheLegendsWereTrue": "TheLegendsWereTrueMirror",
    "ThisOrThat": "ThisOrThatMirror",
}


# ---------------------------------------------------------------------------
# Slugs and names.
# ---------------------------------------------------------------------------

_CAMEL = re.compile(r"([a-z0-9])([A-Z])")


def slugify(name: str) -> str:
    """`StringHelper.Slugify`, for the one input shape we hand it: a C# type
    name. CamelCase gets an underscore at each lower->upper boundary and the
    whole thing is upper-cased, which is exactly what `ModelDb.GetEntry` does
    to produce an `Id.Entry`."""
    return _CAMEL.sub(r"\1_\2", name.strip()).upper()


def normalise(text: str) -> str:
    """A heading or a class name reduced to comparable letters."""
    out = re.sub(r"[^a-z0-9]+", "", text.lower())
    return out


def match_base(heading: str, index: Dict[str, dict]) -> Optional[str]:
    """Which base event class a face's `## - [ ] <name>` heading names.

    The headings are the wiki's English titles and the classes are the game's
    identifiers, and they disagree in exactly two ways: punctuation (`This or
    That?`, `The Future of Potions_`) and a leading article (`The Sunken
    Statue` is `SunkenStatue`). Normalising both sides and retrying without a
    leading "the" settles every act-1 heading; anything left over is a refusal,
    not a guess.
    """
    want = normalise(heading)
    by_norm = {normalise(cls): cls for cls in index}
    if want in by_norm:
        return by_norm[want]
    stripped = want[3:] if want.startswith("the") else want
    for norm, cls in by_norm.items():
        bare = norm[3:] if norm.startswith("the") else norm
        if bare == stripped:
            return cls
    return None


def class_name_from_title(title: str) -> str:
    """The dressed C# class name for a face's `### <title>` line.

    A leading article is dropped and every non-alphanumeric character with it,
    which is the rule the spike's own `SpringvaleCheeseCellar` (from "The
    Springvale Cheese Cellar") already followed. The name is the WHOLE
    identity of a dressed event -- `Id.Entry`, every loc key, the portrait
    path and the ModelDb row all derive from it -- so it is checked for
    uniqueness across faces before anything is written.
    """
    text = title.strip()
    text = re.sub(r"^(the|a|an)\s+", "", text, flags=re.IGNORECASE)
    # Apostrophes are DELETED rather than treated as word breaks, so "The
    # Guild's Standing Commission" is `GuildsStandingCommission` and not
    # `GuildSStandingCommission` -- which would slug to `GUILD_S_STANDING_...`
    # and read as a typo in every loc key the event owns.
    text = re.sub(r"[’']", "", text)
    words = re.findall(r"[A-Za-z0-9]+", text)
    return "".join(w[:1].upper() + w[1:] for w in words)


# ---------------------------------------------------------------------------
# The base-event index (--refresh).
# ---------------------------------------------------------------------------

_CLASS_RE = re.compile(r"public\s+(sealed\s+)?class\s+(\w+)\s*:\s*(\w+)")
_KILL_RE = re.compile(r"\.(ThatDoesDamage|ThatDecreasesMaxHp|ThatWillKillPlayerIf)\(")


def harvest_option_counts() -> Dict[str, object]:
    """Option counts from the frozen harvest, keyed by normalised heading.

    The value is an int, or the string "none" for an event the harvest marks
    `<<NO OPTIONS SECTION ON PAGE>>` -- The Merchant___ is the one today. That
    marker is a SKIP and not a refusal: the wiki page has no options section,
    so there is nothing for a face to disagree with.
    """
    text = HARVEST.read_text(encoding="utf-8")
    out: Dict[str, object] = {}
    for block in re.split(r"^### ", text, flags=re.M)[1:]:
        head, _, body = block.partition("\n")
        name = re.sub(r"^\[[^\]]*\]\s*", "", head).strip()
        if "<<NO OPTIONS SECTION ON PAGE>>" in body:
            out[normalise(name)] = "none"
            continue
        out[normalise(name)] = len(re.findall(r"^\s*\[", body, flags=re.M))
    return out


def refresh_index(decomp: Path) -> int:
    """Rebuild `tools/data/sts2_base_events.json` from a local decompile.

    Reads ONLY identifiers: the class name, whether it is sealed, its base
    class, the loc-key literals it contains and whether any option is marked
    lethal. No method body and no base-game string ever leaves this function.
    """
    if not decomp.is_dir():
        print(f"gen_teyvat_events: no decompile at {decomp}", file=sys.stderr)
        print("  regenerate with: ilspycmd -p -o <dir> \"<GameDir>\\...\\sts2.dll\"",
              file=sys.stderr)
        return 2

    harvest = harvest_option_counts()
    index: Dict[str, dict] = {}
    for path in sorted(decomp.glob("*.cs")):
        src = path.read_text(encoding="utf-8", errors="replace")
        m = _CLASS_RE.search(src)
        if not m:
            continue
        cls, base = m.group(2), m.group(3)
        entry = slugify(cls)
        literals = re.findall(r'"(' + re.escape(entry) + r'[^"]*)"', src)

        options: List[str] = []
        pages: List[str] = []
        prefix = entry + ".pages.INITIAL.options."
        for lit in literals:
            if lit.startswith(prefix):
                # A truncated literal (`"...options."` built up by
                # concatenation, as Colorful Philosophers and Endless Conveyor
                # do) yields an EMPTY name. It is not an option key; it is a
                # sign the event builds its keys dynamically, which
                # `dynamic_keys` already records and which keeps the event off
                # the generatable list until a mirror is written for it.
                name = lit[len(prefix):]
                if name and name not in options:
                    options.append(name)
            else:
                suffix = lit[len(entry) + 1:]
                if suffix and suffix not in pages:
                    pages.append(suffix)

        norm = normalise(cls)
        count = harvest.get(norm)
        if count is None:
            # The harvest is keyed by the wiki's title, which may carry a
            # leading article the class name drops.
            for key, value in harvest.items():
                bare = key[3:] if key.startswith("the") else key
                if bare == (norm[3:] if norm.startswith("the") else norm):
                    count = value
                    break

        index[cls] = {
            "entry": entry,
            "sealed": bool(m.group(1)),
            "base": base,
            "option_keys": options,
            "page_keys": pages,
            "can_kill": bool(_KILL_RE.search(src)),
            "dynamic_keys": any("{" in lit for lit in literals),
            "harvest_options": count,
        }

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_comment": (
            "GENERATED by tools/gen_teyvat_events.py --refresh from a local "
            "0.111.0 decompile of MegaCrit.Sts2.Core.Models.Events. "
            "Identifiers only -- no base-game bodies or prose (.gitignore:28)."
        ),
        "game": "0.111.0",
        "events": index,
    }
    INDEX_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")
    print(f"gen_teyvat_events: index refreshed, {len(index)} base events "
          f"-> {INDEX_PATH.relative_to(REPO)}")
    return 0


def load_index() -> Dict[str, dict]:
    if not INDEX_PATH.exists():
        raise SystemExit(
            f"gen_teyvat_events: missing {INDEX_PATH.relative_to(REPO)}; "
            f"run with --refresh on a machine that has the decompile")
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))["events"]


# ---------------------------------------------------------------------------
# The face parser.
# ---------------------------------------------------------------------------


@dataclass
class FaceEvent:
    base_heading: str
    title: str
    subtitle: str
    body: str
    options: List[Tuple[str, str]] = field(default_factory=list)
    loss: Optional[str] = None
    line: int = 0


_OPTION_RE = re.compile(r"^-\s+\*\*(.+?)\*\*\s+[—-]\s+(.*)$")


def parse_face(path: Path) -> List[FaceEvent]:
    """Read one curated face file.

    The format is fixed by the curation pass: `## - [ ] <base event>`, then
    `### <title> - <nation> / <faction> - [literal|loose -] REUSED|DRAFTED`,
    then the scene paragraphs, then `- **<label>** - <outcome>` lines, then
    prose notes ending in `Mechanics check:`. Anything after the first option
    line that is not itself an option line is a NOTE and is not emitted: the
    notes restate the harvest for a human reader and are not player-facing
    text.

    An optional `Loss: <text>` line anywhere in the section supplies the
    `.loss` row for an event whose base can kill; without one the engine falls
    back to `DEFAULT_EVENT_LOSS_MESSAGE`, which `NRunHistory` reaches through
    `LocString.GetIfExists`.
    """
    events: List[FaceEvent] = []
    current: Optional[FaceEvent] = None
    body_lines: List[str] = []
    seen_option = False

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.rstrip()
        if line.startswith("## ") and not line.startswith("### "):
            if current is not None:
                current.body = _join(body_lines)
                events.append(current)
            heading = re.sub(r"^##\s*-\s*\[\s*[xX ]?\s*\]\s*", "", line).strip()
            current = FaceEvent(base_heading=heading, title="", subtitle="",
                                body="", line=lineno)
            body_lines, seen_option = [], False
            continue
        if current is None:
            continue
        if line.startswith("### "):
            head = line[4:].strip()
            parts = re.split(r"\s+[—]\s+", head)
            current.title = parts[0].strip()
            current.subtitle = head
            continue
        m = _OPTION_RE.match(line)
        if m:
            seen_option = True
            current.options.append((m.group(1).strip(), m.group(2).strip()))
            continue
        if line.lower().startswith("loss:"):
            current.loss = line.split(":", 1)[1].strip()
            continue
        if not seen_option and line and not line.startswith("---"):
            body_lines.append(line)

    if current is not None:
        current.body = _join(body_lines)
        events.append(current)
    return [e for e in events if e.title]


def _join(lines: Sequence[str]) -> str:
    return " ".join(l.strip() for l in lines if l.strip()).strip()


# ---------------------------------------------------------------------------
# Emission.
# ---------------------------------------------------------------------------

BANNER = (
    "// <auto-generated>\n"
    "//     GENERATED by tools/gen_teyvat_events.py from\n"
    "//     {source}\n"
    "//     Do not edit by hand: `python tools/gen_teyvat_events.py --check`\n"
    "//     fails on any drift, and the next run overwrites it.\n"
    "// </auto-generated>\n"
)


def cs_string(text: str) -> str:
    """One C# string literal, wrapped at a readable width as a `+` chain.

    Escaped rather than verbatim so a quote in the curated prose cannot end
    the literal, and wrapped because these are two-to-five-sentence scene
    paragraphs and a single 600-column line is unreviewable.
    """
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    if len(escaped) <= 66:
        return f'"{escaped}"'
    words, lines, cur = escaped.split(" "), [], ""
    for word in words:
        if cur and len(cur) + 1 + len(word) > 66:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}" if cur else word
    if cur:
        lines.append(cur)
    out = [f'"{lines[0]} "']
    for i, chunk in enumerate(lines[1:]):
        tail = "" if i == len(lines) - 2 else " "
        out.append(f'  + "{chunk}{tail}"')
    return "\n".join(out)


@dataclass
class Dressed:
    face: FaceSpec
    base_class: str
    mirror: str
    cls: str
    entry: str
    base_entry: str
    face_event: FaceEvent
    option_keys: List[str]
    page_keys: List[str]
    can_kill: bool

    def rows(self) -> List[Tuple[str, str]]:
        """Every loc row this dressed event needs, in key order.

        An option key is a PREFIX and the engine suffixes it twice --
        `EventModel.GetOptionTitle` is `key + ".title"` and
        `GetOptionDescription` is `key + ".description"`, and `GetIfExists`
        answers NULL for an absent key, which `EventOption`'s constructor then
        dereferences through `CharacterModel.AddDetailsTo`. A flat row per
        option is the defect that took the spike's page down to `options: []`
        (EB-765), so both rows are always written.
        """
        out: List[Tuple[str, str]] = [
            (f"{self.entry}.title", self.face_event.title),
            (f"{self.entry}.pages.INITIAL.description", self.face_event.body),
        ]
        paired = {
            key: (strip_base_gloss(label, key), outcome)
            for key, (label, outcome) in zip(self.option_keys, self.face_event.options)
        }
        for key in self.option_keys:
            base = f"{self.entry}.pages.INITIAL.options.{key}"
            out.append((base + ".title", paired[key][0]))
            out.append((base + ".description", paired[key][1]))
        for page in self.page_keys:
            out.append((f"{self.entry}.{page}", _page_text(paired, page)))
        if self.can_kill and self.face_event.loss:
            out.append((f"{self.entry}.loss", self.face_event.loss))
        return out


def strip_base_gloss(label: str, option_key: str) -> str:
    """A face's option label with its base-game gloss removed.

    The curation writes a renamed option as `Taste the Racks (Gorge)` so a
    reader can check it against the harvest. The parenthetical is EDITORIAL,
    not player-facing, and it is stripped only when it names the base event's
    own option key -- `(Gorge)` slugs to `GORGE`, so it goes; a parenthetical
    that is part of the dressing (`Broach the Wild Cask (Let Go)` names the
    base option too, and goes for the same reason) is distinguished by the
    same test and nothing else is touched.
    """
    m = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", label)
    if m and slugify_words(m.group(2)) == option_key:
        return m.group(1).strip()
    return label.strip()


def slugify_words(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", text).upper().strip("_")


def _page_text(paired: Dict[str, Tuple[str, str]], page: str) -> str:
    """The text for a non-INITIAL page key.

    A page key is `pages.<OPTION>.description` (the outcome screen the option
    leads to) or `pages.<OPTION>.selectionScreenPrompt` (the grid header).
    Both are derived from the face's own option line rather than authored
    here: the outcome sentence IS the page description, and the prompt
    restates the option's label. `<OPTION>` is the BASE event's key, and
    `paired` is that key already matched to this face's line by position --
    the same pairing the option rows are written from, so a page description
    and its option can never come from different lines.
    """
    tail = page[len("pages."):] if page.startswith("pages.") else page
    option, _, kind = tail.partition(".")
    label, outcome = paired.get(option, ("", ""))
    if kind == "selectionScreenPrompt":
        return label or option.replace("_", " ").title()
    return outcome or label


def dressed_class_source(item: Dressed, face_file: str) -> str:
    return (
        BANNER.format(source=f"docs/current/dossiers/content/event-faces/{face_file}")
        + "\n"
        + "using KleeMod.Teyvat.Events.Mirrors;\n"
        + "\n"
        + f"namespace KleeMod.Teyvat.Events.{item.face.folder};\n"
        + "\n"
        + "/// <summary>\n"
        + f"/// {item.face_event.title} -- {item.base_class}, dressed for "
        + f"{item.face.folder}.\n"
        + "///\n"
        + f"/// {item.face_event.subtitle}\n"
        + "///\n"
        + "/// NOTHING MECHANICAL IS HERE AND THERE IS NOWHERE FOR IT TO BE. The\n"
        + f"/// base event's clauses are in <see cref=\"{item.mirror}\"/>, written\n"
        + "/// once and shared by every nation that dresses this event; this class\n"
        + "/// is a NAME. `ModelDb.GetEntry` slugifies it into\n"
        + f"/// `{item.entry}`, `EventModel.Title` and `InitialDescription`\n"
        + "/// derive from that, and `EventModel.OptionKey` slugifies\n"
        + "/// `GetType().Name` -- so every loc key the mirror asks for is already\n"
        + "/// this dressing's. The rows are in `TeyvatLoc.GeneratedEventRows`.\n"
        + "/// </summary>\n"
        + f"public sealed class {item.cls} : {item.mirror}\n"
        + "{\n"
        + "}\n"
    )


def generated_cs_source(items: Sequence[Dressed]) -> str:
    rows: List[str] = []
    for item in items:
        rows.append(f"            // {item.cls} ({item.face.folder} / {item.base_class})")
        for key, value in item.rows():
            rows.append(f'            ["{key}"] =')
            body = cs_string(value)
            rows.append("\n".join("                " + l.strip() if i else "                " + l
                                  for i, l in enumerate(body.splitlines())) + ",")
    portraits = "\n".join(
        f'            ["{item.entry}"] =\n'
        f'                "res://images/events/{item.base_entry.lower()}.png",'
        for item in items
    )
    subs = "\n".join(
        f"            [(TeyvatFrame.{_frame_const(item.face.act)}, typeof({item.base_class}))] =\n"
        f"                () => ModelDb.Event<Events.{item.face.folder}.{item.cls}>(),"
        for item in items
    )
    shapes = "\n".join(
        "            [typeof(Events.{face}.{cls})] = new EventShape(\n"
        "                \"{base_entry}\", \"{mirror}\",\n"
        "                {opts},\n"
        "                {pages},\n"
        "                {kill}),".format(
            face=item.face.folder, cls=item.cls,
            base_entry=item.entry, mirror=item.mirror,
            opts=_cs_array(item.option_keys),
            pages=_cs_array(item.page_keys),
            kill="true" if (item.can_kill and item.face_event.loss) else "false")
        for item in items
    )
    return (
        BANNER.format(source="docs/current/dossiers/content/event-faces/*.md")
        + "\n"
        + "using System;\n"
        + "using System.Collections.Generic;\n"
        + "using MegaCrit.Sts2.Core.Models;\n"
        + "using MegaCrit.Sts2.Core.Models.Events;\n"
        + "\n"
        + "namespace KleeMod.Teyvat;\n"
        + "\n"
        + _generated_loc_doc()
        + "internal static partial class TeyvatLoc\n"
        + "{\n"
        + "    internal static readonly IReadOnlyDictionary<string, string> GeneratedEventRows =\n"
        + "        new Dictionary<string, string>(StringComparer.Ordinal)\n"
        + "        {\n"
        + "\n".join(rows) + "\n"
        + "        };\n"
        + "}\n"
        + "\n"
        + _generated_table_doc()
        + "internal static class TeyvatGeneratedEvents\n"
        + "{\n"
        + "    /// <summary>What a dressed event's mirror asks the loc table for:\n"
        + "    /// the option key names, in the base event's order, and the other\n"
        + "    /// page keys. Read by the headless pins, which check the key set\n"
        + "    /// against the merged rows without constructing a model.</summary>\n"
        + "    internal sealed record EventShape(\n"
        + "        string BaseEntry,\n"
        + "        string Mirror,\n"
        + "        IReadOnlyList<string> OptionKeys,\n"
        + "        IReadOnlyList<string> PageKeys,\n"
        + "        bool HasLossRow);\n"
        + "\n"
        + "    /// <summary>Dressed event type -> its shape.</summary>\n"
        + "    internal static readonly IReadOnlyDictionary<Type, EventShape> Shapes =\n"
        + "        new Dictionary<Type, EventShape>\n"
        + "        {\n"
        + shapes + "\n"
        + "        };\n"
        + "\n"
        + "    /// <summary>(dressing act entry, base event type) -> the dressed\n"
        + "    /// model that stands in for it at pull time. Consumed by\n"
        + "    /// `Patches/PullNextEventPatch`; see that file for why the\n"
        + "    /// substitution happens downstream of the shuffle.</summary>\n"
        + "    internal static readonly IReadOnlyDictionary<(string Dressing, Type BaseEvent), Func<EventModel>> Substitutions =\n"
        + "        new Dictionary<(string, Type), Func<EventModel>>\n"
        + "        {\n"
        + subs + "\n"
        + "        };\n"
        + "\n"
        + _portrait_doc()
        + "    internal static readonly IReadOnlyDictionary<string, string> Portraits =\n"
        + "        new Dictionary<string, string>(StringComparer.Ordinal)\n"
        + "        {\n"
        + portraits + "\n"
        + "        };\n"
        + "}\n"
    )


def _portrait_doc() -> str:
    return (
        "    /// <summary>\n"
        "    /// A dressed event's `Id.Entry` -> the image the default event layout\n"
        "    /// draws for it until one of its own is supplied (EB-764).\n"
        "    ///\n"
        "    /// `EventModel.InitialPortraitPath` is `ImageHelper.GetImagePath(\n"
        "    /// \"events/\" + Id.Entry.ToLowerInvariant() + \".png\")` -- DERIVED from\n"
        "    /// the id, `private`, and not virtual -- so a dressed event asks the\n"
        "    /// pack for a path nothing produces and `NEventLayout.InitializeVisuals`\n"
        "    /// threw `AssetLoadException` before the page was drawn. The value is the\n"
        "    /// BASE event's own image, which is the same borrowing\n"
        "    /// `TeyvatFrame.AssetAlias` makes for a dressing's backgrounds, and it\n"
        "    /// retires the same way: `Patches/EventPortraitPatch` asks\n"
        "    /// `ResourceLoader.Exists` of the DRESSED path first, so a real portrait\n"
        "    /// dropped at `events/&lt;dressed entry&gt;.png` wins with no code change.\n"
        "    ///\n"
        "    /// GENERATED, so a dressed event cannot exist without a portrait row --\n"
        "    /// which is exactly the shape EB-764 was.\n"
        "    /// </summary>\n"
    )


def _cs_array(values: Sequence[str]) -> str:
    """A C# `string[]` literal, or `Array.Empty<string>()` when there is
    nothing in it -- `new[] { }` does not compile."""
    if not values:
        return "Array.Empty<string>()"
    return "new[] { " + ", ".join(f'"{v}"' for v in values) + " }"


def _frame_const(act: str) -> str:
    return act.capitalize()


def _generated_loc_doc() -> str:
    return (
        "/// <summary>\n"
        "/// THE DRESSED EVENTS' LOC ROWS, generated from the curated faces.\n"
        "///\n"
        "/// EVERY KEY IS THIS ARM'S OWN. A `LocTable.MergeWith` is GLOBAL and\n"
        "/// overwrites, so a row whose key drifted onto a base event's family\n"
        "/// would silently rewrite the shipped game's text -- and the `events`\n"
        "/// table has no dressed-key trick to fall back on the way the monster\n"
        "/// names do. Every key below is prefixed with a DRESSED `Id.Entry`,\n"
        "/// which no base event has, and a pin asserts it.\n"
        "///\n"
        "/// AN OPTION KEY IS A PREFIX, NOT A STRING (EB-765). `EventOption`'s\n"
        "/// constructor reads `GetOptionTitle(key)` and `GetOptionDescription(key)`\n"
        "/// -- `key + \".title\"` and `key + \".description\"` -- and `GetIfExists`\n"
        "/// answers NULL for an absent key, which `AddLocVars` then dereferences.\n"
        "/// The generator writes both rows for every option, always.\n"
        "/// </summary>\n"
    )


def _generated_table_doc() -> str:
    return (
        "/// <summary>\n"
        "/// THE GENERATED TABLES the arm's two readers consult: the shape a\n"
        "/// dressed event's mirror has, and the substitution the `PullNextEvent`\n"
        "/// postfix makes. Both are generated from the same face files and the\n"
        "/// same base-event index as the classes and the rows above, so the\n"
        "/// three cannot disagree about what a dressing contains.\n"
        "/// </summary>\n"
    )


# ---------------------------------------------------------------------------
# The plan.
# ---------------------------------------------------------------------------


@dataclass
class Plan:
    items: List[Dressed] = field(default_factory=list)
    refusals: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    no_mirror: List[str] = field(default_factory=list)


def build_plan() -> Plan:
    index = load_index()
    harvest = harvest_option_counts()
    plan = Plan()
    claimed: Dict[str, str] = {}

    for face in FACES:
        if not face.active:
            continue
        path = FACE_DIR / face.file
        if not path.exists():
            plan.refusals.append(f"{face.key}: no face file at {path.relative_to(REPO)}")
            continue
        for event in parse_face(path):
            base = match_base(event.base_heading, index)
            if base is None:
                plan.refusals.append(
                    f"{face.key}: '{event.base_heading}' (line {event.line}) names no "
                    f"base event in {INDEX_PATH.relative_to(REPO)}")
                continue

            info = index[base]
            want = info.get("harvest_options")
            if want is None:
                want = harvest.get(normalise(base))
            if want == "none":
                plan.skipped.append(
                    f"{face.key}: {base} -- the harvest marks it "
                    f"<<NO OPTIONS SECTION ON PAGE>>, nothing to dress")
                continue
            mismatch = (
                f"{face.key}: {base} -- the face gives {len(event.options)} option(s) "
                f"(line {event.line}) and the harvest freezes {want}"
                if isinstance(want, int) and want != len(event.options) else None)

            # A MISMATCH ON AN EVENT WITH NO MIRROR IS A NOTE, NOT A REFUSAL,
            # and the difference is what the count is FOR. The count check
            # exists to stop a face's option lines being paired with the wrong
            # base option keys; an event with no mirror is not generated at
            # all, so there is no pairing to get wrong and nothing to refuse.
            # Some harvest entries also count a multi-page event's later-page
            # options inline (Abyssal Baths lists Linger and Exit Baths beside
            # the two INITIAL options), so a mirror-less mismatch is as often
            # the harvest's shape as the face's -- and it is settled when the
            # mirror is written and the event becomes generatable, which is
            # exactly when the refusal below starts biting.
            mirror = MIRRORS.get(base)
            if mirror is None:
                note = f" [option count {len(event.options)} vs harvest {want}]" \
                    if mismatch else ""
                plan.no_mirror.append(f"{face.key}: {base} ({event.title}){note}")
                continue

            if mismatch:
                plan.refusals.append(mismatch)
                continue

            option_keys = list(info["option_keys"])
            if len(option_keys) != len(event.options):
                plan.refusals.append(
                    f"{face.key}: {base} -- the mirror's {len(option_keys)} option "
                    f"key(s) {option_keys} cannot be paired with the face's "
                    f"{len(event.options)} option line(s)")
                continue

            cls = class_name_from_title(event.title)
            if cls in claimed:
                plan.refusals.append(
                    f"{face.key}: '{event.title}' slugs to {cls}, already claimed by "
                    f"{claimed[cls]} -- a dressed name IS the id and must be unique")
                continue
            claimed[cls] = f"{face.key}/{base}"

            plan.items.append(Dressed(
                face=face, base_class=base, mirror=mirror, cls=cls,
                entry=slugify(cls), base_entry=info["entry"], face_event=event,
                option_keys=option_keys,
                page_keys=list(info["page_keys"]),
                can_kill=bool(info["can_kill"]),
            ))

    return plan


def plan_files(plan: Plan) -> Dict[Path, str]:
    out: Dict[Path, str] = {}
    for item in plan.items:
        out[EVENTS_ROOT / item.face.folder / f"{item.cls}.cs"] = \
            dressed_class_source(item, item.face.file)
    out[GENERATED_CS] = generated_cs_source(plan.items)
    return out


def report(plan: Plan) -> None:
    by_face: Dict[str, int] = {}
    for item in plan.items:
        by_face[item.face.key] = by_face.get(item.face.key, 0) + 1
    for face in FACES:
        if face.active:
            print(f"  {face.key}: {by_face.get(face.key, 0)} dressed event(s)")
    for line in plan.skipped:
        print(f"  SKIP    {line}")
    for line in plan.no_mirror:
        print(f"  NO MIRROR {line}")
    for line in plan.refusals:
        print(f"  REFUSE  {line}", file=sys.stderr)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="fail if regenerating would change anything")
    ap.add_argument("--refresh", action="store_true",
                    help="rebuild tools/data/sts2_base_events.json from a decompile")
    ap.add_argument("--decompile", type=Path, default=DECOMP_DEFAULT,
                    help="the decompiled MegaCrit.Sts2.Core.Models.Events directory")
    args = ap.parse_args(argv)

    if args.refresh:
        return refresh_index(args.decompile)

    plan = build_plan()
    files = plan_files(plan)

    if plan.refusals:
        report(plan)
        return 1

    if args.check:
        stale: List[str] = []
        for path, text in files.items():
            if not path.exists():
                stale.append(f"missing: {path.relative_to(REPO)}")
            elif path.read_text(encoding="utf-8") != text:
                stale.append(f"stale: {path.relative_to(REPO)}")
        for face in FACES:
            folder = EVENTS_ROOT / face.folder
            if not folder.is_dir():
                continue
            for existing in sorted(folder.glob("*.cs")):
                if existing not in files:
                    stale.append(f"extra: {existing.relative_to(REPO)}")
        if stale:
            print("gen_teyvat_events --check: generated output is out of date")
            for line in stale:
                print(f"  {line}")
            return 1
        print(f"gen_teyvat_events --check: {len(files)} file(s) up to date")
        report(plan)
        return 0

    for face in FACES:
        folder = EVENTS_ROOT / face.folder
        if folder.is_dir():
            for existing in sorted(folder.glob("*.cs")):
                if existing not in files:
                    existing.unlink()
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(f"gen_teyvat_events: wrote {len(files)} file(s)")
    report(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
