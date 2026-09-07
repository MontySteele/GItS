"""`EB-623`: no printed surface says "morning".

[USER]'s Kokomi act-1 run of 2026-09-07 read "Morning" as a word the kit
invents for a thing the base game already has a phrase for -- "the start of
your next turn" -- so a face, a tip or a page line that says it is asking the
player to learn a synonym. The word is retired from every PRINTED surface and
kept everywhere the engine names a thing: `block_per_plan_this_morning`,
`plans_carried_out_this_morning`, `kk_plans_this_morning`,
`KokomiOverhaulLedger.PlansThisMorning`, `LAST_MORNING_NOTE`,
`MorningDamageKey` and every comment and docstring that explains the rule.

THIS IS A LINT, not a pin on one sentence, because the word's whole problem
was that it had spread: a card face, two hover tips and two page lines, each
landed for its own good reason and none of them looking at the others. A pin
on the five would not stop a sixth. So the check is the shape the defect had
-- read the four surfaces a player actually sees and fail on the word.

WHAT COUNTS AS PRINTED. In C#: a double-quoted literal that is not on a
comment line and that contains a space (a loc key like
`"KLEEMOD-MORNING_DAMAGE_RIDER"` is an identifier wearing quotes, not
English). In Python: the same space rule, over the string constants `ast` reports minus
every docstring -- so `obs["last_morning"]`'s subscript is a field name and
not a sentence. Both rules are deliberately generous to the engine and strict
about English.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

#: The C# surfaces a player reads: the generated card localization (every
#: `("description", "...")` and hover line the codegen emits) and the two
#: hand-written tip files that hang off them.
CS_SURFACES = (
    REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated",
    REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "ArmKeywordTips.cs",
    REPO / "klee-mod" / "KleeCode" / "Cards" / "KokomiRiderTips.cs",
    # The loc table the tip TITLES come out of, which is where the word
    # survived one pass of this row: the bodies were rewritten and
    # `MorningDamageKey`'s title still read "Damage from the morning".
    REPO / "klee-mod" / "KleeCode" / "KleeMod.cs",
)

#: The blind page's two: the glossary and notes it prints from, and the
#: renderer that lays the sections out.
PY_SURFACES = (
    REPO / "understudy" / "blindplay_notes.py",
    REPO / "understudy" / "blindplay_render.py",
)

_CS_STRING = re.compile(r'"((?:[^"\\\n]|\\.)*)"')


def _cs_printed_strings(path: Path) -> list[tuple[int, str]]:
    """Every string literal on a non-comment line that reads as English."""
    out: list[tuple[int, str]] = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("//"):
            continue
        for m in _CS_STRING.finditer(line):
            text = m.group(1)
            if " " in text:
                out.append((n, text))
    return out


def _py_printed_strings(path: Path) -> list[tuple[int, str]]:
    """Every string constant that is not a docstring."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef,
                             ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                docstrings.add(id(body[0].value))
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in docstrings and " " in node.value):
            out.append((node.lineno, node.value))
    return out


def _cs_files() -> list[Path]:
    files: list[Path] = []
    for entry in CS_SURFACES:
        if entry.is_dir():
            files += sorted(entry.glob("*.cs"))
        else:
            files.append(entry)
    return files


def test_no_generated_card_or_tip_string_prints_the_word():
    """The C# half: faces and hover tips."""
    hits = [f"{p.name}:{n}: {s}"
            for p in _cs_files()
            for n, s in _cs_printed_strings(p)
            if "morning" in s.lower()]
    assert not hits, "printed C# strings still say 'morning':\n" + "\n".join(hits)


def test_no_blind_page_line_prints_the_word():
    """The page half: the glossary, the notes and the renderer."""
    hits = [f"{p.name}:{n}: {s}"
            for p in PY_SURFACES
            for n, s in _py_printed_strings(p)
            if "morning" in s.lower()]
    assert not hits, "printed page strings still say 'morning':\n" + "\n".join(hits)


def test_the_engine_still_names_the_morning():
    """The other half of the row, and the reason this is a lint on PRINTED
    strings rather than a grep on the tree: the ops, the counters and the
    accessors keep the word, because renaming them would move a rule while
    pretending to move a sentence."""
    surface = (REPO / "docs" / "prototype-surface.yaml").read_text(
        encoding="utf-8")
    assert "block_per_plan_this_morning" in surface
    assert "plans_carried_out_this_morning" in surface

    state = (REPO / "tier0" / "engine" / "state.py").read_text(encoding="utf-8")
    assert "kk_plans_this_morning" in state

    ledger = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
              / "KokomiOverhaulLedger.cs").read_text(encoding="utf-8")
    assert "PlansThisMorning" in ledger

    notes = (REPO / "understudy" / "blindplay_notes.py").read_text(
        encoding="utf-8")
    assert "LAST_MORNING_NOTE" in notes


def test_the_lint_would_bite():
    """A check nobody has watched fail is not a check. Both readers are given
    a line they must catch, in the shape the defect actually had."""
    fake_cs = 'yield return new HoverTip(k, "carried out this morning.");'
    assert any("morning" in s.lower()
               for _, s in [(1, m.group(1))
                            for m in _CS_STRING.finditer(fake_cs)])

    fake_py = ast.parse('NOTE = "The morning is empty."')
    found = [n.value for n in ast.walk(fake_py)
             if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    assert any("morning" in s.lower() for s in found)


def test_a_loc_key_is_not_english():
    """`MorningDamageKey`'s value is a string literal with the word in it and
    is not a printed surface -- the C# reader skips it because it has no
    space, which is the rule that keeps this lint off the engine."""
    keys = [s for _, s in _cs_printed_strings(
        REPO / "klee-mod" / "KleeCode" / "Cards" / "KokomiRiderTips.cs")]
    assert not any(s == "KLEEMOD-MORNING_DAMAGE_RIDER" for s in keys)
    assert "KLEEMOD-MORNING_DAMAGE_RIDER" in (
        REPO / "klee-mod" / "KleeCode" / "Cards"
        / "KokomiRiderTips.cs").read_text(encoding="utf-8")
