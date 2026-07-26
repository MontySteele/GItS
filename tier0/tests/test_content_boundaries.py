"""Content-boundary validation, un-inverted.

Audit sec.5: "the two smallest content files (potions, relics) validate loudly;
the two largest (events 340 L, act pools 720 L) read every key through
`.get()`". Plus the sheet half: a misspelled `op:` or `if:` loaded fine and
raised the first time the card resolved -- which, for a rare, means in front of
a player rather than in a test, and on the co-op seat there is no simulator
backstop at all.

Three guards, one idea. Each of the new allowlists is only worth having if it
cannot drift away from the reader it claims to describe, so every one of them
is checked against the code in BOTH directions:

  * a name the code accepts but the allowlist omits  -> the validator rejects
    valid content
  * a name the allowlist carries but the code ignores -> the allowlist
    documents a key nothing reads, which is the defect it was built to catch

The negative tests below are as load-bearing as the positive ones: an
allowlist validator that never rejects anything passes silently forever.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from tier0.content import loader
from tier0.engine import effects
from tier05 import acts, events

ROOT = Path(__file__).resolve().parents[2]
EFFECTS_SRC = (ROOT / "tier0" / "engine" / "effects.py").read_text(
    encoding="utf-8")


# =========================================================================
# 1. Sheet op / predicate names, validated at LOAD
# =========================================================================

def _predicate_chain_source() -> str:
    body = EFFECTS_SRC[EFFECTS_SRC.index("def _predicate("):]
    return body[:body.index("\ndef ")]


def test_predicate_registry_matches_the_if_chain_exactly():
    """`PREDICATE_NAMES` is data mirroring code; nothing stops it rotting.

    So it is derived from the chain here and compared, rather than trusted.
    A predicate added to `_predicate` without being registered would load-
    validate as a typo and reject a legitimate card.
    """
    src = _predicate_chain_source()
    exact = set(re.findall(r'name == "([a-z_]+)"', src))
    prefixes = set(re.findall(r'name\.startswith\("([a-z_]+)"\)', src))
    assert exact == set(effects.PREDICATE_NAMES), (
        f"chain-only: {sorted(exact - set(effects.PREDICATE_NAMES))}, "
        f"registry-only: {sorted(set(effects.PREDICATE_NAMES) - exact)}")
    assert prefixes == set(effects.PREDICATE_PREFIXES), (
        f"chain-only: {sorted(prefixes - set(effects.PREDICATE_PREFIXES))}, "
        f"registry-only: {sorted(set(effects.PREDICATE_PREFIXES) - prefixes)}")


def test_every_shipped_card_passes_the_vocabulary_check():
    """The positive control: 367 cards of real content, all valid."""
    index = loader._card_index()
    assert len(index) > 300, "suspiciously small card index"
    for cid, card in index.items():
        loader._validate_effect_vocabulary(cid, card.effects)


def test_a_misspelled_op_is_rejected_at_load_not_at_play():
    with pytest.raises(ValueError, match="unknown op"):
        loader._validate_effect_vocabulary(
            "probe", [{"op": "damgae", "amount": 5}])


def test_a_misspelled_predicate_is_rejected_at_load():
    with pytest.raises(ValueError, match="unknown predicate"):
        loader._validate_effect_vocabulary(
            "probe", [{"op": "conditional", "if": "has_sparks",
                       "then": [{"op": "draw", "amount": 1}]}])


def test_validation_recurses_into_conditional_branches():
    """An unreachable-today branch is where a typo survives longest."""
    with pytest.raises(ValueError, match="unknown op"):
        loader._validate_effect_vocabulary(
            "probe", [{"op": "conditional", "if": "has_spark",
                       "then": [{"op": "draw", "amount": 1}],
                       "else": [{"op": "no_such_op"}]}])


def test_parameterised_predicates_must_carry_a_real_argument():
    """`fanfare_at_least_ten` used to pass a name check and die in int()."""
    assert effects.is_known_predicate("fanfare_at_least_10")
    assert not effects.is_known_predicate("fanfare_at_least_ten")
    assert not effects.is_known_predicate("fanfare_at_least_")
    # target_has_power_ takes a power NAME, so any suffix is legal by design.
    assert effects.is_known_predicate("target_has_power_vulnerable")


# =========================================================================
# 2. events.yaml key allowlist
# =========================================================================

def test_event_allowlists_cover_the_shipped_pool_with_nothing_spare():
    """Both directions, so the allowlist can neither reject nor rot."""
    raw = yaml.safe_load(
        (ROOT / "tier05" / "content" / "events.yaml").read_text(
            encoding="utf-8"))
    seen_event, seen_option = set(), set()
    for evs in raw.values():
        for ev in evs or []:
            seen_event.update(ev)
            for body in (ev.get("variants") or [ev]):
                for opt in body.get("options") or []:
                    seen_option.update(opt)

    assert seen_event <= events.EVENT_KEYS, sorted(seen_event - events.EVENT_KEYS)
    assert seen_option <= events.OPTION_KEYS, \
        sorted(seen_option - events.OPTION_KEYS)

    # The rot direction. `card_screens` is documented grammar the reader
    # honours but no shipped event uses yet, so it is allowed to be spare;
    # anything ELSE spare means a key was invented and never wired.
    spare = events.OPTION_KEYS - seen_option - {"card_screens"}
    assert not spare, (
        f"OPTION_KEYS carries {sorted(spare)}, used by no shipped event -- "
        "either wire it or drop it")


def test_every_allowed_option_key_is_actually_read_by_events_py():
    src = (ROOT / "tier05" / "events.py").read_text(encoding="utf-8")
    unread = [k for k in events.OPTION_KEYS
              if f'"{k}"' not in src.split("OPTION_KEYS = frozenset({")[1]
              .split("})", 1)[1]]
    assert not unread, (
        f"OPTION_KEYS names {sorted(unread)}, which events.py never reads -- "
        "an allowlisted key nothing consumes is the silent no-op this guard "
        "exists to prevent")


def test_an_unknown_event_key_is_rejected():
    with pytest.raises(ValueError, match="unknown key"):
        events._validate_pool(
            {"act1": [{"id": "probe", "name": "P", "hiden": True,
                       "options": []}]})


def test_an_unknown_option_key_is_rejected():
    with pytest.raises(ValueError, match="unknown key"):
        events._validate_pool(
            {"act1": [{"id": "probe", "name": "P",
                       "options": [{"label": "x", "heal_frac_": 1.0}]}]})


def test_option_validation_reaches_inside_variants():
    with pytest.raises(ValueError, match="unknown key"):
        events._validate_pool(
            {"act1": [{"id": "probe", "name": "P",
                       "variants": [{"options": [{"gld": 5}]}]}]})


# =========================================================================
# 3. act-pool key allowlist
# =========================================================================

POOL_FILES = ["act1_pool.yaml", "act2_pool.yaml", "act3_pool.yaml"]


@pytest.mark.parametrize("pool_file", POOL_FILES)
def test_shipped_act_pools_validate(pool_file):
    assert acts._load(pool_file)


def test_act_allowlists_carry_nothing_the_pools_do_not_use():
    """The rot direction, across all three acts at once."""
    seen_enc, seen_enemy, seen_intent = set(), set(), set()
    for pool_file in POOL_FILES:
        for encounters in acts._load(pool_file).values():
            for enc in encounters:
                seen_enc.update(enc)
                for enemy in enc.get("enemies") or []:
                    seen_enemy.update(enemy)
                    for intent in enemy.get("intents") or []:
                        seen_intent.update(intent)
    assert acts.ENCOUNTER_KEYS - seen_enc == set()
    assert acts.ENEMY_KEYS - seen_enemy == set()
    assert acts.INTENT_KEYS - seen_intent == set()


def test_the_audits_own_typo_is_now_loud():
    """`is_bos: true` -- a non-boss boss with no signal anywhere."""
    with pytest.raises(ValueError, match=r"unknown key\(s\) \['is_bos'\]"):
        acts._validate_pool("probe.yaml", {"boss": [
            {"id": "p", "name": "P",
             "enemies": [{"name": "p", "hp": 10, "is_bos": True}]}]})


def test_an_unknown_intent_key_is_rejected():
    with pytest.raises(ValueError, match="unknown key"):
        acts._validate_pool("probe.yaml", {"easy": [
            {"id": "p", "name": "P", "enemies": [
                {"name": "p", "hp": 10,
                 "intents": [{"kind": "attack", "ammount": 5}]}]}]})


def test_an_unknown_pool_tier_is_rejected():
    with pytest.raises(ValueError, match="unknown pool tier"):
        acts._validate_pool("probe.yaml", {"medium": []})
