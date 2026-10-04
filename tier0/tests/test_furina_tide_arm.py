"""FURINA, THE SALON'S TAB: the arm's rules in the one-seat sim.

`review/active/furina-research-proposal-2026-10-05.md` sec.2 and sec.16, with
sec.17's two edits, built as the release Furina (2026-10-05). The arm runs on
the research slice's rules (`tier0/engine/furina_tide.py`) through
`tier0/engine/furina_stage.py` and the sheet's `stage_*` ops. One pin per
rule: the line, the drained ledger, Repay's cap, the curtain call, Fanfare
from HP lost and repaid, Revelry, the fixed price, the Drain mode's gate,
Salon's Tab's Energy next turn, and Curtain Rise's 12. The C# twins are
`klee-mod/KleeTests/Prototype/FurinaTideTests.cs`.
"""

from __future__ import annotations

import pytest

from tier0.content import loader
from tier0.engine import combat, effects, furina_stage as FS, resources
from tier0.tests.conftest import make_enemy, make_state


def _row(cid):
    return next(c for c in loader.prototype_cards() if c.id == cid)


def _furina(hp=78, max_hp=78, decider=None):
    st = make_state(enemies=[make_enemy(hp=300)], hp=max_hp)
    st.player.character_id = "furina"
    st.player.hp = hp
    st.player.stage_decider = decider
    st.in_player_turn = True
    st.turn = 1
    FS.reset_for_combat(st.player)
    return st


class _Never:
    """Takes the plain mode every time."""

    def spend_mode(self, state, modes):
        return 0

    def drain(self, *_):
        return False

    def spend(self, *_):
        return False

    def spend_all(self, *_):
        return False


class _Priced:
    """Takes the priced (second) mode whenever it is offered."""

    def spend_mode(self, state, modes):
        return 1 if len(modes) > 1 and FS.mode_offered(
            state.player, modes[1]) else 0


# ---- rule 1: the line ------------------------------------------------------

def test_the_line_is_half_the_hp_she_entered_combat_with():
    st = _furina(hp=60)
    assert FS.can_drain(st.player, 30)
    assert not FS.can_drain(st.player, 31)
    # Read at entry, not off max HP and not off her HP now.
    assert FS.drain(st, 20)
    assert st.player.hp == 40
    assert FS.can_drain(st.player, 10)
    assert not FS.can_drain(st.player, 11)


def test_a_drain_past_the_line_does_nothing():
    st = _furina(hp=20)
    assert not FS.drain(st, 11)
    assert st.player.hp == 20
    assert FS.drained(st.player) == 0
    assert FS.fanfare(st.player) == 0


# ---- rule 2: the ledger and Repay's cap -------------------------------------

def test_a_drain_is_recorded_and_prints_fanfare_one_for_one():
    st = _furina()
    assert FS.drain(st, 5)
    assert st.player.hp == 73
    assert FS.drained(st.player) == 5
    assert FS.fanfare(st.player) == 5


def test_repay_never_returns_more_than_was_drained():
    st = _furina()
    FS.drain(st, 4)
    assert FS.repay(st, 10) == 4
    assert st.player.hp == 78
    assert FS.drained(st.player) == 0
    # Nothing drained, nothing to Repay.
    assert FS.repay(st, 3) == 0
    assert st.player.hp == 78


def test_repay_prints_fanfare_per_hp_repaid():
    st = _furina()
    FS.drain(st, 6)
    before = FS.fanfare(st.player)
    FS.repay(st, 2)
    assert FS.fanfare(st.player) == before + 2


def test_hp_lost_to_an_enemy_prints_fanfare_and_is_not_drained():
    st = _furina()
    st.player.hp -= 7
    resources.note_player_hp_loss(st, 7)
    assert FS.fanfare(st.player) == 7
    assert FS.drained(st.player) == 0


# ---- the curtain call ------------------------------------------------------

def test_the_curtain_call_returns_every_drained_hp_and_prints_nothing():
    st = _furina()
    FS.drain(st, 9)
    fanfare = FS.fanfare(st.player)
    FS.close_combat(st)
    assert st.player.hp == 78
    assert FS.fanfare(st.player) == fanfare


def test_the_curtain_call_does_not_return_hp_lost_to_enemies():
    st = _furina()
    FS.drain(st, 5)
    st.player.hp -= 10
    resources.note_player_hp_loss(st, 10)
    FS.close_combat(st)
    assert st.player.hp == 68


def test_run_fight_carries_the_curtain_call_into_the_run():
    """The HP a won fight reports is after the curtain call: a Drain costs
    nothing past the fight."""
    from tier0.engine.state import Enemy, Player

    p = Player(hp=78, max_hp=78,
               draw_pile=[_row("proto_fs_curtain_rise") for _ in range(10)])
    p.character_id = "furina"
    p.stage_decider = _Priced()
    enemy = Enemy(hp=30, max_hp=30, name="paper",
                  intents=[{"kind": "block", "amount": 0}])

    def pilot(s):
        return next((c for c in s.player.hand
                     if combat.card_playable(s, c)
                     and c.cost <= s.player.energy), None)

    st = combat.run_fight(p, [enemy], pilot, seed=1)
    assert st.player.alive and not st.living_enemies
    assert any(e["event"] == "ftd_drain" for e in st.log)
    assert st.player.hp == 78


# ---- Spend and Revelry ------------------------------------------------------

def test_revelry_doubles_every_gain_and_two_copies_triple_it():
    st = _furina()
    effects.resolve_card(st, _row("proto_fs_universal_revelry"))
    FS.drain(st, 3)
    assert FS.fanfare(st.player) == 6
    st.player.hp -= 2
    resources.note_player_hp_loss(st, 2)
    assert FS.fanfare(st.player) == 10
    effects.resolve_card(st, _row("proto_fs_universal_revelry"))
    FS.repay(st, 1)
    assert FS.fanfare(st.player) == 13


def test_spend_takes_the_full_price_or_nothing():
    st = _furina()
    FS.drain(st, 3)
    assert FS.spend(st, 4) == 0
    assert FS.fanfare(st.player) == 3
    assert FS.spend(st, 3) == 3
    assert FS.fanfare(st.player) == 0


# ---- the fixed price and the Drain mode's gate ------------------------------

def test_a_fixed_drain_card_is_unplayable_past_the_line():
    crab = _row("proto_fs_mademoiselle_crabaletta")
    assert FS.fixed_price(crab) == ("stage_drain", 5)
    st = _furina(hp=78)
    crab.cost = 0
    st.player.energy = 3
    assert combat.card_playable(st, crab)
    st.player.hp = 43          # the line is 39: 43 - 5 < 39
    assert not combat.card_playable(st, crab)


def test_a_drain_mode_is_withheld_past_the_line():
    rise = _row("proto_fs_curtain_rise")
    plain, priced = rise.effects[0]["modes"]
    st = _furina(hp=78)
    assert FS.mode_offered(st.player, priced)
    st.player.hp = 41          # the line is 39: 41 - 3 < 39
    assert not FS.mode_offered(st.player, priced)
    assert FS.mode_offered(st.player, plain)
    assert "below the Drain line" in FS.mode_refusal(st.player, priced)


def test_curtain_rise_drains_3_for_12():
    """sec.17: Curtain Rise's Drain mode deals 12 [16]."""
    st = _furina(decider=_Priced())
    hp = st.enemies[0].hp
    effects.resolve_card(st, _row("proto_fs_curtain_rise"))
    assert st.player.hp == 75
    assert st.enemies[0].hp == hp - 12
    st2 = _furina(decider=_Never())
    hp2 = st2.enemies[0].hp
    effects.resolve_card(st2, _row("proto_fs_curtain_rise"))
    assert st2.player.hp == 78
    assert st2.enemies[0].hp == hp2 - 7


def test_salons_tab_gives_its_energy_next_turn_not_now():
    st = _furina(decider=_Priced())
    energy = st.player.energy
    effects.resolve_card(st, _row("proto_fs_salons_tab"))
    assert st.player.energy == energy
    # 2026-10-05 ruling: Draw 2; Drain 4: also gain 2 Energy next turn.
    assert st.player.ftd.energy_next == 2
    assert FS.drained(st.player) == 4


# ---- guests ------------------------------------------------------------------

def test_three_seats_and_the_oldest_leaves_first():
    st = _furina()
    for who in ("charlotte", "wriothesley", "lynette"):
        FS.guest_star(st, who)
    assert FS.stage(st.player) == ["charlotte", "wriothesley", "lynette"]
    FS.guest_star(st, "clorinde")
    assert FS.stage(st.player) == ["wriothesley", "lynette", "clorinde"]


# ---- off-character -----------------------------------------------------------

@pytest.mark.parametrize("cid", sorted(
    {c for c in FS.STARTER_IDS + FS.POOL_IDS if c.startswith("proto_fs_")}))
def test_off_character_her_cards_never_throw(cid):
    st = make_state(enemies=[make_enemy(hp=300)])
    st.player.character_id = "klee"
    st.in_player_turn = True
    effects.resolve_card(st, _row(cid))
    assert st.player.hp == 80
