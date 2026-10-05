"""Seat fixes, 2026-10-01 (Varka and Furina seats, wave 9b).

Display truth only: no card number moves. Each test names the seat's report.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""

import copy
import re
from pathlib import Path

from understudy import blindplay
from understudy.blindplay_notes import ARM_KEYWORDS

from tier0.tests.test_understudy_blindplay import combat_state

REPO = Path(__file__).resolve().parents[2]
CODE = REPO / "klee-mod" / "KleeCode"


def _read(*parts: str) -> str:
    return (REPO.joinpath(*parts)).read_text(encoding="utf-8")


def _state(rows=(), potions=None) -> dict:
    state = copy.deepcopy(combat_state())
    state["player"]["resolutions"] = list(rows)
    if potions is not None:
        state["player"]["potions"] = potions
    return state


# ---- 1. "Overload hit Varka" ------------------------------------------------

def test_a_hit_on_you_inside_a_card_says_it_was_you_and_not_a_reaction():
    """A seat read a hit on Varka under Diluc's row as Overload's splash. The
    splash reaches `CombatState.HittableEnemies` only; the hit was something
    answering the attack. The row now says whose HP it was."""
    page = blindplay.observe(_state([{
        "card_id": "diluc", "card": "Diluc: Searing Onslaught",
        "auto_played": False, "carried": False, "overflowed": False,
        "hits": [
            {"target": "Nibbit", "amount": 8, "blocked": 0, "combat_id": "1"},
            {"target": "Varka", "amount": 3, "blocked": 0, "combat_id": "0",
             "on_player": True},
        ]}]))
    assert "1. **Nibbit** -- 8" in page
    # 2026-10-04: no dealer on this wire and no Thorns on the board, so the
    # line says whose HP it was and names nobody.
    assert "2. **Varka** (you) -- 3, taken while it resolved" in page
    assert "a reaction never hits you" not in page


def test_the_ledger_marks_a_hit_on_a_player():
    src = _read("klee-mod", "KleeCode", "Powers", "ResolutionLedger.cs")
    assert "bool OnPlayer = false" in src
    assert "target?.IsPlayer" in src
    assert '["on_player"] = hit.OnPlayer' in src


def test_overload_splash_reaches_enemies_only():
    src = _read("klee-mod", "KleeCode", "Powers", "ReactionEffects.cs")
    body = src[src.index("case Reaction.Overload:"):
               src.index("case Reaction.ElectroCharged:")]
    assert "HittableEnemies" in body
    assert "Creatures" not in body.replace("HittableEnemies", "")


def test_an_amplifier_off_an_application_says_there_was_no_hit():
    """Barbara's Hydro printed "Vaporize ... off Varka" and did nothing."""
    src = _read("klee-mod", "KleeCode", "Powers", "ElementalHit.cs")
    assert src.count("NoteNoHit(") == 2      # definition + Consume (no Spend since 2026-10-03)
    assert "nothing to amplify" in src


# ---- 3. Spend ---------------------------------------------------------------

def test_the_spend_tip_says_whose_fanfare_pays():
    # The re-founding (2026-10-04): her one Fanfare number pays a Spend.
    assert ARM_KEYWORDS["Spend"] == (
        "Pay that much Fanfare. Offered only if you have enough.")


# ---- 4. Arkhe Alignment -----------------------------------------------------


# ---- 5. Frozen blocked by Artifact ------------------------------------------

def test_a_frozen_artifact_blocked_is_said_on_the_row_and_the_preview():
    effects = _read("klee-mod", "KleeCode", "Powers", "ReactionEffects.cs")
    note = effects.index("ReactionLog.Note(reaction, target, dealer, cardSource);")
    assert "FrozenArtifactDetail(target)" in effects[note - 600:note]
    assert "OfType<ArtifactPower>()" in effects
    tips = _read("klee-mod", "KleeCode", "Cards", "KleeCardTooltips.cs")
    assert "ReactionEffects.FrozenArtifactDetail(enemy) != null" in tips
    assert "blocks the" in tips


# ---- 8. Four Winds' Ascension -----------------------------------------------

def test_four_winds_says_its_oath_damage_is_one_hit():
    """20 then 39: Strength counts once on the Oath hit, because it is one."""
    sheet = _read("docs", "prototype-surface.yaml")
    row = sheet[sheet.index("id: proto_vk_four_winds_ascension"):]
    row = row[:row.index("\n\n")]
    assert "as that element, in one hit." in row
    assert "per: 3" in row                      # no number moved
    card = _read("klee-mod", "KleeCode", "Cards", "Prototype", "Generated",
                 "ProtoVkFourWindsAscension.cs")
    assert "as that element, in one hit." in card


# ---- 9. `use potion 1` -------------------------------------------------------

def test_the_belt_prints_the_number_use_potion_takes():
    page = blindplay.observe(_state(potions=[
        {"slot": 0, "name": "Power Potion", "description": "Choose a Power.",
         "target_type": "Self"},
        {"slot": 2, "name": "Glowwater Potion",
         "description": "Exhaust your hand. Draw 10 cards.",
         "target_type": "AnyPlayer"},
    ]))
    assert "- 1. **Power Potion**" in page
    assert "- 2. **Glowwater Potion**" in page
    assert re.search(r"^- \*\*Power Potion\*\*", page, re.M) is None
