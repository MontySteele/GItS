"""The Kokomi review, round 8 (2026-10-14): items 1 to 12.

`review/active/kokomi-review-r8-2026-10-14.md`, Claude's (Kokomi is at
Prototype). Five cards that pay Block now (items 1-5), Mend's "(N will land)"
read live (6), Sucrose's "(no aura: no Swirl)" (7), one wording for when Plans
happen (8), a carry-out's receipt naming the reaction that raised it (9), a
power that keeps its row when its text cannot be read (10), and two seat-page
lines (11, 12). The C# twin is
`klee-mod/KleeTests/Prototype/KokomiReviewR8Tests.cs`.
"""
from __future__ import annotations

from pathlib import Path

from tier0.content import loader, upgrades
from tier0.engine import combat, effects, kokomi_plan
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import plan_card
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, kokomi_state)
from tier0.tests.test_understudy_blindplay import (_past_lethal_state,
                                                   morning_of,
                                                   plans_combat_state)
from tools import gen_klee_cards
from understudy import (blindplay, blindplay_faces, blindplay_notes,
                        blindplay_render)

REPO = Path(__file__).resolve().parents[2]
ATTACKING = [{"kind": "attack", "amount": 5}]


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _sheet_row(cid):
    import yaml
    rows = yaml.safe_load((REPO / "docs" / "prototype-surface.yaml")
                          .read_text(encoding="utf-8"))
    rows = rows["cards"] if isinstance(rows, dict) else rows
    return next(r for r in rows if r["id"] == cid)


def _schedule_plans(st, n):
    for i in range(n):
        kokomi_plan.schedule(st, plan_card([{"op": "draw", "amount": 1}],
                                           cid=f"proto_kk_p{i}"))


# ---- item 1: Shell of Sanctuary -------------------------------------------

def test_shell_of_sanctuary_is_a_flat_retained_block():
    """Superseded by Kokomi review r9 (2026-10-15, item 4): 6 [9], Retain."""
    row = loader.get_card("proto_kk_shell_of_sanctuary")
    assert row.plan == [] and row.retain
    assert row.effects == [{"op": "block", "amount": 6}]
    assert _up("proto_kk_shell_of_sanctuary").effects[0]["amount"] == 9
    st = kokomi_state()
    effects.resolve_card(st, row)
    assert st.player.block == 6
    _schedule_plans(st, 3)
    st.player.block = 0
    effects.resolve_card(st, row)
    assert st.player.block == 6



# ---- item 2: Evening Watch ------------------------------------------------

def test_evening_watch_gives_6_per_attacker():
    row = loader.get_card("proto_kk_evening_watch")
    assert row.effects[0] == {"op": "kokomi", "kind": "block_per_attacker",
                              "amount": 6}
    assert _up("proto_kk_evening_watch").effects[0]["amount"] == 8
    st = kokomi_state(n_enemies=2)
    for enemy in st.enemies:
        enemy.intents = list(ATTACKING)
    st.player.draw_pile = [card("proto_kk_feint")]
    ew = card("proto_kk_evening_watch")
    st.player.hand.append(ew)
    combat.play_card(st, ew)
    assert st.player.block == 6 * 2


# ---- item 3: Undercurrent Snare -------------------------------------------

def test_undercurrent_snare_blocks_8_and_keeps_its_plan():
    row = loader.get_card("proto_kk_undercurrent_snare")
    assert row.effects[0] == {"op": "block", "amount": 8}
    assert row.effects[1] == {"op": "apply_power", "power": "weak",
                              "amount": 2, "target": "enemy"}
    assert row.plan == [{"op": "lose_strength_this_turn", "amount": 4,
                         "target": "enemies_intending_attack"}]
    up = _up("proto_kk_undercurrent_snare")
    assert (up.effects[0]["amount"], up.plan[0]["amount"]) == (11, 5)


# ---- item 4: Surging Shoal ------------------------------------------------

def test_surging_shoal_hits_all_and_blocks_now_with_no_plan():
    row = loader.get_card("proto_kk_surging_shoal")
    assert (row.cost, row.rarity, row.plan) == (2, "uncommon", [])
    up = _up("proto_kk_surging_shoal")
    assert (up.effects[0]["amount"], up.effects[1]["amount"]) == (13, 13)
    st = kokomi_state(n_enemies=3)
    before = [e.hp for e in st.enemies]
    effects.resolve_card(st, row)
    assert [b - e.hp for b, e in zip(before, st.enemies)] == [10, 10, 10]
    assert st.player.block == 10


# ---- item 5: Feint --------------------------------------------------------

def test_feints_now_line_is_a_flat_8_whatever_waits():
    row = loader.get_card("proto_kk_feint")
    assert row.effects == [{"op": "damage", "amount": 8, "target": "enemy"}]
    assert row.plan == [{"op": "damage_per_plan_this_turn", "amount": 6,
                         "target": "front_enemy"}]
    up = _up("proto_kk_feint")
    assert (up.effects[0]["amount"], up.plan[0]["amount"]) == (10, 8)
    enemy = make_enemy(hp=100)
    st = kokomi_state()
    st.enemies = [enemy]
    _schedule_plans(st, 2)
    effects.resolve_card(st, row)
    assert 100 - enemy.hp == 8


def test_the_five_faces_print_the_ruled_text():
    assert _sheet_row("proto_kk_shell_of_sanctuary")["description"] == (
        "Gain {Block:diff()} [gold]Block[/gold].")
    assert _sheet_row("proto_kk_evening_watch")["description"] == (
        "Gain {KkAmount:diff()} [gold]Block[/gold] for each enemy intending "
        "to attack. Draw 1 card.")
    assert _sheet_row("proto_kk_undercurrent_snare")["description"].startswith(
        "Gain 8 [gold]Block[/gold]. Apply 2 [gold]Weak[/gold]. ")
    assert _sheet_row("proto_kk_surging_shoal")["description"] == (
        "Deal 10 [gold]Hydro[/gold] damage to ALL enemies. Gain 10 "
        "[gold]Block[/gold].")
    assert _sheet_row("proto_kk_feint")["description"].startswith(
        "Deal 8 [gold]Hydro[/gold] damage. [gold]Plan[/gold]: ")


# ---- item 6: Mend's "(N will land)" is read at format time ----------------

def test_mend_lands_formats_through_the_cap_not_the_printed_number():
    """The face's bare `{MendLands}` is formatted through `ToString()` /
    `IConvertible`, which read the printed number. `MendLandsVar` answers
    `MendWouldLand` there now; the sim's `effects.mend` is the same cap."""
    src = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "ProtoBakeKuragePower.cs").read_text(encoding="utf-8")
    var = src[src.index("public sealed class MendLandsVar"):]
    assert "protected override decimal GetBaseValueForIConvertible() => Live;" \
        in var
    assert "public override string ToString() =>" in var
    live = var[var.index("internal int Live"):]
    assert "KokomiRules.MendWouldLand(owner, Printed(card, BaseValue))" in live
    # The seat's case: at the HP it entered with, a Mend 6 heals 0.
    st = kokomi_state(hp=80)
    assert effects.mend(st, 6) == 0
    st.player.hp = 76
    assert effects.mend(st, 6) == 4


# ---- item 7: Sucrose's "(no aura: no Swirl)" ------------------------------

def test_sucrose_swirl_faces_carry_the_no_aura_clause():
    token = "{InCombat:{SwirlAura}|}"
    for cid, phrase in (
            ("proto_mc_sucrose_mollis_favonius",
             "[gold]Swirl[/gold] the enemy"),
            ("proto_mc_sucrose_gust", "[gold]Swirl[/gold] ALL enemies"),
            ("proto_mc_sucrose_astable", "[gold]Swirl[/gold] ALL enemies")):
        row = _sheet_row(cid)
        desc, args = gen_klee_cards.swirl_aura_face_lines(
            row, row["description"])
        assert phrase + token in desc, cid
        assert args == [("SwirlAura", "SwirlAuraFace.Line(this)")]
    # Not Sucrose's Catalyst Conversion (no Swirl), not another Swirl row.
    for cid in ("proto_mc_sucrose_catalyst_conversion",
                "proto_mc_jean_gale_blade"):
        row = _sheet_row(cid)
        assert gen_klee_cards.swirl_aura_face_lines(
            row, row["description"]) == (row["description"], [])


def test_the_words_match_the_mods():
    src = (REPO / "klee-mod" / "KleeCode" / "Cards" / "SwirlAuraFace.cs"
           ).read_text(encoding="utf-8")
    assert (f'public const string NoAura = "{gen_klee_cards.SWIRL_AURA_WORDS}";'
            in src)
    assert gen_klee_cards.SWIRL_AURA_WORDS == " (no aura: no Swirl)"


# ---- item 8: one wording for when Plans happen -----------------------------

def test_the_panel_says_after_your_draw_and_never_before_you_play():
    assert "before you play" not in blindplay_notes.PLAN_BLOCK_NOTE
    assert "still standing in" in blindplay_notes.PLAN_BLOCK_NOTE
    state = _past_lethal_state(queue=[{"name": "Kurage's Oath",
                                       "clauses": 1}], hp=40)
    page = blindplay.render(blindplay.observation(state))
    assert "- Plans carry out after your draw." in page
    assert "before you play anything" not in page


# ---- item 9: the receipt names the reaction --------------------------------

def test_a_receipt_names_the_vaporize_that_raised_it():
    said = {"number": 63, "asked": 42, "kind": "damage",
            "moved": [{"target": "Louse Progenitor", "amount": 63}],
            "board_read": True, "reactions": ["Vaporize"]}
    assert blindplay_render._kind_clause(said, [], {}) == (
        " — asked for 42, 63 landed: Vaporize.")


def test_the_wire_carries_reactions_onto_the_page():
    state = plans_combat_state(morning_of(
        {"card": "Masterstroke", "number": 63, "kind": "damage",
         "asked": 42, "line": "Bake-Kurage: Masterstroke, 63",
         "moved": [], "reactions": ["Vaporize"]}))
    obs = blindplay.observation(state)
    row = obs["combat"]["plans"]["carried_out"][0]
    assert row["reactions"] == ["Vaporize"]
    assert ("Masterstroke, 63 — asked for 42, 63 landed: Vaporize."
            in blindplay.render(obs))


def test_an_older_mod_with_no_reactions_prints_what_it_did():
    said = {"number": 63, "asked": 42, "kind": "damage", "moved": [],
            "board_read": True}
    assert blindplay_render._kind_clause(said, [], {}) == (
        " — the 63 is damage; the clause asked for 42.")


# ---- item 10: a power keeps its row ---------------------------------------

def test_an_unreadable_power_keeps_its_row_and_says_so():
    blob = {"status": [{"id": "KLEEMOD-AT_WATERS_EDGE_POWER",
                        "name": "At Water's Edge", "amount": 1,
                        "stack": "Counter", "type": "Buff",
                        "description": None, "keywords": [],
                        "unreadable": "NullReferenceException"}]}
    power = blindplay_faces._powers(blob)[0]
    assert power["unreadable"] is True
    line = blindplay_render._render_power(power, "- ")
    assert line == ("- At Water's Edge 1 (buff) — still on you; the game "
                    "would not give its text on this screen")


def test_the_bridge_keeps_the_row_on_a_throw():
    src = (REPO / "vendor" / "STS2_MCP" / "McpMod.StateBuilder.cs"
           ).read_text(encoding="utf-8")
    assert "GitsPowerRow.Unreadable(" in src
    assert "catch { /* skip this power - game engine state" not in src


# ---- item 11: what Sloth counted ------------------------------------------

SLOTH = {"name": "Sloth", "stacks": 3,
         "text": "You cannot play more than 3 cards each turn."}


def test_sloth_names_the_cards_it_counted_a_plans_companion_included():
    rows = [{"card": "Noelle", "auto_played": True, "play_count": 2},
            {"card": "Kurage's Oath+", "auto_played": False},
            {"card": "Strike", "carried": True},
            {"card": "Partner's Strike", "is_local": False}]
    assert blindplay_render._played_cap_lines(SLOTH, rows) == [
        "    - Counted this turn: **Noelle** (played for you) x2, "
        "**Kurage's Oath+**."]
    assert blindplay_render._played_cap_lines(SLOTH, []) == []
    assert blindplay_render._played_cap_lines(SLOTH, None) == []
    shell = {"name": "Hardened Shell", "stacks": 12,
             "text": "Cannot lose more than 20 HP each turn."}
    assert blindplay_render._played_cap_lines(shell, rows) == []


# ---- item 12: a Power with nothing to measure ------------------------------

def test_a_power_with_no_measurable_output_says_it_is_on_you():
    row = {"card": "Resolve of Watatsumi", "card_type": "Power",
           "auto_played": False, "carried": False, "overflowed": False,
           "hits": [], "killed": []}
    lines = blindplay_render._resolution_lines([row])
    assert lines[1] == blindplay_notes.RESOLUTION_POWER_PLAYED
    assert "Nothing this page can count" not in "\n".join(lines)
    skill = dict(row, card="Defend", card_type="Skill")
    assert blindplay_render._resolution_lines([skill])[1] == (
        blindplay_notes.RESOLUTION_NO_HITS)
