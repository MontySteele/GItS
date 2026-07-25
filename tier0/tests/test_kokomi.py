"""Kokomi kickoff roster v0.1: engine-level tests for Charge, Flawless
Strategy, Conscript, Sly, the prevention ward, and the Ceremonial Garment
state (docs/kokomi-kickoff-v1.md; these lock the SYSTEMS — statline work
waits on the ruling asks; every constant is PROPOSED).
"""

import random

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, effects, powers, refpowers
from tier0.engine.state import Card, CombatState
from tier0.pilot.policy import make_pilot
from tier0.tests.conftest import make_enemy

NULL_PILOT = lambda s: None


def kokomi_state(enemies=None, seed=0):
    p = loader.build_player("kokomi")
    return CombatState(player=p, enemies=enemies or [make_enemy(hp=300)],
                       rng=random.Random(seed))


def kokomi_card(**kw):
    d = dict(id="kokomi_test", name="t", cost=0, type="skill",
             character="kokomi")
    d.update(kw)
    return Card(**d)


# --- character spec ---

def test_build_kokomi_skeleton():
    p = loader.build_player("kokomi")
    assert p.character_id == "kokomi" and p.element == "hydro"
    assert p.cadence == "catalyst"
    assert p.burst_max == 20 and p.charge == 0   # v0.4 O4: a real Burst
                                                 # again (v0.3's fast-cycle
                                                 # 10 is the floor
                                                 # comparator, not the arm)
    assert "tamakushi_casket" in p.relic_hooks
    assert [k.id for k in p.kit_cards] == ["ceremonial_garment"]
    assert loader.character_nation("kokomi") == "inazuma"
    assert p.fanfare_cap == 0                # no Furina resources


def test_garment_kit_amount_matches_constant():
    """The sheet's printed state duration and the constant must agree —
    the kit/sheet cross-check pattern (drift guard)."""
    kit = loader.get_card("ceremonial_garment")
    (state_fx,) = [fx for fx in kit.effects
                   if fx.get("power") == "ceremonial_garment"]
    assert state_fx["amount"] == C.CEREMONIAL_GARMENT_TURNS


def test_catalyst_cadence_applies_hydro_on_attacks():
    st = kokomi_state()
    effects.resolve_card(st, kokomi_card(
        type="attack", effects=[{"op": "damage", "amount": 4}]))
    assert st.enemies[0].aura == "hydro"


# --- Charge accrual (the ONE exhaust funnel) ---

def test_exhaust_funnel_gains_charge_and_burst():
    st = kokomi_state()
    p = st.player
    refpowers.exhaust_card(st, kokomi_card())
    assert p.charge == C.CHARGE_PER_EXHAUST
    assert p.burst_energy == C.KOKOMI_BURST_PER_EXHAUST
    assert any(ev["event"] == "gain_charge" and ev["source"] == "exhaust"
               for ev in st.log)


def test_played_exhaust_card_feeds_charge():
    """A played Exhaust card routes through result_pile -> exhaust_card:
    the universal rule needs no per-card text."""
    st = kokomi_state()
    card = kokomi_card(effects=[{"op": "block", "amount": 1}], exhaust=True)
    st.player.hand.append(card)
    st.player.energy = 3
    combat.play_card(st, card)
    assert st.player.charge == C.CHARGE_PER_EXHAUST


def test_mid_card_exhausts_feed_charge_via_sweep():
    """exhaust_from appends directly; the after_card_played sweep fires
    the funnel per victim — Charge must arrive exactly once each."""
    st = kokomi_state()
    st.player.hand = [kokomi_card(id="fodder_a"), kokomi_card(id="fodder_b")]
    burner = kokomi_card(
        id="burner", effects=[{"op": "exhaust_from", "amount": 2}])
    st.player.hand.append(burner)
    st.player.energy = 3
    combat.play_card(st, burner)
    assert st.player.charge == 2 * C.CHARGE_PER_EXHAUST


def test_no_charge_without_casket():
    """Universal accrual is gated on the relic hook: every other
    character's exhausts are a dead branch (anchor safety)."""
    p = loader.build_player("ref_ironclad")
    st = CombatState(player=p, enemies=[make_enemy(hp=50)],
                     rng=random.Random(0))
    refpowers.exhaust_card(st, kokomi_card())
    assert p.charge == 0


def test_gain_charge_op_is_additive_premium():
    st = kokomi_state()
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "gain_charge", "amount": 4}]))
    assert st.player.charge == 4


# --- Flawless Strategy (Strength -> Charge) ---

def test_strength_converts_to_charge():
    st = kokomi_state()
    powers.apply_power(st, st.player, "strength", 2)
    assert st.player.powers.get("strength", 0) == 0
    assert st.player.charge == 2
    assert any(ev["event"] == "strength_converted" for ev in st.log)


def test_negative_strength_still_applies():
    """Mangle-class Strength LOSS is not a gain and must land normally."""
    st = kokomi_state()
    powers.apply_power(st, st.player, "strength", -3)
    assert st.player.powers.get("strength", 0) == -3
    assert st.player.charge == 0


def test_enemy_strength_untouched():
    st = kokomi_state()
    e = st.enemies[0]
    powers.apply_power(st, e, "strength", 2)
    assert e.powers.get("strength", 0) == 2


def test_sara_stormcall_is_the_conversion_exerciser():
    """The one deliberate Strength card in the Inazuma pool: Charge in
    Kokomi's hands, real Strength for anyone else."""
    st = kokomi_state()
    effects.resolve_card(st, loader.get_card("sara_tengu_stormcall"))
    assert st.player.charge == 2
    assert st.player.powers.get("strength", 0) == 0


# --- Conscript ---

def test_conscript_transforms_worst_card_into_recruit():
    st = kokomi_state()
    st.player.hand = [kokomi_card(id="chaff", type="skill",
                                  effects=[{"op": "block", "amount": 1}])]
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "conscript", "amount": 1}]))
    (recruit,) = st.player.hand
    assert recruit.is_companion and recruit.nation == "inazuma"
    assert recruit.conscripted and recruit.exhaust
    base = loader.get_card(recruit.id)
    if isinstance(base.cost, int):
        assert recruit.cost == max(0, base.cost + C.CONSCRIPT_COST_DELTA)


def test_conscript_never_eats_kit_or_companions():
    st = kokomi_state()
    kit = st.player.kit_cards[0]
    recruit_already = loader.get_card("gorou_war_banner")
    st.player.hand = [kit, recruit_already]
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "conscript", "amount": 1}]))
    assert any(ev["event"] == "conscript_whiffed" for ev in st.log)
    assert st.player.hand == [kit, recruit_already]


def test_conscript_create_mode_adds_to_hand():
    st = kokomi_state()
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "conscript", "amount": 2, "mode": "create"}]))
    assert len(st.player.hand) == 2
    assert all(c.conscripted and c.exhaust for c in st.player.hand)
    assert st.cards_created_this_turn == 2


def test_conscripted_companion_is_self_sourced_for_provenance():
    """Ask §6.7 (PROPOSED): a conscripted recruit's control is Kokomi's
    own, a drafted companion's is not."""
    st = kokomi_state()
    drafted = loader.get_card("sayu_yoohoo_windwheel")
    effects.resolve_card(st, drafted)
    assert st.current_card_companion is True
    conscripted = loader.get_card("sayu_yoohoo_windwheel")
    conscripted.conscripted = True
    effects.resolve_card(st, conscripted)
    assert st.current_card_companion is False


def test_companion_pool_is_inazuma_draftables_only():
    pool = loader.companion_pool("inazuma")
    assert pool and all(c.nation == "inazuma" and c.is_companion
                        and not c.guest_star for c in pool)
    assert any(c.rarity == "rare" for c in pool)     # the Itto jackpot


# --- Sly ---

def test_sly_fires_on_card_effect_discard_only():
    st = kokomi_state()
    lantern = loader.get_card("drifting_lantern")
    st.player.hand = [lantern]
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "discard", "amount": 1}]))
    assert st.player.block == 4                  # the sly line paid
    assert any(ev["event"] == "sly" for ev in st.log)


def test_sly_silent_on_end_of_turn_hand_flush():
    st = kokomi_state()
    st.player.hand = [loader.get_card("drifting_lantern")]
    pilot = NULL_PILOT
    combat._player_turn(st, pilot)
    assert not any(ev["event"] == "sly" for ev in st.log)


# --- prevention ward (kickoff §2.4) ---

def _ward_state():
    st = kokomi_state()
    st.player.powers["prevent_exhaust_ward"] = 6
    st.player.draw_pile = [kokomi_card(id=f"fuel_{i}") for i in range(5)]
    return st


def test_ward_prevents_first_unblocked_hit_and_exhausts_fuel():
    st = _ward_state()
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 8}]
    combat._enemy_turn(st, e)
    assert st.player.hp == st.player.max_hp - 2      # 6 of 8 prevented
    assert len(st.player.exhaust_pile) == 1
    assert st.player.charge == C.CHARGE_PER_EXHAUST  # the proc IS fuel
    assert any(ev["event"] == "prevent_exhaust" and ev["amount"] == 6
               for ev in st.log)


def test_ward_procs_once_per_round():
    st = _ward_state()
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 8, "times": 2}]
    combat._enemy_turn(st, e)
    # First hit: 6 prevented, 2 lands. Second hit: latch spent, 8 lands.
    assert st.player.hp == st.player.max_hp - 10
    assert len(st.player.exhaust_pile) == 1


def test_ward_cannot_pay_from_an_empty_deck():
    st = _ward_state()
    st.player.draw_pile = []
    st.player.discard_pile = []
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 8}]
    combat._enemy_turn(st, e)
    assert st.player.hp == st.player.max_hp - 8      # defenseless
    assert not st.player.exhaust_pile


def test_ward_latch_resets_each_player_turn():
    st = _ward_state()
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 8}]
    combat._enemy_turn(st, e)
    combat._player_turn(st, NULL_PILOT)
    combat._enemy_turn(st, e)
    assert len(st.player.exhaust_pile) >= 2          # proc'd again


# --- Ceremonial Garment (Shape B) ---

def test_garment_state_reads_charge_on_attacks():
    st = kokomi_state()
    p = st.player
    p.powers["ceremonial_garment"] = 2
    p.charge = 8
    e = st.enemies[0]
    hp0 = e.hp
    effects.resolve_card(st, kokomi_card(
        type="attack", effects=[{"op": "damage", "amount": 4}]))
    bonus = 8 // C.GARMENT_CHARGE_DIVISOR
    assert hp0 - e.hp == 4 + bonus


def test_garment_state_decays_per_turn():
    st = kokomi_state()
    st.player.powers["ceremonial_garment"] = 2
    powers.on_turn_end(st, st.player)
    assert st.player.powers["ceremonial_garment"] == 1


def test_charge_is_read_never_spent():
    st = kokomi_state()
    st.player.charge = 10
    effects.resolve_card(st, loader.get_card("nereids_ascension"))
    assert st.player.charge == 10                    # read, not consumed


def test_nereids_ascension_reads_charge():
    st = kokomi_state()
    e = st.enemies[0]
    st.player.charge = 10
    hp0 = e.hp
    effects.resolve_card(st, loader.get_card("nereids_ascension"))
    assert hp0 - e.hp == 12 + 10 // 2      # v0.3 base 12


def test_all_streams_flow_is_the_on_curve_reader():
    """v0.3 charge-curve pass: the sub-Rare read exists and scales."""
    st = kokomi_state()
    e = st.enemies[0]
    st.player.charge = 10
    hp0 = e.hp
    effects.resolve_card(st, loader.get_card("all_streams_flow"))
    assert hp0 - e.hp == 5 + 10 // 2
    assert st.player.charge == 10          # read, never spent


# --- v0.4 O4 salvage: the Kurage summon + Garment riders ---

def test_bake_kurage_fields_a_summon_for_the_constant_duration():
    st = kokomi_state()
    effects.resolve_card(st, loader.get_card("bake_kurage"))
    assert st.player.powers["kurage_summon"] == C.KURAGE_DURATION
    assert st.player.charge == 1           # the +1 Charge survives the rework


def test_kurage_pulse_reads_the_bank_and_grants_block():
    st = kokomi_state()
    e = st.enemies[0]
    st.player.charge = 12
    st.player.powers["kurage_summon"] = C.KURAGE_DURATION
    hp0, block0 = e.hp, st.player.block
    effects.player_turn_end_triggers(st)
    assert hp0 - e.hp == C.KURAGE_PULSE_BASE + 12 * C.KURAGE_PULSE_PER_CHARGE
    assert st.player.block - block0 == C.KURAGE_PULSE_BLOCK
    assert st.player.charge == 12          # read, never spent
    assert st.player.powers["kurage_summon"] == C.KURAGE_DURATION - 1


def test_kurage_summon_expires_and_stops_pulsing():
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1
    effects.player_turn_end_triggers(st)
    assert st.player.powers["kurage_summon"] == 0
    e = st.enemies[0]
    hp0 = e.hp
    effects.player_turn_end_triggers(st)
    assert e.hp == hp0                     # gone means gone


def test_resummoning_refreshes_and_never_stacks():
    """A second jellyfish is not a bigger jellyfish (plan §1.1)."""
    st = kokomi_state()
    effects.resolve_card(st, loader.get_card("bake_kurage"))
    effects.player_turn_end_triggers(st)
    assert st.player.powers["kurage_summon"] == C.KURAGE_DURATION - 1
    effects.resolve_card(st, loader.get_card("bake_kurage"))
    assert st.player.powers["kurage_summon"] == C.KURAGE_DURATION


def test_garment_cast_refreshes_a_fielded_kurage(monkeypatch):
    """The Tamakushi Casket link: her canon E-into-Q loop (plan §1.3).

    NOTE the monkeypatch, and why it is not cheating: at the SHIPPED
    KURAGE_DURATION of 1 this mechanic is unobservable. A fielded Kurage is
    always at exactly 1, so "refresh to full" is a no-op, and at 0 the guard
    correctly declines to conjure one from nothing. The link is real in code
    and inert in play -- the known consequence recorded on KURAGE_DURATION.
    This test raises the duration so the behaviour is still PINNED, which is
    what makes restoring a longer duration safe.
    """
    monkeypatch.setattr(C, "KURAGE_DURATION", 3)
    st = kokomi_state()
    st.player.powers["kurage_summon"] = 1          # decayed, 2 turns burned
    effects.resolve_card(st, loader.get_card("ceremonial_garment"))
    assert st.player.powers["kurage_summon"] == 3


def test_garment_cast_does_not_conjure_a_kurage_from_nothing():
    st = kokomi_state()
    effects.resolve_card(st, loader.get_card("ceremonial_garment"))
    assert st.player.powers.get("kurage_summon", 0) == 0


def test_garment_attacks_also_grant_block():
    st = kokomi_state()
    st.player.powers["ceremonial_garment"] = C.CEREMONIAL_GARMENT_TURNS
    block0 = st.player.block
    effects.resolve_card(st, loader.get_card("waters_edge"))
    assert st.player.block - block0 == C.GARMENT_ATTACK_BLOCK


def test_garment_attack_block_does_not_fire_without_the_state():
    st = kokomi_state()
    block0 = st.player.block
    effects.resolve_card(st, loader.get_card("waters_edge"))
    assert st.player.block == block0


def test_kurages_oath_adds_block_to_every_pulse():
    """v0.4: the mending half of the canon Bake-Kurage, drafted rather than
    baseline (KURAGE_PULSE_BLOCK is 0)."""
    st = kokomi_state()
    e = st.enemies[0]
    st.player.powers["kurage_summon"] = 1
    hp0, block0 = e.hp, st.player.block
    effects.player_turn_end_triggers(st)
    assert st.player.block == block0        # no ward yet: damage only

    oath = loader.get_card("kurages_oath")
    (ward,) = [fx for fx in oath.effects if fx.get("power") == "kurage_ward"]
    st2 = kokomi_state()
    effects.resolve_card(st2, oath)
    st2.player.powers["kurage_summon"] = 1
    b0 = st2.player.block
    effects.player_turn_end_triggers(st2)
    # Read the PRINTED number rather than pinning a literal: this one is an
    # explicitly-flagged rebalance candidate ([USER]: "maybe too strong"), so
    # the test guards the wiring, not the balance dial.
    assert st2.player.block - b0 == ward["amount"]


def test_kurages_oath_is_inert_without_a_fielded_kurage():
    st = kokomi_state()
    effects.resolve_card(st, loader.get_card("kurages_oath"))
    b0 = st.player.block
    effects.player_turn_end_triggers(st)
    assert st.player.block == b0            # the ward mends nothing alone


def test_kurage_constants_are_exercised_knobs():
    """KNOB_READS: every v0.4 constant is named AND read (plan ask 2)."""
    effects.KNOB_READS.clear()
    st = kokomi_state()
    st.player.powers["ceremonial_garment"] = 1
    effects.resolve_card(st, loader.get_card("bake_kurage"))
    effects.resolve_card(st, loader.get_card("waters_edge"))
    effects.player_turn_end_triggers(st)
    for knob in ("KURAGE_DURATION", "KURAGE_PULSE_PER_CHARGE",
                 "GARMENT_ATTACK_BLOCK"):
        assert effects.KNOB_READS.get(knob, 0) > 0, knob


def test_pilot_actually_fields_the_kurage():
    """The DECISIONS-53 selector lesson: a card the pilot cannot price is a
    card the arm never gets. Bake-Kurage is the whole O4 arm."""
    p = loader.build_player("kokomi")
    pilot = make_pilot(loader.pilot_weights("priest"))
    st = combat.run_fight(p, [make_enemy(hp=200)], pilot, seed=11)
    assert any(ev["event"] == "summon_kurage" for ev in st.log)


# --- integration: batteries run clean ---

def test_priest_deck_runs_and_accrues_charge():
    p = loader.build_player("kokomi", "priest_weighted")
    pilot = make_pilot(loader.pilot_weights("priest"))
    st = combat.run_fight(p, [make_enemy(hp=120)], pilot, seed=7)
    assert any(ev["event"] == "fight_end" for ev in st.log)
    assert p.charge > 0                              # the engine turned


def test_commander_deck_conscripts_in_play():
    p = loader.build_player("kokomi", "commander_weighted")
    pilot = make_pilot(loader.pilot_weights("commander"))
    conscripted = 0
    for seed in range(6):
        p = loader.build_player("kokomi", "commander_weighted")
        st = combat.run_fight(p, [make_enemy(hp=120)], pilot, seed=seed)
        conscripted += sum(1 for ev in st.log if ev["event"] == "conscript")
    assert conscripted > 0


# --- v0.2 sheet pass laws (R51/R52, 2026-07-24): catch -> lint culture ---

def _kokomi_sheet_rows():
    import yaml
    text = (loader.DOCS_DIR / "kokomi-cards.yaml").read_text(encoding="utf-8")
    return yaml.safe_load(text)


def _walk_printed(row):
    """Every printed effect: main list, conditional branches, sly riders."""
    stack = list(row.get("effects", [])) + list(row.get("sly", []))
    while stack:
        fx = stack.pop()
        yield fx
        for branch in ("then", "else"):
            if isinstance(fx.get(branch), list):
                stack.extend(fx[branch])


def test_law2_no_heals_anywhere_in_her_pool():
    """R52 ask 1: NO heals, period — no amendment taken and none planned
    (Furina holds the mod's one). The v0.1 sango_prayer heal is gone; this
    gate keeps the ruling from being 'rediscovered' by a future card."""
    offenders = [row["id"] for row in _kokomi_sheet_rows()
                 if any(fx.get("op") == "heal" for fx in _walk_printed(row))]
    assert not offenders, f"R52 ask 1 violated by {offenders}"


def test_r51_debuffs_ride_exhaust_or_sly_pieces_only():
    """R51 texture (user, verbatim intent): Weak/Vulnerable are engine
    payoffs on exhaust/Sly pieces — never a spammable cheap AoE debuff at
    common (the excluded Furina commanding-gaze shape). Machine form:
    an enemy-target weak/vuln in the MAIN effects requires exhaust: true;
    a Sly rider is gated by the Sly mechanism itself; either way the card
    sits above common."""
    def enemy_debuffs(fx_list):
        return [fx for fx in fx_list
                if fx.get("op") == "apply_power"
                and fx.get("power") in ("weak", "vulnerable")
                and fx.get("target", "self") != "self"]

    offenders = []
    for row in _kokomi_sheet_rows():
        in_main = enemy_debuffs([fx for fx in _walk_printed(row)
                                 if fx not in row.get("sly", [])])
        in_sly = enemy_debuffs(row.get("sly", []))
        if not in_main and not in_sly:
            continue
        if row.get("rarity") in ("basic", "common"):
            offenders.append(f"{row['id']} (common-tier debuff)")
        if in_main and not row.get("exhaust"):
            offenders.append(f"{row['id']} (main-effect debuff, no Exhaust)")
    assert not offenders, f"R51 texture violated: {offenders}"


def test_sango_prayer_stills_the_spears():
    """R52 rework: Weak 2 to all + Block 5, zero HP restored."""
    st = kokomi_state(enemies=[make_enemy(hp=50), make_enemy(hp=50)])
    hp0 = st.player.hp
    effects.resolve_card(st, loader.get_card("sango_prayer"))
    assert all(e.powers.get("weak", 0) == 2 for e in st.enemies)
    assert st.player.block == 5
    assert st.player.hp == hp0                       # the healer heals no HP


def test_exposing_current_marks_and_burns():
    st = kokomi_state()
    e = st.enemies[0]
    hp0 = e.hp
    card = loader.get_card("exposing_current")
    assert card.exhaust                              # R51: exhaust piece
    effects.resolve_card(st, card)
    assert hp0 - e.hp == 8                           # v0.3 reprice
    assert e.powers.get("vulnerable", 0) == 2


def test_tidal_lure_sly_bell_is_a_debuff():
    st = kokomi_state()
    st.player.hand = [loader.get_card("tidal_lure")]
    effects.resolve_card(st, kokomi_card(
        effects=[{"op": "discard", "amount": 1}]))
    assert st.enemies[0].powers.get("vulnerable", 0) == 1
    assert any(ev["event"] == "sly" for ev in st.log)


def test_raiden_is_a_rare_conscript_payoff():
    """R52 ask 9: the opposed apex exists, Rare only, in the pool."""
    pool = loader.companion_pool("inazuma")
    (raiden,) = [c for c in pool if c.id == "raiden_musou_no_hitotachi"]
    assert raiden.rarity == "rare" and raiden.star == 5


# --- v0.2 upgrade sheet (rest-smith dependency for the act sims) ---

def test_kokomi_upgrade_coverage_is_complete():
    """Every draftable Kokomi/Inazuma card has an expressible upgrade;
    the kit Burst deliberately has none (sparks_n_splash precedent)."""
    from tier0.content import upgrades
    import yaml
    for sheet in ("kokomi-cards.yaml", "inazuma-companions.yaml"):
        rows = yaml.safe_load(
            (loader.DOCS_DIR / sheet).read_text(encoding="utf-8"))
        for row in rows:
            if row.get("kit_card"):
                assert not upgrades.has_upgrade(row["id"])
            else:
                assert upgrades.has_upgrade(row["id"]), row["id"]


def test_kokomi_upgrades_respect_the_resource_curve():
    """Klee R1 precedent applied to her engine: no upgrade moves a
    gain_charge line or a conscript count. Checked by applying every
    upgrade and diffing the printed resource ops."""
    import yaml

    def resource_shape(card):
        return [(fx.get("op"), fx.get("amount"))
                for fx in card.effects
                if fx.get("op") in ("gain_charge", "conscript")]

    for sheet in ("kokomi-cards.yaml", "inazuma-companions.yaml"):
        rows = yaml.safe_load(
            (loader.DOCS_DIR / sheet).read_text(encoding="utf-8"))
        for row in rows:
            if row.get("kit_card"):
                continue
            base = loader.get_card(row["id"])
            upped = loader.get_card(row["id"] + "+")
            assert resource_shape(base) == resource_shape(upped), row["id"]


def test_oath_ward_is_pinned_to_the_pulse_frequency_it_was_measured_at():
    """P1 coupling pin (playtest sprint, Track P).

    Kurage's Oath pays its ward ONCE PER PULSE, so what a run actually gets
    is (ward x pulses per play). The 12 was measured against a summon that
    pulses ONCE per play -- KURAGE_DURATION 1, doubling to twice once
    bake_kurage is upgraded (kurage_turns +1). Neither of those numbers is
    the Oath's own, and neither is guarded by the Oath's own tests, so a
    duration change silently reprices a card that already carries a
    [USER] "maybe too strong" flag as the first knob back.

    If this fails, you moved the pulse frequency. That is allowed. It is not
    allowed SILENTLY: re-measure the Oath at the new frequency, then move
    this pin and the note beside the sheet row together, in one change.
    """
    assert C.KURAGE_DURATION == 1
    upgraded = upgrades.apply_upgrade(loader.get_card("bake_kurage"))
    (summon,) = [fx for fx in upgraded.effects
                 if fx.get("op") == "summon_kurage"]
    assert summon["amount"] == 2
    (ward,) = [fx for fx in loader.get_card("kurages_oath").effects
               if fx.get("power") == "kurage_ward"]
    assert ward["amount"] == 12


def test_vigil_upgrade_moves_the_cap_with_the_amount():
    """Single-application encoding: max_stacks == amount must ride along
    or the upgrade is silently swallowed (pass-2 fix lineage)."""
    upped = loader.get_card("vigil_of_the_deep+")
    (fx,) = [f for f in upped.effects
             if f.get("power") == "prevent_exhaust_ward"]
    assert fx["amount"] == 8 and fx["max_stacks"] == 8


# --- v0.5 partial fill: threshold reads and the deck-size accounting ---

def test_charge_threshold_predicate_reads_the_bank_and_never_spends_it():
    """`charge_at_least_N` is the v0.5 fill's one new predicate.

    Two things are asserted, and the second is the one that matters: the
    bar works, AND crossing it leaves the bank untouched. Charge is
    read-never-spent everywhere else in her kit (ChargeResource.Spend is a
    documented no-op on the C# side); a predicate that quietly consumed it
    would be the one place the rule broke, and every scaling number on the
    sheet was measured against a bank that only grows.
    """
    st = kokomi_state()
    st.player.charge = 9
    assert effects._predicate(st, "charge_at_least_10") is False
    st.player.charge = 10
    assert effects._predicate(st, "charge_at_least_10") is True
    assert st.player.charge == 10          # reading is free


def test_read_the_current_pays_the_bar_as_a_flat_bonus_not_a_slope():
    """The threshold shape, pinned against the §2.2 rate-limit grammar.

    all_streams_flow's per-point slope is rate-limited because a slope is
    what makes a late bank frightening. A BAR is not: it pays a printed
    amount once and then stops, which is why this one is legal at uncommon.
    If someone converts this row to a formula, the sub-Rare read ladder has
    changed shape and needs re-measuring, not just re-pricing.
    """
    card = loader.get_card("read_the_current")
    assert card.rarity == "uncommon"
    base, cond = card.effects
    assert base == {"op": "damage", "amount": 7, "target": "enemy"}
    assert cond["if"] == "charge_at_least_10"
    assert cond["then"] == [{"op": "damage", "amount": 6, "target": "enemy"}]
    assert "else" not in cond              # base-plus-bonus, not either/or

    st = kokomi_state()
    st.player.charge = 0
    effects.resolve_card(st, card)
    low = 300 - st.enemies[0].hp

    st = kokomi_state()
    st.player.charge = 10
    effects.resolve_card(st, card)
    high = 300 - st.enemies[0].hp
    assert (low, high) == (7, 13)


def test_threshold_bars_do_not_move_on_upgrade():
    """Resource-curve law, extended to the new shape.

    Lowering a threshold is exactly as much of a resource-curve move as
    raising a gain_charge line -- it makes the engine arrive sooner. The
    upgrades for both threshold cards buy their always-live half instead,
    and this fails if a later pass sells the bar.
    """
    for cid, bar in (("read_the_current", "charge_at_least_10"),
                     ("the_tide_remembers", "exhaust_pile_at_least_6")):
        for card in (loader.get_card(cid), loader.get_card(cid + "+")):
            (cond,) = [fx for fx in card.effects
                       if fx.get("op") == "conditional"]
            assert cond["if"] == bar, cid
            assert cond["then"][0]["amount"] == (
                6 if cid == "read_the_current" else 5), cid


def test_decksize_lint_counts_the_card_copying_ops():
    """LAW 4's accounting must see every op that MINTS a card.

    `copy_companion_in_hand` was invisible to the lint until
    shoulder_to_shoulder wanted it at Common -- a Common carrying it would
    have netted +1 and passed clean, which is the law failing silently
    rather than loudly. The whole copy family is enumerated now; this test
    is the guard, because the next such op will be added by someone who
    never reads this file.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "_decksize_lint",
        loader.DOCS_DIR.parent / "tools" / "lint_kokomi_decksize.py")
    lint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lint)

    for op in ("copy_companion_in_hand", "copy_spotlighted_in_hand"):
        assert lint.card_delta(
            {"rarity": "common", "effects": [{"op": op, "amount": 1}]}) == 1
    # No `amount` field and unbounded by the row: counted as the whole hand
    # rather than guessed at 1.
    assert lint.card_delta({
        "rarity": "common",
        "effects": [{"op": "copy_companions_played_this_combat"}],
    }) == lint.ALL_SENTINEL
    # The shipped row is the balanced case: burn one, copy one, net zero.
    row = next(r for r in lint.yaml.safe_load(
        (loader.DOCS_DIR / "kokomi-cards.yaml").read_text(encoding="utf-8"))
        if r["id"] == "shoulder_to_shoulder")
    assert lint.card_delta(row) == 0


def test_the_burst_is_a_skill_so_it_never_pays_itself_the_charge_read():
    """The Garment's entry splash must not read the bank that the Garment
    turns on.

    `flat_attack_bonus` gates on `card.type == "attack"`, and the C# rider
    gates on CardType.Attack for the same reason. So the card TYPE is the
    only thing standing between "a Burst that opens a scaling window" and "a
    Burst that also cashes the window on the way in" -- at a priest-median
    bank the splash would roughly triple, and every number measured for this
    card would be describing a different card.

    Nothing about a damage-dealing Skill looks wrong at a glance, which is
    exactly why this is pinned rather than trusted: retyping it to `attack`
    would read as a tidy-up and would silently reprice her whole Burst.
    """
    kit = loader.get_card("ceremonial_garment")
    assert kit.type == "skill"

    st = kokomi_state()
    st.player.charge = 20                    # a bank worth cashing
    e = st.enemies[0]
    hp0 = e.hp
    effects.resolve_card(st, kit)
    printed = next(fx["amount"] for fx in kit.effects if fx["op"] == "damage")
    assert hp0 - e.hp == printed
    # ...and the window it just opened is live for the NEXT attack.
    assert st.player.powers["ceremonial_garment"] == C.CEREMONIAL_GARMENT_TURNS
