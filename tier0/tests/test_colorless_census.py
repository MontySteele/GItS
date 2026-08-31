"""Regression tests for the colorless-pool census plumbing.

Same contract as `test_extract_base_game_pool.py`, and for the same reason:
tiny synthetic sources, no base-game data reproduced, no ilspycmd and no game
installation required, so CI can hold the shape even though CI can never run
the extraction itself.

What is worth pinning here is not the arithmetic -- it is the three places the
census could lie QUIETLY:

  1. a pool that parses SHORT (a decompiler shape change dropping members)
     would understate the pool size with no error;
  2. a magnitude mean averaged over cards that print no magnitude at all would
     drag the band toward zero and manufacture the opposite of the premium the
     anchor exists to measure;
  3. a per-energy mean that treats a 0-cost card as cost 1 would manufacture
     that premium instead.
"""

import pytest

from tools import colorless_census as census


def _card(name, rarity, cost, *, damage=None, block=None, keywords=()):
    return {
        "name": name, "rarity": rarity, "cost": cost, "type": "Attack",
        "keywords": list(keywords),
        "vars": {k: v for k, v in (("Damage", damage), ("Block", block))
                 if v is not None},
        "powers": [], "cmds": [], "multiplayer_only": False,
    }


def test_a_pool_that_parses_short_is_refused_rather_than_censused(tmp_path):
    """The declared array size is the only independent witness to how many
    members there SHOULD be. If the member regex ever stops matching some
    shape, the census must die loudly instead of reporting a smaller pool."""
    src = tmp_path / "MegaCrit" / "Models" / "CardPools"
    src.mkdir(parents=True)
    (src / "ColorlessCardPool.cs").write_text(
        "namespace MegaCrit.Sts2.Core.Models.CardPools;\n"
        "public sealed class ColorlessCardPool : CardPoolModel {\n"
        "  protected override CardModel[] GenerateAllCards() {\n"
        "    return new CardModel[3] { ModelDb.Card<Alpha>(),\n"
        "      ModelDb.Card<Beta>() };\n"
        "  }\n}\n", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        census.pool_members(tmp_path)
    assert "3" in str(exc.value) and "2" in str(exc.value)


def test_a_pool_that_parses_whole_reports_its_members_in_order(tmp_path):
    src = tmp_path / "MegaCrit" / "Models" / "CardPools"
    src.mkdir(parents=True)
    (src / "ColorlessCardPool.cs").write_text(
        "namespace MegaCrit.Sts2.Core.Models.CardPools;\n"
        "public sealed class ColorlessCardPool : CardPoolModel {\n"
        "  protected override CardModel[] GenerateAllCards() {\n"
        "    return new CardModel[2] { ModelDb.Card<Alpha>(),\n"
        "      ModelDb.Card<Beta>() };\n"
        "  }\n}\n", encoding="utf-8")
    members, declared = census.pool_members(tmp_path)
    assert members == ["Alpha", "Beta"]
    assert declared == 2


def test_cards_printing_no_magnitude_stay_out_of_the_mean():
    """A utility card is not a zero-damage card. Averaging it in as one would
    understate every band and invert the comparison the anchor is for."""
    cards = [_card("Hit", "Uncommon", 1, damage=10),
             _card("Utility", "Uncommon", 1)]
    band = census.magnitude_bands(cards)["Uncommon"]
    assert band["n"] == 2
    assert band["damage"]["n_printing"] == 1
    assert band["damage"]["coverage"] == 0.5
    assert band["damage"]["mean"] == 10.0


def test_zero_cost_cards_are_excluded_from_the_per_energy_rate():
    """A 0-cost body has no rate. Counting one as cost 1 would invent the
    premium; the census reports it as an exclusion instead."""
    cards = [_card("Free", "Uncommon", 0, damage=8),
             _card("Priced", "Uncommon", 2, damage=10)]
    dmg = census.magnitude_bands(cards)["Uncommon"]["damage"]
    assert dmg["n_printing"] == 2
    assert dmg["n_zero_cost_excluded"] == 1
    assert dmg["mean_per_energy"] == 5.0
    # The flat mean still sees both -- only the RATE drops the free card.
    assert dmg["mean"] == 9.0


def test_a_band_with_only_free_cards_reports_no_rate_rather_than_a_fake_one():
    cards = [_card("Free", "Rare", 0, block=50)]
    blk = census.magnitude_bands(cards)["Rare"]["block"]
    assert blk["mean"] == 50.0
    assert blk["mean_per_energy"] is None


def test_the_census_counts_exhaust_as_a_share_of_the_whole_pool():
    cards = [_card("A", "Uncommon", 1, keywords=("Exhaust",)),
             _card("B", "Uncommon", 1),
             _card("C", "Rare", 2, keywords=("Exhaust", "Retain")),
             _card("D", "Rare", 0)]
    agg = census.census(cards)
    assert agg["pool_size"] == 4
    assert agg["by_rarity"] == {"Rare": 2, "Uncommon": 2}
    assert agg["exhaust_count"] == 2
    assert agg["exhaust_share"] == 0.5
    assert agg["keyword_counts"] == {"Exhaust": 2, "Retain": 1}
