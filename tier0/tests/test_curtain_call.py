"""Curtain Call sweep (R85): engine pins for the Track B power conversions
and the Track C vocabulary additions.

Five skills became Powers under the §4 quota, each on an ACTIVITY trigger
(the sheet header's no-passive-accrual law: a silent turn pays nothing):

  salon_deploy_block   Fortissimo Guard -- block per member DEPLOY event
  salon_bow_block/_encore  Stagehands -- payout per member FINAL BOW
  encore_spend_draw    The Gallery Stirs -- first Encore SPEND each turn
  first_attack_draw    Quick Change -- first ATTACK play each turn
  cross_examination    Courtroom Drama -- first REACTION each turn

Plus the Track C read grammar: bonus_formula N_per_M_encore (Body Slam is
the StS precedent -- an attack priced off a defensive pool, READ only).
"""

import random

from tier0.content import loader
from tier0.engine import combat, effects, reactions, resources
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy


def furina_state(enemies=None, seed=0):
    p = loader.build_player("furina")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def _card(**kw):
    d = dict(id="cc_test", name="t", cost=0, type="skill",
             character="furina")
    d.update(kw)
    return Card(**d)


# --- the five conversions are on the sheet as Powers ---

def test_the_five_conversions_are_powers_on_the_sheet():
    for cid in ("fortissimo_guard", "pit_orchestra", "courtroom_drama",
                "crowd_work", "quick_change"):
        c = loader.get_card(cid)
        assert c.type == "power", cid
        # Every one has a PERSISTING body -- that is what made the conversion
        # from skill to Power meaningful. Asserted as "at least one
        # apply_power" rather than "nothing but apply_power": the Fanfare
        # rework (Track B, 2026-07-28) added a printed `raise_fanfare_cap`
        # line to courtroom_drama and crowd_work, replacing the invisible
        # floor grant every Power used to receive. A one-shot line beside a
        # persisting one does not make the card stop persisting, and the
        # stricter form would have blocked exactly the change that makes
        # these Powers' Fanfare value visible.
        assert any(fx["op"] == "apply_power" for fx in c.effects), cid
        assert all(fx["op"] in ("apply_power", "raise_fanfare_cap")
                   for fx in c.effects), cid


def test_salon_deploy_block_pays_per_deploy_event():
    st = furina_state()
    p = st.player
    p.powers["salon_deploy_block"] = 5
    effects.resolve_card(st, _card(effects=[
        {"op": "apply_power", "power": "salon_member", "amount": 1,
         "target": "self", "member": "usher"}]))
    assert p.block == 5
    # a triple deploy (Full Ensemble) is three cues -- fresh empty stage so
    # no displaced member's own bow block muddies the count
    st2 = furina_state()
    st2.player.powers["salon_deploy_block"] = 5
    effects.resolve_card(st2, loader.get_card("full_ensemble"))
    assert st2.player.block == 15


def test_stagehands_pay_on_the_final_bow_not_the_deploy():
    st = furina_state()
    p = st.player
    p.powers["salon_bow_block"] = 5
    p.powers["salon_bow_encore"] = 2
    deploy = _card(effects=[
        {"op": "apply_power", "power": "salon_member", "amount": 1,
         "target": "self", "member": "usher"}])
    from tier0 import constants as C
    for _ in range(C.SALON_MEMBER_SLOTS):        # fill the stage: no bows yet
        effects.resolve_card(st, deploy)
    assert p.block == 0 and p.encore == 0
    effects.resolve_card(st, deploy)             # displaces the oldest: 1 bow
    # the usher's own bow block ALSO lands; the power's share is exactly 5,
    # so assert the delta against a control state without the power
    ctrl = furina_state()
    for _ in range(C.SALON_MEMBER_SLOTS + 1):
        effects.resolve_card(ctrl, deploy)
    assert p.block == ctrl.player.block + 5
    assert p.encore == ctrl.player.encore + 2


def test_gallery_stirs_draws_on_first_spend_only():
    st = furina_state()
    p = st.player
    st.encore_spend_draws_this_turn = 0
    p.powers["encore_spend_draw"] = 1
    p.encore = 10
    p.draw_pile.extend(_card(id=f"filler{i}") for i in range(5))
    before = len(p.hand)
    resources.spend_encore(st, 2)
    assert len(p.hand) == before + 1             # first spend: draw 1
    resources.spend_encore(st, 2)
    assert len(p.hand) == before + 1             # second spend: latched
    # dry spend moves no Encore and must not draw
    st2 = furina_state()
    st2.encore_spend_draws_this_turn = 0
    st2.player.powers["encore_spend_draw"] = 1
    st2.player.draw_pile.append(_card(id="filler"))
    h2 = len(st2.player.hand)
    resources.spend_encore(st2, 3)               # encore is 0: nothing spent
    assert len(st2.player.hand) == h2


def test_quick_change_draws_on_first_attack_only():
    st = furina_state()
    p = st.player
    p.powers["first_attack_draw"] = 1
    p.draw_pile.extend(_card(id=f"filler{i}") for i in range(5))
    st.attacks_played_this_turn = 0
    swing = _card(type="attack", effects=[{"op": "damage", "amount": 3}])
    p.hand.append(swing)
    p.energy = 3
    before = len(p.hand)                         # includes the swing
    combat.play_card(st, swing)
    # played card left hand (-1), first-attack draw came in (+1)
    assert len(p.hand) == before
    swing2 = _card(id="cc_test2", type="attack",
                   effects=[{"op": "damage", "amount": 3}])
    p.hand.append(swing2)
    before = len(p.hand)
    combat.play_card(st, swing2)
    assert len(p.hand) == before - 1             # second attack: no draw


def test_cross_examination_debuffs_first_reaction_target_once():
    st = furina_state()
    p = st.player
    p.powers["cross_examination"] = 1
    e = st.enemies[0]
    st.reactions_this_turn = 0
    reactions.apply_aura(st, e, "hydro")
    reactions.resolve_hit(st, e, "pyro", 5)      # vaporize: first reaction
    assert e.powers.get("vulnerable", 0) >= 1
    assert e.powers.get("weak", 0) >= 1
    v, w = e.powers["vulnerable"], e.powers["weak"]
    reactions.apply_aura(st, e, "hydro")
    reactions.resolve_hit(st, e, "pyro", 5)      # second reaction: latched
    assert e.powers["vulnerable"] == v and e.powers["weak"] == w


def test_poised_riposte_reads_the_buffer_and_never_spends_it():
    st = furina_state()
    p = st.player
    p.encore = 9
    e = st.enemies[0]
    hp = e.hp
    effects.resolve_card(st, loader.get_card("poised_riposte"))
    assert hp - e.hp == 6 + 9 // 3               # 6 printed + 1 per 3 held
    assert p.encore == 9                         # READ, never consumed
