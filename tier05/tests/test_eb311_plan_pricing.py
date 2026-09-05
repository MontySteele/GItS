"""EB-311: the drafter and the pilot price a Plan line (INSTRUMENT ONLY).

`tier05.draft._static_power` priced a row's `effects:` list and never its
`plan:` list, and had no price for `mend`, the Max-HP fraction, Undertow's
`conditional`, or the queue verbs. Sixteen of the twenty-eight `proto_kk_` rows
therefore scored exactly 0.00 at offer, under `DRAFT_SKIP_THRESHOLD` -- so the
balance read's pick rates were a measurement of the drafter rather than of the
cards, which the read says of itself
(`review/records/balance-read-prototype-2026-09-02.md` sec.3). Beside it,
`tier0.pilot.policy._active_effects` swapped in the planned half and valued it
at FACE, with no discount for the turn of delay (the same record, sec.5).

THIS FILE'S FIRST JOB IS THE PROOF THAT NO STAMP MOVES. The change lands under
`RT12/D18/P11/C21` unbumped, and that is a claim about OUTPUT: a `plan:` list
is prototype-surface only, the new op prices belong to verbs no
`docs/*-cards.yaml` row spells, and the one new conditional predicate is a name
no shipped sheet prints. `test_every_shipped_price_is_byte_identical` is that
claim as a fixture hash over every committed row and every upgraded face, and
`test_no_shipped_sheet_prints_a_prototype_only_predicate` is the half a hash
cannot state -- the day one of those predicates is authored onto a shipped
sheet, this goes red and the name owes a `DRAFTER_VERSION` bump.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B). The
prototype figures below are pinned as ARITHMETIC -- each is written as the
expression that produces it -- not published as a statement about the design.
"""

import hashlib
import json

import pytest
import yaml

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import kokomi_plan
from tier0.engine.state import Card
from tier05 import draft


# ---------------------------------------------------------------------------
# 1. THE PROOF: every shipped price is byte-identical
# ---------------------------------------------------------------------------

#: sha256 over `[[card id, "%.10f" % _static_power(card)], ...]` for every
#: committed row and every upgraded face, sorted by id. First taken at
#: `origin/main` `a63c2b0a`, BEFORE any of EB-311's edits, and unchanged after
#: them. Rebuild it only alongside a `DRAFTER_VERSION` bump and the re-baseline
#: that bump owes, OR when the POPULATION moves and every surviving row's price
#: is proved identical first -- a diff here is a moved world, not a stale
#: fixture, and which kind of move it was has to be shown rather than assumed.
#:
#: RE-PINNED ONCE, at `EB-83` (2026-09-02, `RT12` -> `RT13`). The Wood Carvings
#: conversion added `tengu_flurry` and `chinju_ward` to
#: `tier0/content/cards/colorless_event.yaml`; neither takes an upgrade, so the
#: population went 618 -> 620 exactly. NO EXISTING PRICE MOVED, and
#: `test_the_eb83_rows_are_the_only_reason_the_digest_moved` below is that
#: proof rather than this comment -- the digest over the pool MINUS those two
#: ids still equals the pre-EB-83 hash, which is kept below for it to check.
#: `DRAFTER_VERSION` therefore stayed at 18, on the same argument EB-311's own
#: no-bump proof makes: content entering the pool is an `RT` fact, and what
#: this hash guards is the drafter's arithmetic.
SHIPPED_PRICE_DIGEST =     "c674c433cdc34d52510de771e006e84cf57127df28d38c8e24176347a4ed99c3"
#: 620 rows since `EB-83`. Pinned beside the hash because a hash of a shrinking
#: population also never changes.
SHIPPED_PRICE_ROWS = 620

#: The pre-`EB-83` pair, kept as what the re-pin is CHECKED against rather than
#: as history. Retire them only when a bump re-derives the hash for a reason
#: that is not a population change.
PRE_EB83_PRICE_DIGEST =     "5c40b256cd69e17cc5d4ac0f105a6b689cfdcab88583d3944e3e231488deca7b"
EB83_ROWS = ("chinju_ward", "tengu_flurry")


def _shipped_rows() -> list[Card]:
    """Every committed card, base face and upgraded face.

    `game_ref/` rows are EXCLUDED and that is not a convenience: the reference
    sheets are gitignored, so a fixture over them would hash differently on a
    fresh clone than on the deploy host and the pin would be untrustworthy
    exactly where it is checked.

    Every face comes through `loader.get_card`, which hands back a FRESH deep
    copy. `upgrades.apply_upgrade` mutates its argument in place -- its own
    first line says "Mutate a (deep-copied) base card" -- so calling it on the
    shared `_card_index()` prototypes would rewrite the pool this fixture is
    supposed to be measuring, and every later reader's too.
    """
    external = {d["id"] for d in loader._external_cards()}
    rows: list[Card] = []
    for cid in sorted(loader._card_index()):
        if cid in external:
            continue
        rows.append(loader.get_card(cid))
        # Some sheets carry the upgraded row as a card of its own
        # (`albedo_solar_isotoma+`); it is already in the index above.
        if cid.endswith(upgrades.SUFFIX) or not upgrades.has_upgrade(cid):
            continue
        try:
            rows.append(loader.get_card(cid + upgrades.SUFFIX))
        except (ValueError, KeyError):     # UNAPPLIABLE / unexpressible delta
            continue
    return rows


def _digest(rows: list[Card]) -> str:
    blob = json.dumps(
        sorted((c.id, f"{draft._static_power(c):.10f}") for c in rows),
        sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


def test_every_shipped_price_is_byte_identical():
    """THE NO-BUMP PROOF. Not "close", not "unchanged for the arms we looked
    at": the same digits, card for card, on every committed row and both of its
    faces."""
    assert _digest(_shipped_rows()) == SHIPPED_PRICE_DIGEST


def test_the_eb83_rows_are_the_only_reason_the_digest_moved():
    """The re-pin's proof, and the reason the hash above could be rewritten
    without a `DRAFTER_VERSION` bump.

    A re-pinned fixture is worth exactly as much as the argument for re-pinning
    it, and "two cards were added" is not an argument -- a sheet edit can move
    a price on rows it never touched, through a shared price table or a rarity
    term. So the claim is checked rather than asserted: strike the two `EB-83`
    ids out of the population and the pre-EB-83 hash comes back, digit for
    digit, across all 618 rows that existed before it.
    """
    rows = _shipped_rows()
    survivors = [c for c in rows if c.id not in EB83_ROWS]
    assert len(rows) - len(survivors) == len(EB83_ROWS)
    assert _digest(survivors) == PRE_EB83_PRICE_DIGEST


def test_the_digest_covers_the_whole_committed_pool():
    """A hash of nothing also never changes. Pin the population too."""
    rows = _shipped_rows()
    assert len(rows) == SHIPPED_PRICE_ROWS
    assert not any(c.plan for c in rows), \
        "a shipped row grew a `plan:` list -- the no-bump argument is spent"


def test_no_shipped_sheet_prints_a_prototype_only_predicate():
    """`STATIC_PROTOTYPE_CONDITIONS`' scope, checked rather than asserted.

    The set is priced at the mean of its branches on the strength of ONE fact:
    no shipped sheet spells any of these names, so crediting them cannot move a
    published number. That fact is checked here against the sheets themselves,
    and `docs/prototype-surface.yaml` is excluded because it IS the prototype
    surface.
    """
    def names(effect_list) -> set[str]:
        found: set[str] = set()
        for fx in effect_list or ():
            if not isinstance(fx, dict):
                continue
            if fx.get("op") == "conditional":
                found.add(fx.get("if", ""))
                found |= names(fx.get("then"))
                found |= names(fx.get("else"))
            elif fx.get("op") == "choose_one":
                for mode in fx.get("modes") or ():
                    found |= names(mode.get("effects"))
        return found

    printed: set[str] = set()
    for sheet in sorted(loader.DOCS_DIR.glob("*.yaml")):
        if sheet.name == "prototype-surface.yaml":
            continue
        for row in yaml.safe_load(sheet.read_text(encoding="utf-8")) or []:
            if isinstance(row, dict):
                printed |= names(row.get("effects"))
    assert not (printed & draft.STATIC_PROTOTYPE_CONDITIONS), (
        "a shipped sheet now prints a predicate priced as prototype-only; it "
        "owes a STATIC_STATE_CONDITIONS row, a measured share and a "
        "DRAFTER_VERSION bump")


# ---------------------------------------------------------------------------
# 2. THE PLAN LINE IS PRICED
# ---------------------------------------------------------------------------

def _proto(cid: str) -> Card:
    """The row as `docs/prototype-surface.yaml` SPELLS it, re-parsed.

    Deliberately NOT `loader.peek_card`. That door hands out the shared
    `_prototype_index()` template -- the one branch of `_card_prototype` that
    does not deep-copy on the way out, because its contract says read-only --
    and it is a template, so it can also be one CI's checkout has and another's
    does not. What these tests are about is the SHEET, so they read the sheet:
    `loader.prototype_cards()` re-parses `docs/prototype-surface.yaml` on every
    call and builds fresh `Card`s, and it needs no flag to do so.
    """
    return {c.id: c for c in loader.prototype_cards()}[cid]


@pytest.fixture
def overhaul(monkeypatch):
    """Her flag on, with the id-resolving caches cleared both ways -- the
    `test_kokomi_overhaul` fixture's arrangement, for its reasons."""
    loader._card_prototype.cache_clear()
    monkeypatch.setattr(C, "KOKOMI_OVERHAUL", True)
    yield
    loader._card_prototype.cache_clear()


def test_no_prototype_kokomi_row_raises(overhaul):
    """The op-parity discipline, on the surface the lint cannot sweep:
    `_static_power` has a branch for every verb these rows print."""
    for card in loader.prototype_cards():
        draft._static_power(card)


def test_a_plan_only_row_is_no_longer_worth_nothing():
    """A Plan-only row -- EMPTY body, "Plan: deal N to the front enemy" --
    used to price at 0.00: blank cardboard to the drafter. It now prices at
    its planned damage, discounted once for the turn of delay.

    SYNTHETIC, not a real row: `R250` pick 1 (round-4d sec.6) moved six of the
    seven Plan-only Kokomi rows onto Feint's two-halved shape (Ambush was this
    test's row before it), so the surviving real example carries a duration
    rather than damage. The RULE under test is "an empty now-line still prices
    its Plan", which is a fact about the pricing function and not about which
    row happens to have this shape today -- the same argument the sheet
    rebalance note beside this file already makes about NUMBERS.
    """
    card = Card(id="proto_kk_t_plan_only", name="t", cost=1, type="skill",
                effects=[],
                plan=[{"op": "damage", "amount": 12, "target": "front_enemy"}])
    assert not card.effects
    planned = card.plan[0]["amount"]
    assert draft._static_power(card) == planned * C.PLAN_DELAY_DISCOUNT


def test_both_halves_of_a_printed_face_are_counted():
    """Feint: a damage line now, a bigger one planned, cost 1. The SUM, not the
    max -- the argument for crediting the CHOICE is at the call site."""
    card = _proto("proto_kk_feint")
    now = card.effects[0]["amount"]
    planned = card.plan[0]["amount"]
    assert card.cost == 1 and planned > now
    assert draft._static_power(card) == now + planned * C.PLAN_DELAY_DISCOUNT


def test_chain_of_command_sums_its_now_line_and_its_plan():
    """`R250` pick 1 (round-4d sec.6): Chain of Command gained a now-line
    priced through `amount_formula`'s neutral one-unit read, beside the Plan
    line's own `damage_per_companion_last_turn` read -- SUMMED, the same rule
    `test_both_halves_of_a_printed_face_are_counted` pins for Feint's plain
    damage, now over the `amount_formula` rail too."""
    card = _proto("proto_kk_chain_of_command")
    now = card.effects[0]
    assert now["op"] == "damage" and "amount_formula" in now
    now_price = now["amount_formula"]["per"]        # one neutral Companion
    planned = card.plan[0]["amount"]
    assert draft._static_power(card) == (
        now_price + planned * C.PLAN_DELAY_DISCOUNT)


def test_a_planned_aoe_line_takes_the_same_aoe_multiple():
    """A Plan-only AoE line takes the same `STATIC_AOE_MULT` the now-line
    does -- the whole design of the plan branch. Synthetic for the reason
    `test_a_plan_only_row_is_no_longer_worth_nothing` gives (Kurage's Oath
    was this test's row before `R250` pick 1 gave it a now-line too)."""
    card = Card(id="proto_kk_t_plan_aoe", name="t", cost=1, type="skill",
                effects=[],
                plan=[{"op": "damage", "amount": 7, "target": "all_enemies"}])
    clause = card.plan[0]
    assert clause["target"] == "all_enemies"
    assert draft._static_power(card) == (
        clause["amount"] * draft.STATIC_AOE_MULT * C.PLAN_DELAY_DISCOUNT)


def test_the_delay_discount_is_the_only_difference_between_the_halves():
    """Two synthetic rows, one body, printed on either side of the face."""
    body = [{"op": "block", "amount": 8}]
    now = Card(id="proto_kk_t1", name="t", cost=1, type="skill", effects=body)
    late = Card(id="proto_kk_t2", name="t", cost=1, type="skill",
                effects=[], plan=body)
    assert draft._static_power(late) == \
        draft._static_power(now) * C.PLAN_DELAY_DISCOUNT


def test_a_plan_line_reaches_the_tempo_and_block_classifiers():
    """Battle Plan's whole printed text is "Plan: gain 2 Energy, draw 1". Its
    PRICE stays 0.00 -- `draw` and `energy` are the v3 sweep's measured dead
    dials and moving those is a shipped-world question -- but it is a tempo
    card, and the late-run discipline's hatch has to be able to see that."""
    battle_plan = Card(id="proto_kk_t3", name="t", cost=1, type="skill",
                       effects=[],
                       plan=[{"op": "energy", "amount": 2},
                             {"op": "draw", "amount": 1}])
    assert draft._has_tempo(battle_plan)
    assert not draft._has_tempo(
        Card(id="proto_kk_t4", name="t", cost=1, type="skill", effects=[]))
    blocker = Card(id="proto_kk_t5", name="t", cost=1, type="skill",
                   effects=[], plan=[{"op": "block", "amount": 6}])
    assert draft._has_block(blocker)


# ---------------------------------------------------------------------------
# 3. THE OPS THAT HAD NO PRICE
# ---------------------------------------------------------------------------

def test_mend_prices_one_for_one_with_block():
    """The Moon, A Ship: Mend now, more Mend planned. Every point of it is one
    point of Block."""
    assert draft.STATIC_MEND_VALUE == 1.0
    card = _proto("proto_kk_the_moon_a_ship")
    now = card.effects[0]
    planned = card.plan[0]
    assert now["op"] == planned["op"] == "mend"
    assert draft._static_power(card) == (
        now["amount"] + planned["amount"] * C.PLAN_DELAY_DISCOUNT) / card.cost


def test_the_max_hp_fraction_reads_the_character_sheet():
    """Sango Isshin, R243: a quarter of her Max HP to ALL enemies if the
    jellyfish already carried out a Plan this turn, a flat hit otherwise.

    The 80 is `tier0/content/characters/kokomi.yaml`, the same key
    `build_player` seats her with -- not a constant invented here. The row's
    own shape supplies everything else, including which branch is which, so
    this survives the next time the sheet moves.
    """
    quarter = loader._character_index()["kokomi"]["hp"] // kokomi_plan.QUARTER
    assert quarter == 20
    card = _proto("proto_kk_sango_isshin")
    branch = card.effects[0]
    assert branch["if"] in draft.STATIC_PROTOTYPE_CONDITIONS
    hit = branch["then"][0]
    assert hit["op"] == "damage_quarter_max_hp"
    assert hit["target"] == "all_enemies"
    then_power = quarter * draft.STATIC_AOE_MULT
    else_power = branch["else"][0]["amount"]
    assert draft._static_power(card) == (
        else_power + draft.STATIC_PROTOTYPE_CONDITIONAL_SHARE
        * (then_power - else_power)) / card.cost


def test_the_renamed_max_hp_spelling_prices_the_same():
    """A parallel branch may land `damage_max_hp_fraction`. Priced now, so the
    rename cannot arrive as a silent zero on a row a read already quotes."""
    for fx in ({"op": "damage_quarter_max_hp", "target": "enemy"},
               {"op": "damage_max_hp_fraction", "target": "enemy",
                "divisor": 4},
               {"op": "damage_max_hp_fraction", "target": "enemy",
                "fraction": 0.25}):
        card = Card(id="proto_kk_t6", name="t", cost=1, type="attack",
                    character="kokomi", effects=[fx])
        assert draft._static_power(card) == 20


def test_a_row_whose_character_is_unknown_refuses_rather_than_guesses():
    """"A quarter of your Max HP" with no `your` is not a number."""
    card = Card(id="proto_kk_t7", name="t", cost=1, type="attack",
                effects=[{"op": "damage_quarter_max_hp", "target": "enemy"}])
    assert draft._static_power(card) == 0.0


def test_undertow_is_priced_at_the_mean_of_its_branches():
    """The record's own proof that the zeros were the instrument: damage that
    RISES against a debuff, above Strike on either branch, priced 0.00 because
    `target_has_debuff` had no entry anywhere.

    `EB-441` REWROTE THE ROW AND NOT THE PRICE. The two branches are one damage
    op with a `bonus_vs_debuff` rider now -- so the face can be folded by the
    engine, which a branch literal could not be -- and the number this table
    reaches is unchanged: base + bonus/2 IS the mean of the branches, half
    being the share the table already gives a live predicate."""
    card = _proto("proto_kk_undertow")
    hit = card.effects[0]
    assert hit["op"] == "damage"
    lo = hit["amount"]
    hi = lo + hit["bonus_vs_debuff"]
    assert draft._static_power(card) == (hi + lo) / 2 / card.cost


def test_the_queue_verbs_price_off_dials_this_table_already_holds():
    """Change of Plans and Moon's Reflection, each derived from
    `STATIC_AUTOPLAY_VALUE` -- one neutral card resolved without being paid
    for, which is what both of them hand you.

    NEREID'S ASCENSION IS NOT ON THIS LIST ANY MORE (`EB-492`). It was a
    `plan_twice` clause and had its own line here; it is a Rare POWER now, so
    it takes the generic self-power credit every printed engine takes
    (`STATIC_POWER_ENGINE_VALUE`) and the `plan_twice` price is retired with
    the op. `test_the_rare_power_takes_the_engine_credit` below is the pin.
    """
    # Change of Plans: one resolution moved a turn earlier, not created.
    card = _proto("proto_kk_change_of_plans")
    assert draft._static_power(card) == (
        draft.STATIC_AUTOPLAY_VALUE * (1 - C.PLAN_DELAY_DISCOUNT) / card.cost)
    # Moon's Reflection: one card out of the exhaust pile, a turn late.
    card = _proto("proto_kk_moons_reflection")
    assert draft._static_power(card) == (
        draft.STATIC_AUTOPLAY_VALUE * C.PLAN_DELAY_DISCOUNT / card.cost)


def test_the_rare_power_takes_the_engine_credit():
    """`EB-492`. Nereid's Ascension is a Rare Power printing one self
    `apply_power`, so `_static_power` falls to the generic engine branch --
    the drafter cannot see a payout curve at offer time, which is the same
    conservative convention Durin and the Kurage summon take. The point of
    pinning it is that the row reaches a branch AT ALL: the retired
    `plan_twice` price would have been a stale entry, and `lint_op_parity`
    calls one of those out."""
    card = _proto("proto_kk_nereids_ascension")
    assert card.type == "power" and card.plan == []
    assert draft._static_power(card) == (
        draft.STATIC_POWER_ENGINE_VALUE / card.cost)


def test_damage_per_companion_last_turn_prices_against_one_companion():
    """The neutral single-unit estimate every live count in the file takes,
    off `damage_per_companion_last_turn` directly. Synthetic rather than
    Chain of Command (`test_chain_of_command_sums_its_now_line_and_its_plan`
    covers the real row): `R250` pick 1 gave it a now-line of its own, whose
    separate price this test has no business depending on."""
    card = Card(id="proto_kk_t_per_companion", name="t", cost=1, type="skill",
                effects=[],
                plan=[{"op": "damage_per_companion_last_turn", "amount": 6,
                       "target": "front_enemy"}])
    per_companion = card.plan[0]["amount"]
    assert draft._static_power(card) == (
        per_companion * C.PLAN_DELAY_DISCOUNT / card.cost)


def test_rally_takes_cost_mods_measured_dead_dial():
    """Its discount is a `cost_mod` wearing a kit name, so it takes cost_mod's
    zero: Rally's whole price is the Weak it applies."""
    card = _proto("proto_kk_rally")
    weak = next(fx for fx in card.effects if fx.get("power") == "weak")
    assert any(fx["op"] == "next_companion_discount" for fx in card.effects)
    assert draft._static_power(card) == (
        weak["amount"] * draft.STATIC_DEBUFF_VALUE / card.cost)


def test_cleansing_wave_credits_the_debuff_it_removes():
    """Block and one debuff off her now, more Block planned."""
    card = _proto("proto_kk_cleansing_wave")
    now_block = card.effects[0]["amount"]
    planned_block = card.plan[0]["amount"]
    assert any(fx["op"] == "remove_debuff" for fx in card.effects)
    assert draft._static_power(card) == (
        now_block + draft.STATIC_DEBUFF_VALUE
        + planned_block * C.PLAN_DELAY_DISCOUNT) / card.cost


def test_the_arm_has_no_unpriced_verb_left():
    """Every verb in the arm's index answers, and none of them answers with the
    blanket zero this row replaced."""
    priced = {op: draft.STATIC_OP_PRICING[op]
              for op in draft.KOKOMI_OVERHAUL_OPS}
    assert len(priced) == len(draft.KOKOMI_OVERHAUL_OPS)
    assert not [op for op, why in priced.items()
                if why.startswith("ZERO: prototype surface only")]


# ---------------------------------------------------------------------------
# 4. THE PILOT CHARGES THE SAME DELAY
# ---------------------------------------------------------------------------

def test_the_pilot_and_the_drafter_read_one_constant():
    """The point of putting the dial in `constants.py`: the offer screen and
    the hand cannot come to disagree about what a Plan is worth."""
    from tier0.pilot import policy
    assert 0.0 < C.PLAN_DELAY_DISCOUNT < 1.0
    assert policy._plan_discounted({"op": "block", "amount": 8})["amount"] == \
        8 * C.PLAN_DELAY_DISCOUNT


def test_the_pilot_never_scales_a_clause_with_no_magnitude():
    """A clause with no numeric `amount` -- the Max-HP fraction, the exhaust
    replay -- passes the discount untouched, because there is no magnitude to
    scale.

    THE DURATION CARVE-OUT IS GONE (`EB-492`): `plan_twice` was the one
    planned amount that meant TURNS, and Nereid's Ascension is a Power now, so
    every remaining numeric `amount` in a `plan:` list is a magnitude."""
    from tier0.pilot import policy
    for fx in ({"op": "damage_quarter_max_hp", "target": "all_enemies"},
               {"op": kokomi_plan.REPLAY_EXHAUSTED}):
        assert policy._plan_discounted(fx) == fx


def test_the_pilot_never_scales_a_repeat_count():
    """`EB-492`. `times` is a COUNT OF HITS, not a magnitude: Pincer's planned
    line is three hits of a discounted 3, and every term downstream already
    multiplies `amount` by `times`. Scaling both would take the delay twice."""
    from tier0.pilot import policy
    out = policy._plan_discounted(
        {"op": "damage", "amount": 3, "target": "front_enemy", "times": 3})
    assert out["times"] == 3
    assert out["amount"] == 3 * C.PLAN_DELAY_DISCOUNT


def test_the_discount_never_writes_on_the_sheets_own_clause():
    """`card.plan` is shared by every instance of the row and read again when
    the Plan is carried out; a forecast that rewrote it would decay the
    card."""
    from tier0.pilot import policy
    clause = {"op": "damage", "amount": 9, "target": "front_enemy"}
    out = policy._plan_discounted(clause)
    assert out is not clause
    assert clause["amount"] == 9
