"""`EB-699` -- no power is titled after a card that does not make it.

THE FIND (Kokomi r30 lane 1). Kujou Sara's Tengu Stormcall promises "next
turn, your Attacks deal 5 more damage", and the buff that keeps that promise
arrived on the player's bar titled **Fantastic Voyage** -- Bennett's card, a
different companion, from a different nation, that the seat had never drafted.
Nothing on any screen connected the two.

IT WAS TRUE ONCE AND STOPPED BEING TRUE. `AttackUpThisTurnPower` was Bennett's
burst, and only Bennett's, when it was written. The Mondstadt redesign moved
that card onto real `StrengthPower` (`CompanionPowers.cs`, the note above
`CelestialGiftPower`'s turn-start hook) and left the power behind with its
name; Sara's `TenguStormcallPower` then picked it up as the thing it pays into,
because a "this turn" window already summed by every damage path is exactly
what "next turn" needs. So the title outlived its one owner.

THE FIX IS THE ROW'S FIRST OPTION, AND THE LINT IS THE SECOND HALF OF IT. A
power a single card makes may wear that card's name; a power more than one card
can make is named for what it does. This file is the check, and it is
STRUCTURAL rather than a list: it reads the mod's own sources for which card
classes apply which powers, and refuses a power whose title is some card's
title while that card is not among the classes that apply it.

THE ONE JUDGEMENT IN IT is the guard on indirect application. A power handed
out by a kit rail rather than by a card face (`SpotlightSystem`,
`KokomiOverhaulKit`, the Kurage summon entry points) has no card applier this
scrape can see, so its title cannot be checked against one and it is reported
as UNCHECKED rather than failed -- a silent skip is how a rule stops covering
what it claims to. The powers with a card applier are checked, and that is the
family the defect lives in.
"""

from __future__ import annotations

import collections
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
CODE = REPO / "klee-mod" / "KleeCode"

#: `("title", "...")` inside a class body -- the mod's `ILocalizationProvider`
#: rows. `$"..."` is accepted because several powers interpolate a constant
#: into the description beside a literal title.
_TITLE = re.compile(r'\("title",\s*\$?"([^"]*)"\)')
_CLASS = re.compile(r"\bclass\s+(\w+)")
_APPLY = re.compile(r"PowerCmd\.Apply<(\w+)>")

#: A companion card's title is "<Character> -- <Card>", em dash. The power
#: wears the card half.
_EM_DASH = "—"


def _sources() -> dict[pathlib.Path, str]:
    return {
        path: path.read_text(encoding="utf-8", errors="replace")
        for path in CODE.rglob("*.cs")
    }


def _owner_of(text: str):
    """Position -> the class whose body it falls in, by source order.

    Good enough and deliberately so: every file in this tree declares its
    classes at the top level in source order, and the alternative (a real C#
    parse) would be a second toolchain to keep alive for one lint.
    """
    classes = [(m.start(), m.group(1)) for m in _CLASS.finditer(text)]

    def owner(pos: int) -> str | None:
        found = None
        for start, name in classes:
            if start < pos:
                found = name
            else:
                break
        return found

    return owner


def _scrape():
    card_titles: dict[str, str] = {}
    power_titles: dict[str, str] = {}
    appliers: dict[str, set[str]] = collections.defaultdict(set)
    for path, text in _sources().items():
        owner = _owner_of(text)
        is_power = "/Powers/" in path.as_posix()
        for match in _TITLE.finditer(text):
            cls = owner(match.start())
            if cls is None:
                continue
            (power_titles if is_power else card_titles)[cls] = match.group(1)
        for match in _APPLY.finditer(text):
            cls = owner(match.start())
            if cls is not None:
                appliers[match.group(1)].add(cls)
    return card_titles, power_titles, appliers


def _reachable(power: str, appliers: dict[str, set[str]]) -> set[str]:
    """Every class that applies this power, directly or through a power that
    does -- Sara's promise applies the window from inside another power."""
    seen = set(appliers.get(power, ()))
    frontier = list(seen)
    while frontier:
        node = frontier.pop()
        for nxt in appliers.get(node, ()):
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    return seen


@pytest.fixture(scope="module")
def scrape():
    return _scrape()


def test_no_power_is_titled_after_a_card_that_does_not_apply_it(scrape):
    card_titles, power_titles, appliers = scrape

    by_title: dict[str, set[str]] = collections.defaultdict(set)
    for cls, title in card_titles.items():
        by_title[title.split(_EM_DASH)[-1].strip()].add(cls)

    findings = []
    for power, title in sorted(power_titles.items()):
        named = by_title.get(title)
        if not named:
            continue                       # titled after nothing; fine
        reached = _reachable(power, appliers)
        # UNCHECKED, not passed: no card face applies this power, so the
        # scrape has no card to compare the title against.
        if not (reached & set(card_titles)):
            continue
        if not (named & reached):
            findings.append(
                f"{power} is titled {title!r}, which is "
                f"{sorted(named)}'s card -- applied by {sorted(reached)}")
    assert not findings, "\n".join(findings)


def test_saras_window_is_named_for_its_effect(scrape):
    """The row's own card, pinned by name so a rename cannot drift back."""
    _, power_titles, appliers = scrape

    assert power_titles["AttackUpThisTurnPower"] == "Attack Up"
    # And the promise that pays into it is still the only thing that does,
    # which is what makes the shared-power reading the right one.
    reached = _reachable("AttackUpThisTurnPower", appliers)
    assert "ProtoMiSaraTenguStormcall" in reached
    assert "BennettFantasticVoyage" not in reached


def test_the_lint_can_see_a_power_titled_after_its_own_card(scrape):
    """Non-vacuity: the rule permits the ordinary case, so a green run is not
    a scrape that found nothing. Gorou's banner IS titled after its card."""
    _, power_titles, appliers = scrape

    assert power_titles["WarBannerPower"] == "General's War Banner"
    assert "ProtoMiGorouWarBanner" in _reachable("WarBannerPower", appliers)
