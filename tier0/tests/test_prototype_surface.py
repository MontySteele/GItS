"""EB-147 / R213 B: the QUARANTINED prototype surface.

THE ACCEPTANCE SENTENCE, WHICH IS WHAT THIS FILE IS FOR:

    "a row stages and reaches no pool or stamp."

Every claim below is one half of that. The fixture row lives in a TEMPORARY
sheet written per test, never on the shipped surface, because R213 B's deletion
rule -- *"once a slice is accepted or rejected its prototype rows leave the
surface -- it is never a second permanent pool"* -- makes EMPTY the healthy
committed state. A permanent fixture row would be the second permanent pool the
ruling forbids, one row deep, and it would be the row nobody ever deletes.

The cost of that choice is stated rather than hidden: with an empty surface the
committed C# proves only that an empty surface compiles. The proof that a REAL
prototype card compiles is a manual step recorded in the packet
(`review/active/eb147-prototype-surface-2026-08-27.md`): stage the fixture, run
the dev codegen, `dotnet build -p:PrototypeCards=true`, revert. That is
deliberately not automated here -- the suite has no game assembly to build
against.
"""

from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from tier0.content import loader

REPO = Path(__file__).resolve().parents[2]

# One expressible Kokomi row. Expressible matters: `gen_prototype_cards` REFUSES
# a blocked row rather than listing it, so a fixture the emitter cannot print
# would fail the wrong assertion for the right reason and teach nothing.
FIXTURE = {
    "id": "proto_kokomi_tidecall",
    "name": "Tidecall (Prototype)",
    "character": "kokomi",
    # EB-190: required on every row, and stripped before the emitter sees it.
    "authored_by": ["claude"],
    "cost": 1,
    "type": "skill",
    "rarity": "common",
    "effects": [
        {"op": "block", "amount": 5},
        {"op": "draw", "amount": 1},
    ],
}


def _sheet(tmp_path: Path, rows) -> Path:
    path = tmp_path / "prototype-surface.yaml"
    path.write_text(yaml.safe_dump(rows, sort_keys=False), encoding="utf-8")
    return path


# --- (a) it validates under the SHIPPED schema -------------------------------

def test_fixture_row_validates_under_the_card_schema(tmp_path):
    """R213 B: 'STILL checked for schema validity'.

    `prototype_cards` runs the row through `Card.from_dict` -- which is TOTAL
    on unknown and retired fields -- and then through the same
    effect-vocabulary and recall-shape validators the shipped index runs.
    """
    cards = loader.prototype_cards(_sheet(tmp_path, [FIXTURE]))
    assert [c.id for c in cards] == ["proto_kokomi_tidecall"]
    assert cards[0].character == "kokomi"


def test_the_shipped_surface_loads_whatever_is_on_it():
    """The committed surface parses, and every row on it passes the gate.

    THIS TEST USED TO ASSERT THE SURFACE WAS EMPTY. Empty is still the healthy
    STEADY state -- R213 B's deletion rule makes it so, and the test below is
    what keeps it from becoming a second permanent pool -- but a slice IN
    FLIGHT legitimately has rows on it, and the first one (the Kokomi slice,
    R216) is what found that the old assertion could not tell a slice from a
    leak. So the empty check moves to the test that can tell them apart, and
    this one keeps the half that is true either way: whatever is here loads,
    through the shipped validators.
    """
    assert loader.PROTOTYPE_SHEET.exists()
    rows = yaml.safe_load(
        loader.PROTOTYPE_SHEET.read_text(encoding="utf-8")) or []
    cards = loader.prototype_cards()
    assert len(cards) == len(rows)
    for card in cards:
        assert card.id.startswith(loader.PROTOTYPE_ID_PREFIX)


def test_the_surface_is_non_empty_only_while_a_slice_is_open():
    """R213 B's DELETION RULE, as a gate rather than a paragraph.

        "Once a slice is ACCEPTED or REJECTED, its rows LEAVE this surface."

    A row that has outlived its slice is the failure the rule names -- "a row
    that has sat here across two slices is a defect in the process" -- and it
    is invisible to every other check, because such a row is perfectly valid.
    What makes it visible is that a LIVE slice always has a packet open under
    `review/active/` explaining what its rows are asking; an abandoned row has
    nothing pointing at it. So the surface may carry rows exactly while some
    active packet names it, and the day the slice's packet is filed away the
    rows have to go with it or this test says so.

    Deliberately generic -- it names no slice. Hard-coding "the Kokomi slice"
    here would make the guard expire quietly the moment that slice closed.
    """
    rows = yaml.safe_load(
        loader.PROTOTYPE_SHEET.read_text(encoding="utf-8")) or []
    if not rows:
        return                      # the healthy steady state
    active = REPO / "review" / "active"
    citing = sorted(p.name for p in active.glob("*.md")
                    if "prototype-surface.yaml" in p.read_text(
                        encoding="utf-8", errors="replace"))
    assert citing, (
        f"the prototype surface carries {len(rows)} row(s) but no packet "
        f"under review/active/ names docs/prototype-surface.yaml. Under "
        f"R213 B a slice's rows leave the surface when the slice is accepted "
        f"or rejected -- either the packet was filed away without deleting "
        f"its rows, or these rows never had one.")


@pytest.mark.parametrize("mutate, expect", [
    (lambda r: r.update(id="kokomi_tidecall"), "must start"),
    (lambda r: r.update(id="all_hands"), "must start"),
    (lambda r: r.pop("character"), "`character:`"),
    (lambda r: r.update(character="ironclad"), "`character:`"),
    (lambda r: r.update(nonsense=1), "unknown fields"),
    (lambda r: r.update(effects=[{"op": "not_an_op", "amount": 1}]), "not_an_op"),
])
def test_bad_prototype_rows_are_refused_by_name(tmp_path, mutate, expect):
    row = dict(FIXTURE)
    mutate(row)
    with pytest.raises(ValueError) as excinfo:
        loader.prototype_cards(_sheet(tmp_path, [row]))
    assert expect in str(excinfo.value)


def test_a_prototype_id_may_not_collide_with_a_shipped_card(tmp_path, monkeypatch):
    """Two cards cannot share a ModelId, and `give_card` matches on the entry.

    The prefix rule usually gets there first, so the collision check is proved
    with the prefix rule lifted -- otherwise this test would pass on the wrong
    refusal and go on passing after somebody deleted the collision check.
    """
    monkeypatch.setattr(loader, "PROTOTYPE_ID_PREFIX", "")
    shipped = sorted(loader._card_index())[0]
    row = dict(FIXTURE, id=shipped)
    with pytest.raises(ValueError) as excinfo:
        loader.prototype_cards(_sheet(tmp_path, [row]))
    assert "collides with a shipped card" in str(excinfo.value)


def test_no_shipped_card_wears_the_prototype_prefix():
    """The prefix is only worth something while it is unclaimed."""
    assert not any(cid.startswith(loader.PROTOTYPE_ID_PREFIX)
                   for cid in loader._card_index())


# --- (b) the DEV profile emits it; the DEFAULT profile does not --------------

def _proto_plan(monkeypatch, tmp_path, rows):
    import tools.gen_prototype_cards as genproto
    sheet = _sheet(tmp_path, rows)
    out = tmp_path / "Generated"
    monkeypatch.setattr(genproto, "SHEET", sheet)
    monkeypatch.setattr(genproto, "OUT_DIR", out)
    monkeypatch.setattr(genproto, "MANIFEST", out / "manifest.json")
    monkeypatch.setattr(genproto, "DIR_PROFILE", replace(
        genproto.DIR_PROFILE, sheet=sheet, out_dir=out,
        manifest=out / "manifest.json"))
    # EB-213: a row's `upgrade:` block is REGISTERED into the merged delta
    # index, which is memoized module-wide. Hand the plan a COPY so a fixture
    # id cannot survive into another test's index -- monkeypatch puts the real
    # one back on teardown.
    import tools.gen_klee_cards as gen
    monkeypatch.setattr(gen, "_upgrade_deltas", dict(gen.upgrade_deltas()))
    return genproto, genproto.plan(), out


def test_dev_profile_emits_the_row(monkeypatch, tmp_path):
    genproto, plan, _ = _proto_plan(monkeypatch, tmp_path, [FIXTURE])
    assert "proto_kokomi_tidecall" in plan.generated
    source = plan.generated["proto_kokomi_tidecall"]
    assert "namespace KleeMod.Cards.Prototype.Generated;" in source
    assert "public sealed class ProtoKokomiTidecall : CustomCardModel" in source
    # The OWNER's identity rides through: a Kokomi prototype is a Kokomi card,
    # cadence and all, or it is not testing what the slice thinks it tests.
    assert 'public string CharacterId => "kokomi";' in source
    manifest = json.loads(plan.manifest_src)
    assert manifest["generated"] == ["proto_kokomi_tidecall"]
    assert manifest["owners"] == {"proto_kokomi_tidecall": "kokomi"}


def test_default_generator_run_emits_no_prototype(monkeypatch, tmp_path):
    """R213 B: 'the default generator run does not emit them'.

    Three independent statements of the same fact, because one of them alone
    would be an accident: the prototype sheet is not any character profile's
    sheet, `--character all` cannot select it (it is not in PROFILES), and no
    character's PLAN puts the id in its output.
    """
    import tools.gen_klee_cards as gen
    import tools.gen_prototype_cards as genproto

    assert "prototype" not in gen.PROFILES
    assert "prototype" not in gen.PLAN_BUILDERS
    assert genproto.SHEET not in {p.sheet for p in gen.PROFILES.values()}
    assert genproto.OUT_DIR not in {p.out_dir for p in gen.PROFILES.values()}

    for profile in gen.PROFILES.values():
        plan = gen.PLAN_BUILDERS[profile.character_id](profile)
        assert not any(k.startswith(loader.PROTOTYPE_ID_PREFIX)
                       for k in plan.generated)
        assert loader.PROTOTYPE_ID_PREFIX not in plan.manifest_src


def test_an_inexpressible_prototype_row_stops_the_run(monkeypatch, tmp_path):
    """A blocked prototype is a build failure, not a manifest line.

    A character sheet may legitimately run ahead of the runtime. This surface
    exists to be played at the real game this week, so a row the emitter
    cannot print is a row the funnel cannot use -- and carrying it as a
    manifest entry is how a slice reaches [USER] with a card that is not there.
    """
    row = dict(FIXTURE, effects=[{"op": "block", "amount": 5}], retain=True,
               requires={"never_implemented_gate": True})
    with pytest.raises(SystemExit) as excinfo:
        _proto_plan(monkeypatch, tmp_path, [row])
    assert "NOT EXPRESSIBLE" in str(excinfo.value)


# --- (b2) the row's own upgrade channel (EB-213) -----------------------------
#
# Shipped upgrades are keyed by shipped card id in
# `docs/<character>-upgrades.yaml`. A `proto_` key there would give R213 B's
# deletion rule a second file to remember, so a prototype row carries its
# `upgrade:` block itself and the generator registers it into the merged delta
# index BEFORE emitting. Everything downstream is the shipped path: same
# expressibility check, same `OnUpgrade`, same campfire. Before this the
# surface had no channel at all and a staged card could not be smithed.

UPGRADEABLE = dict(FIXTURE, upgrade={"block": +3})


def test_a_row_carrying_an_upgrade_emits_the_shipped_upgrade_path(
        monkeypatch, tmp_path):
    genproto, plan, _ = _proto_plan(monkeypatch, tmp_path, [UPGRADEABLE])
    source = plan.generated["proto_kokomi_tidecall"]
    assert "protected override void OnUpgrade()" in source
    assert 'DynamicVars.Block.UpgradeValueBy(3m)' in source
    # And the delta is on the ROW's manifest, not in an upgrades sheet.
    assert json.loads(plan.manifest_src)["upgrades"] == {
        "proto_kokomi_tidecall": {"block": 3}}


def test_a_row_without_an_upgrade_stays_base_only(monkeypatch, tmp_path):
    """The channel is opt-in. Every row on this surface was base-only before
    EB-213 and a row that declares nothing still is -- and says so, rather
    than acquiring a delta from somewhere."""
    genproto, plan, _ = _proto_plan(monkeypatch, tmp_path, [FIXTURE])
    source = plan.generated["proto_kokomi_tidecall"]
    assert "NO upgrade path" in source
    assert json.loads(plan.manifest_src)["upgrades"] == {}


def test_an_inexpressible_declared_upgrade_stops_the_run(monkeypatch,
                                                         tmp_path):
    """Same rule as the body, for the same reason: a declared upgrade the
    emitter silently drops is a campfire that does nothing on a card staged
    to be tried at a campfire. On a character sheet that is a
    `no_upgrade_path` manifest line; here it is a build failure."""
    row = dict(FIXTURE, upgrade={"vulnerable": +2})
    with pytest.raises(SystemExit) as excinfo:
        _proto_plan(monkeypatch, tmp_path, [row])
    assert "`upgrade:` is NOT EXPRESSIBLE" in str(excinfo.value)


def test_the_row_and_a_shipped_sheet_cannot_both_rule_one_id(monkeypatch):
    """One id, one delta. The registration is in-process, so the only way two
    homes could disagree is a `proto_` key that reached an upgrades sheet --
    which is exactly what the row-carried channel exists to prevent."""
    import tools.gen_klee_cards as gen
    monkeypatch.setattr(gen, "_upgrade_deltas", dict(gen.upgrade_deltas()))
    gen.register_upgrade_deltas("proto_kokomi_tidecall", {"block": 3})
    gen.register_upgrade_deltas("proto_kokomi_tidecall", {"block": 3})   # idempotent
    with pytest.raises(SystemExit, match="one id, one delta"):
        gen.register_upgrade_deltas("proto_kokomi_tidecall", {"block": 4})


def test_the_sim_reads_the_same_row_carried_delta_and_only_when_reachable(
        tmp_path, monkeypatch):
    """The two engines take the delta off ONE place -- tier0 merges the row's
    own block into its upgrade index (`upgrades._prototype_deltas`). The merge
    is filtered by REACHABILITY, and that filter is the quarantine: this index
    is what `has_upgrade` answers from, and `get_card` must be able to honour
    every yes it gives. A row no live door resolves is registered nowhere, so
    a flag-off tree -- which is every shipped tree -- has the index it always
    had.

    The substituted case, where the answer is YES and the campfire reaches the
    ruled number, is `tier0/tests/test_kurage_base_kit.py`'s EB-213 block; it
    needs a live substitution, which a fixture row does not have.
    """
    from tier0.content import upgrades
    monkeypatch.setattr(loader, "PROTOTYPE_SHEET", _sheet(tmp_path,
                                                          [UPGRADEABLE]))
    loader.reset_caches()
    try:
        assert loader.prototype_cards()[0].upgrade == {"block": 3}
        assert not loader._substituted_card_index()      # no live door
        assert not upgrades.has_upgrade("proto_kokomi_tidecall")
        assert "proto_kokomi_tidecall" not in upgrades._upgrade_index()
    finally:
        loader.reset_caches()


# --- (b3) the row's own face (EB-215) ----------------------------------------
#
# `gen_klee_cards` renders a card's text from its BODY, and a Power's text per
# POWER ID -- which is what makes a shipped face unable to drift from what the
# card does. A prototype that rewrites a shipped power's clause therefore
# could not say so without moving the shipped card's face with it, and the mod
# worked around that by MERGING a replacement string into the loc table at
# pool-build time. Two channels described one card and the generated file was
# wrong until the override ran. R224 A takes `M57`(2) on those duplication
# grounds: the row states its face, codegen emits it into the same
# `Localization` list every shipped row uses, and the merge is gone.

FACED = dict(FIXTURE, description="Gain {Block:diff()} Block. Draw a card.")


def test_a_rows_description_is_the_emitted_face(monkeypatch, tmp_path):
    genproto, plan, _ = _proto_plan(monkeypatch, tmp_path, [FACED])
    source = plan.generated["proto_kokomi_tidecall"]
    assert ('("description", "Gain {Block:diff()} Block. Draw a card."),'
            in source)


def test_a_row_without_a_description_is_still_rendered_from_its_body(
        monkeypatch, tmp_path):
    """The channel is opt-in and the body renderer is still the default --
    which is the property that keeps a face honest wherever it is not
    overridden."""
    genproto, plan, _ = _proto_plan(monkeypatch, tmp_path, [FIXTURE])
    source = plan.generated["proto_kokomi_tidecall"]
    assert '("description", "Gain' in source
    assert "Draw" in source


def test_the_face_reaches_the_generated_file_with_no_merge_in_the_path():
    """`EB-215`'s acceptance, on the SHIPPED surface rather than a fixture:
    the committed C# is right as committed. Before this the file carried the
    shipped Oath's pulse wording and only a boot-time loc merge made it read
    correctly, so the generated artifact and the played card disagreed."""
    row = next(r for r in yaml.safe_load(
        loader.PROTOTYPE_SHEET.read_text(encoding="utf-8")) or []
        if r["id"] == "proto_kurages_oath_memory")
    emitted = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
               / "Generated" / "ProtoKuragesOathMemory.cs").read_text(
                   encoding="utf-8")
    assert f'("description", "{row["description"]}"),' in emitted
    assert "memory" in row["description"]


def test_no_shipped_sheet_row_carries_a_description():
    """The field is the prototype surface's alone. A shipped face is rendered
    from the body so it cannot drift from what the card does; hand text on a
    shipped row would put that guarantee back in a person's hands."""
    for sheet in loader.DOCS_CARD_SHEETS:
        path = loader.DOCS_DIR / sheet
        if not path.exists():
            continue
        rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        assert not [r["id"] for r in rows if "description" in r], sheet


def test_the_loc_merge_is_gone_from_the_mod():
    """The other half of the duplication: one channel means the pool builder
    no longer rewrites a face it did not generate."""
    pool = (REPO / "klee-mod" / "KleeCode" / "KokomiCardPool.cs").read_text(
        encoding="utf-8")
    assert "InjectPrototypeLoc" not in pool
    assert "LocManager" not in pool


# --- (c) no pool, no manifest, no digest, no distinctness, no stamp ----------

def test_prototype_rows_never_enter_the_sim_card_index(tmp_path, monkeypatch):
    """The exclusion is STRUCTURAL: there is no filter, the rows never enter.

    `_card_index` is the single index behind `get_card`, `all_cards`,
    `character_pool`, every reward roll, every run template and every balance
    report. `prototype_cards` builds its own list and puts nothing back.
    """
    monkeypatch.setattr(loader, "PROTOTYPE_SHEET", _sheet(tmp_path, [FIXTURE]))
    assert loader.prototype_cards()          # the row loads...
    index = loader._card_index()
    assert "proto_kokomi_tidecall" not in index                 # ...and stays out
    assert not any(cid.startswith(loader.PROTOTYPE_ID_PREFIX) for cid in index)

    # tier05 is the run half: its reward pools are a filter over the SAME
    # index, so an absence there is an absence in every draft, shop and
    # transform without tier05 needing to know this surface exists.
    from tier05 import rewards
    for character in ("klee", "furina", "kokomi"):
        by_rarity = rewards.character_pool(character)
        assert by_rarity, character
        for cards in by_rarity.values():
            assert not any(c.id.startswith(loader.PROTOTYPE_ID_PREFIX)
                           for c in cards)


def test_version_stamps_cannot_see_the_prototype_surface():
    """R213 B: 'ignored by ... version stamps'.

    `lint_sheet_stamp`'s digest IS the sheet half of the stamp law. A staged
    prototype must not bump SHEET_DIGEST: nothing measured moved, and a stamp
    that bumps several times a week for scratch stops meaning anything.
    """
    from tools import lint_sheet_stamp

    assert loader.PROTOTYPE_SHEET not in lint_sheet_stamp.sheets()
    assert "docs/prototype-surface.yaml" in lint_sheet_stamp.EXCLUDED
    before = lint_sheet_stamp.digest()
    text = loader.PROTOTYPE_SHEET.read_text(encoding="utf-8")
    try:
        loader.PROTOTYPE_SHEET.write_text(
            text + "\n# staged, for one assertion\n", encoding="utf-8")
        assert lint_sheet_stamp.digest() == before
    finally:
        loader.PROTOTYPE_SHEET.write_text(text, encoding="utf-8")


def test_distinctness_report_cannot_see_the_prototype_surface():
    """R213 B: 'ignored by ... distinctness'. Its numbers are pool ratios."""
    from tools import card_distinctness_report as cdr

    assert "prototype-surface.yaml" in cdr.EXCLUDED_SHEETS
    assert not any(Path(p).name == "prototype-surface.yaml" for p in cdr.SHEETS)


def test_release_build_does_not_compile_the_prototype_classes():
    """R213 B: 'absent from ... release manifests and ordinary runs'.

    The strongest available statement of it: without `PrototypeCards=true` the
    directory is not compiled, so a shipped mod holds no prototype class and
    there is no id for any route -- reward, transform or hand-typed -- to
    resolve. `deploy.ps1` and `validate.ps1` are the release path and never
    set the property.
    """
    csproj = (REPO / "klee-mod" / "KleeCode" / "KleeCode.csproj").read_text(
        encoding="utf-8")
    assert '<Compile Remove="Cards/Prototype/**/*.cs" />' in csproj
    assert "'$(PrototypeCards)' != 'true'" in csproj
    assert "PROTOTYPE_CARDS" in csproj

    for script in ("deploy.ps1", "validate.ps1"):
        body = (REPO / "klee-mod" / "build" / script).read_text(
            encoding="utf-8", errors="replace")
        assert "PrototypeCards" not in body, f"{script} sets the dev flag"

    hook = (REPO / "klee-mod" / "KleeCode" / "PrototypeCards.cs").read_text(
        encoding="utf-8")
    assert "#if PROTOTYPE_CARDS" in hook
    assert "System.Array.Empty<CardModel>()" in hook


def test_prototype_cards_are_off_pool_in_every_character(tmp_path, monkeypatch):
    """In the pool (Pool resolves) and out of GetUnlockedCards (no rolls).

    Not "in no pool": a poolless card falls through to MockCardPool and throws
    "You monster!" the first time the real game draws or previews it, which is
    exactly what a staged turn does. See tools/lint_pool_membership.py.
    """
    code = REPO / "klee-mod" / "KleeCode"
    for path, character in (("KleeOffPoolCards.cs", "klee"),
                            ("FurinaCardPool.cs", "furina"),
                            ("KokomiCardPool.cs", "kokomi")):
        body = (code / path).read_text(encoding="utf-8")
        assert f'PrototypeCards.For("{character}")' in body, path
        # The off-pool list is what FilterThroughEpochs strips from rolls.
        assert "OffPool" in body

    from tools import lint_pool_membership
    roster = (code / "Cards" / "Prototype" / "Generated" / "PrototypeRoster.cs")
    assert roster in lint_pool_membership.MEMBERSHIP_FILES
    assert roster.is_file()


def test_the_emitted_prototype_passes_the_structural_gate(monkeypatch, tmp_path):
    """R213 B: 'runtime legality'. L1-L4 on the emitted .cs, not on the sheet.

    `lint_generated_structure` parses the artifact rather than calling back
    into the generator, so a bug that makes the emitter drop a var cannot also
    make this stop looking for it. The prototype surface is held to it.
    """
    from tools import lint_generated_structure as lgs

    genproto, plan, out = _proto_plan(monkeypatch, tmp_path, [FIXTURE])
    genproto.gen._write_plan(genproto.DIR_PROFILE, plan)
    assert lgs.problems(genproto.DIR_PROFILE) == []


# --- (d) reachable by id through the grant tooling ---------------------------

def test_the_scenario_grants_the_fixture_row_by_id():
    """R213 B: 'reachable only by id through the scenario/grant tooling'.

    The LIVE run is deferred (another lane owns the game). What is pinned here
    is that the committed scenario names the fixture row in the wire's own id
    spelling -- `KLEEMOD-` + the ModelDb entry, which is the sheet id upper-
    cased -- so the deferred run fails on the GAME's answer and never on a
    typo in this repo.
    """
    path = (REPO / "understudy" / "scenarios"
            / "eb147-prototype-grant.yaml")
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert doc["character"] == "KLEEMOD-KOKOMI"
    grants = [step["give"] for step in doc["steps"] if "give" in step]
    assert grants, "the scenario must grant something"
    assert grants[0]["card"] == "KLEEMOD-" + FIXTURE["id"].upper()
    # And the emitted class name is the one the roster registers, so the grant
    # can resolve at all.
    from tools.gen_klee_cards import pascal
    assert pascal(FIXTURE["id"]) == "ProtoKokomiTidecall"


# --- (f) the grammar THIS SLICE added, and its red cases --------------------
#
# The Kokomi slice (R216) needed two things the surface did not have: a
# per-turn exhaust count for arm 1, and a modal COMPANION for arm 2. Both are
# quarantined-use-only -- no shipped row carries either -- so these are the
# only tests that exercise them, and each is paired with the failure it is
# supposed to make impossible.

def test_the_per_turn_exhaust_count_includes_the_card_own_victim():
    """Arm 1's whole point, and the reason it needed a NEW counter.

    `cards_exhausted_this_turn` is the AfterCardExhausted hook counter and is
    DEFERRED while a card resolves -- `exhaust_card` returns early at
    card_play_depth > 0 and `_op_exhaust_from` never reaches it at all -- so a
    card that Exhausts and then reads would not see the card it had just
    Exhausted. The prototype reads `exhausts_this_turn`, counted at the pile
    append, and this is the difference stated as an assertion.
    """
    import random

    from tier0.engine import combat
    from tier0.engine.state import CombatState, Enemy, Player

    # Through the surface's own reader, because `peek_card` CANNOT see a
    # prototype row -- that inability is the quarantine, and the test would be
    # worthless if it could.
    rows = {c.id: c for c in loader.prototype_cards()}
    card = rows.get("proto_pearl_barrage_turn")
    if card is None:
        pytest.skip("arm 1's row has left the surface (the deletion rule)")
    victim = loader.peek_card("coral_guard")
    player = Player(hp=50, max_hp=70, energy=3,
                    hand=[copy.deepcopy(card), copy.deepcopy(victim)],
                    character_id="kokomi")
    state = CombatState(player=player,
                        enemies=[Enemy(hp=200, max_hp=200, name="dummy",
                                       intents=[{"kind": "block",
                                                 "amount": 0}])],
                        rng=random.Random(0), turn=1)
    assert state.exhausts_this_turn == 0
    combat.play_card(state, player.hand[0])
    # One card was Exhausted -- the one this card chose -- and the count saw it.
    assert state.exhausts_this_turn == 1
    # base 5 + per 3 * 1 = 8. The number is not the question (R215 C); that
    # the count reached ONE by the time damage resolved is.
    assert state.enemies[0].hp == 200 - 8


def test_the_per_turn_exhaust_count_is_a_turn_window():
    """"This turn", not "this fight" -- which is the whole difference from
    `exhaust_pile`, the count the shipped sheet already had."""
    import random

    from tier0.engine import refpowers
    from tier0.engine.state import CombatState, Enemy, Player

    state = CombatState(player=Player(hp=50, max_hp=70, character_id="kokomi"),
                        enemies=[Enemy(hp=10, max_hp=10, name="dummy",
                                       intents=[{"kind": "block",
                                                 "amount": 0}])],
                        rng=random.Random(0), turn=1)
    refpowers.exhaust_card(state, loader.peek_card("coral_guard"))
    assert state.exhausts_this_turn == 1
    assert len(state.player.exhaust_pile) == 1
    refpowers.reset_turn_counters(state)
    # The window closed; the PILE did not.
    assert state.exhausts_this_turn == 0
    assert len(state.player.exhaust_pile) == 1


def test_a_misspelled_runtime_count_is_refused_at_load(tmp_path):
    """The red case for the new token. `_validate_effect_vocabulary` runs on
    prototype rows exactly as it runs on shipped ones (R213 B: "STILL checked
    for schema validity"), so a typo'd count is a load error and not a card
    that compiles and quietly pays its base forever."""
    row = dict(FIXTURE, effects=[{
        "op": "damage", "target": "enemy",
        "amount_formula": {"base": 5, "per": 3,
                           "count": "exhausts_this_turnn"}}])
    with pytest.raises(ValueError) as excinfo:
        loader.prototype_cards(_sheet(tmp_path, [row]))
    assert "exhausts_this_turnn" in str(excinfo.value)


def test_a_modal_companion_keeps_its_element(monkeypatch, tmp_path):
    """Arm 2's silent-failure case, and it is silent in the worst way: the
    card compiles, plays, and simply stops applying the element it exists to
    apply. A companion's element rides the CARD-level IElementalCard, so
    "is this card elemental" is a question about the whole card and has to
    walk the mode bodies too."""
    row = {
        "id": "proto_fixture_modal_companion",
        "name": "Fixture Companion (Prototype)",
        "authored_by": ["claude"],
        "character": "klee", "nation": "inazuma", "star": 4,
        "rarity": "common", "role_c": "applier", "element": "electro",
        "cost": 2, "type": "skill",
        "effects": [{"op": "choose_one", "modes": [
            {"label": "Deal 3 damage",
             "effects": [{"op": "damage", "amount": 3, "target": "enemy",
                          "applies_element": True}]},
            {"label": "Gain 4 Block",
             "effects": [{"op": "block", "amount": 4}]}]}],
    }
    # It loads under the shipped schema...
    assert loader.prototype_cards(_sheet(tmp_path, [row]))[0].element == "electro"
    # ...and it emits ELEMENTAL, which is the half that used to be lost.
    _genproto, plan, _out = _proto_plan(monkeypatch, tmp_path, [row])
    source = plan.generated["proto_fixture_modal_companion"]
    assert "IElementalCard" in source
    assert "Element.Electro" in source


def test_every_prototype_mode_face_is_carried_by_the_prototype_roster():
    """EB-150 again, on this surface. A mode face in no pool takes
    CardModel.Pool through MockCardPool inside the choice screen's _Ready and
    soft-locks the turn -- and a staged prototype turn is precisely a turn
    that draws and previews the card."""
    generated = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
                 / "Generated")
    roster = (generated / "PrototypeRoster.cs").read_text(encoding="utf-8")
    manifest = json.loads(
        (generated / "manifest.json").read_text(encoding="utf-8"))
    faces = [name for names in manifest.get("mode_faces", {}).values()
             for name in names]
    for name in faces:
        assert f"ModelDb.Card<{name}>()" in roster, name
    # And the manifest is not lying about what exists: every face it names is
    # a class in the emitted tree.
    emitted = "".join(p.read_text(encoding="utf-8")
                      for p in generated.glob("*.cs"))
    for name in faces:
        assert f"class {name} " in emitted, name
