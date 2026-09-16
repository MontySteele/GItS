"""`EB-693`: Sango Isshin's quarter-of-Max-HP hit is ATTACK damage, one kind,
in both engines.

WHAT THE SEAT SAW (Kokomi r29, lane 1 (c)). The quarter hit took her Strength
-- 22 where the face said 20 -- and did NOT take the Effigy's Slow, while
Strike and Feint took that same Slow on the next turn. One seat, one turn
apart, two hits obeying two different rule sets, off a card whose own type is
`Attack`.

WHY. The C# now-line went out through `ElementalHit.Deal`, which is the
UNPOWERED door: it hand-rolls the dealer's Strength and the target's
Vulnerable and then reaches `CreatureCmd.Damage` as `ValueProp.Unpowered` with
`dealer: null`. Every game power that answers an ATTACK -- Slow included --
gates on `props.IsPoweredAttack()` and is therefore skipped by construction.
That door is right for a Bomb and for a Plan carry-out, where the rule IS that
the hit is nobody's attack; it is wrong for an Attack card's own damage.

THE D DEFAULT, APPLIED (the row's Next action, at its stated default): it is
Attack damage with ALL modifiers -- Strength AND Slow, Weak and Vulnerable --
in both engines, because the face calls itself an Attack and nothing on the
card asks for an exception.

WHAT MOVED. The C# only. The sim was already the default:
`effects._op_damage_quarter_max_hp` deals the quarter with
`source="attack" if card.type == "attack"`, and Sango Isshin is an attack -- so
this file is the PARITY read that says the two engines now answer the same
question the same way, plus the behavioural half the sim can actually run.

THE PLANNED HALF IS UNTOUCHED and that is the point of the last test here: a
Plan's carry-out is the jellyfish's and not hers (`EB-334`, R246 pick 1), so it
keeps the unpowered door and the `Plan` keyword goes on printing that rule.
One card, two clauses, two rules, both printed where they are read.

NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

from pathlib import Path

from tier0.content import loader
from tier0.engine import effects
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import (  # noqa: F401
    carry_out, kokomi_state, overhaul)

REPO = Path(__file__).resolve().parents[2]
MOD = REPO / "klee-mod" / "KleeCode"

SANGO = "proto_kk_sango_isshin"


def _quarter_board(strength: int = 0, vulnerable: int = 0):
    """A board where the quarter is 20 (Max HP 80) and one enemy is alive."""
    enemy = make_enemy(hp=200)
    if vulnerable:
        enemy.powers["vulnerable"] = vulnerable
    state = kokomi_state(enemies=[enemy], hp=80)
    if strength:
        state.player.powers["strength"] = strength
    carry_out(state, [{"op": "draw", "amount": 1}])   # arms the branch
    assert state.kk_plan_carried_out_this_turn is True
    return state, enemy


def test_the_quarter_hit_takes_her_strength(overhaul):
    """Half one of the seat's read, and this half was already true: 20 + 2."""
    state, enemy = _quarter_board(strength=2)
    before = enemy.hp
    effects.resolve_card(state, loader.get_card(SANGO))
    assert before - enemy.hp == 22


def test_the_quarter_hit_takes_the_targets_terms_too(overhaul):
    """Half two, and the half the C# door was skipping. `Slow` is a base-game
    power this engine does not model, so the readable twin of "the target's
    side counts" is Vulnerable -- the same phase of the same pipeline, reached
    through the same `source="attack"`, and the one the sim can run."""
    state, enemy = _quarter_board(vulnerable=1)
    before = enemy.hp
    effects.resolve_card(state, loader.get_card(SANGO))
    assert before - enemy.hp == 30                  # 20 x 1.5


def test_the_quarter_is_the_same_kind_of_damage_as_the_cards_floor(overhaul):
    """ONE DAMAGE KIND, which is the row's acceptance sentence. The card's
    floor (`Deal 8`) and its payoff go through one pipeline, so a term that
    moves one moves the other by the same rule -- here Vulnerable, x1.5 on
    both."""
    state, enemy = _quarter_board(vulnerable=1)
    floor_state = kokomi_state(enemies=[enemy], hp=80)
    floor_state.player.powers.clear()
    assert floor_state.kk_plan_carried_out_this_turn is False

    before = enemy.hp
    effects.resolve_card(floor_state, loader.get_card(SANGO))
    floor = before - enemy.hp
    assert floor == 12                              # 8 x 1.5

    before = enemy.hp
    effects.resolve_card(state, loader.get_card(SANGO))
    assert (before - enemy.hp) / floor == 30 / 12


def test_the_csharp_now_line_goes_through_the_attack_builder():
    """THE C# HALF, read the only way this suite can read it. A number in the
    mod needs a live `CombatState` (KleeTests/README.md, the headless
    boundary), so what is pinned is WHICH DOOR the call site takes -- the same
    discipline `ElementalHit.DealWithoutDealerMods` exists to make pinnable.

    `DamageCmd.Attack` is the powered door: it carries `ValueProp.Move`, so
    Slow, Weak, Strength and Vulnerable all answer it, and the element still
    lands because `KleeElementalHooks.BeforeDamageReceived` applies the aura
    for any powered hit whose `cardSource` is an `IElementalCard`.
    """
    src = (MOD / "Powers" / "Prototype" / "ProtoBakeKuragePower.cs").read_text(
        encoding="utf-8")
    body = src[src.index("public static async Task QuarterMaxHp("):
               src.index("// ---- the Mend rule")]
    assert body.count("DamageCmd.Attack(amount)") == 2
    assert "ElementalHit.Deal(" not in body
    # Both clauses take the card and the play: `DamageCmd.Attack` needs a
    # source for the element and for every power that answers an attack.
    assert body.count(".FromCard(card, cardPlay)") == 2


def test_the_emitted_card_hands_the_call_its_card_and_play():
    """The generator's twin of the line above, on the one row that prints the
    op. A signature that grew a parameter the emitter did not pass would
    compile nowhere, but a row that stopped printing the op at all would take
    the pin with it silently -- so the card is named."""
    card = (MOD / "Cards" / "Prototype" / "Generated"
            / "ProtoKkSangoIsshin.cs").read_text(encoding="utf-8")
    assert "KokomiRules.QuarterMaxHpAll(choiceContext, Owner.Creature, " \
           "this, cardPlay)" in card


def test_the_planned_half_keeps_the_unpowered_rule(overhaul):
    """AND THE OTHER CLAUSE DID NOT MOVE. A Plan's carry-out is dealt by the
    Bake-Kurage (`EB-334`, R246 pick 1), so it folds HER terms at writing time
    and nothing of the target's at the morning -- which is exactly what the
    `Plan` keyword prints and what a seat commits a turn against.

    Read here as the contrast the row is about: the same quarter, carried out
    as a Plan, does NOT take the Strength standing on her at the morning -- the
    now-line above does, because the now-line is her own Attack. (The target's
    Vulnerable still multiplies a carry-out: `powered=False` drops the DEALER's
    side and nothing else, which is `deal_damage_to_enemy`'s own rule.)
    """
    enemy = make_enemy(hp=200)
    state = kokomi_state(enemies=[enemy], hp=80)
    state.player.powers["strength"] = 2
    before = enemy.hp
    carry_out(state, [{"op": "damage_quarter_max_hp", "target": "all_enemies"}])
    assert before - enemy.hp == 20                  # not 22

    # And her own now-line on the same board does.
    armed = kokomi_state(enemies=[enemy], hp=80)
    armed.player.powers["strength"] = 2
    carry_out(armed, [{"op": "draw", "amount": 1}])
    before = enemy.hp
    effects.resolve_card(armed, loader.get_card(SANGO))
    assert before - enemy.hp == 22
