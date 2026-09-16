"""`EB-754` -- no `{var}` reaches the page off a power's static row.

THE FIND (Klee r27, the Codex seat, fight 4). Amber's buff printed the literal
`{Damage}` on the page, where a number should have been.

THE RULE IS THE GAME'S AND IT IS ONE BRANCH WIDE. `PowerModel.HoverTips` binds
`DynamicVars.AddTo(locString)` on the SMART branch alone -- the branch taken
only when `HasSmartDescription && IsMutable`. The other branch calls
`AddDumbVariablesToDescription`, which binds exactly three names: `Amount`,
`singleStarIcon` and `energyPrefix`. The base game says so about itself, in a
comment on `SmartDescription`: "Unlike other models' DynamicDescription, this
doesn't include any variables." So a `{Damage}` written on a power's static
`description` row is a placeholder nothing will ever fill, and SmartFormat
hands it to the screen as typed.

`EB-353` found this on Thoma's Blazing Barrier and Diona's Icy Paws and fixed
both by splitting the row: the static compendium line carries the clause with
its CONSTANT, and a `smartDescription` beside it carries the live var. `EB-754`
is the same defect on the two `ISummonDamagePower` rows -- Amber's Baron Bunny
and Chiori's Tamoto -- whose `{Damage}` is `EB-463`'s snapshot of the card's
folded number.

THIS FILE IS THE LINT THE ROW ASKED FOR, and it is what turns two fixes into a
family that cannot come back. It reads every `("description", ...)` row in the
mod's power sources and refuses any placeholder outside the game's own three.

WHAT IT CAN AND CANNOT SEE. A row assembled from literals -- which is every row
in this tree bar `ProtoBombPower`'s grid, whose fragments are private consts
and which selects among its rows by overriding `SmartDescriptionLocKey` -- is
read whole. A `$"..."` fragment is C# interpolation, resolved by the compiler
before any of this exists, so its braces are not placeholders and are skipped;
that distinction is per FRAGMENT, because a single row is routinely a
concatenation of both kinds.
"""

from __future__ import annotations

import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
POWERS = REPO / "klee-mod" / "KleeCode" / "Powers"

#: The three names `PowerModel.AddDumbVariablesToDescription` binds, read off
#: the 0.111.0 decompile. Everything else is a smart-branch var.
DUMB = frozenset({"Amount", "singleStarIcon", "energyPrefix"})

#: `("description", <expr>)` up to the closing paren of the tuple. Non-greedy
#: to the first `),` that ends a row -- every row in this tree ends that way.
_ROW = re.compile(r'\("description",(.*?)\),\s*\n', re.DOTALL)

#: A C# string literal, with its `$` marker if it has one.
_FRAGMENT = re.compile(r'(\$?)@?"((?:[^"\\]|\\.)*)"')

#: A SmartFormat placeholder: `{Name}`, `{Name:format}`. `{{` is an escape and
#: renders literally, so it is excluded by requiring a non-brace first char.
_PLACEHOLDER = re.compile(r"(?<!\{)\{([A-Za-z_][A-Za-z0-9_]*)[:}]")


def _owner_of(text: str):
    classes = [(m.start(), m.group(1))
               for m in re.finditer(r"\bclass\s+(\w+)", text)]

    def owner(pos: int) -> str | None:
        found = None
        for start, name in classes:
            if start < pos:
                found = name
            else:
                break
        return found

    return owner


def _static_rows():
    """(class, file, row text) for every static `description` in Powers/."""
    out = []
    for path in sorted(POWERS.rglob("*.cs")):
        text = path.read_text(encoding="utf-8")
        owner = _owner_of(text)
        for match in _ROW.finditer(text):
            out.append((owner(match.start()), path, match.group(1)))
    return out


def _placeholders(expr: str) -> set[str]:
    """Every name the localizer will be asked to bind in this row.

    A `$`-prefixed fragment is compiler interpolation and contributes none.
    """
    names: set[str] = set()
    for marker, body in _FRAGMENT.findall(expr):
        if marker == "$":
            continue
        names.update(_PLACEHOLDER.findall(body))
    return names


def test_no_static_power_row_writes_a_var_the_game_will_not_bind():
    findings = []
    for cls, path, expr in _static_rows():
        loose = _placeholders(expr) - DUMB
        if loose:
            findings.append(
                f"{cls} ({path.name}): {sorted(loose)} on the STATIC row -- "
                "move the clause to a `smartDescription` and leave the "
                "constant here")
    assert not findings, "\n".join(findings)


def test_the_two_summon_rows_say_their_number_twice_over():
    """The row's own two powers, by name. The static line prints the arm's
    constant -- "or print the base number", the row's second option -- and the
    smart line prints the live var, which is what `EB-463` banks at play."""
    text = {}
    for name in ("CompanionOverhaulHooks.cs", "CompanionOverhaulInazuma.cs"):
        text[name] = (POWERS / "Prototype" / name).read_text(encoding="utf-8")

    bunny = text["CompanionOverhaulHooks.cs"].split(
        "class BaronBunnyPower")[1].split("class ")[0]
    tamoto = text["CompanionOverhaulInazuma.cs"].split(
        "class TamotoPower")[1].split("class ")[0]

    for body, constant in ((bunny, "CompanionOverhaulLaw.BaronBunnyDamage"),
                           (tamoto, "CompanionOverhaulLaw.TamotoDamage")):
        assert '("smartDescription",' in body
        assert "{Damage}" in body
        # The static row prints the constant the var is SEEDED from, so an
        # unfolded play and the compendium agree.
        assert constant in body


def test_the_two_summon_rows_keep_the_key_the_game_probes_for():
    """`PowerModel.SmartDescriptionLocKey` is `Id.Entry + ".smartDescription"`
    and `HasSmartDescription` is a `LocString.Exists` probe on it, so the row's
    KEY has to be that exact suffix -- `EB-353`'s third pin, one arm over.
    `ProtoBombPower` overrides the property to select among a grid of rows;
    these two must not, or the row they declare would be registered under a key
    nothing looks up, which is the same class of miss as the raw `{Damage}`."""
    for name, cls in (("CompanionOverhaulHooks.cs", "BaronBunnyPower"),
                      ("CompanionOverhaulInazuma.cs", "TamotoPower")):
        src = (POWERS / "Prototype" / name).read_text(encoding="utf-8")
        body = src.split("class " + cls)[1].split("class ")[0]
        assert "SmartDescriptionLocKey" not in body, cls


def test_the_lint_is_not_vacuous():
    """It sees rows at all, and it sees the dumb vars it is meant to allow --
    a scrape that found nothing would pass the test above in silence."""
    rows = _static_rows()
    assert len(rows) > 60
    assert any("Amount" in _placeholders(expr) for _, _, expr in rows)


@pytest.mark.parametrize("expr,expected", [
    ('"deal [blue]{Damage}[/blue] damage"', {"Damage"}),
    ('$"deal [blue]{Law.Thing}[/blue] damage"', set()),
    ('"lasts {Amount:plural:turn|turns}"', {"Amount"}),
    ('"a literal {{Damage}} brace"', set()),
    ('"one " + $"{Law.X} " + "and [blue]{Left}[/blue]"', {"Left"}),
])
def test_the_scrape_tells_a_placeholder_from_an_interpolation(expr, expected):
    assert _placeholders(expr) == expected
