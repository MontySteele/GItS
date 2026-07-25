"""Event pools for acts 2-3, and the grammar they needed (§11.2).

Two kinds of test here, and the first kind matters more.

VALIDATION (`test_every_option_is_expressible` and friends) walks the whole
pool file and asserts that every id it names actually resolves -- curses,
event cards, event relics, escalation targets. The event pool is content, and
content rots silently: a renamed curse or a typo'd relic id would otherwise
surface as a mid-run KeyError on one seed in a thousand, or worse, as an
option that quietly does nothing. This is the file's real job.

BEHAVIOUR tests pin the ops the new content needed. The valuation constants
they exercise are deliberately NOT pinned to specific choices -- the policy is
a declared confounder (events.py header), so a test that froze "which option
the pilot takes" would be pinning the confounder rather than the mechanic.
The exception is `test_ladders_are_reachable`, which pins a property, not a
preference: an escalating ladder must be climbable at all, because the
myopic valuation this replaced made every ladder dead content.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier05 import events, relics as relic_pool


def _st(**kw):
    base = dict(character="ref_ironclad", archetype="generic", hp=70,
                max_hp=80, gold=200, deck_ids=_deck())
    base.update(kw)
    return events.EventState(**base)


def _deck(n=8):
    ids = sorted(loader.character_packages("ref_ironclad")
                 .get("archetype_package", []))
    return (ids * 3)[:n]


def _all_events():
    raw = events._pool()
    return [e for section in raw.values() for e in section]


def _all_options():
    return [(e, o) for e in _all_events() for o in events.options_of(e)]


# --- validation: every id the content names must resolve -------------------

def test_every_named_card_exists():
    for _, opt in _all_options():
        for key in ("curse", "add_card"):
            if opt.get(key):
                assert loader.peek_card(opt[key]) is not None


def test_every_named_relic_is_in_the_event_pool():
    """`relic_id` may only name an EVENT-pool relic. Pointing it at a common
    relic would make that relic reachable twice -- as loot and as a guaranteed
    event payout -- which is not how any of these events work."""
    pool = relic_pool.event_pool()
    named = [o["relic_id"] for _, o in _all_options() if o.get("relic_id")]
    assert named, "no event relic is referenced; the pool wiring is untested"
    for rid in named:
        assert rid in pool, f"{rid} is not an event-pool relic"
        assert relic_pool.get_relic(rid)["effects"]


def test_event_relics_are_never_loot():
    """The closed pool stays closed: no roll, Neow offer or Ancient offer can
    produce one. If this fails, every run silently gained a relic tier."""
    ids = set(relic_pool.event_pool())
    assert ids
    assert not ids & set(relic_pool.common_pool())
    assert not ids & set(relic_pool.neow_pool())
    assert not ids & set(relic_pool.ancient_pool())
    assert not ids & set(relic_pool.unowned_common([], "ref_ironclad"))


def test_every_escalation_target_exists_and_is_hidden():
    for _, opt in _all_options():
        nxt = opt.get("escalate")
        if not nxt:
            continue
        target = events.get_event(nxt)
        assert target.get("hidden"), f"{nxt} is escalate-only but rollable"


def test_hidden_stages_are_never_rolled_directly():
    for act in range(3):
        for e in events.pool_for(act):
            assert not e.get("hidden")


def test_event_ids_are_unique():
    ids = [e["id"] for e in _all_events()]
    assert len(ids) == len(set(ids))


def test_variant_events_declare_no_bare_options():
    """`variants` and `options` are alternatives. An event carrying both would
    have half its content silently unreachable -- materialize() overwrites
    `options` with the rolled variant's."""
    for e in _all_events():
        if "variants" in e:
            assert "options" not in e
            assert len(e["variants"]) >= 2
            for v in e["variants"]:
                assert v["options"] and v.get("name")


def test_acts_2_and_3_have_pools():
    """The §11 ship left both empty; an Unknown that rolled `event` there
    found nothing and passed. This is the regression guard for that."""
    for act in (1, 2):
        pool = events.pool_for(act)
        assert len(pool) >= 5, f"act {act + 1} pool is {len(pool)}"
        own = {e["id"] for e in (events._pool().get(f"act{act + 1}") or [])}
        assert own, f"act {act + 1} has no events of its own"


def test_also_acts_widens_without_duplicating():
    """A shared event appears in every act it declares, exactly once each."""
    for act in (0, 1):
        ids = [e["id"] for e in events.pool_for(act)]
        assert ids.count("brain_leech") == 1
        assert ids.count("room_full_of_cheese") == 1
    assert "brain_leech" not in [e["id"] for e in events.pool_for(2)]


# --- the ops acts 2-3 needed ----------------------------------------------

def test_ladders_are_reachable():
    """The escalate lookahead, as a PROPERTY: a ladder whose rungs each cost
    something and pay later must be climbable. With the old myopic valuation
    Colossal Flower's "Reach Deeper" scored as a pure -5 HP and the run could
    never reach levels 2-3 at all."""
    st = _st()
    ev = events.get_event("colossal_flower")
    deeper = [o for o in ev["options"] if o.get("escalate")][0]
    surface = [o for o in ev["options"] if not o.get("escalate")][0]
    assert events.option_value(deeper, st) > events.option_value(surface, st)


def test_lookahead_terminates_on_the_deepest_ladder():
    st = _st()
    for eid in ("tablet_of_truth", "colossal_flower"):
        for o in events.get_event(eid)["options"]:
            assert isinstance(events.option_value(o, st), float)


def test_random_card_filters_the_pool():
    st = _st()
    ev = events.get_event("infested_automaton")
    study = [o for o in ev["options"] if o["label"] == "Study"][0]
    before = len(st.deck_ids)
    events.resolve(random.Random(0), ev, study, st)
    assert len(st.deck_ids) == before + 1
    assert loader.peek_card(st.deck_ids[-1]).type == "power"


def test_random_card_option_locks_when_nothing_matches(monkeypatch):
    st = _st()
    ev = events.get_event("infested_automaton")
    monkeypatch.setattr(events, "_filtered_pool", lambda s, spec: [])
    assert events.available(ev, st) == []
    assert events.choose(random.Random(0), ev, st) is None


def test_add_card_adds_exactly_that_card():
    st = _st()
    ev = events.get_event("bugslayer")
    opt = ev["options"][1]                     # Squash
    events.resolve(random.Random(0), ev, opt, st)
    assert st.deck_ids[-1] == "squash"


def test_event_cards_are_never_offered_as_loot():
    """exterminate/squash are colorless event cards. If they leaked into a
    character's reward pool they would be free uncommons for everyone."""
    from tier05 import rewards
    for ch in ("ref_ironclad", "klee", "furina"):
        ids = {c.id for cs in rewards.character_pool(ch).values() for c in cs}
        assert not ids & {"exterminate", "squash"}


def test_downgrade_then_upgrade_order():
    """Reflections states downgrade first, so an upgraded card may be knocked
    down and picked straight back up. The test pins the ORDER by checking the
    downgrade can be undone -- if upgrades ran first the count could only
    fall."""
    up = [cid + upgrades.SUFFIX for cid in _deck(6)
          if upgrades.has_upgrade(cid)]
    if not up:
        pytest.skip("anchor package has no upgrade paths loaded")
    st = _st(deck_ids=list(up))
    ev = events.get_event("reflections")
    opt = ev["options"][0]
    events.resolve(random.Random(1), ev, opt, st)
    assert sum(1 for c in st.deck_ids if c.endswith(upgrades.SUFFIX)) == len(up)


def test_duplicate_deck_copies_before_the_curse_lands():
    st = _st(deck_ids=_deck(6))
    n = len(st.deck_ids)
    ev = events.get_event("reflections")
    shatter = ev["options"][1]
    events.resolve(random.Random(2), ev, shatter, st)
    assert len(st.deck_ids) == 2 * n + 1          # doubled, then ONE curse
    assert st.deck_ids.count("curse_bad_luck") == 1


def test_card_screens_are_independent_draws():
    st = _st(deck_ids=_deck(4))
    n = len(st.deck_ids)
    ev = {"id": "x", "options": [{"label": "two", "card_screens": 2}]}
    events.resolve(random.Random(3), ev, ev["options"][0], st)
    assert len(st.deck_ids) == n + 2


def test_relic_count_grants_that_many():
    held = relic_pool.HeldRelics.empty("ref_ironclad")
    st = _st()
    ev = {"id": "x", "options": [{"label": "two", "relic": 2}]}
    events.resolve(random.Random(4), ev, ev["options"][0], st, held=held)
    assert len(st.relics_granted) == 2
    assert len(set(st.relics_granted)) == 2       # distinct: held gates rerolls


def test_named_relic_grant_is_not_duplicated():
    held = relic_pool.HeldRelics.empty("ref_ironclad")
    st = _st()
    ev = {"id": "x", "options": [{"label": "core",
                                  "relic_id": "pollinous_core"}]}
    for _ in range(2):
        events.resolve(random.Random(5), ev, ev["options"][0], st, held=held)
    assert st.relics_granted == ["pollinous_core"]


# --- variants --------------------------------------------------------------

def test_every_variant_is_reachable_and_only_one_per_visit():
    ev = events.get_event("the_trial")
    seen = set()
    for s in range(200):
        got = events.materialize(random.Random(s), ev)
        assert len(got["options"]) == 2       # ONE trial, not all three
        seen.add(got["variant"])
    assert len(seen) == len(ev["variants"])


def test_variant_is_recorded_in_the_log():
    st = _st()
    held = relic_pool.HeldRelics.empty("ref_ironclad")
    events.visit(random.Random(0), 2, st, set(), held=held)
    trial = [e for e in st.log if e["event"] == "the_trial"]
    for entry in trial:
        assert entry.get("variant")


# --- the derived gold rate -------------------------------------------------

def test_gold_rate_matches_the_shops_own_prices():
    """GOLD_PER_HP is derived from the shop, not chosen. If someone retunes
    CARD_HP or RELIC_HP without revisiting it, the file starts contradicting
    itself again -- which is exactly the bug this replaced."""
    assert C.SHOP_CARD_PRICE / events.CARD_HP == events.GOLD_PER_HP
    assert C.SHOP_RELIC_PRICE / events.RELIC_HP == events.GOLD_PER_HP


# --- integration -----------------------------------------------------------

@pytest.mark.parametrize("act", [0, 1, 2])
def test_every_event_in_every_act_resolves(act):
    """Exhaust each act's pool repeatedly. Catches an option that references
    a missing id only on the seed that picks it."""
    for s in range(60):
        rng = random.Random(s)
        held = relic_pool.HeldRelics.empty("ref_ironclad")
        st = _st(gold=400)
        seen = set()
        for _ in range(len(events.pool_for(act))):
            events.visit(rng, act, st, seen, held=held)
            if st.hp <= 0:
                break
        assert st.max_hp >= 1
        for cid in st.deck_ids:
            assert loader.peek_card(cid) is not None
