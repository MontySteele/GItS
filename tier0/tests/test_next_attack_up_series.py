"""`next_attack_up` is POPPED, and the pop is the whole behaviour.

Audit sec.4 item 2: unpinned on both sides. The load-bearing distinction —
`.pop()` for this power, `.get()` for its siblings in the same summation — is
stated in prose in three files and asserted in none, and the C# side of it
(`IsFirstInSeries`, not `IsLastInSeries`) is a one-token edit away from the
divergence the 2026-07-21 bug hunt found: Passion Overload (+4) -> Study Buddy
-> Kaeya dealt 18 in game where the sim dealt 14.

Both engines, because the defect had one shape on each side and the fix was
written twice.

The tier0 half is EXECUTABLE — the pop happens in `resolve_card`, so a real
series can be played and the payout counted. The C# half is source-text: the
divergence lives in `CardPlay.IsFirstInSeries` inside a compiled Godot run,
where there is nothing for the simulator to execute.

The line both engines draw, stated once so neither can drift from it alone:

    A SERIES is the replay loop     — N separate resolutions of one card
                                      (tier0 OneTwoPunch / Study Buddy;
                                      C# CardPlay series). Bonus pays ONCE.
    A TAIL is `repeat_this`         — one resolution re-running its own
                                      effects after `current_attack_bonus` is
                                      already snapshotted. Bonus rides EVERY
                                      repetition, and must.
"""

from __future__ import annotations

import re
from pathlib import Path

from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state

ROOT = Path(__file__).resolve().parents[2]
COMPANION_POWERS = (
    ROOT / "klee-mod" / "KleeCode" / "Powers" / "CompanionPowers.cs"
).read_text(encoding="utf-8")

PROBE = "kaboom"          # klee common, single `damage` effect, no riders


def _damage_dealt(before, after):
    return before - after


def _play(st, card):
    """Play a card through the real `combat.play_card`, not `resolve_card`.

    The series semantics under test live in `play_card`'s replay loop, so
    these tests must not shortcut to `resolve_card` the way a per-effect test
    would -- that is precisely the layer where the bonus is popped once.
    `play_card` expects the card in hand and the energy to pay for it.
    """
    st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 9)
    combat.play_card(st, card)


# --- tier0: the pop ------------------------------------------------------

def test_bonus_pays_once_across_a_replay_series():
    """OneTwoPunch plays one attack twice. The buff covers the first only.

    This is the sim-14 side of the sim-14/game-18 divergence, made
    executable: `combat.play_card` issues N separate `resolve_card` calls and
    the pop lands on the first, so replay #2 sees nothing.
    """
    card = loader.get_card(PROBE)
    base = card.effects[0]["amount"]

    st = make_state(enemies=[make_enemy(hp=500)])
    st.player.powers["next_attack_up"] = 4
    st.player.powers["one_two_punch"] = 1
    hp0 = st.enemies[0].hp
    _play(st, card)
    dealt = _damage_dealt(hp0, st.enemies[0].hp)

    # Two resolutions; the +4 rode exactly one of them.
    assert dealt == base * 2 + 4, (
        f"expected {base}+4 then {base}, got {dealt} total -- the bonus rode "
        "more than the first play of the series")
    assert "next_attack_up" not in st.player.powers or \
        st.player.powers["next_attack_up"] == 0


def test_the_pop_is_what_ends_it_not_the_turn():
    """Two separate attack plays: the second is unbuffed, same turn."""
    card = loader.get_card(PROBE)
    base = card.effects[0]["amount"]

    st = make_state(enemies=[make_enemy(hp=500)])
    st.player.powers["next_attack_up"] = 4

    hp0 = st.enemies[0].hp
    _play(st, card)
    first = _damage_dealt(hp0, st.enemies[0].hp)

    hp1 = st.enemies[0].hp
    _play(st, card)
    second = _damage_dealt(hp1, st.enemies[0].hp)

    assert first == base + 4
    assert second == base, "the buff survived its own consumption"


def test_siblings_in_the_same_sum_are_read_not_consumed():
    """The `.get()` half. This is what makes the pop load-bearing.

    `flat_attack_bonus` sums several flat riders; only `next_attack_up` is
    consumed at the call site. If a future edit "tidies" the summation by
    consuming all of them uniformly, this fails and the tidy is the defect.
    """
    card = loader.get_card(PROBE)
    base = card.effects[0]["amount"]

    st = make_state(enemies=[make_enemy(hp=500)])
    st.player.powers["next_attack_up"] = 4
    st.player.powers["attack_up_this_turn"] = 2

    hp0 = st.enemies[0].hp
    _play(st, card)
    assert _damage_dealt(hp0, st.enemies[0].hp) == base + 4 + 2

    hp1 = st.enemies[0].hp
    _play(st, card)
    # The turn-window buff is still up; the next-attack buff is not.
    assert _damage_dealt(hp1, st.enemies[0].hp) == base + 2
    assert st.player.powers["attack_up_this_turn"] == 2


def test_zero_cost_rider_also_survives_the_pop():
    """Second sibling, second `.get()`: Spark Knight Style's zero-cost rider."""
    st = make_state(enemies=[make_enemy(hp=500)])
    free = Card(id="probe_free_attack", name="Probe", cost=0, type="attack",
                effects=[{"op": "damage", "amount": 5, "target": "enemy"}])
    st.player.powers["next_attack_up"] = 4
    st.player.powers["zero_cost_attacks_up"] = 3

    hp0 = st.enemies[0].hp
    _play(st, free)
    assert _damage_dealt(hp0, st.enemies[0].hp) == 5 + 4 + 3

    hp1 = st.enemies[0].hp
    _play(st, free)
    assert _damage_dealt(hp1, st.enemies[0].hp) == 5 + 3
    assert st.player.powers["zero_cost_attacks_up"] == 3


def test_the_repeat_tail_keeps_the_bonus():
    """The other side of the line, and the one a naive fix breaks.

    `repeat_this` re-runs `_resolve_effects` INSIDE one `resolve_card`, after
    `current_attack_bonus` has been snapshotted. So the tail keeps the bonus
    even though the power is already popped. A "fix" that moved the pop
    earlier, or re-read the power per effect, would silently change this.
    """
    st = make_state(enemies=[make_enemy(hp=500)])
    tail = Card(
        id="probe_repeat_attack", name="Probe", cost=1, type="attack",
        effects=[{"op": "damage", "amount": 5, "target": "enemy"},
                 {"op": "repeat_this", "times": 1}])
    st.player.powers["next_attack_up"] = 4

    hp0 = st.enemies[0].hp
    effects.resolve_card(st, tail)
    # Both the original resolution and its tail carry the +4.
    assert _damage_dealt(hp0, st.enemies[0].hp) == (5 + 4) * 2, \
        "the repeat tail lost the bonus the snapshot was supposed to hold"


# --- C#: IsFirstInSeries -------------------------------------------------

def _next_attack_up_after_card_played() -> str:
    """The body of NextAttackUpPower.AfterCardPlayed."""
    cls = COMPANION_POWERS.index("class NextAttackUpPower")
    end = COMPANION_POWERS.find("\npublic ", cls)
    body = COMPANION_POWERS[cls:end if end != -1 else len(COMPANION_POWERS)]
    hook = body.index("AfterCardPlayed")
    return body[hook:]


def test_csharp_consumes_on_the_first_play_of_the_series():
    body = _next_attack_up_after_card_played()
    assert "IsFirstInSeries" in body, (
        "NextAttackUpPower must remove itself on the FIRST play of a series; "
        "tier0's resolve_card pops the power and combat.py issues N separate "
        "resolve_card calls, so replay #2 must see nothing")
    assert "IsLastInSeries" not in body, (
        "IsLastInSeries is the pre-fix gate: it let the bonus ride every "
        "replay of a Study Buddy series -- Passion Overload (+4) -> Study "
        "Buddy -> Kaeya dealt 18 where the sim deals 14")


def test_csharp_pays_out_from_the_additive_phase():
    """The payout phase is parity too, not just the consumption phase.

    tier0 folds this into `flat_attack_bonus` BEFORE strength and vulnerable
    (`effects.py`: 'flat, folded in before strength/vulnerable'), which is
    the additive phase on this side. Moving it to the multiplicative phase
    would make the buff scale with Vulnerable, which the sim never does.
    """
    cls = COMPANION_POWERS.index("class NextAttackUpPower")
    end = COMPANION_POWERS.find("\nclass ", cls)
    body = COMPANION_POWERS[cls:end if end != -1 else len(COMPANION_POWERS)]
    assert re.search(r"override\s+decimal\s+ModifyDamageAdditive\s*\(", body)
    assert not re.search(
        r"override\s+decimal\s+ModifyDamageMultiplicative\s*\(", body)


def test_csharp_payout_is_gated_to_attack_cards():
    """tier0's `flat_attack_bonus` returns 0 for any non-attack card."""
    cls = COMPANION_POWERS.index("class NextAttackUpPower")
    end = COMPANION_POWERS.find("\nclass ", cls)
    body = COMPANION_POWERS[cls:end if end != -1 else len(COMPANION_POWERS)]
    assert "CardType.Attack" in body
