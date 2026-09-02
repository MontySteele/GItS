"""EB-256: an unwinnable-AND-unloseable fight is now reportable.

THE DEFECT (playtest 2026-08-31 B4). A 0-cost mustered *Gorou - Forward Unto
Victory* stacks Metallicize 2 -- turn-start, Dex-exempt, never decaying -- at
+2 Block a turn against the Matriarch's +2 damage a turn, so from turn 16 she
deals 0 forever while her Strength drain floors the player's own damage at 0.
Nobody can win it and nobody can lose it. The turn cap stopped it running
forever, and then filed it as a LOSS, which is the wrong word for a fight that
could not be lost -- and no instrument anywhere in either engine could say
that a fight had ended for that reason rather than any other.

WHAT LANDED. `combat._stall_fingerprint` samples, at every round end,
everything a fight can make progress ON: HP and Block on both sides, and the
deck. `combat.STALL_ROUNDS` (10) consecutive BYTE-IDENTICAL samples end the
fight as a recorded stall -- `CombatState.stalled`, a `fight_stall` event, a
`stalled=` key on `fight_end`, and `tier05.model.RunResult.outcome` reading
`"stalled"` instead of `"died"`.

WHAT DELIBERATELY DID NOT MOVE, and it is half the row. `fight_end.won` is
untouched, `RunResult.won` is untouched, and a stalled run still exits through
the same death door at the same node. A stall was already a not-won fight
before the detector existed; re-lettering it would be a measurement change
made under an engineering row, and no shipped run has ever reached this branch
anyway (`review/records/` carries no `fight_stall` and no MAX_TURNS fight).
So the third word is ADDED beside the two that were there, never swapped in.

THE FALSE-POSITIVE SIDE IS THE ONE THAT COULD COST SOMETHING. A detector that
fired on a slow fight would silently truncate real combats and move every
table in the repo. Two things keep it from doing that: the fingerprint has to
repeat exactly, on every quantity at once, for a third of the fight's whole
clock -- and the sweep at the bottom of this file runs the real encounters and
asserts it never fires.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat
from tier0.engine.state import Card, CombatState, Enemy, Player
from tier0.tests.conftest import make_enemy


def _pass_pilot(state):
    """A pilot that never plays. The stalls below are constructed from a deck
    that cannot act, so this is the honest partner for them."""
    return None


def _deadlocked_fight(metallicize: int = 4, enemy_hit: int = 4,
                      enemy_hp: int = 9999) -> CombatState:
    """The B4 shape, reduced to its two moving parts and then frozen.

    The player gains exactly as much Block at turn start as the enemy removes
    on its turn, and deals no damage because it has no cards -- the sim's
    cheapest spelling of "Strength drained to the floor". Nobody's HP moves,
    nobody's Block survives the round, and the deck is empty, so the round is
    byte-identical to the one before it, forever.
    """
    player = Player(hp=80, max_hp=80)
    player.powers["metallicize"] = metallicize
    enemy = Enemy(hp=enemy_hp, max_hp=enemy_hp, name="matriarch_like",
                  intents=[{"kind": "attack", "amount": enemy_hit}])
    return combat.run_fight(player, [enemy], _pass_pilot, seed=7)


def test_the_deadlock_ends_as_a_stall_and_not_at_the_turn_cap():
    st = _deadlocked_fight()
    assert st.stalled is True
    assert st.turn < C.MAX_TURNS, (
        "the detector must be reachable BEFORE the turn cap, or it reports "
        "a stall nobody can act on")


def test_the_stall_fires_at_exactly_stall_rounds_of_no_progress():
    """`STALL_ROUNDS` consecutive REPEATS, so the fight runs one round to
    establish the fingerprint and `STALL_ROUNDS` more to repeat it."""
    st = _deadlocked_fight()
    assert st.turn == combat.STALL_ROUNDS + 1


def test_the_stall_is_recorded_as_its_own_event():
    st = _deadlocked_fight()
    stalls = [ev for ev in st.log if ev["event"] == "fight_stall"]
    assert len(stalls) == 1
    assert stalls[0]["rounds"] == combat.STALL_ROUNDS + 1
    assert stalls[0]["enemies_alive"] == 1
    assert stalls[0]["hp"] == 80          # the fight never scratched anyone


def test_the_stall_is_neither_a_win_nor_a_loss_but_still_reads_not_won():
    """Both halves of the ruling in one case. `fight_stall` is the new word;
    `won` is the old one and it did not move, so a reader that predates this
    row reads a stall exactly as it read one before."""
    st = _deadlocked_fight()
    end = st.log[-1]
    assert end["event"] == "fight_end"
    assert end["won"] is False            # untouched
    assert st.stalled is True             # the new word, on the state
    assert st.player.alive and st.living_enemies   # nobody won it


def test_fight_end_grew_no_key():
    """The log of a fight that does not stall is byte-identical to what it
    was before this row. Two acceptance digests pin whole logs
    (`test_klee_overhaul`, `test_spark_alt_cost`) so that an instrument
    change cannot pass itself off as no change -- so the stall's record is
    its OWN event and `fight_end` is untouched. A stalled fight is the only
    fight whose log grows, and it grows by one row nothing had before."""
    quiet = combat.run_fight(loader.build_player("klee"),
                             [make_enemy(hp=60)], _greedy_pilot, seed=3)
    assert set(quiet.log[-1]) == {"turn", "event", "won", "turns", "hp_left"}
    stalled = _deadlocked_fight()
    assert set(stalled.log[-1]) == {"turn", "event", "won", "turns",
                                    "hp_left"}
    assert [ev["event"] for ev in quiet.log].count("fight_stall") == 0


def test_the_detector_is_not_a_dead_enemy_test():
    """A corpse must not mask a living body: the fingerprint carries every
    enemy, alive or not. Two enemies, one already dead, and the stall is
    still read off the one that is still standing."""
    player = Player(hp=80, max_hp=80)
    player.powers["metallicize"] = 4
    dead = Enemy(hp=0, max_hp=10, name="corpse",
                 intents=[{"kind": "attack", "amount": 40}])
    alive = Enemy(hp=9999, max_hp=9999, name="wall",
                  intents=[{"kind": "attack", "amount": 4}])
    st = combat.run_fight(player, [dead, alive], _pass_pilot, seed=7)
    assert st.stalled is True


# --- the false-positive side -------------------------------------------


def test_a_fight_that_makes_progress_never_stalls():
    """The plain case: one side is losing HP every round, so no two rounds
    can carry the same fingerprint."""
    player = loader.build_player("klee")
    st = combat.run_fight(player, [make_enemy(hp=60)],
                          _greedy_pilot, seed=3)
    assert st.stalled is False
    assert not [ev for ev in st.log if ev["event"] == "fight_stall"]


def test_a_fight_where_only_the_deck_moves_never_stalls():
    """The subtle case, and the reason the deck is in the fingerprint at all.
    Neither side's HP or Block changes -- the enemy sleeps and the player
    deals nothing -- but the draw pile empties into the discard, so the fight
    is still going somewhere and must not be cut."""
    player = Player(hp=80, max_hp=80)
    player.draw_pile = [Card(id=f"filler_{i}", name="filler", cost=0,
                             type="skill", rarity="basic", effects=[])
                        for i in range(40)]
    enemy = Enemy(hp=9999, max_hp=9999, name="sleeper",
                  intents=[{"kind": "block", "amount": 0}])
    st = combat.run_fight(player, [enemy], _pass_pilot, seed=1)
    assert st.turn == C.MAX_TURNS          # ran to the cap, as it always did
    assert st.stalled is False


@pytest.mark.parametrize("encounter_id", sorted(loader.encounter_ids()))
@pytest.mark.parametrize("character", ["klee", "furina", "kokomi"])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_the_detector_never_fires_on_a_real_encounter(
        encounter_id, character, seed):
    """The claim the rest of the repo's numbers rest on: the whole frozen
    battery, three characters, three seeds. If this ever goes red, a shipped
    table has been truncated and the row that did it is this one -- which is
    why the sweep lives beside the detector rather than in a scratch run
    nobody re-runs."""
    # A sequence encounter is several fights; each stage is one, and each one
    # is what the detector sees.
    try:
        stages = [loader.build_encounter(encounter_id)]
    except ValueError:
        stages = [loader.build_encounter(s)
                  for s in loader.encounter_stages(encounter_id)]
    for enemies in stages:
        player = loader.build_player(character)
        st = combat.run_fight(player, enemies, _greedy_pilot, seed=seed)
        assert st.stalled is False
        assert not [ev for ev in st.log if ev["event"] == "fight_stall"]


def _greedy_pilot(state):
    """The smallest real pilot: play the first playable card, else pass.
    Enough to make a fight move, and it keeps this file independent of the
    weighted pilot's versioned weights."""
    for card in state.player.hand:
        if combat.card_playable(state, card):
            return card
    return None


# --- the tier-0.5 half --------------------------------------------------


def test_the_run_result_outcome_kind():
    """`RunResult.outcome` is the third word. `won` and `death_node` keep
    their exact meanings, which is what keeps every published run table
    valid."""
    from tier05.model import RunResult

    def _res(**kw):
        base = dict(seed=0, won=False, death_node=None, hp_by_node=[],
                    deck_ids=[], node_kinds=[])
        base.update(kw)
        return RunResult(**base)

    assert _res(won=True).outcome == "won"
    assert _res(death_node=4).outcome == "died"
    assert _res(death_node=4, stall_node=4).outcome == "stalled"
    # A stalled run is STILL not won and STILL exits at its node, so nothing
    # that reads only the old two fields sees a different number.
    assert _res(death_node=4, stall_node=4).won is False


def test_the_runner_files_the_stall_node(monkeypatch):
    """`resolve_fight` reads `CombatState.stalled` off the fight it just ran
    and files the node. Patched through the module seam `RunState` documents
    (`run_fight` is called unqualified precisely so the suite can do this)."""
    from tier05 import model

    real = model.run_fight

    def stalling_run_fight(player, enemies, pilot, seed):
        st = real(player, enemies, pilot, seed)
        st.stalled = True
        for e in st.enemies:               # nobody won it
            e.hp = max(e.hp, 1)
        st.player.hp = max(st.player.hp, 1)
        return st

    def _no_draft(rng, deck, offers, archetype):
        return None

    monkeypatch.setattr(model, "run_fight", stalling_run_fight)
    res = model.run_one("klee", "demolition", "demolition", _no_draft, 11)
    assert res.won is False
    assert res.stall_node is not None
    assert res.death_node == res.stall_node
    assert res.outcome == "stalled"
