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

THE NO-BUMP PROOF this file opened with (a fixture hash over every shipped
row's price) left with the shipped sheets at legacy cleanup stage 6.
`test_no_shipped_sheet_prints_a_prototype_only_predicate` stays: the day one
of those predicates is authored onto a non-prototype sheet, this goes red and
the name owes a `DRAFTER_VERSION` bump.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B). The
prototype figures below are pinned as ARITHMETIC -- each is written as the
expression that produces it -- not published as a statement about the design.
"""


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

#: THE NO-BUMP DIGEST OVER THE SHIPPED ROWS (`SHIPPED_PRICE_DIGEST`, 620
#: faces) left with the shipped sheets at legacy cleanup stage 6; it read back
#: in git. What stays is the predicate check below.


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
    loader.reset_arm_caches()
    yield
    loader.reset_arm_caches()


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
    """Ambush: a debuff now, a hit planned, cost 1. The SUM, not the max --
    the argument for crediting the CHOICE is at the call site. (Kokomi core
    pass: the now-line is 2 Vulnerable, priced at STATIC_DEBUFF_VALUE.)"""
    card = _proto("proto_kk_ambush")
    now = card.effects[0]["amount"] * draft.STATIC_DEBUFF_VALUE
    planned = card.plan[0]["amount"]
    assert card.cost == 1
    assert draft._static_power(card) == now + planned * C.PLAN_DELAY_DISCOUNT


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
    """The Moon, A Ship (R276 pick 1): Block now, Mend planned. Every point of
    the Mend is one point of Block, so the card prices as its two numbers."""
    assert draft.STATIC_MEND_VALUE == 1.0
    card = _proto("proto_kk_the_moon_a_ship")
    now = card.effects[0]
    planned = card.plan[0]
    assert now["op"] == "block" and planned["op"] == "mend"
    assert draft._static_power(card) == (
        now["amount"] + planned["amount"] * C.PLAN_DELAY_DISCOUNT) / card.cost


def test_the_max_hp_fraction_reads_the_character_sheet():
    """The quarter of her Max HP, R243. The 80 is
    `tier0/content/characters/kokomi.yaml`, the same key `build_player`
    seats her with -- not a constant invented here.

    SANGO ISSHIN LEFT THE OP (the Casket pass, 2026-09-28): it deals 8 to ALL,
    plus 6 per Plan carried out this turn, now (the base since 2026-09-29), priced at the neutral single count
    every live count here takes. The op stays registered and priced, which
    the rename test below holds.
    """
    quarter = loader._character_index()["kokomi"]["hp"] // kokomi_plan.QUARTER
    assert quarter == 20
    card = _proto("proto_kk_sango_isshin")
    hit = card.effects[0]
    assert hit["op"] == "damage"
    assert hit["target"] == "all_enemies"
    assert hit["amount_formula"]["count"] == "plans_carried_out_this_turn"
    assert draft._static_power(card) > 0


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
