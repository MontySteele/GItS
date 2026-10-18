"""The Kokomi review, round 6 (2026-10-14): section 3 and the ruled picks.

`review/active/kokomi-review-r6-2026-10-14.md`. [USER]: "2,3,4) Good with the
defaults, other than the first question." Then, on pick 1: "Let's go with
(a)." Numbers (items 1-6), the seat page's text and display (items 7-11), the
three checks (item 12), the harness (item 13), Mend's cap printed (pick 1
(a)), the two reaction Powers cut for two Hydro sources (pick 2 (b)) and Read
the Field's free card (pick 3 (a)). The C# twin is
`klee-mod/KleeTests/Prototype/KokomiReviewR6Tests.cs`.
"""
from __future__ import annotations

import collections

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import kokomi_plan, powers
from tier0.engine.state import Card
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, carry_out, kokomi_state, write)
from tier0.tests.test_understudy_blindplay import (TWO_PLANS,
                                                   _past_lethal_state,
                                                   combat_state, morning_of,
                                                   plans_combat_state)
from understudy import blindplay, blindplay_render


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _amounts(cid, where="effects", i=0):
    return (getattr(loader.get_card(cid), where)[i]["amount"],
            getattr(_up(cid), where)[i]["amount"])


# ---- items 1-5: numbers ---------------------------------------------------

def test_the_numbers_pass():
    assert _amounts("proto_kk_watatsumi_drill") == (7, 10)
    wake = loader.get_card("proto_kk_kurages_wake")
    assert (wake.effects[0]["amount"], wake.effects[0]["times"]) == (5, 2)
    assert _amounts("proto_kk_watchful_shoal") == (4, 6)
    assert _amounts("proto_kk_grand_strategist") == (6, 8)
    assert _amounts("proto_kk_tidal_riposte") == (8, 11)


# ---- item 6: Sea Glass Harvest reaches the Discard Pile -------------------

def test_sea_glass_harvest_transforms_every_pile_she_holds():
    st = kokomi_state()
    dazed = Card(id="status_dazed", name="Dazed", cost=-1, type="status",
                 effects=[])
    st.player.hand.append(dazed)
    st.player.draw_pile.append(Card(id="status_dazed", name="Dazed", cost=-1,
                                    type="status", effects=[]))
    st.player.discard_pile.append(Card(id="status_dazed", name="Dazed",
                                       cost=-1, type="status", effects=[]))
    n = kokomi_plan.transform_statuses(st, upgraded=False)
    assert n == 3
    for pile in (st.player.hand, st.player.draw_pile, st.player.discard_pile):
        assert not any(c.id == "status_dazed" for c in pile)
    face = loader.get_card("proto_kk_sea_glass_harvest")
    assert face.plan == [{"op": "transform_statuses_you_have"}]


# ---- pick 2 (b): the cut and the two new Powers ---------------------------

def test_the_reaction_powers_are_cut_and_two_hydro_sources_take_their_slots():
    ids = list(C.KOKOMI_OVERHAUL_POOL_IDS)
    rows = {c.id for c in loader.prototype_cards()}
    for cid in ("proto_kk_jellyfish_current", "proto_kk_coordinated_tide"):
        assert cid not in ids and cid not in rows, cid
    for cid, power, amounts in (
            ("proto_kk_kurage_vanguard", "kk_kurage_vanguard", (4, 6)),
            ("proto_kk_following_current", "kk_following_current", (3, 4))):
        assert cid in ids and cid in rows, cid
        row = loader.get_card(cid)
        assert (row.rarity, row.type, row.cost) == ("uncommon", "power", 1)
        assert row.effects[0]["power"] == power
        assert _amounts(cid) == amounts
    assert len(ids) == 79  # Kokomi v3 (2026-10-18): Unbroken Tide
    rarity = collections.Counter(loader.get_card(cid).rarity for cid in ids)
    assert rarity == {"common": 20, "uncommon": 39, "rare": 20}


def test_kurage_vanguard_hits_the_front_enemy_for_hydro_each_turn():
    st = kokomi_state(n_enemies=2)
    st.player.powers[kokomi_plan.KURAGE_VANGUARD] = 4
    front, back = st.enemies
    hp = (front.hp, back.hp)
    kokomi_plan.kurage_vanguard(st)
    assert (front.hp, back.hp) == (hp[0] - 4, hp[1])
    assert front.aura == "hydro"


def test_following_current_hits_once_per_carry_out():
    st = kokomi_state()
    st.player.powers[kokomi_plan.FOLLOWING_CURRENT] = 3
    write(st, card("proto_kk_tidal_screen"))
    write(st, card("proto_kk_tidal_screen"))
    hp = st.enemies[0].hp
    carry_out(st)
    assert st.enemies[0].hp == hp - 6


# ---- pick 3 (a): Read the Field's card costs 0 ----------------------------

def test_read_the_fields_plan_card_costs_0_this_turn():
    st = kokomi_state()
    st.player.draw_pile = [card("proto_kk_spearhead")]
    pick = kokomi_plan.draw_pile_to_hand(st)
    assert pick is not None and pick.free_this_turn
    assert "It costs 0 this turn." in (
        _row("proto_kk_read_the_field")["description"])


def _row(cid):
    import yaml
    with open("docs/prototype-surface.yaml", encoding="utf-8") as f:
        return next(r for r in yaml.safe_load(f) if r["id"] == cid)


# ---- item 12: the checks ---------------------------------------------------

def test_kelp_wall_says_attack_damage():
    """Only an enemy Attack's absorbed damage moves Kelp Wall's count
    (`KokomiOverhaulLedger.NoteEnemyHit`, pinned in C#; the sim calls
    `note_enemy_hit` from an enemy's attack alone), so Disintegration's
    damage Block absorbs does not. The face says so."""
    assert "the Attack damage you blocked" in (
        _row("proto_kk_kelp_wall")["description"])


def test_seas_reproach_fires_on_weak_a_plan_applies():
    st = kokomi_state()
    st.player.powers[kokomi_plan.SEAS_REPROACH] = 5
    hp = st.enemies[0].hp
    write(st, card("proto_kk_slack_water"))
    carry_out(st)
    assert st.enemies[0].powers.get("weak", 0) > 0
    assert st.enemies[0].hp < hp


def test_heizou_counts_swirls_before_his_own_hit():
    """His count is read when the hit is computed, so his own Swirl does not
    raise it: 6 with no Swirl before him this turn."""
    st = kokomi_state()
    st.mi_swirls_this_turn = 0
    row = loader.get_card("proto_mi_heizou_heartstopper")
    formula = row.effects[0]["amount_formula"]
    assert formula == {"base": 6, "per": 4, "count": "swirls_this_turn"}


# ---- items 7-11 and pick 1 (a): the seat page -----------------------------

def _page(queue, enemies=None) -> list[str]:
    state = _past_lethal_state(queue=queue, hp=40, enemies=enemies)
    return blindplay.render(blindplay.observation(state)).splitlines()


SCULPTOR = {"entity_id": "SCULPTOR_0", "combat_id": 1, "name": "Sculptor",
            "hp": 30, "max_hp": 30, "block": 0, "status": [],
            "intents": [{"type": "Buff", "label": "", "title": "Strategic",
                         "description": "This enemy intends to Buff."}]}


def test_a_counter_plan_no_enemy_attacks_into_is_warned_about():
    lines = _page([{"name": "Brine Sting", "clauses": 1,
                    "needs_attack": "attackers",
                    "live": "No enemy intends to attack"}],
                  enemies=[SCULPTOR])
    assert ("     - Sculptor does not intend to attack: Brine Sting's Plan "
            "hits no one.") in lines


def test_no_warning_where_an_enemy_attacks():
    lines = _page([{"name": "Brine Sting", "clauses": 1,
                    "needs_attack": "attackers", "live": "No attack yet"}])
    assert not any("does not intend to attack" in line for line in lines)


def test_the_panel_says_plans_carry_out_after_the_draw():
    lines = _page([{"name": "Kurage's Oath", "clauses": 1}])
    assert "- Plans carry out after your draw." in lines


def test_an_all_plan_names_what_vulnerable_makes_of_it():
    body = dict(SCULPTOR, status=[{"id": "VULNERABLE", "name": "Vulnerable",
                                   "amount": 2, "type": "Debuff",
                                   "description": ""}])
    lines = _page([{"name": "Pearl Current", "clauses": 1, "aim": "all",
                    "written": 10}], enemies=[body])
    assert ("     - Lands 10 to ALL next turn (15 on Sculptor, after "
            "Vulnerable).") in lines


def test_a_mend_receipt_names_the_cap():
    state = plans_combat_state(morning_of(
        {"card": "The Moon, A Ship O'er the Seas", "number": 1,
         "kind": "HP healed", "asked": 6,
         "line": "Bake-Kurage: The Moon, A Ship O'er the Seas, 1"}))
    page = blindplay.render(blindplay.observation(state))
    assert ("The Moon, A Ship O'er the Seas, 1 — Mend 6, 1 landed: Mend never "
            "heals above the HP you started this combat with.") in page


def test_a_receipt_names_a_bonus_the_way_it_names_a_cap():
    said = {"number": 4, "asked": 3, "kind": "Block", "moved": [],
            "board_read": False}
    you = {"powers": [{"name": "Watchful Shoal", "stacks": 1}]}
    assert blindplay_render._kind_clause(said, [], you) == (
        " — asked for 3, 4 landed: Watchful Shoal.")


def test_the_energy_line_names_relic_energy():
    you = {"energy": 4, "max_energy": 3, "relics": [
        {"name": "Lantern", "text": "At the start of each combat, gain 1 "
                                    "Energy."}]}
    assert blindplay_render._energy_line(you) == (
        "Energy 4 (3 a turn, +1 Lantern)")
    assert blindplay_render._energy_line(
        {"energy": 2, "max_energy": 3}) == "Energy 2 left of 3"


def test_ripple_basin_greys_out_once_an_attack_is_planned():
    plans = dict(TWO_PLANS, queue=[{"name": "Kurage's Oath", "clauses": 1,
                                    "attack": True}])
    assert blindplay_render._planned_attack(plans)
    assert not blindplay_render._planned_attack(TWO_PLANS)


# ---- item 13: the harness ---------------------------------------------------

def test_a_bare_name_takes_any_copy_whose_live_number_differs():
    state = combat_state()
    hand = state["player"]["hand"]
    twin = dict(hand[3])
    twin["description"] = str(twin.get("description") or "") + " (7)"
    hand.append(twin)
    res = blindplay.act(state, 'play "Coral Guard"')
    assert res["ok"], res["refusal"]
    assert res["post"]["card_index"] == 3


def test_seas_reproach_reads_the_applier_as_her():
    """The C# `SeasReproachPower.Pays` asks the applier be her; a Plan's
    debuff is applied BY HER (`kokomi_plan._debuff`, `applier=state.player`).
    """
    st = kokomi_state()
    st.player.powers[kokomi_plan.SEAS_REPROACH] = 5
    hp = st.enemies[0].hp
    powers.apply_power(st, st.enemies[0], "weak", 1, applier=st.player)
    assert st.enemies[0].hp == hp - 5
