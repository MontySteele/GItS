"""EB-118: the card-connectivity instrument's pins.

Four things are held here, and each one is a way the tool could quietly
become wrong:

  1. ONE FIXTURE PER VOCABULARY ENTRY. Every shared and private state in
     `SHARED_STATES` / `PRIVATE_STATES` has a card that trips it and is
     asserted to trip it. An entry nobody can demonstrate is an entry
     nobody can trust.
  2. A RED FIXTURE. A plain 7-damage card must trip NOTHING -- no hook,
     no choice, no external reach, no automatic value. Every classifier
     that counts things can be made to look thorough by counting too
     much; this is the test that says it does not.
  3. NO SILENT ZEROES. The op table covers `effects.OPS` exactly, the
     live sheets classify with zero UNCLASSIFIED, and an unknown op,
     predicate, formula, count token, power, tag or card-level field
     comes back as UNCLASSIFIED rather than as nothing.
  4. THE HONEST STOP. `game_ref/` is gitignored: absent on a fresh clone
     and in a worktree, present in the main checkout. So the tool has two
     legitimate paths -- the mod-only diagnostic and the eight-pool
     comparison -- and the real invocation is pinned to whichever one
     this checkout can actually support. The canon reader is additionally
     exercised against a SYNTHETIC decompiled tree in a temp dir, so the
     canon half is covered either way.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tier0.engine import effects
from tools import card_connectivity_report as ccr
from tools import extract_base_game_pool as _extract

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _no_canon_dial_leak():
    """`extract.decompile_character` COMPLETES the tag-scoped power dial in
    place -- by design, at the one moment the power's decompiled source is
    readable. That mutation is a property of the extractor, not of this
    tool; but this suite is the first thing in the tier0 process to reach
    the canon reader, so without this the completed name leaks into every
    later test in the session (`test_extract_base_game_pool` asserts the
    COMMITTED dial holds only the prefix, and would fail on ordering
    alone). Snapshot and restore, so the side effect stays inside the
    test that provoked it."""
    saved = (dict(_extract.SUPPORTED_POWERS), dict(_extract.UPGRADE_POWER_KEY))
    try:
        yield
    finally:
        _extract.SUPPORTED_POWERS.clear()
        _extract.SUPPORTED_POWERS.update(saved[0])
        _extract.UPGRADE_POWER_KEY.clear()
        _extract.UPGRADE_POWER_KEY.update(saved[1])


def _row(**kwargs) -> dict:
    row = {"id": "fixture", "name": "Fixture", "cost": 1, "type": "skill",
           "rarity": "common", "solve": ["utility"],
           "tempo_band": {"fight": ["early"], "run": ["early"]},
           "archetypes": ["generic"], "role": "glue", "effects": []}
    row.update(kwargs)
    return row


def classify(row: dict, junk_rarity=None) -> dict:
    return ccr.classify_row(row, "fixture", junk_rarity)


def hooks_of(record: dict) -> set[tuple[str, str]]:
    return ({("shared", s) for s in record["shared_reads"]}
            | {("shared", s) for s in record["shared_writes"]}
            | {("private", s) for s in record["private_reads"]}
            | {("private", s) for s in record["private_writes"]})


# --- 1. one fixture per vocabulary entry, sheet side ------------------------
#
# Each entry is (row, the fixture's one-line reason). The reason is not
# decoration: it is what a reader checks the row against when the
# classifier moves.
SHEET_FIXTURES: dict[str, dict] = {
    "hp_ledger": _row(effects=[{"op": "damage", "amount": 3,
                                "target": "self"}]),
    "discard_chosen": _row(effects=[{"op": "discard", "amount": 1,
                                     "select": "chosen"}]),
    "discard_random": _row(effects=[{"op": "discard", "amount": 1}]),
    "exhaust_other_chosen": _row(effects=[{"op": "exhaust_from", "amount": 1,
                                           "select": "chosen"}]),
    "exhaust_other_random": _row(effects=[{"op": "exhaust_from",
                                           "amount": 1}]),
    "self_exhaust": _row(exhaust=True),
    "ethereal": _row(tags=["ethereal"]),
    "junk_create": _row(effects=[{"op": "add_card", "card": "junky",
                                  "zone": "discard"}]),
    "junk_remove": _row(effects=[{"op": "exhaust_from", "amount": 1,
                                  "filter": "status"}]),
    "hand_contents": _row(effects=[{"op": "draw", "amount": 1}]),
    "draw_pile": _row(effects=[{"op": "draw", "amount": 1}]),
    "discard_pile": _row(effects=[{"op": "discard", "amount": 1}]),
    "exhaust_pile": _row(effects=[{"op": "block", "amount": 1,
                                   "bonus_formula": {"base": 1, "per": 1,
                                                     "count": "exhaust_pile"}}]),
    "block_held": _row(effects=[{"op": "block", "amount": 5}]),
    "enemy_count": _row(effects=[{"op": "damage", "amount": 5,
                                  "target": "all_enemies"}]),
    "enemy_intent": _row(effects=[{"op": "conditional",
                                   "if": "enemy_intends_attack",
                                   "then": [{"op": "block", "amount": 3}]}]),
    "aura_reaction": _row(effects=[{"op": "apply_aura", "element": "hydro",
                                    "target": "enemy"}]),
    "plays_this_turn": _row(effects=[{"op": "block", "amount": 1,
                                      "bonus_formula":
                                      "2_per_companion_played_this_turn"}]),
    "card_identity": _row(effects=[{"op": "cost_mod", "delta": -1,
                                    "duration": "this_turn",
                                    "scope": "companion_cards"}]),
    "card_timing": _row(retain=True),
    "universal_verb_power": _row(effects=[{"op": "apply_power",
                                           "power": "feel_no_pain",
                                           "amount": 1, "target": "self"}]),
    "bombs": _row(effects=[{"op": "place_bomb", "amount": 1,
                            "target": "enemy", "bomb_damage": 5}]),
    "sparks": _row(effects=[{"op": "gain_spark", "amount": 1}]),
    "encore": _row(effects=[{"op": "gain_encore", "amount": 5}]),
    "fanfare": _row(effects=[{"op": "raise_fanfare_cap", "amount": 5}]),
    "salon": _row(effects=[{"op": "apply_power", "power": "salon_member",
                            "amount": 1, "target": "self",
                            "member": "usher"}]),
    "spotlight": _row(effects=[{"op": "spotlight_designate"}]),
    "charge": _row(effects=[{"op": "gain_charge", "amount": 2}]),
    "burst": _row(requires="burst_energy_full"),
    "conscript_sly": _row(effects=[{"op": "conscript", "amount": 1}]),
    "kurage": _row(effects=[{"op": "summon_kurage", "amount": 3}]),
}
# The three canon-side private states cannot be reached from a sheet row --
# no GItS card channels an Orb. Their fixtures are decompiled sources.
CANON_ONLY_STATES = ("orbs", "stars", "osty")


@pytest.mark.parametrize("state", sorted(SHEET_FIXTURES))
def test_every_sheet_vocabulary_entry_has_a_fixture_that_trips_it(state):
    record = classify(SHEET_FIXTURES[state],
                      junk_rarity=lambda cid: "status")
    scope = "shared" if state in ccr.SHARED_STATES else "private"
    assert (scope, state) in hooks_of(record), record
    assert not record["unclassified"], record["unclassified"]


def test_every_vocabulary_entry_is_covered_by_some_fixture():
    covered = set(SHEET_FIXTURES) | set(CANON_ONLY_STATES)
    missing = (set(ccr.SHARED_STATES) | set(ccr.PRIVATE_STATES)) - covered
    assert not missing, f"vocabulary entries with no fixture: {sorted(missing)}"


# --- 2. the red fixture -----------------------------------------------------

def test_red_fixture_trips_nothing():
    """A plain attack is connected to nothing and must read that way."""
    record = classify(_row(type="attack", effects=[
        {"op": "damage", "amount": 7, "target": "enemy"}]))
    assert hooks_of(record) == set()
    assert record["chosen_actions"] == []
    assert record["external_reach"] is False
    assert record["automatic_value"] is False
    assert record["random_damage"] is False
    assert record["random_placement"] is False
    assert record["unclassified"] == []


def test_red_fixture_survives_the_pool_derived_fields():
    """`competing_uses` and `automatic_only` must stay False for it too."""
    plain = _row(id="plain", type="attack",
                 effects=[{"op": "damage", "amount": 7, "target": "enemy"}])
    meter = _row(id="spender", effects=[{"op": "spend_encore", "amount": 3}])
    other = _row(id="spender2", effects=[{"op": "spend_encore", "amount": 1}])
    records = [classify(r) for r in (plain, meter, other)]
    ccr.pool_stats(records)
    by_id = {r["id"]: r for r in records}
    assert by_id["plain"]["competing_uses"] is False
    assert by_id["plain"]["automatic_only"] is False
    # ...while the two spenders DO contest the meter they both spend.
    assert by_id["spender"]["competing_uses"] is True


def test_target_choice_is_not_a_chosen_action():
    """Picking whom to hit is a target, and targets are excluded by the
    registration. Only non-target selections count."""
    record = classify(_row(type="attack", effects=[
        {"op": "damage", "amount": 7, "target": "all_enemies"}]))
    assert record["chosen_actions"] == []


# --- 3. no silent zeroes ----------------------------------------------------

def test_op_table_covers_the_engine_exactly():
    assert set(ccr.OP_HOOKS) == set(effects.OPS)


def test_every_live_sheet_row_classifies():
    for pool, records in ccr.mod_corpus().items():
        bad = [(r["id"], r["unclassified"]) for r in records
               if r["unclassified"]]
        assert not bad, f"{pool}: {bad}"


@pytest.mark.parametrize("row,expected", [
    (_row(effects=[{"op": "not_an_op"}]), "unknown op"),
    (_row(effects=[{"op": "conditional", "if": "moon_is_full",
                    "then": []}]), "unknown predicate"),
    (_row(effects=[{"op": "block", "amount": 1,
                    "bonus_formula": "9_per_nothing"}]), "formula"),
    (_row(effects=[{"op": "block", "amount": 1,
                    "bonus_formula": {"base": 1, "per": 1,
                                      "count": "moons"}}]), "count token"),
    (_row(effects=[{"op": "apply_power", "power": "hypnosis", "amount": 1,
                    "target": "self"}]), "unknown power"),
    (_row(tags=["glitter"]), "unknown tag"),
    (_row(mystery_field=True), "unknown card field"),
    (_row(requires="a_thing"), "requires"),
])
def test_unknown_vocabulary_is_unclassified_never_zero(row, expected):
    record = classify(row)
    assert any(expected in note for note in record["unclassified"]), record


def test_enemy_poison_total_is_unclassified_not_folded_in():
    """A real engine token with no vocabulary entry must SAY so."""
    record = classify(_row(effects=[
        {"op": "damage", "amount": 1, "target": "enemy",
         "bonus_formula": {"base": 1, "per": 1,
                           "count": "enemy_poison_total"}}]))
    assert any("enemy_poison_total" in note
               for note in record["unclassified"])


# --- the effect TREE, not the top level -------------------------------------

def test_hooks_inside_a_conditional_branch_are_seen():
    """The `sparkly_explosion` shape: the real mechanic is in `then:`."""
    row = _row(effects=[{"op": "conditional", "if": "killed_target",
                         "then": [{"op": "place_bomb", "amount": 1,
                                   "target": "enemy", "bomb_damage": 5}],
                         "else": [{"op": "gain_spark", "amount": 1}]}])
    record = classify(row)
    assert ("private", "bombs") in hooks_of(record)
    assert ("private", "sparks") in hooks_of(record)


def test_sly_riders_are_this_cards_connectivity():
    row = _row(sly=[{"op": "gain_charge", "amount": 1}])
    record = classify(row)
    assert ("private", "charge") in hooks_of(record)
    assert ("private", "conscript_sly") in hooks_of(record)


def test_sly_autoplay_marker_is_not_priced_as_an_op():
    row = _row(sly=[{"op": ccr.effect_walk.SLY_AUTOPLAY_OP}])
    record = classify(row)
    assert record["unclassified"] == []
    assert ("shared", "plays_this_turn") in hooks_of(record)


# --- 4. the canon path, against a SYNTHETIC tree ----------------------------
#
# This worktree has no `game_ref/`, on purpose (it is gitignored, and
# OPERATIONS forbids linking one in). The canon reader is therefore
# exercised against fixture files shaped like the real extraction surface:
# a `<Character>CardPool` type naming `ModelDb.Card<X>` types, each of
# which is a `CardModel` subclass -- exactly what
# `extract_base_game_pool.read_pool` reads.

CARD_NS = "MegaCrit.Sts2.Core.Models.Cards"
POOL_NS = "MegaCrit.Sts2.Core.Models.CardPools"

CANON_CARD = """namespace {ns};

public class {name} : CardModel
{{
    public {name}()
        : base({cost}, CardType.{ctype}, CardRarity.Common, TargetType.{target})
    {{
    }}

    public override async Task OnPlay(CardPlay cardPlay)
    {{
        {body}
    }}
}}
"""
CANON_POOL = """namespace {ns};

public class {character}CardPool : CardPoolModel
{{
    public override List<CardModel> Cards => new List<CardModel>
    {{
        {entries}
    }};
}}
"""


def _write_canon_tree(tmp_path: Path, bodies: dict[str, str],
                      characters=ccr.CANON_CHARACTERS,
                      extra: dict[str, str] | None = None) -> Path:
    """A decompiled-project-shaped tree holding `bodies` for every pool."""
    root = tmp_path / "tree"
    cards = root / "Cards"
    pools = root / "CardPools"
    cards.mkdir(parents=True)
    pools.mkdir(parents=True)
    for name, body in bodies.items():
        (cards / f"{name}.cs").write_text(
            CANON_CARD.format(ns=CARD_NS, name=name, cost=1, ctype="Attack",
                              target="Enemy", body=body), encoding="utf-8")
    for name, src in (extra or {}).items():
        (root / f"{name}.cs").write_text(src, encoding="utf-8")
    entries = "".join(f"ModelDb.Card<{name}>(), " for name in bodies)
    for character in characters:
        (pools / f"{character}CardPool.cs").write_text(
            CANON_POOL.format(ns=POOL_NS, character=character,
                              entries=entries), encoding="utf-8")
    return root


CANON_FIXTURES: dict[str, str] = {
    "hp_ledger": "CreatureCmd.Damage(base.Owner.Creature, 3);",
    "block_held": "CreatureCmd.GainBlock(base.Owner.Creature, 5);",
    "draw_pile": "CardPileCmd.Draw(base.CombatState, 1);",
    "hand_contents": "CardPileCmd.Draw(base.CombatState, 1);",
    "discard_pile": "CardCmd.Discard(base.CombatState, card);",
    "discard_chosen": "CardSelectCmd.FromHandForDiscard(base.CombatState, 1);"
                      " CardCmd.Discard(base.CombatState, card);",
    "discard_random": "CardCmd.Discard(base.CombatState, card);",
    "exhaust_pile": "CardCmd.Exhaust(base.CombatState, card);",
    "exhaust_other_chosen": "CardSelectCmd.FromHand(base.CombatState, 1); "
                            "CardCmd.Exhaust(base.CombatState, card);",
    "exhaust_other_random": "CardCmd.Exhaust(base.CombatState, card);",
    "enemy_count": "DamageCmd.Attack(base.CombatState.HittableEnemies, 5);",
    "plays_this_turn": "int n = base.CombatState.CardsPlayedThisTurnCount;",
    "card_identity": "CardCmd.Upgrade(item);",
    "card_timing": "int x = ResolveEnergyXValue();",
    # The junk axis needs TWO tokens agreeing, so its fixtures carry both.
    # Creation's WRITE side cannot be reached from a body at all -- it is
    # read off the created card's own model -- and has its own test below.
    "junk_create": "if (card.Type == CardType.Status) "
                   "{ AfterCardGeneratedForCombat(card, creator); }",
    "junk_remove": "foreach (CardModel c in hand.Where("
                   "(CardModel c) => c.Type == CardType.Status)) "
                   "{ await CardCmd.Exhaust(choiceContext, c); }",
    "enemy_intent": "if (target.Monster.NextMove.Intents.Any("
                    "(AbstractIntent i) => i.IntentType == IntentType.Attack))"
                    " { }",
    "orbs": "OrbCmd.Channel<LightningOrb>(base.CombatState, 1);",
    "stars": "ForgeCmd.Forge(base.CombatState, 1);",
    "osty": "OstyCmd.Summon(base.CombatState, 1);",
}


def _canon_record(src_body: str, keywords=(), reader=None) -> dict:
    from tools import extract_base_game_pool as extract
    src = CANON_CARD.format(ns=CARD_NS, name="Fixture", cost=1,
                            ctype="Attack", target="Enemy", body=src_body)
    if keywords:
        src += "\n" + "\n".join(f"// CardKeyword.{k}" for k in keywords)
    card = extract.parse_card(src, "Fixture")
    assert card is not None
    card["keywords"] = sorted(keywords) or card["keywords"]
    return ccr.classify_canon_card(card, src, "fixture", reader)


@pytest.mark.parametrize("state", sorted(CANON_FIXTURES))
def test_every_grounded_canon_entry_has_a_fixture_that_trips_it(state):
    record = _canon_record(CANON_FIXTURES[state])
    scope = "shared" if state in ccr.SHARED_STATES else "private"
    assert (scope, state) in hooks_of(record), record


@pytest.mark.parametrize("keyword,state", [
    ("Exhaust", "self_exhaust"), ("Ethereal", "ethereal"),
    ("Retain", "card_timing"), ("Innate", "card_timing"),
])
def test_canon_keyword_fixtures(keyword, state):
    record = _canon_record("DamageCmd.Attack(cardPlay.Target, 5);",
                           keywords=(keyword,))
    assert ("shared", state) in hooks_of(record)


def test_no_shared_entry_is_ungrounded():
    """`junk_create`, `junk_remove` and `enemy_intent` were the last three
    and are grounded above. The classifier freezes ONCE and complete."""
    assert [s for s, (_w, st) in ccr.SHARED_STATES.items()
            if st == ccr.UNGROUNDED] == []


def test_the_ungrounded_path_still_reports_unclassified(monkeypatch):
    """...so the mechanism has no live entry to demonstrate it, and is
    exercised against a temporary one instead of being deleted with the
    last real one. The next entry to arrive without a token must still
    report UNCLASSIFIED rather than a silent zero."""
    monkeypatch.setitem(ccr.SHARED_STATES, "fixture_state",
                        ("an entry with no canon token", ccr.UNGROUNDED))
    record = _canon_record("DamageCmd.Attack(cardPlay.Target, 5);")
    assert any(note.startswith("fixture_state")
               for note in record["unclassified"]), record


# --- the junk axis and enemy intent, grounded (EB-118 W1) -------------------

def test_junk_creation_is_read_off_the_created_cards_own_model(tmp_path):
    """A name list would be game data AND a maintenance debt. The verdict
    comes from the created model's own ctor, exactly as the sheet adapter
    reads the created row's own `rarity:`."""
    (tmp_path / "Junky.cs").write_text(
        "namespace MegaCrit.Sts2.Core.Models.Cards;\n"
        "public sealed class Junky : CardModel {\n"
        "  public Junky() : base(-1, CardType.Status, CardRarity.Status,\n"
        "    TargetType.None) { }\n}\n", encoding="utf-8")
    (tmp_path / "Handy.cs").write_text(
        "namespace MegaCrit.Sts2.Core.Models.Cards;\n"
        "public sealed class Handy : CardModel {\n"
        "  public Handy() : base(0, CardType.Skill, CardRarity.Token,\n"
        "    TargetType.Self) { }\n}\n", encoding="utf-8")
    reader = ccr.CanonReader(tmp_path)

    junk = _canon_record("CardModel c = base.CombatState.CreateCard<Junky>("
                         "base.Owner);", reader=reader)
    assert ("shared", "junk_create") in hooks_of(junk)
    assert junk["external_reach"] is True

    # ...and a card that mints a TOKEN mints no junk. Same call, same shape:
    # only the created model's own rarity separates them.
    token = _canon_record("CardModel c = base.CombatState.CreateCard<Handy>("
                          "base.Owner);", reader=reader)
    assert ("shared", "junk_create") not in hooks_of(token)


def test_an_unreadable_created_model_is_unclassified_not_not_junk():
    record = _canon_record(
        "CardModel c = base.CombatState.CreateCard<Nowhere>(base.Owner);")
    assert any("Nowhere" in note for note in record["unclassified"]), record


def test_junk_removal_needs_a_filter_and_a_removal_verb():
    """Exhausting or transforming a junk-filtered set removes junk.
    Exhausting anything else does not, and neither does a bare filter."""
    both = _canon_record(CANON_FIXTURES["junk_remove"])
    assert ("shared", "junk_remove") in hooks_of(both)
    assert both["external_reach"] is True

    verb_only = _canon_record("await CardCmd.Exhaust(choiceContext, card);")
    assert ("shared", "junk_remove") not in hooks_of(verb_only)

    filter_only = _canon_record(
        "if (card.Type == CardType.Status) { base.EnergyCost"
        ".SetUntilPlayed(0); }")
    assert ("shared", "junk_remove") not in hooks_of(filter_only)


def test_the_junk_conjunction_is_per_source_not_over_the_join(tmp_path):
    """A card that Exhausts, applying a Power that merely mentions junk, is
    not a junk remover -- and would read as one if the two texts were
    concatenated before the filter and the verb were looked for."""
    (tmp_path / "MentionPower.cs").write_text(
        "namespace MegaCrit.Sts2.Core.Models.Powers;\n"
        "public sealed class MentionPower : PowerModel {\n"
        "  public override async Task AfterCardDrawn(CardModel card) {\n"
        "    if (card.Type == CardType.Status) { Flash(); }\n"
        "  }\n}\n", encoding="utf-8")
    reader = ccr.CanonReader(tmp_path)
    record = _canon_record(
        "await CardCmd.Exhaust(choiceContext, card); "
        "await PowerCmd.Apply<MentionPower>(base.Owner.Creature, 1);",
        reader=reader)
    assert ("shared", "junk_remove") not in hooks_of(record)


def test_junk_creation_is_also_read_through_an_applied_power(tmp_path):
    """Half the base game's junk-watching lives on a Power, so reading only
    the card would report a silent zero for the card that applies it."""
    (tmp_path / "WatchPower.cs").write_text(
        "namespace MegaCrit.Sts2.Core.Models.Powers;\n"
        "public sealed class WatchPower : PowerModel {\n"
        "  public override async Task AfterCardGeneratedForCombat("
        "CardModel card, Player? creator) {\n"
        "    if (card.Type == CardType.Status) { Flash(); }\n"
        "  }\n}\n", encoding="utf-8")
    reader = ccr.CanonReader(tmp_path)
    record = _canon_record(
        "await PowerCmd.Apply<WatchPower>(base.Owner.Creature, 1);",
        reader=reader)
    assert ("shared", "junk_create") in hooks_of(record)
    assert record["external_reach"] is True


def test_enemy_intent_reads_and_writes_are_separate():
    read = _canon_record(CANON_FIXTURES["enemy_intent"])
    assert "enemy_intent" in read["shared_reads"]
    assert "enemy_intent" not in read["shared_writes"]
    # Stun replaces the move the enemy had telegraphed: a WRITE.
    write = _canon_record("await CreatureCmd.Stun(cardPlay.Target);")
    assert "enemy_intent" in write["shared_writes"]


def test_a_plain_attack_touches_neither_junk_nor_intent():
    record = _canon_record("DamageCmd.Attack(cardPlay.Target, 5);")
    for state in ("junk_create", "junk_remove", "enemy_intent"):
        assert ("shared", state) not in hooks_of(record), state
    assert record["unclassified"] == []


@pytest.mark.parametrize("keyword", sorted(ccr.CANON_KEYWORDS_NO_HOOK))
def test_listed_hookless_keywords_are_classified_not_unclassified(keyword):
    """`Unplayable` and `Eternal` are printed rules that touch no vocabulary
    state; `None` says the card carries no keyword at all. Listed rather
    than ignored, so a keyword the enum grows later still reports."""
    record = _canon_record("DamageCmd.Attack(cardPlay.Target, 5);",
                           keywords=(keyword,))
    assert record["unclassified"] == []


def test_an_unlisted_keyword_is_still_unclassified():
    record = _canon_record("DamageCmd.Attack(cardPlay.Target, 5);",
                           keywords=("Sparkly",))
    assert any("Sparkly" in note for note in record["unclassified"])


def test_every_grounded_shared_entry_has_a_canon_fixture():
    """The canon half of pin 1. A `grounded` status is a claim that the
    detector exists; a claim nobody can demonstrate is one to distrust."""
    covered = set(CANON_FIXTURES) | {
        "self_exhaust", "ethereal",              # test_canon_keyword_fixtures
        "universal_verb_power",                  # the power tag-through test
    }
    grounded = {s for s, (_w, st) in ccr.SHARED_STATES.items()
                if st == ccr.GROUNDED}
    assert not grounded - covered, sorted(grounded - covered)


def test_canon_absent_entries_have_no_canon_detector():
    """Auras/reactions are a GItS system; zero is the true canon value."""
    absent = [s for s, (_w, st) in ccr.SHARED_STATES.items()
              if st == ccr.CANON_ABSENT]
    assert "aura_reaction" in absent
    detected = {hook[1] for _p, hook, _a in ccr.CANON_SIGNALS}
    assert not (set(absent) & detected)


def test_canon_power_tag_through_reads_the_powers_own_model(tmp_path):
    """A card that applies a Power inherits what the POWER touches --
    the recursion canon_role_tempo established, not a name table."""
    power_src = ("namespace MegaCrit.Sts2.Core.Models.Powers;\n"
                 "public class ThingPower : PowerModel {\n"
                 "  public override async Task AfterCardExhausted() {\n"
                 "    CreatureCmd.GainBlock(base.Owner.Creature, 3);\n"
                 "  }\n}\n")
    (tmp_path / "ThingPower.cs").write_text(power_src, encoding="utf-8")
    reader = ccr.CanonReader(tmp_path)
    record = _canon_record(
        "PowerCmd.Apply<ThingPower>(base.Owner.Creature, 1);", reader=reader)
    assert ("shared", "universal_verb_power") in hooks_of(record)
    assert ("shared", "block_held") in hooks_of(record)
    assert record["external_reach"] is True


def test_canon_power_with_an_unreadable_model_is_unclassified():
    record = _canon_record(
        "PowerCmd.Apply<MissingPower>(base.Owner.Creature, 1);")
    assert any("MissingPower" in note for note in record["unclassified"])


def test_canon_corpus_reads_a_synthetic_five_pool_tree(tmp_path):
    root = _write_canon_tree(tmp_path, {
        "Alpha": CANON_FIXTURES["block_held"],
        "Beta": CANON_FIXTURES["orbs"],
    })
    pools, problems = ccr.canon_corpus(root)
    assert sorted(pools) == sorted(c.lower() for c in ccr.CANON_CHARACTERS)
    assert not [p for p in problems if "missing canon pools" in p]
    stats = ccr.pool_stats(pools["ironclad"])
    assert stats["n"] == 2
    assert stats["private_ratio"]["orbs"]["writers"] == 1


def test_canon_corpus_refuses_a_partial_tree(tmp_path):
    """Four pools out of five is not a canon baseline. All five or none."""
    root = _write_canon_tree(tmp_path, {"Alpha": CANON_FIXTURES["block_held"]},
                             characters=ccr.CANON_CHARACTERS[:4])
    pools, problems = ccr.canon_corpus(root)
    assert pools == {}
    assert any("missing canon pools" in p for p in problems)


def test_canon_corpus_on_a_missing_tree_is_a_reason_not_a_crash(tmp_path):
    pools, problems = ccr.canon_corpus(tmp_path / "nope")
    assert pools == {}
    assert problems and "does not exist" in problems[0]


# --- the honest stop, or the full read, depending on this checkout ----------
#
# game_ref/ is gitignored: present in the main checkout, absent from a
# worktree (OPERATIONS forbids linking it in). Both are legitimate places to
# run the suite, so these pin the tool's behaviour in whichever one we are in
# rather than pinning the checkout itself.

HAS_GAME_REF = (REPO / "game_ref").exists()


def test_real_invocation_prints_the_report_this_checkout_can_support():
    proc = subprocess.run(
        [sys.executable, "tools/card_connectivity_report.py"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    for pool in ("klee", "furina", "kokomi"):
        assert f"--- {pool} (" in out
    if HAS_GAME_REF:
        # The canon half is reachable: all eight pools, no honest-stop banner.
        assert "INCOMPLETE REPORT -- MOD POOLS ONLY, NO CANON BASELINE" not in out
        for canon in ("ironclad", "silent", "defect", "necrobinder", "regent"):
            assert f"--- {canon} (" in out
    else:
        assert "INCOMPLETE REPORT -- MOD POOLS ONLY, NO CANON BASELINE" in out
        assert "why the canon half is missing" in out
        for canon in ("ironclad", "silent", "defect", "necrobinder", "regent"):
            assert f"--- {canon} (" not in out


def test_report_completeness_matches_the_corpus_and_carries_no_threshold():
    report = ccr.build_report()
    assert report["complete"] is HAS_GAME_REF
    if HAS_GAME_REF:
        assert sorted(report["canon_pools"]) == [
            "defect", "ironclad", "necrobinder", "regent", "silent"]
    else:
        assert report["canon_pools"] == []
    assert sorted(report["mod_pools"]) == ["furina", "klee", "kokomi"]
    # NO GATE. The registration carries no pass/fail threshold and no
    # target share, so the report must hold no verdict of any kind: every
    # key is a count, a share, a ratio or a listing.
    verdicts = ("threshold", "pass", "fail", "floor", "target", "gate",
                "violation", "ok")
    keys = {k for k in report} | {k for stats in report["pools"].values()
                                  for k in stats}
    words = {word for key in keys for word in key.lower().split("_")}
    assert not (words & set(verdicts)), sorted(words & set(verdicts))
    source = (REPO / "tools" / "card_connectivity_report.py").read_text(
        encoding="utf-8")
    assert "SystemExit(2)" not in source        # no stop-and-surface exit
    assert "0.55" not in source and "0.65" not in source


def test_report_is_deterministic():
    assert ccr.render(ccr.build_report()) == ccr.render(ccr.build_report())
