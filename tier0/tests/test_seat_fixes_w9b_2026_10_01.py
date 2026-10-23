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


def test_a_damaging_melt_or_vaporize_gets_no_amplify_note():
    """Klee round 2026-10-11, lane 2: a Bomb's Melt printed "nothing to
    amplify" beside a correct 17. The note is for element-only applications:
    Deal passes hadHit true, ApplyOnly false, and only false notes it."""
    src = _read("klee-mod", "KleeCode", "Powers", "ElementalHit.cs")
    deal = src[src.index("public static async Task<int> Deal("):
               src.index("public static Task<int> DealWithoutDealerMods(")]
    apply_only = src[src.index("public static async Task ApplyOnly("):
                     src.index("public const string NoHitToAmplify")]
    assert "hadHit: true" in deal and "hadHit: false" not in deal
    assert "hadHit: false" in apply_only and "hadHit: true" not in apply_only
    resolve = src[src.index("private static async Task ResolveOnAura("):]
    assert "if (!hadHit) NoteNoHit(consumed, element);" in resolve


# ---- 3. Spend ---------------------------------------------------------------

def test_the_spend_tip_says_whose_fanfare_pays():
    # The re-founding (2026-10-04): her one Fanfare number pays a Spend.
    # The Spend paper (2026-10-10): the second sentence names Spend up to X.
    assert ARM_KEYWORDS["Spend"] == (
        "Pay that much Fanfare. With less, you cannot play the card or its "
        "Spend mode. "
        "Spend up to X pays X, or all you have if that is less.")


# ---- 4. Arkhe Alignment -----------------------------------------------------


# ---- 5. Frozen blocked by Artifact ------------------------------------------

def test_a_frozen_artifact_blocked_is_said_on_the_row_and_the_preview():
    effects = _read("klee-mod", "KleeCode", "Powers", "ReactionEffects.cs")
    note = effects.index("ReactionLog.Note(reaction, target, dealer, cardSource);")
    assert "FrozenArtifactDetail(target)" in effects[note - 600:note]
    assert "OfType<ArtifactPower>()" in effects
    tips = _read("klee-mod", "KleeCode", "Cards", "KleeCardTooltips.cs")
    assert "ReactionEffects.ArtifactWillBlock(reaction, enemy)" in tips
    # Co-op seat (2026-10-16): a blocked Frozen is its own row, and the
    # preview never reads the hit-scoped Shatter mark.
    assert "new HashSet<(Reaction, bool, Element)>()" in tips
    assert "FrozenArtifactDetail(enemy)" not in tips
    assert "blocks the" in tips


# ---- 8. Four Winds' Ascension -----------------------------------------------

def test_four_winds_prints_its_oath_hit_total_in_combat():
    """20 then 39: Strength counts once on the Oath hit, because it is one.
    Text pass 2026-10-13 ([USER]: "I don't think we need the 'as one hit'
    bit"): the words go, the in-combat total says it, the hit stays one."""
    sheet = _read("docs", "prototype-surface.yaml")
    row = sheet[sheet.index("id: proto_vk_four_winds_ascension"):]
    row = row[:row.index("\n\n")]
    assert "in one hit" not in row
    assert ("damage per [gold]Oath[/gold] of your [gold]current element"
            "[/gold], as that element.{InCombat:\\n(Deals {VkHit:diff()} "
            "damage)|}") in row
    assert "per: 3" in row                      # no number moved
    card = _read("klee-mod", "KleeCode", "Cards", "Prototype", "Generated",
                 "ProtoVkFourWindsAscension.cs")
    assert "in one hit" not in card
    assert "new VarkaCurrentElementHitVar()" in card


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
