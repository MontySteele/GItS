"""EB-118 -- the Exhaust identity context across the three engines that have
to agree about it: the tier0 kernel, the C# mod, and the drafter's price.

Three separate correspondences, one per section:

  1. THE PARITY ROW. Both engines emit a row per resolved selection carrying
     the victim ids and every derived value. The COLUMN NAMES are read out of
     the C# source here and compared with tier0's, so neither side can add or
     rename a column alone -- the same instrument tools/lint_constant_parity.py
     is, pointed at a different correspondence.

  2. CODEGEN. No shipped card reads the new counts (staged infrastructure), so
     the generator is exercised on a SYNTHETIC sheet row -- the future card,
     written down. Without this the first row that uses the grammar finds out
     in the mod build.

  3. THE DRAFTER'S PRICE, pinned rather than changed. `_neutral_amount` prices
     an `amount_formula` as base + per and never looks at `count`, so a new
     count name reaches the offer-time estimate as the same generic
     approximation every other formula gets. That is the whole argument for
     taking new names without a DRAFTER_VERSION bump, and it is only true for
     as long as the pricer keeps ignoring the count.
"""
import re
from pathlib import Path

from tier0.engine import effects
from tier05 import draft
from tools import gen_klee_cards as gen

ROOT = Path(__file__).resolve().parents[2]
CS_SRC = (ROOT / "klee-mod" / "KleeCode" / "Powers"
          / "ExhaustSelection.cs").read_text(encoding="utf-8")


# =========================================================================
# 1. the emitted parity row
# =========================================================================

def _cs_row_keys() -> tuple[str, ...]:
    body = CS_SRC[CS_SRC.index("public static readonly string[] RowKeys"):]
    return tuple(re.findall(r'"([a-z_]+)"', body[:body.index("};")]))


def test_both_engines_declare_the_same_row_columns_in_the_same_order():
    assert _cs_row_keys() == effects.EXHAUST_SELECTION_ROW_KEYS


def test_every_derived_column_is_a_readable_amount_token():
    """The row's derived columns and the sheet vocabulary are the same list.
    A column a card cannot read would be telemetry nobody can design against;
    a token that is not a column would be a number no parity test can see."""
    derived = [k for k in effects.EXHAUST_SELECTION_ROW_KEYS
               if k not in ("card", "victims")]
    assert derived == list(effects.exhaust_selection_counts([]))
    assert ([effects.EXHAUST_SELECTION_PREFIX + k for k in derived]
            == list(gen.EXHAUST_SELECTION_COUNTS))


def test_the_mod_records_the_printed_cost_not_the_modified_one():
    """tier0's descriptor keeps `card.cost`, the PRINTED cost. The C# twin
    must read EnergyCost.Canonical for the same reason -- GetAmountToSpend()
    is that cost after this instance's modifiers, so the same card would
    record two different numbers in two runs."""
    code = "\n".join(line for line in CS_SRC.splitlines()
                     if not line.lstrip().startswith(("///", "//")))
    assert "EnergyCost.Canonical" in code
    # The doc comment NAMES the rejected accessor, so comments are stripped
    # first: what must be absent is the call.
    assert "GetAmountToSpend" not in code


# =========================================================================
# 2. codegen -- the future sheet row, written down
# =========================================================================

def _reader_row(count: str, base: int = 3, per: int = 2) -> dict:
    """A hypothetical Kokomi card: rotate a card out, then hit for a number
    the selection sets. NOT a sheet row -- no shipped card uses this grammar
    (EB-118 is staged infrastructure), which is exactly why the generator has
    to be exercised on one written here."""
    return {
        "id": "recycle_probe", "name": "Recycle Probe", "cost": 1,
        "type": "attack", "rarity": "uncommon", "role": "payoff",
        "archetypes": ["priest"], "solve": ["frontload"],
        "tempo_band": {"fight": ["mid"], "run": ["early"]},
        "effects": [
            {"op": "exhaust_from", "amount": 1, "select": "chosen"},
            {"op": "damage", "target": "enemy",
             "amount_formula": {"base": base, "per": per, "count": count}},
        ],
    }


def test_every_new_count_generates_a_calculated_var_bound_to_it():
    for count, accessor in gen.EXHAUST_SELECTION_COUNTS.items():
        card = _reader_row(count)
        assert gen.blocked_reason(card, gen.KOKOMI_PROFILE) is None, count
        source = gen.emit(card, gen.KOKOMI_PROFILE)
        assert (f"WithMultiplier(static (card, _) => "
                f"ExhaustSelection.{accessor}(card))") in source, count
        # The reader is worth nothing without the selector block that FILLS
        # the context, and the two are only ever in one card together.
        assert "ExhaustSelection.Open(this);" in source, count
        assert "ExhaustSelection.Close(this);" in source, count


def test_the_generated_reader_renders_base_and_per_through_the_triple():
    """base + per * count is the CalculatedDamageVar's own shape, so the
    face, the hover preview and the resolved hit share one value path -- the
    Track L-C rule. A `damage` literal here would be a face that lies."""
    source = gen.emit(_reader_row("exhaust_selection_cost", base=3, per=2),
                      gen.KOKOMI_PROFILE)
    assert "CalculationBaseVar(3)" in source or "CalculationBase" in source
    assert "ExtraDamage" in source
    # And the PER term is printed, not merely asserted: {CalculatedDamage}
    # previews base + per * 0 here (the selection does not exist until the
    # card resolves), so a bare "Scales with ..." sentence left the rate --
    # the only number that makes the card readable -- off the face entirely.
    assert ("plus {ExtraDamage:diff()} per cost of the card you just "
            "[gold]Exhausted[/gold].") in source
    assert "Scales with" not in source


def test_an_unknown_count_stays_a_named_blocker():
    """The UNPARSEABLE discipline: guessing emits a card that compiles and
    pays its base forever while the face promises scaling."""
    reason = gen.blocked_reason(_reader_row("exhaust_selection_curses"),
                                gen.KOKOMI_PROFILE)
    assert reason is not None and "amount_formula" in reason


def test_the_upgrade_deltas_land_on_the_rendered_vars(monkeypatch):
    """`formula_base` / `formula_per` on an exhaust-selection reader bump the
    same two vars the exhaust-pile reader's do -- both render through the
    same triple, so a delta that missed them would upgrade a number the face
    never shows. The ratified-delta sheet is stubbed because the card is
    hypothetical: no shipped row may read this grammar yet."""
    card = _reader_row("exhaust_selection_attacks")
    monkeypatch.setattr(gen, "upgrade_deltas",
                        lambda: {"recycle_probe": {"formula_per": 2,
                                                   "formula_base": 1}})
    plan, why = gen.upgrade_plan(card)
    assert why is None, why
    assert plan == {"formula_per": 2, "formula_base": 1}
    source = gen.emit(card, gen.KOKOMI_PROFILE)
    assert "DynamicVars.ExtraDamage.UpgradeValueBy(2m);" in source
    assert "DynamicVars.CalculationBase.UpgradeValueBy(1m);" in source


# =========================================================================
# 3. the drafter's price -- PINNED, not changed
# =========================================================================

def test_new_count_names_price_the_same_generic_base_plus_per():
    """THE PIN THE PACKET ASKED FOR. `_neutral_amount` reads `base` and `per`
    and never consults `count`, so every exhaust-selection reader arrives at
    the offer-time estimate as the SAME generic approximation an exhaust-pile
    reader already gets. That is why the new vocabulary needs no
    DRAFTER_VERSION bump -- and it stops being true the moment the pricer
    starts reading the count, which is what this test is watching for."""
    prices = {
        count: draft._neutral_amount(
            {"amount_formula": {"base": 3, "per": 2, "count": count}})
        for count in (list(gen.EXHAUST_SELECTION_COUNTS)
                      + ["exhaust_pile", "player_block"])
    }
    assert set(prices.values()) == {5}


def test_the_price_moves_only_with_base_and_per():
    assert draft._neutral_amount(
        {"amount_formula": {"base": 0, "per": 1,
                            "count": "exhaust_selection_size"}}) == 1
    assert draft._neutral_amount(
        {"amount_formula": {"count": "exhaust_selection_size"}}) == 1
