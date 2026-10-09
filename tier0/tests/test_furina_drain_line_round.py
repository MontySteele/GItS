"""THE DRAIN-LINE ROUND'S FOUR CHANGES, in the sim, the generator and the page
(2026-10-09).

`review/records/furina-drain-line-round-2026-10-09.md`, "What to change":
every Repay preview with a floor names its payout ("(Repays 0, +3 Block)"),
a guest act's Drain stops at the line, the curtain-call sentence reads
"Drained HP above your line returns after combat.", and Critics' Darling's
hit has a line in the stage log. The C# twin is
`klee-mod/KleeTests/Prototype/FurinaDrainLineRoundTests.cs`.
"""

from __future__ import annotations

import random
from pathlib import Path

import pytest
import yaml

from tier0.content import loader
from tier0.engine import furina_tide as T
from tier0.engine.state import CombatState, Enemy
from tools import gen_klee_cards as gen
from understudy import blindplay, blindplay_notes, blindplay_render


def _state(hp=78, enemies=2, enemy_hp=200):
    p = T.build_player([])
    p.hp = hp
    st = CombatState(player=p,
                     enemies=[Enemy(hp=enemy_hp, max_hp=enemy_hp, name="paper",
                                    intents=[{"kind": "block", "amount": 0}])
                              for _ in range(enemies)],
                     rng=random.Random(0))
    st.turn = 1
    st.current_attack_bonus = 0
    T.turn_open(st)
    return st


def _rows():
    raw = yaml.safe_load(
        Path(loader.PROTOTYPE_SHEET).read_text(encoding="utf-8"))
    return {d["id"]: d for d in raw}


# ---- 1. the Repay preview names its payout -----------------------------------

PAYOUTS = {
    "proto_fs_fountain_of_lucine": "PayBlock",
    "proto_fs_hymn_of_many_waters": "PayBlock",
    "proto_fs_gentle_current": "PayBlock",
    "proto_fs_grand_entrance": "PayBlock",
    "proto_fs_pneuma_tides": "PayVigor",
    "proto_fs_surging_waters": "PayDamage",
    "proto_fs_hydro_lance": "PayDamage",
    "proto_fs_cleansing_torrent": "PayDamage",
}

NO_PAYOUT = ("proto_fs_soothing_waters", "proto_fs_pneuma_refrain",
             "proto_fs_balance_the_books", "proto_fs_grand_absolution",
             "proto_fs_singer_of_many_waters", "proto_fs_riptide_lunge",
             "proto_fs_clean_slate", "proto_fs_ebb_and_flow")


@pytest.mark.parametrize("cid,pay", sorted(PAYOUTS.items()))
def test_a_card_with_a_floor_previews_its_payout(cid, pay):
    call = gen.stage_repay_call(_rows()[cid])
    assert call.endswith(f", FurinaStageFacePreview.{pay})"), call


@pytest.mark.parametrize("cid", NO_PAYOUT)
def test_a_card_with_no_payout_keeps_the_plain_line(cid):
    call = gen.stage_repay_call(_rows()[cid])
    assert call and "FurinaStageFacePreview.Pay" not in call, call


def test_the_preview_words_are_one_short_line():
    src = (Path(__file__).resolve().parents[2] / "klee-mod" / "KleeCode"
           / "Powers" / "Prototype" / "FurinaStageBowPreview.cs").read_text(
               encoding="utf-8")
    assert '$"\\n(Repays {repays}, +{amount - repays} {payout})"' in src
    for word in ('"Block"', '"Vigor"', '"damage"'):
        assert word in src


# ---- 2. a guest act's Drain stops at the line --------------------------------

def test_lyneys_act_drains_only_the_room_above_the_line():
    st = _state(hp=50)
    f = st.player.ftd
    f.stage = ["lyney"]
    assert T.line_hp(st.player) == 49
    assert T.guest_drain_room(st, T.LYNEY_ACT_DRAIN) == 1
    T.act(st, "lyney")
    assert st.player.hp == 49 and f.drained == 1 and f.drained_past == 0
    assert all(e.hp == 200 - 8 for e in st.enemies)
    # At the line: no Drain, the damage unchanged.
    assert T.guest_drain_room(st, T.LYNEY_ACT_DRAIN) == 0
    T.act(st, "lyney")
    assert st.player.hp == 49 and f.drained == 1
    assert all(e.hp == 200 - 16 for e in st.enemies)


def test_the_players_own_drain_still_goes_past_the_line():
    st = _state(hp=50)
    assert T.drain(st, 5)
    assert st.player.hp == 45 and st.player.ftd.drained_past == 5


def test_lyneys_badge_says_his_drain_stops_at_the_line():
    src = (Path(__file__).resolve().parents[2] / "klee-mod" / "KleeCode"
           / "Powers" / "Prototype" / "FurinaStageBadges.cs").read_text(
               encoding="utf-8")
    assert '", never past your line. Deal " + act' in src


# ---- 3. the curtain-call sentence --------------------------------------------

def test_the_page_says_drained_hp_above_the_line_returns():
    assert "Drained HP above your line returns after combat." in (
        blindplay_notes.ARM_KEYWORDS["Drain"])
    assert "Drained HP above your line returns after combat." in (
        blindplay_render.STAGE_DRAIN_LINE)
    assert "it returns when combat ends" not in blindplay_render.STAGE_DRAIN_LINE


# ---- 4. Critics' Darling's hit in the stage log ------------------------------

def _stage(log):
    return {"live": True, "fanfare": 3, "gained_this_turn": 0,
            "spent_this_turn": 0, "paid_this_turn": 0, "rehearsal": 0,
            "capacity": 3, "seats": [], "log": log}


def _page(stage):
    player = {
        "character": "Furina", "hp": 62, "max_hp": 78, "block": 0,
        "energy": 3, "max_energy": 3, "gold": 0, "hand": [],
        "draw_pile_count": 5, "discard_pile_count": 2,
        "exhaust_pile_count": 0, "draw_pile": [], "discard_pile": [],
        "exhaust_pile": [], "relics": [], "potions": [], "status": [],
        "resources": {}, "pets": [], "furina_stage": stage,
    }
    return blindplay.observe({
        "state_type": "monster", "screen": "combat", "floor": 3,
        "battle": {"round": 3}, "player": player,
        "enemies": [{"name": "Nibbit", "hp": 20, "max_hp": 44, "block": 0,
                     "intents": [{"kind": "attack", "amount": 12}],
                     "status": []}],
    })


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


def test_a_power_hit_prints_a_log_line_naming_the_power():
    def beat(source, moved, reason):
        return {"event": "hit", "member": "charlotte", "name": "Charlotte",
                "seat": -1, "fanfare": 3, "moved": moved, "reason": reason,
                "target": "", "target_id": "", "source": source}

    page = _page(_stage([
        {"event": "drain", "member": "charlotte", "name": "Charlotte",
         "seat": -1, "fanfare": 3, "moved": 3, "reason": "", "target": "",
         "target_id": "", "source": ""},
        beat("Critics' Darling", 3, "random"),
        beat("Salon's Encore", 3, "all"),
    ]))
    assert "You drained 3 HP." in page
    assert "**Critics' Darling** dealt 3 damage to a random enemy." in page
    assert "**Salon's Encore** dealt 3 damage to ALL enemies." in page
