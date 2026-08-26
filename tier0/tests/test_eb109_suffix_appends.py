"""EB-109 — the reachability read on the three `id + upgrades.SUFFIX` sites.

THE ROW'S OWN INSTRUCTION was to do the reachability read FIRST and only then
decide, because `refpowers._upgraded` (one of the two sites already fixed) had
a documented already-upgraded branch to fall into and these three might not.
The read, with its call chain, is recorded once in
`tools/lint_upgrade_suffix_appends.SITES` and the lint refuses to let it go
stale. The answers were:

  `_generate` (Stoke+)                 NOT reachable. `pick` is a deepcopy of
      `rng.choice(_generation_pool(...))` -- card-SHEET prototypes out of
      `get_pool` / `cards_in_pool`, whose ids are `_card_index()` keys. A mark
      is attached only by `enchantments.decorate`, and only onto a RUN DECK
      list, so a generation pool cannot hold one. Guarded by `has_upgrade`
      besides.

  `_op_add_card` (HiddenDaggers+ / StormOfSteel+)   NOT reachable. `cid` is
      the literal id printed on the card's own effect dict
      (`fx['card_id'] or fx['card']`), or a member of
      `loader.cards_in_pool(fx['pool'])` for Secret Stash. Both are sheet ids
      out of committed YAML; no deck-list id reaches the op.

  `_op_autoplay_from_exhaust` (KnifeTrap+)          REACHABLE, and it does not
      crash. `victims` are live instances off `p.exhaust_pile` -- real deck
      cards -- and `loader._card_prototype` sets `card.id` to the DECORATED
      id, so an exhausted enchanted card arrives with its mark on.

So nothing was fixed: a site that provably crashes on an enchanted card may be
repaired on the crashing path, and none of the three does. What the reachable
one does instead is pinned below, because "it happens to be fine" is a claim
that has to be measurable or it is just the previous author's confidence.

WHAT THIS FILE PINS is the ARITHMETIC of the two decorations -- the four id
shapes and what each does when the suffix is appended -- plus the one site
that meets a decorated id. The structural half (every append site declares its
reachability answer, and a new one fails) is the lint's, run here so a red
gate cannot hide behind a green suite.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tier0.content import enchantments, loader, upgrades
from tier0.engine import effects
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state

REPO = Path(loader.__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import lint_upgrade_suffix_appends as lint      # noqa: E402


def _upgradable_attack() -> str:
    for cid, card in sorted(loader._card_index().items()):
        if (upgrades.has_upgrade(cid) and card.type == "attack"
                and not card.kit_card and card.rarity != "curse"):
            return cid
    raise AssertionError("no upgradable attack on the sheet")


# ---------------------------------------------------------------------------
#  The four id shapes
# ---------------------------------------------------------------------------

def test_appending_the_suffix_to_an_enchanted_id_keeps_the_enchantment():
    """`x@sharp-2` -> `x@sharp-2+`. The mark rides INSIDE the suffix, which is
    the one spelling `enchantments.split` round-trips, so the plain append
    happens to land on it correctly -- and the rider survives."""
    cid = _upgradable_attack()
    enchanted = enchantments.decorate(cid, "sharp", 2)
    card = loader.get_card(enchanted + upgrades.SUFFIX)
    assert card.id == enchanted + upgrades.SUFFIX
    assert card.enchant_damage == 2
    assert upgrades.SUFFIX in card.name


def test_an_enchanted_id_with_no_amount_appends_the_same_way():
    cid = _upgradable_attack()
    enchanted = enchantments.decorate(cid, "perfect_fit")
    card = loader.get_card(enchanted + upgrades.SUFFIX)
    assert card.enchant_top_of_draw is True


def test_an_already_upgraded_enchanted_id_raises_a_value_error():
    """`x@sharp-2+` + `+` puts the second suffix INSIDE the decoration, so
    `split` reaches `int('2+')` before the card index is ever consulted. This
    is the throw that killed Aggression's recall, and the reason a site that
    only expected a KeyError miss was not enough."""
    cid = _upgradable_attack()
    both = enchantments.decorate(cid + upgrades.SUFFIX, "sharp", 2)
    with pytest.raises(ValueError):
        loader.get_card(both + upgrades.SUFFIX)


def test_an_already_upgraded_plain_id_raises_a_key_error():
    """The undecorated twin of the case above, and the shape every one of
    these sites was written against."""
    cid = _upgradable_attack()
    with pytest.raises(KeyError):
        loader.get_card(cid + upgrades.SUFFIX + upgrades.SUFFIX)


def test_has_upgrade_is_the_enchant_aware_predicate():
    """Why `has_upgrade` counts as a guard in the lint's table: it splits the
    mark off AND refuses an id already ending in the suffix, so both throwing
    shapes are filtered before any append."""
    cid = _upgradable_attack()
    assert upgrades.has_upgrade(enchantments.decorate(cid, "sharp", 2))
    assert not upgrades.has_upgrade(cid + upgrades.SUFFIX)
    assert not upgrades.has_upgrade(
        enchantments.decorate(cid + upgrades.SUFFIX, "sharp", 2))


# ---------------------------------------------------------------------------
#  The one reachable site, on the id shape that reaches it
# ---------------------------------------------------------------------------

def _autoplay(state, victim: Card) -> None:
    state.player.exhaust_pile.append(victim)
    effects._op_autoplay_from_exhaust(
        state, {"op": "autoplay_from_exhaust", "upgrade_first": True},
        Card(id="knife_trap_like", name="probe", cost=2, type="skill",
             effects=[]))


def test_the_reachable_site_upgrades_an_enchanted_victim_and_keeps_the_rider():
    state = make_state([make_enemy(hp=200)])
    cid = _upgradable_attack()
    victim = loader.get_card(enchantments.decorate(cid, "sharp", 2))
    _autoplay(state, victim)
    played = [e for e in state.log if e.get("event") == "autoplay_from_exhaust"]
    assert played, state.log
    assert played[-1]["card"] == cid + "@sharp-2" + upgrades.SUFFIX


def test_the_reachable_site_degrades_rather_than_dying_on_an_upgraded_one():
    """An already-upgraded enchanted victim throws the `int('2+')` ValueError,
    which this site's pre-existing `except (KeyError, ValueError)` catches: it
    logs UNIMPLEMENTED and plays the victim as it stands, which is what an
    already-upgraded card should do and exactly what the undecorated `x++`
    KeyError already did. No crash, and so nothing to fix here."""
    state = make_state([make_enemy(hp=200)])
    cid = _upgradable_attack()
    both = enchantments.decorate(cid + upgrades.SUFFIX, "sharp", 2)
    _autoplay(state, loader.get_card(both))
    unimpl = [e for e in state.log
              if e.get("event") == "UNIMPLEMENTED"
              and e.get("op") == "autoplay_from_exhaust"]
    assert unimpl, state.log
    played = [e for e in state.log if e.get("event") == "autoplay_from_exhaust"]
    assert played[-1]["card"] == both


# ---------------------------------------------------------------------------
#  The structural half
# ---------------------------------------------------------------------------

def test_the_append_site_lint_passes():
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" /
                             "lint_upgrade_suffix_appends.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "site(s)" in res.stdout, res.stdout


def test_the_three_sites_the_row_names_all_carry_an_answer():
    keys = {(p, f) for (p, f, _) in lint.SITES}
    for func in ("_generate", "_op_add_card", "_op_autoplay_from_exhaust"):
        assert ("tier0/engine/effects.py", func) in keys, func
    reach = {f: r["reach"] for (p, f, _), r in lint.SITES.items()
             if p == "tier0/engine/effects.py"}
    assert reach == {"_generate": "sheet", "_op_add_card": "sheet",
                     "_op_autoplay_from_exhaust": "deck"}, reach
