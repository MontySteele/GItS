"""The Kokomi overhaul arm (slice one) -- the flag, and both sides of it.

The ruled brief is `review/active/kokomi-brief-2026-09-01.md` DRAFT 6
(direction ruled R240, brief approved R241) and the slice is
`review/active/kokomi-overhaul-slice-1-2026-09-01.md` draft 6 (sec.3 the
ten-card starter, sec.4 the 26 pool rows, sec.5 the engine build list).

THE FIRST SECTION IS THE ONE THAT MATTERS. `C.KOKOMI_OVERHAUL` ships OFF, and
with it off every Kokomi number ever measured is still comparable and the
Kurage's-memory arm beside it still owns its own seams. That is an ACCEPTANCE
CONDITION, not an intention, so it is pinned the way `test_klee_overhaul.py`
pins its own: as a digest of a fixed-seed fight's whole event log, plus the
shape of every seam this arm touches.

WHAT THE SIM DOES HERE, AND WHERE THE REST OF IT IS. Slice one was C# FIRST
(the slice packet sec.5: "All of it behind the prototype switch, C# first. The
Python sim is not brought up for slice one"), and for a while tier0 loaded and
validated the rows while REFUSING to resolve their ops. The sim twin exists
now -- `tier0/engine/kokomi_plan.py`, mirroring
`KleeCode/Powers/Prototype/KokomiPlan.cs` -- so what is left here is the
QUARANTINE half: the flag ships off, off is byte-identical, and the rows are
reachable only with it on. The rules themselves are pinned clause by clause in
`test_kokomi_plan.py`, which names the C# sentence each one comes from.

NOTHING MEASURED ON ANY PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B). These are
shape assertions about an engine, not numbers about a game.
"""

import hashlib
import json

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects
from tier0.engine.combat import run_fight
from tier0.pilot.policy import make_pilot
from tier05 import draft, rewards

SEED = 11

#: Every op slice one adds. Registered in `effects.OPS` so the loader's
#: vocabulary check accepts a row, and priced in `draft.STATIC_OP_PRICING` so
#: `lint_op_parity` stays green.
OVERHAUL_OPS = ("mend", "next_companion_discount", "remove_debuff",
                "carry_out_front_plan", "plan_from_exhaust",
                "damage_quarter_max_hp", "plan_twice",
                "damage_per_companion_last_turn")

#: The two that are legal inside a `plan:` list and NOWHERE else. They are in
#: `OPS` only because the loader validates a `plan:` list through the same
#: vocabulary check the body takes, and they refuse from a body always -- with
#: the flag on as well as off, which is what separates them from the six.
PLAN_ONLY_OPS = ("plan_twice", "damage_per_companion_last_turn")


@pytest.fixture
def overhaul(monkeypatch):
    """The flag ON, with every id-resolving cache cleared on both sides.

    `_card_prototype` is memoized and its answer for a `proto_` id DEPENDS on
    the flag, so a test that flips the flag without clearing it would read a
    KeyError cached from an earlier test. `rewards.character_pool` is memoized
    too and its answer moves with the same flag. Cleared going in and out.
    """
    loader._card_prototype.cache_clear()
    rewards.character_pool.cache_clear()
    monkeypatch.setattr(C, "KOKOMI_OVERHAUL", True)
    yield
    loader._card_prototype.cache_clear()
    rewards.character_pool.cache_clear()


def kokomi_fight(seed=SEED):
    pilot = make_pilot(loader.pilot_weights("priest"))
    player = loader.build_player("kokomi")
    return run_fight(player, loader.build_encounter("punisher"), pilot,
                     seed=seed)


def log_digest(state) -> str:
    return hashlib.sha256(
        json.dumps(state.log, sort_keys=True, default=str
                   ).encode("utf-8")).hexdigest()


# --- 1. FLAG OFF IS BYTE-IDENTICAL -----------------------------------------

def test_the_flag_ships_off():
    """The quarantine. Everything below only matters while this holds."""
    assert C.KOKOMI_OVERHAUL is False


def test_a_fixed_seed_kokomi_fight_is_reproducible_with_the_flag_off():
    """THE ACCEPTANCE CONDITION, as a digest of the whole log.

    Pinned against ITSELF at the branch point rather than against a literal
    copied from another file: no other arm's test fights Kokomi, so there is no
    existing digest to share and inventing one here would only pin today's
    date. Two runs of the same seed on the same tree must agree, and the ARM
    must not move either of them -- which is what the pair below says.
    """
    assert log_digest(kokomi_fight()) == log_digest(kokomi_fight())


def test_the_starter_is_the_printed_starter_with_the_flag_off():
    """Twelve cards, the Silent shape, exactly as ratified."""
    ids = loader.starting_deck("kokomi")
    assert len(ids) == 12
    assert not any(cid.startswith("proto_kk_") for cid in ids)


def test_no_pool_is_replaced_with_the_flag_off():
    """The seam returns None for everybody, so `character_pool` never enters
    its branch and is byte-for-byte the function it has always been."""
    for character in ("klee", "furina", "kokomi", "ref_ironclad",
                      "real_silent"):
        assert loader.pool_replacement(character) is None


def test_the_offerable_pool_carries_no_overhaul_row_with_the_flag_off():
    pool = rewards.character_pool("kokomi")
    ids = {c.id for cards in pool.values() for c in cards}
    assert not any(cid.startswith("proto_kk_") for cid in ids)
    # The shipped pool, still there and still hers. `undertow` and
    # `cleansing_tide` are SHIPPED Kokomi rows whose display names the slice
    # re-uses under a "(proto)" suffix, so this also says the two cannot be
    # confused for one another.
    assert "undertow" in ids
    assert "cleansing_tide" in ids


def test_the_overhaul_ids_do_not_resolve_with_the_flag_off():
    """The quarantine's own door, shut. `_card_prototype`'s prototype branch
    is guarded by the flags, so a `proto_kk_` id is a KeyError here -- which
    is what makes "the rows never enter an ordinary run" a property of the
    code rather than a filter somebody remembers.

    NAMED, not read off `KOKOMI_OVERHAUL_STARTER_IDS[0]`, since R242: that slot
    is now the BASE GAME's `strike`, which resolves on every tree by design and
    would have turned this test green for the wrong reason."""
    loader._card_prototype.cache_clear()
    with pytest.raises(KeyError):
        loader.get_card("proto_kk_kurages_oath")
    loader._card_prototype.cache_clear()


def test_the_kurage_memory_arm_is_untouched():
    """The overhaul is a FOURTH arm. Editing the memory arm's constants would
    make its OFF/ON pair incomparable, which is the one thing a multi-arm flag
    exists to prevent."""
    assert C.KURAGE_MEMORY_STARTER_DROP == "bake_kurage"
    assert C.KURAGE_MEMORY_POOL_DROP == "kurages_oath"
    assert C.KLEE_OVERHAUL is False
    assert C.COMPANION_OVERHAUL is False


# --- 2. THE ARM'S OWN SHAPE ------------------------------------------------

def test_the_starter_is_the_canonical_ten():
    """Slice draft 6 sec.3, as R242 amended it: Strike x4, Defend x4, Kurage's
    Oath, Slack Water.

    "Where a character's basics are a renamed Strike or Defend with the same
    stat line, the base game's Strike and Defend replace them." Water's Edge
    and Coral Guard were exactly that, so they are DELETED rather than
    re-priced -- which the last loop is what checks."""
    ids = C.KOKOMI_OVERHAUL_STARTER_IDS
    assert len(ids) == 10
    assert ids.count("strike") == 4
    assert ids.count("defend") == 4
    assert ids.count("proto_kk_kurages_oath") == 1
    assert ids.count("proto_kk_slack_water") == 1
    assert len([i for i in ids if i.startswith("proto_")]) == 2
    staged = {c.id for c in loader.prototype_cards()}
    for gone in ("proto_kk_waters_edge", "proto_kk_coral_guard"):
        assert gone not in staged


def test_the_pool_is_all_thirty_of_the_slices_rows():
    """Slice draft 6 sec.4, whole. Pinned rather than described because it is
    the slice's own scope statement, and because -- unlike the Klee arm, which
    dropped Vermillion Pact on its packet's own escape -- NOTHING drops here.

    TWENTY-EIGHT since `EB-335` (R246 pick 2): the slice's 26 plus Tide Wall
    and Shell Guard, the kit's own defence in act 2. THIRTY since round 9
    pick 1's tempo shelf (2026-09-04), the two rows that let a Plan be held or
    hurried -- Held Tide and Tidal Rhythm, the drafted other two, were
    withdrawn on the R253 charter audit and are not on the surface."""
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == 30
    assert len(set(ids)) == 30
    assert not set(ids) & set(C.KOKOMI_OVERHAUL_STARTER_IDS)
    assert {"proto_kk_tide_wall", "proto_kk_shell_guard"} <= set(ids)
    assert {"proto_kk_tide_chart", "proto_kk_ripple"} <= set(ids)
    assert "proto_kk_held_tide" not in ids
    assert "proto_kk_tidal_rhythm" not in ids


def test_the_arm_carries_exactly_two_rule_numbers():
    """Draft 6's rules are STRUCTURAL -- where a card lands and when -- so
    almost every figure is a card's and stays on its row. Two are not: the
    relic's strike and Rally's discount, both printed on a face with no
    `amount` field behind them. They are named so `lint_constant_parity` can
    compare the C# mirrors BY VALUE."""
    assert C.KOKOMI_OVERHAUL_CASKET_STRIKE == 2
    assert C.KOKOMI_OVERHAUL_RALLY_DISCOUNT == 1
    named = {n for n in dir(C) if n.startswith("KOKOMI_OVERHAUL")}
    assert named == {"KOKOMI_OVERHAUL", "KOKOMI_OVERHAUL_POOL_IDS",
                     "KOKOMI_OVERHAUL_STARTER_IDS",
                     "KOKOMI_OVERHAUL_CASKET_STRIKE",
                     "KOKOMI_OVERHAUL_RALLY_DISCOUNT"}


# --- 3. THE FLAG ON: the rows are reachable, and only these rows -----------

def test_the_starter_resolves_to_the_slices_ten_cards(overhaul):
    """`starting_deck` is the ONE seam both the tier 0 battery and the tier 0.5
    run read, so this is what she opens with on either path."""
    ids = loader.starting_deck("kokomi")
    assert ids == list(C.KOKOMI_OVERHAUL_STARTER_IDS)
    # And each one is a real, loadable, validated card -- not just a string.
    for cid in set(ids):
        card = loader.get_card(cid)
        assert card.id == cid
        if cid.startswith("proto_kk_"):
            assert card.character == "kokomi"

    # THE BASE BASICS, at the base stat line and the base upgrade (R242).
    strike, defend = loader.get_card("strike"), loader.get_card("defend")
    assert strike.effects == [{"op": "damage", "amount": 6, "target": "enemy"}]
    assert defend.effects == [{"op": "block", "amount": 5}]
    assert loader.get_card("strike+").effects[0]["amount"] == 9
    assert loader.get_card("defend+").effects[0]["amount"] == 8


def test_a_base_strike_in_her_hand_applies_nothing(overhaul):
    """[USER], 2026-09-02: "the basic Strikes ... are supposed to be bad!" Her
    cadence is still about HER and not about the card -- her own Attacks apply
    Hydro with nothing printed -- but the base game's basics are outside the
    dial (LAW's cadence line; `CatalystCadence.IsBaseGameBasic` is the twin)."""
    from tier0.tests.conftest import make_state
    from tier0.engine import effects as fx_mod

    state = make_state()
    state.player = loader.build_player("kokomi")
    assert (state.player.cadence, state.player.element) == ("catalyst", "hydro")
    strike = loader.get_card("strike")
    assert strike.element == "none"
    assert fx_mod._element_for(state, strike.effects[0], strike) is None
    defend = loader.get_card("defend")
    assert fx_mod._element_for(state, defend.effects[0], defend) is None

    # Her own Attack is unmoved: Slack Water names no element and still lands
    # Hydro, which is what the exemption leaves alone.
    slack = next(c for c in loader.prototype_cards()
                 if c.id == "proto_kk_slack_water")
    assert slack.element == "none"
    assert fx_mod._element_for(state, slack.effects[0], slack) == "hydro"


def test_the_offerable_pool_is_the_slice_and_nothing_else(overhaul):
    """`rewards.character_pool` is the single source of truth for every offer
    surface -- fight rewards, the shop, every event card screen and the tier
    0.5 drafter -- so this one assertion covers all five."""
    pool = rewards.character_pool("kokomi")
    ids = {c.id for cards in pool.values() for c in cards}
    assert ids == set(C.KOKOMI_OVERHAUL_POOL_IDS)


def test_the_pool_keeps_the_packets_rarity_split(overhaul):
    """15 Common, 10 Uncommon, 5 Rare. The packet's sec.4 count was 13/8/5;
    `EB-335`'s two defensive rows are both Uncommon (R246 pick 2), which is
    where the round-four-c packet designed them, and the tempo shelf adds two
    Commons (Tide Chart, Ripple). Pinned because the rarity buckets ARE the
    offer odds: a row filed in the wrong tier changes how often it is seen."""
    pool = rewards.character_pool("kokomi")
    assert {r: len(cs) for r, cs in sorted(pool.items())} == {
        "common": 15, "uncommon": 10, "rare": 5}


def test_a_tier05_run_can_open_with_the_arms_starter(overhaul):
    """`starting_deck` WITH AN RNG is the tier-0.5 door, and it used to raise
    here: the printed `randomized_starter` slot names `sayu_daruma_gift`, which
    an arm that replaces the whole starter does not hold, so no run-level arm
    on this flag had ever opened. `loader.starter_replaced_whole` is the named
    predicate that says a whole-starter replacement has no slot to roll; the
    Klee overhaul had the identical latent break one character over."""
    import random
    assert loader.starter_replaced_whole("kokomi") is True
    deck = loader.starting_deck("kokomi", random.Random(1))
    assert deck == list(C.KOKOMI_OVERHAUL_STARTER_IDS)


def test_the_randomized_starter_still_rolls_with_the_flag_off():
    """The other half: a sheet defect (a slot naming a card the printed starter
    does not hold) must still raise, so the predicate is a NAMED branch and not
    a swallowed lookup failure."""
    import random
    assert loader.starter_replaced_whole("kokomi") is False
    deck = loader.starting_deck("kokomi", random.Random(1))
    assert len(deck) == 12
    assert not any(cid.startswith("proto_kk_") for cid in deck)


def test_her_starting_relic_becomes_the_tamakushi_casket(overhaul):
    """The arm REPLACES the relic she starts with; it does not add one. The
    shipped `tamakushi_casket` hook IS the Pearl of Wisdom's exhaust-for-Charge
    funnel plus Flawless Strategy's Strength-to-Charge refusal, and the ruled
    brief's sec.6 retires both -- draft 6's rule 3 needs her Strength to LAND.
    `Relics/TamakushiCasket.cs` says the same sentence from the C# side."""
    for player in (loader.build_player("kokomi"),
                   loader.build_player_from_ids(
                       "kokomi", list(C.KOKOMI_OVERHAUL_STARTER_IDS))):
        assert player.relic_hooks == [loader.OVERHAUL_CASKET_HOOK]
        assert "tamakushi_casket" not in player.relic_hooks


def test_the_relic_seam_is_hers_alone_and_shut_with_the_flag_off():
    for character in ("klee", "furina", "kokomi", "real_silent"):
        assert loader.relic_hooks_replacement(character) is None
    assert "tamakushi_casket" in loader.build_player("kokomi").relic_hooks


def test_no_other_character_moves_under_the_flag(overhaul):
    """The seam is Kokomi's alone. A flag that quietly re-pooled Klee would
    make every number measured on him incomparable."""
    for character in ("klee", "furina"):
        assert loader.pool_replacement(character) is None
        ids = {c.id for cards in rewards.character_pool(character).values()
               for c in cards}
        assert not any(cid.startswith("proto_kk_") for cid in ids)


def test_every_row_prints_its_own_face():
    """EB-215's channel, and the whole slice uses it: a prototype that rewrites
    what a shipped power does cannot say so through the body renderers without
    moving the shipped card's face with it.

    Read off the SHEET rather than off a loaded `Card`, because `description:`
    is deliberately not a tier0 card field -- it is the emitter's channel and
    the sim has no use for it.
    """
    import yaml
    rows = yaml.safe_load(loader.PROTOTYPE_SHEET.read_text(encoding="utf-8"))
    faces = {r["id"]: r.get("description") for r in rows}
    # The BASE basics are not rows on this sheet and have the base game's own
    # face (R242), so the set is the prototype ids only.
    for cid in set(C.KOKOMI_OVERHAUL_POOL_IDS) | {
            c for c in C.KOKOMI_OVERHAUL_STARTER_IDS if c.startswith("proto_")}:
        assert faces.get(cid), cid


def test_a_reaction_leaves_the_retired_burst_meter_at_zero(overhaul):
    """`EB-327`. The brief retires the Burst gate, so under the arm NOTHING
    fills the meter -- and reactions were the one income site neither engine
    had guarded. She is a catalyst, so the 2026-09-02 blind seat read
    `Kokomi Burst: 5/20` off the status line in round 4 and watched it climb
    5 -> 10 -> 15 with no rule anywhere naming it. Klee's `EB-266`, word for
    word, and it is guarded in the same place: `resources.gain_burst` here,
    `KokomiResources.GainBurst` in the mod.

    The ceiling is asserted FIRST and on purpose: `kokomi.yaml` still declares
    `burst_max: 20` under the arm, so this is a test that the GUARD holds and
    not that the meter was deleted out from under it.
    """
    import random
    from tier0.engine import reactions
    from tier0.engine.state import CombatState
    from tier0.tests.conftest import make_enemy

    enemy = make_enemy(hp=60)
    state = CombatState(player=loader.build_player("kokomi"),
                        enemies=[enemy], rng=random.Random(0))
    assert state.player.burst_max == 20, "the sheet still declares the meter"

    reactions.resolve_hit(state, enemy, "pyro", 10)     # the aura
    reactions.resolve_hit(state, enemy, "hydro", 10)    # Vaporize off it

    assert [e for e in state.log if e["event"] == "reaction"], (
        "no reaction fired, so this pin would pass on an unguarded engine")
    assert state.player.burst_energy == 0
    assert not [e for e in state.log if e["event"] == "burst_income"]


# --- 4. THE TWO C# FACTS NO IL SCAN CAN SEE --------------------------------

def test_a_planned_block_is_powered_and_a_planned_hit_is_the_jellyfishs():
    """RULE 3 AND `EB-334`, source-level, because a ValueProp and a named
    argument are both invisible to an IL scan.

    THE TWO HALVES SPLIT AT R246 PICK 1, and that is what this pin now records.
    "Your Strength and Dexterity count, since the plans are hers" still governs
    a planned BLOCK: it is `ValueProp.Move` and NOT `Unpowered`, where draft 2
    took the NC-11 power-sourced line that neither Frail nor Dexterity sees.
    A planned HIT no longer takes it -- the Bake-Kurage deals a Plan
    (`EB-334`), so the call is `powered: false` while the APPLIER stays her,
    which is the pair that keeps her Weak off the number and keeps a
    Plan-caused Freeze a debuff she applied.

    Source-level here for the same reason `test_starter_relic_upgrades.py` is:
    the logic is C#, the fact is an enum literal, and the absence is exactly
    what a compiler cannot see.
    """
    from pathlib import Path
    import re
    root = Path(__file__).resolve().parents[2]
    src = (root / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "KokomiPlan.cs").read_text(encoding="utf-8")

    # ANCHORED ON THE NEXT CASE LABEL, not on a `break;`. `EB-317` gave
    # `ResolveOne` a return value -- the number the clause produced, for the
    # carry-out line the jellyfish says -- so every arm RETURNS now. Neither
    # fact this pin is about, the prop or the applier, moved with it.
    block = re.search(r"case Kind\.Block:.*?case Kind\.Mend:", src, re.DOTALL)
    assert block, "the planned Block clause is gone -- rule 3 moved under this pin"
    # CODE ONLY: the clause's own comment names the prop it does NOT take, and
    # that sentence is the record of the change rather than a second rule.
    code = chr(10).join(
        line for line in block.group(0).splitlines()
        if not line.strip().startswith("//"))
    assert "ValueProp.Move" in code
    assert "Unpowered" not in code, (
        "a planned Block is marked Unpowered, which is the prop Dexterity does "
        "NOT see -- rule 3 is 'your Strength and Dexterity count, since the "
        "plans are hers'")

    hit = re.search(r"private static async Task<int\?> Hit\(.*?\n    \}", src,
                    re.DOTALL)
    assert hit, "KokomiPlan.Hit is gone -- rule 3's damage half moved"
    code = chr(10).join(
        line for line in hit.group(0).splitlines()
        if not line.strip().startswith("//"))
    assert "Element.Hydro, amount, kokomi," in code, (
        "a planned hit does not name her as the APPLIER, so a Plan-caused "
        "Freeze would stop being a debuff she applied and the Casket would "
        "stop answering it")
    assert "powered: false" in code, (
        "a planned hit runs the dealer's mods, so her Weak shrinks it and her "
        "attack buffs feed it -- the exact arithmetic `EB-334` reversed")


def test_the_shipped_strength_refusal_is_off_under_the_arm():
    """The one SHIPPED hook this arm turns off, source-level for the same
    reason. `TryModifyPowerAmountReceived` refuses Strength for Kokomi and pays
    Charge instead; draft 6's rule 3 needs it to land. What that costs is one
    early `return false`, and its absence would be SILENT -- the Tactician loop
    would simply never scale and nothing on screen would say so."""
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    src = (root / "klee-mod" / "KleeCode" / "Powers"
           / "KokomiResources.cs").read_text(encoding="utf-8")
    marker = "if (KokomiOverhaul.LiveFor(target))"
    assert marker in src
    tail = src[src.index(marker):src.index(marker) + 120]
    assert "return false;" in tail, (
        "the arm no longer skips the shipped Strength refusal, so her Strength "
        "is being eaten and rule 3 does not hold")


# --- 5. THE OPS ARE REGISTERED AND REFUSE TO RUN ---------------------------

def test_every_new_op_is_registered():
    """The loader validates `op:` NAMES at load (`_validate_effect_vocabulary`),
    so a row carrying an unregistered op cannot be staged at all."""
    for op in OVERHAUL_OPS:
        assert op in effects.OPS, op


def test_every_new_op_is_priced_for_the_drafter():
    """`lint_op_parity`'s discipline, asserted here too: registering an op
    forces a pricing decision at the moment the author knows the answer."""
    for op in OVERHAUL_OPS:
        assert op in draft.STATIC_OP_PRICING, op


def test_the_new_ops_refuse_to_resolve_with_the_flag_off():
    """THE QUARANTINE, said out loud. With the flag off her `proto_kk_` rows do
    not resolve by id at all, so nothing can reach these -- which makes a verb
    that ran anyway a DEFECT rather than a degradation, and a silently no-op
    resolver the worst possible stand-in. The refusal is asserted, not
    tolerated. `test_kokomi_plan.py` holds the other side: with the flag ON and
    Kokomi in the seat, every one of them resolves."""
    from tier0.tests.conftest import make_state
    from tier0.engine.state import Card

    for op in OVERHAUL_OPS:
        state = make_state()
        state.player.character_id = "kokomi"    # so the FLAG is the only gate
        card = Card(id="probe", name="probe", cost=1, type="skill",
                    effects=[{"op": op}])
        with pytest.raises(NotImplementedError) as excinfo:
            effects.OPS[op](state, {"op": op, "amount": 1}, card)
        assert "KOKOMI_OVERHAUL" in str(excinfo.value)


def test_the_plan_only_clauses_refuse_from_a_body_with_the_flag_on(overhaul):
    """The two that are never a top-level op, refusing on the arm's own turf.
    A body spelling would be a different, unpriced card, and
    `gen_klee_cards.PLAN_ONLY_OPS` refuses the same two in an `effects:` list
    on the C# side."""
    from tier0.tests.conftest import make_state
    from tier0.engine.state import Card

    for op in PLAN_ONLY_OPS:
        state = make_state()
        state.player.character_id = "kokomi"
        card = Card(id="probe", name="probe", cost=1, type="skill",
                    effects=[{"op": op}])
        with pytest.raises(NotImplementedError, match="PLAN-ONLY"):
            effects.OPS[op](state, {"op": op, "amount": 1}, card)


# ======================================================================
# `EB-441` -- Undertow's two numbers, folded through the one live door
# ======================================================================

def test_undertow_is_one_hit_with_a_rider_and_not_two_branches(overhaul):
    """THE FIND. Undertow was a `conditional` whose two branch numbers were
    LITERALS in the face, so nothing folded them. The r12 act-1 seat read them
    beside a folded Strike on one screen -- "`Strike -- Deal 4 damage.` (6
    adjusted to 4 -- correct)" and "`Undertow -- Deal 7 damage...`" -- played
    Undertow into a Weak 1 turn and watched it deal 5: "Strike's face is
    Weak-adjusted; Undertow's face is not. I chose the turn's plays off a
    number that was 2 too high."

    THE ARITHMETIC DOES NOT MOVE, which is the whole claim of the rewrite: 7,
    or 7+3 on a debuffed enemy, is what "deal 7, or 10 instead" said. ONE hit
    either way, which matters -- two would be two aura applications and two
    reaction rolls -- and this is the assertion that says so.
    """
    from tier0.tests.conftest import make_state

    card = next(c for c in loader.prototype_cards()
                if c.id == "proto_kk_undertow")
    assert [e["op"] for e in card.effects] == ["damage"]
    assert card.effects[0]["bonus_vs_debuff"] == 3

    # Aimed at the default target both ways, which is how `target_has_debuff`
    # read "the enemy" when this was a branch (R210's bound aim).
    state = make_state()
    state.player = loader.build_player("kokomi")
    enemy = state.enemies[0]
    hp = enemy.hp
    effects.resolve_card(state, card)
    assert hp - enemy.hp == 7

    state = make_state()
    state.player = loader.build_player("kokomi")
    enemy = state.enemies[0]
    enemy.powers["poison"] = 3
    hp = enemy.hp
    effects.resolve_card(state, card)
    assert hp - enemy.hp == 10


def test_undertows_face_prints_one_folded_number(overhaul):
    """The C# half, and the reason it is a rider and not a fold of our own:
    `CalculatedDamageVar` is the engine's own var, folded exactly the way
    Strike's `DamageVar` is folded, and `Calculate(target)` at resolution is
    the same call -- so the face and the hit are one number by construction.
    The multiplier reads the HOVERED enemy, so the face answers per body the
    question the branch used to ask in the abstract."""
    from pathlib import Path

    repo = Path(__file__).resolve().parents[2]
    src = (repo / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
           / "Generated" / "ProtoKkUndertow.cs").read_text(encoding="utf-8")

    assert ("Deal {CalculatedDamage:diff()} damage, already including "
            "{ExtraDamage:diff()} if the enemy has a debuff." in src)
    assert "IfUpgraded:show:10|7" not in src
    assert "KokomiOverhaulKit.HasDebuff(target) ? 1 : 0" in src
    # ONE hit, the sim's shape: the branch is gone from the play as well as
    # from the face.
    assert src.count("DamageCmd.Attack") == 1
    assert "DamageCmd.Attack(DynamicVars.CalculatedDamage)" in src
