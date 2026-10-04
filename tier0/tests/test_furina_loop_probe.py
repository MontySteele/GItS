"""Furina's infinite-loop probe (`tier0/harness/furina_loop_probe.py`).

The 2026-10-04 loop audit. Two loops were found by review and fixed on the
sheet (`docs/prototype-surface.yaml`):

* Take the Stage+ cost 0 ("Summon a random Salon member. Draw 1 card."): two
  copies drew each other forever, a Bow (+1 Fanfare) on every play onto a
  full stage. Fixed: it stays at 1 Energy and draws 2 upgraded.
* Warm Reception (1: gain 3 Fanfare, draw 1) and Interval Bell+ (0: Spend 2,
  draw 1, gain 1 Energy) paid for each other at +1 Fanfare a pass. Fixed: the
  Spend mode's Energy comes next turn (Chevreuse's mechanism).

The probe must see both with the fixes taken out (`pre_fix=True`), and must
see neither with them in. The full post-fix sweep's productive loops are
pinned by name (`KNOWN_OPEN`): reported to the main session, not fixed here,
so a new one fails this file and a fix moves the pin.
"""

from __future__ import annotations

import pytest

from tier0.engine import furina_stage as FS
from tier0.harness import furina_loop_probe as P

TAKE_THE_STAGE_UP = ("proto_fs_salon_debut+",)
BELL_AND_RECEPTION = ("proto_fs_interval_bell+", "proto_fs_warm_reception")


def _try(combo, pre_fix, palais=False, power=None):
    return P.try_combo(P.variants(pre_fix), tuple(sorted(combo)), power,
                       palais)


# ---------------------------------------------------------------------------
# The probe catches both known loops with the fixes taken out.
# ---------------------------------------------------------------------------

def test_pre_fix_take_the_stage_plus_is_a_productive_loop():
    hit = _try(TAKE_THE_STAGE_UP, pre_fix=True)
    assert hit is not None and hit.productive
    assert hit.growth["fanfare"] > 0 and hit.growth["energy"] >= 0


def test_pre_fix_warm_reception_and_interval_bell_plus_loop():
    hit = _try(BELL_AND_RECEPTION, pre_fix=True)
    assert hit is not None and hit.productive
    assert hit.growth["fanfare"] > 0 and hit.growth["energy"] >= 0


def test_the_pre_fix_sweep_finds_both_in_a_narrowed_pool():
    only = TAKE_THE_STAGE_UP + BELL_AND_RECEPTION + (
        "proto_fs_salon_debut", "proto_fs_interval_bell",
        "proto_fs_warm_reception+")
    found = P.search(pre_fix=True, powers=[None], only=only)
    productive = {f.cards for f in found if f.productive}
    assert TAKE_THE_STAGE_UP in productive
    assert tuple(sorted(BELL_AND_RECEPTION)) in productive


# ---------------------------------------------------------------------------
# With the fixes in, neither loops (with or without Palais Ledger).
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("palais", [False, True])
def test_take_the_stage_plus_no_longer_loops(palais):
    pool = P.variants(False)
    card = pool["proto_fs_salon_debut+"]
    assert card.cost == 1
    assert [fx["amount"] for fx in card.effects if fx["op"] == "draw"] == [2]
    assert _try(TAKE_THE_STAGE_UP, pre_fix=False, palais=palais) is None


@pytest.mark.parametrize("palais", [False, True])
def test_warm_reception_and_interval_bell_plus_no_longer_loop(palais):
    hit = _try(BELL_AND_RECEPTION, pre_fix=False, palais=palais)
    # Interval Bell+'s draw mode still cycles two copies of itself (inert,
    # pinned below); Warm Reception can no longer ride it.
    assert hit is None or not hit.productive


def test_interval_bells_energy_is_owed_not_paid():
    st = P._state((), {}, 0)
    st.player.hand = [P.variants(False)["proto_fs_interval_bell+"]]
    st.player.discard_pile = [P.variants(False)["proto_fs_warm_reception"]]
    st.player.stage_decider = P.Decider(spend=True)
    from tier0.engine import combat
    combat.play_card(st, st.player.hand[0])
    assert st.player.energy == P.START_ENERGY
    assert st.player.stage_energy_next == 1
    assert st.player.stage_fanfare == P.START_FANFARE - 2
    FS.turn_start(st)
    assert st.player.energy == P.START_ENERGY + 1


# ---------------------------------------------------------------------------
# The static screen is only a necessary condition: it must pass every loop.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("combo,pre_fix", [
    (TAKE_THE_STAGE_UP, True), (BELL_AND_RECEPTION, True),
    (("proto_fs_oratrices_verdict+",), False),
    (("proto_fs_interval_bell",), False)])
def test_the_screen_passes_every_loop_found(combo, pre_fix):
    pool = P.variants(pre_fix)
    assert P.could_cycle([P.profile(pool[c]) for c in combo], {}, False)


# ---------------------------------------------------------------------------
# The post-fix sweep, no Power and no relic: the inert cycles, and the open
# productive loops reported (not fixed) on 2026-10-04.
# ---------------------------------------------------------------------------

#: Inert cycles: 0-cost card-draw that refills the hand and does nothing.
KNOWN_INERT = {
    ("proto_fs_interval_bell",), ("proto_fs_interval_bell+",),
    ("proto_fs_oratrices_verdict",), ("proto_fs_oratrices_verdict+",),
}

#: Oratrice's Verdict+ (0: draw 2) x2 carries any 0-cost card forever.
VERDICT_UP = "proto_fs_oratrices_verdict+"
VERDICT_PAYLOADS = {
    "proto_fs_bis+", "proto_fs_guest_star_charlotte+",
    "proto_fs_guest_star_chevreuse+", "proto_fs_guest_star_lynette+",
    "proto_fs_guest_star_sigewinne+", "proto_fs_guest_star_wriothesley+",
    "proto_fs_quick_cue", "proto_fs_quick_cue+", "proto_fs_step_forward",
    "proto_fs_step_forward+", "proto_fs_surintendante_chevalmarin+",
    "proto_fs_the_last_act", "proto_fs_the_last_act+",
    "proto_fs_warmup_act", "proto_fs_warmup_act+",
}
KNOWN_OPEN = {tuple(sorted((VERDICT_UP, p))) for p in VERDICT_PAYLOADS}


@pytest.mark.battery
def test_the_post_fix_sweep_finds_only_the_known_cycles():
    # No Power, no relic (the full sweep over every Power and Palais Ledger
    # is the CLI's, minutes long; its findings are in the 2026-10-04 report).
    found = P.search_env(False, None, False)
    productive = {f.cards for f in found if f.productive}
    inert = {f.cards for f in found if not f.productive}
    assert productive == KNOWN_OPEN
    assert inert == KNOWN_INERT
    # Neither fixed loop is among them.
    assert TAKE_THE_STAGE_UP not in productive
    assert tuple(sorted(BELL_AND_RECEPTION)) not in productive
