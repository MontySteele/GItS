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
#: committed row and every upgraded face, sorted by id. TAKEN AT `origin/main`
#: `a63c2b0a`, BEFORE any of EB-311's edits, and unchanged after them. Rebuild
#: it only alongside a `DRAFTER_VERSION` bump and the re-baseline that bump
#: owes -- a diff here is a moved world, not a stale fixture.
SHIPPED_PRICE_DIGEST = \
    "5c40b256cd69e17cc5d4ac0f105a6b689cfdcab88583d3944e3e231488deca7b"
#: 618 rows at the commit this landed on. Pinned beside the hash because a hash
#: of a shrinking population also never changes.
SHIPPED_PRICE_ROWS = 618


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
    return loader.peek_card(cid)


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


def test_a_plan_only_row_is_no_longer_worth_nothing(overhaul):
    """Ambush prints an EMPTY body and "Plan: deal 12 to the front enemy". It
    priced at 0.00 -- blank cardboard to the drafter -- and now prices at its
    planned damage, discounted once for the turn of delay."""
    assert draft._static_power(_proto("proto_kk_ambush")) == \
        12 * C.PLAN_DELAY_DISCOUNT


def test_both_halves_of_a_printed_face_are_counted(overhaul):
    """Feint: 4 now, 9 planned, cost 1. The sum, not the max -- the argument
    for crediting the CHOICE is at the call site."""
    assert draft._static_power(_proto("proto_kk_feint")) == \
        4 + 9 * C.PLAN_DELAY_DISCOUNT


def test_a_planned_aoe_line_takes_the_same_aoe_multiple(overhaul):
    """Kurage's Oath: 5 to all enemies, planned. Same per-op prices as the
    now-line gets -- that is the whole design of the plan branch."""
    assert draft._static_power(_proto("proto_kk_kurages_oath")) == \
        5 * draft.STATIC_AOE_MULT * C.PLAN_DELAY_DISCOUNT


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

def test_mend_prices_one_for_one_with_block(overhaul):
    """The Moon, A Ship: Mend 10 now, Mend 15 planned, cost 2."""
    assert draft.STATIC_MEND_VALUE == 1.0
    assert draft._static_power(_proto("proto_kk_the_moon_a_ship")) == \
        (10 + 15 * C.PLAN_DELAY_DISCOUNT) / 2


def test_the_max_hp_fraction_reads_the_character_sheet(overhaul):
    """Sango Isshin: a quarter of her Max HP now, the same to all enemies
    planned. The 80 is `tier0/content/characters/kokomi.yaml`, the same key
    `build_player` seats her with -- not a constant invented here."""
    quarter = loader._character_index()["kokomi"]["hp"] // kokomi_plan.QUARTER
    assert quarter == 20
    assert draft._static_power(_proto("proto_kk_sango_isshin")) == \
        (quarter + quarter * draft.STATIC_AOE_MULT * C.PLAN_DELAY_DISCOUNT) / 2


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


def test_undertow_is_priced_at_the_mean_of_its_branches(overhaul):
    """The record's own proof that the zeros were the instrument: 7 damage
    rising to 10 against a debuff, above Strike on either branch, priced
    0.00 because `target_has_debuff` had no entry."""
    assert draft._static_power(_proto("proto_kk_undertow")) == (7 + 10) / 2


def test_the_queue_verbs_price_off_dials_this_table_already_holds(overhaul):
    """Nereid's window, Change of Plans and Moon's Reflection, each derived
    from `STATIC_AUTOPLAY_VALUE` -- one neutral card resolved without being
    paid for, which is what all three of them hand you."""
    # Nereid's: 2 turns of doubling, one extra Plan a turn, inside a plan line
    assert draft._static_power(_proto("proto_kk_nereids_ascension")) == \
        2 * draft.STATIC_AUTOPLAY_VALUE * C.PLAN_DELAY_DISCOUNT / 2
    # Change of Plans: one resolution moved a turn earlier, cost 0
    assert draft._static_power(_proto("proto_kk_change_of_plans")) == \
        draft.STATIC_AUTOPLAY_VALUE * (1 - C.PLAN_DELAY_DISCOUNT)
    # Moon's Reflection: one card out of exhaust, a turn late
    assert draft._static_power(_proto("proto_kk_moons_reflection")) == \
        draft.STATIC_AUTOPLAY_VALUE * C.PLAN_DELAY_DISCOUNT


def test_chain_of_command_prices_against_one_companion(overhaul):
    """The neutral single-unit estimate every live count in the file takes."""
    assert draft._static_power(_proto("proto_kk_chain_of_command")) == \
        4 * C.PLAN_DELAY_DISCOUNT


def test_rally_takes_cost_mods_measured_dead_dial(overhaul):
    """Its discount is a `cost_mod` wearing a kit name, so it takes cost_mod's
    zero: Rally's whole price is the Weak it applies."""
    assert draft._static_power(_proto("proto_kk_rally")) == \
        draft.STATIC_DEBUFF_VALUE


def test_cleansing_wave_credits_the_debuff_it_removes(overhaul):
    """5 Block and one debuff off her now, 10 Block planned, cost 1."""
    assert draft._static_power(_proto("proto_kk_cleansing_wave")) == \
        5 + draft.STATIC_DEBUFF_VALUE + 10 * C.PLAN_DELAY_DISCOUNT


def test_the_arm_has_no_unpriced_verb_left(overhaul):
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


def test_the_pilot_never_scales_a_duration():
    """`plan_twice`'s amount is Nereid's window in TURNS. Three-quarters of a
    turn is not a thing, so the discount leaves it alone -- and so it leaves
    alone a clause with no numeric amount at all."""
    from tier0.pilot import policy
    for fx in ({"op": "plan_twice", "amount": 2},
               {"op": "damage_quarter_max_hp", "target": "all_enemies"},
               {"op": kokomi_plan.REPLAY_EXHAUSTED}):
        assert policy._plan_discounted(fx) == fx


def test_the_discount_never_writes_on_the_sheets_own_clause():
    """`card.plan` is shared by every instance of the row and read again when
    the Plan is carried out; a forecast that rewrote it would decay the
    card."""
    from tier0.pilot import policy
    clause = {"op": "damage", "amount": 9, "target": "front_enemy"}
    out = policy._plan_discounted(clause)
    assert out is not clause
    assert clause["amount"] == 9
