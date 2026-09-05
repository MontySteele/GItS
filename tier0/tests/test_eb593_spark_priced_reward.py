"""`EB-593`: a reward whose first option is a Spark-priced row is one action.

THE FIND (Klee soak on `0.2.2817+proto`, soak-20260905-161901 lane 1, seed
C55QYVTU8F1U). The floor-2 card reward opened Fwoosh! / Run Away! / Flame
Dance -- `EB-577`'s offer rule had put the Spark-priced row first -- and the
soak cycled `card_reward` and `rewards` for twelve posted actions before the
watchdog filed `no_progress` and stopped the run at floor 2.

THE CYCLE ITSELF WAS THE GAME'S (`EB-594`): the swap handed the screen a
CANONICAL model, and serialising the pick threw `CanonicalModelException`, so
the pilot's perfectly good action never landed. That is fixed in
`SparkSeededReward.cs` and pinned in `SparkSeededRewardTests`.

WHAT WAS THE PILOT'S, and is what this file pins. Replayed headlessly against
the soak's own `state_dump`, every offer on that screen came back APPROXIMATE:

    KLEEMOD-PROTO_KO_FWOOSH -> approx=True, cost 1, effects [damage 6]

`peek_card` answers a `proto_` id only through `_card_prototype`'s FLAGGED
door, and the pilot runs with the sim's constants at their shipped defaults, so
on a `+proto` build every arm row on every screen fell through to the text
approximation. Two consequences, both real:

  * A SPARK PRICE IS NOT ENERGY 0. The wire's `cost` is the ENERGY cost and a
    Spark-priced card prints `"0"` there; the row's real price is a
    `spend_spark` effect the approximation cannot see. Fwoosh! scored 2.8 as a
    free 6-damage Attack, the best card on the screen. Read exactly it scores
    -0.83, because the deck holds no Spark income yet.
  * `_choice_overlay` REFUSES an approximation, so Kokomi's soak of the same
    build (soak-20260905-161950 lane 1) took all three of its `forced_defaults`
    on screens whose options the resolver could not read: an `enchant` screen
    of four `STRIKE_SILENT` plus Slack Water (decision 33), and a Room Full of
    Cheese "Gorge" screen of eight `proto_kk_` rows (decisions 38 and 39).
    Neither was a scored pick; both were "the first untoggled option, FLAGGED".

Both are `adapter.resolve_card`'s, and `EB-572` widened the same function one
step earlier for the same reason.
"""

from __future__ import annotations

import copy

import pytest

from tier0.content import loader
from understudy import adapter, policy_v1

#: The three offers, verbatim from the soak's `defect` record `state_dump`.
FWOOSH = {"id": "KLEEMOD-PROTO_KO_FWOOSH", "name": "Fwoosh!", "type": "Attack",
          "cost": "0", "star_cost": None, "rarity": "Common",
          "is_upgraded": False, "index": 0,
          "description": "Set off. Deal 6 damage."}
RUN_AWAY = {"id": "KLEEMOD-PROTO_KO_RUN_AWAY", "name": "Run Away!",
            "type": "Skill", "cost": "0", "star_cost": None,
            "rarity": "Common", "is_upgraded": False, "index": 1,
            "description": "Gain 3 Block. If a Bomb went off this turn, gain "
                           "4 additional Block."}
FLAME_DANCE = {"id": "KLEEMOD-PROTO_KO_FLAME_DANCE", "name": "Flame Dance",
               "type": "Attack", "cost": "1", "star_cost": None,
               "rarity": "Uncommon", "is_upgraded": False, "index": 2,
               "description": "Set off each enemy whose aura is not Pyro. "
                              "Deal 5 damage to ALL enemies."}

REWARD = {
    "state_type": "card_reward",
    "card_reward": {"cards": [FWOOSH, RUN_AWAY, FLAME_DANCE],
                    "can_skip": True},
    "run": {"act": 1, "floor": 2, "ascension": 0},
    "player": {"character": "Klee", "hp": 56, "max_hp": 62, "block": 0,
               "gold": 118, "status": [], "potions": [],
               "relics": [{"id": "KLEEMOD-POUNDING_SURPRISE",
                           "name": "Pounding Surprise",
                           "description": "Whenever a Bomb goes off, gain 1 "
                                          "Spark."}]},
}

#: Kokomi's two screens, same build, same resolver.
STRIKE_SILENT = {"id": "STRIKE_SILENT", "name": "Strike", "type": "Attack",
                 "cost": "1", "rarity": "basic",
                 "description": "Deal 6 damage."}
SLACK_WATER = {"id": "KLEEMOD-PROTO_KK_SLACK_WATER", "name": "Slack Water",
               "type": "Skill", "cost": "1", "rarity": "basic",
               "description": "Gain 5 Block."}
GORGE_ROWS = [{"id": f"KLEEMOD-PROTO_KK_{n.upper()}",
               "name": n.replace("_", " ").title(), "type": "Skill",
               "cost": "1", "rarity": "common", "description": ""}
              for n in ("ambush", "tide_chart", "riptide", "deep_current",
                        "change_of_plans", "exposed_flank", "pincer",
                        "ripple")]


def _select_screen(cards, screen_type, prompt=""):
    return {"state_type": "card_select",
            "card_select": {"screen_type": screen_type, "prompt": prompt,
                            "cards": cards, "can_confirm": False},
            "player": {"hp": 70, "max_hp": 70, "character": "Kokomi"}}


# --- 1. THE ROWS RESOLVE, AND A SPARK PRICE IS NOT ENERGY 0 ----------------

def test_every_offer_on_that_screen_resolves_to_its_sheet_row_exactly():
    for entry, sid in ((FWOOSH, "proto_ko_fwoosh"),
                       (RUN_AWAY, "proto_ko_run_away"),
                       (FLAME_DANCE, "proto_ko_flame_dance")):
        card, approx = adapter.resolve_card(entry)
        assert card.id == sid
        assert approx is False, (
            f"{sid} came back approximate; the pilot only ever reads a "
            "`proto_` id off a build that has the arm compiled in")


def test_the_spark_price_is_an_effect_and_the_energy_cost_really_is_zero():
    """Which is the whole confusion the row is named for. The wire prints
    `"cost": "0"` because Sparks are not Energy; the price is on the row."""
    card, _ = adapter.resolve_card(FWOOSH)
    assert card.cost == 0
    assert any(e.get("op") == "spend_spark" for e in card.effects)


def test_a_wire_cost_of_zero_is_zero_even_when_the_row_is_approximated():
    """`_text_card` read `isinstance(cost, int)` and the wire sends a STRING,
    so every approximated card on an out-of-combat screen was priced at 1."""
    free, approx = adapter.resolve_card(
        {"id": "SOME_BASE_CARD_NOBODY_MAPPED", "name": "Freebie", "cost": "0",
         "description": "Deal 4 damage."})
    assert approx is True and free.cost == 0
    unstated, _ = adapter.resolve_card(
        {"id": "SOME_BASE_CARD_NOBODY_MAPPED", "name": "X", "cost": "X"})
    assert unstated.cost == 1        # the conservative guess, unchanged


# --- 2. THE SCREEN IS ONE ACTION -------------------------------------------

def test_the_reward_is_picked_or_skipped_in_one_action():
    """THE ACCEPTANCE CONDITION. The soak posted twelve actions at this screen;
    the pilot's answer to it is ONE, and it is one of the two verbs a card
    reward has."""
    decision = policy_v1.decide(copy.deepcopy(REWARD))
    assert decision.available
    verb = decision.action["action"]
    assert verb in ("select_card_reward", "skip_card_reward")
    if verb == "select_card_reward":
        assert decision.action["card_index"] in (0, 1, 2)
    assert not (decision.notes or {}).get("forced_default")
    assert not (decision.notes or {}).get("approximate_offers")


def test_the_same_screen_twice_is_the_same_action():
    """A screen the game does not leave is a screen the pilot is asked about
    again, so an answer that oscillated would cycle even with the game fixed."""
    first = policy_v1.decide(copy.deepcopy(REWARD))
    second = policy_v1.decide(copy.deepcopy(REWARD))
    assert first.action == second.action


def test_read_exactly_the_spark_row_is_not_the_best_card_on_the_screen():
    """Not a taste claim -- a claim about WHICH ROW WAS SCORED. Approximated,
    Fwoosh! was a free 6-damage Attack and won the screen at 2.8. Its real row
    spends a Spark the deck cannot yet make."""
    decision = policy_v1.decide(copy.deepcopy(REWARD))
    assert "Fwoosh!" in decision.rationale
    assert decision.action != {"action": "select_card_reward", "card_index": 0}


def test_with_the_surface_unreachable_it_is_the_soaks_own_reading(monkeypatch):
    """Seen to FAIL. With no prototype row resolvable the offers go back to
    text stubs, which is the state the soak was in."""
    monkeypatch.setattr(loader, "_prototype_index", lambda: {})
    decision = policy_v1.decide(copy.deepcopy(REWARD))
    assert sorted((decision.notes or {}).get("approximate_offers") or []) == [
        "Flame Dance", "Fwoosh!", "Run Away!"]


# --- 3. KOKOMI'S THREE FORCED DEFAULTS -------------------------------------

@pytest.mark.parametrize("cards,screen,prompt", [
    ([STRIKE_SILENT] * 4 + [SLACK_WATER], "enchant",
     "Choose a card to Enchant."),
    (GORGE_ROWS, "simple_select", "Choose 2 Common Cards to Add to Your Deck."),
])
def test_kokomis_screens_are_scored_picks_and_not_forced_defaults(
        cards, screen, prompt):
    decision = policy_v1.decide(_select_screen(cards, screen, prompt))
    assert decision.available
    assert decision.action["action"] == "select_card"
    assert not (decision.notes or {}).get("forced_default")
    assert (decision.notes or {}).get("basis") == "score_offer"


def test_the_silent_basics_are_the_pair_the_kokomi_arm_ships():
    """Read off the constant rather than retyped -- `EB-572`'s own rule for
    the Ironclad pair, one starter over."""
    from tier0 import constants as C

    base = {cid for cid in C.KOKOMI_OVERHAUL_STARTER_IDS
            if not cid.startswith("proto_")}
    assert base <= set(adapter.BASE_CARD_IDS.values())
    assert adapter.resolve_card(STRIKE_SILENT)[1] is False
