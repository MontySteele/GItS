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
(`review/ruled/eb147-prototype-surface-2026-08-27.md`): stage the fixture, run
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


# --- (b3) EVERY ARM ROW UPGRADES, OR SAYS WHY NOT (`EB-315`) -----------------
#
# THE DEFECT, in [USER]'s words playing the Kokomi arm: *"Plan cards often seem
# to lack upgrades, though (Kurage's Oath, Ambush) - I thought we had a test
# for that?"* There was a test, and it asserted the OPPOSITE of what he
# expected: `test_a_row_without_an_upgrade_stays_base_only` pinned that a row
# the rule found no delta for legitimately shipped base-only, which is exactly
# the state he was complaining about. The shipped sheets have always been held
# to "every generated card ships its upgrade" (STATE.md; the three
# `upgrades.no_upgrade_path` lists are empty). The prototype arms never were.
#
# So the invariant is inverted and the old test becomes the OPT-OUT's test: a
# row may ship base-only, but only by SAYING SO on the row, in a sentence, with
# `no_upgrade:`. What was silent is now declared, and the declaration is
# checked both ways (`gen_prototype_cards.upgrade_face_findings` reports an
# opt-out the rule has since caught up with).

def test_a_row_that_declares_no_upgrade_stays_base_only(monkeypatch, tmp_path):
    """The opt-out, and it is the only way onto this surface base-only.

    The row states WHY, the emitted card carries no `OnUpgrade` body, the
    manifest records the reason where a delta would have gone, and the rule is
    not consulted at all.
    """
    row = dict(FIXTURE, id="proto_kk_tidecall",
               no_upgrade="the fixture prints no number the rule may move")
    genproto, plan, _ = _proto_plan(monkeypatch, tmp_path, [row])
    source = plan.generated["proto_kk_tidecall"]
    assert "NO upgrade path" in source
    manifest = json.loads(plan.manifest_src)
    assert manifest["upgrades"] == {}
    assert manifest["no_upgrade"] == {
        "proto_kk_tidecall": "the fixture prints no number the rule may move"}


def test_no_upgrade_beside_an_authored_upgrade_stops_the_run(monkeypatch,
                                                             tmp_path):
    """One row, one answer: a row either has a delta or says why it has none."""
    row = dict(FIXTURE, id="proto_kk_tidecall", upgrade={"block": +3},
               no_upgrade="a reason that contradicts the block beside it")
    with pytest.raises(SystemExit) as excinfo:
        _proto_plan(monkeypatch, tmp_path, [row])
    assert "BOTH `upgrade:` and `no_upgrade:`" in str(excinfo.value)


@pytest.mark.parametrize("value", [True, "", "   "])
def test_a_bare_no_upgrade_flag_is_refused(monkeypatch, tmp_path, value):
    """The value is the REASON. A bare flag is the silent exemption this key
    exists to replace, and it is refused in BOTH engines -- here at the
    emitter, and at load in `tier0.content.loader`."""
    row = dict(FIXTURE, id="proto_kk_tidecall", no_upgrade=value)
    with pytest.raises(SystemExit) as excinfo:
        _proto_plan(monkeypatch, tmp_path, [row])
    assert "must be the REASON" in str(excinfo.value)

    with pytest.raises(ValueError) as loaded:
        loader.prototype_cards(_sheet(tmp_path, [row]))
    assert "must be the REASON" in str(loaded.value)


def test_no_upgrade_is_prototype_surface_only():
    """`docs/<character>-upgrades.yaml` says "this shipped card has no
    upgrade" by the id's ABSENCE. A shipped row carrying the key would be a
    second place to look that contradicts nothing and claims everything.

    Asked of the SHAPE VALIDATOR directly, with a shipped-looking id: every
    loaded card runs through it (`_validate_card_shape`), so a `no_upgrade:`
    on any `docs/*-cards.yaml` row raises at load. The prototype-only rule is
    also true of every shipped card today and stays true by this check, which
    is why no per-sheet sweep is needed beside it.
    """
    from tier0.engine.state import Card

    shipped = Card(id="kokomi_tidecall", name="Tidecall", cost=1,
                   type="skill", no_upgrade="not allowed here")
    with pytest.raises(ValueError) as excinfo:
        loader._validate_no_upgrade_shape(shipped)
    assert "prototype surface only" in str(excinfo.value)
    assert not any(c.no_upgrade for c in loader._card_index().values())


#: The four OVERHAUL arms, and the reason the gate below is scoped to them:
#: they are the arms the Prototype-stage rule claims
#: (`upgrades.PROTOTYPE_DEFAULT_PREFIXES`). The Spark surface predates that
#: rule and its rows carry the SHIPPED cards' upgrades, which are a
#: Balance-stage ruling -- they are excused by name in
#: `gen_prototype_cards.UPGRADE_DEBT` and are not this test's business.
ARM_PREFIXES = ("proto_ko_", "proto_kk_", "proto_mc_", "proto_mi_",
                # The Furina reframe joined the rule's reach on 2026-09-02.
                "proto_fr_")


def test_every_arm_row_on_the_live_surface_can_be_smithed():
    """`EB-315`, THE GATE [USER] EXPECTED TO EXIST.

    Read off the committed MANIFEST rather than off the sheet, because the
    manifest is what the emitted C# was built from: a row whose delta the
    generator dropped between the sheet and the card would still read as
    upgradable if this asked the sheet, and that is the class of defect the
    whole `EB-283` / `EB-277` line has been about.

    Two lists, and every arm row is in exactly one: `upgrades` (a delta, ruled
    or defaulted) or `no_upgrade` (a stated reason). A row in neither is a
    campfire that hands the card back unchanged.
    """
    manifest = json.loads(
        (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"
         / "manifest.json").read_text(encoding="utf-8"))
    arm_rows = [cid for cid in manifest["generated"]
                if cid.startswith(ARM_PREFIXES)]
    assert arm_rows, "no overhaul-arm rows on the surface -- the gate is inert"
    silent = [cid for cid in arm_rows
              if cid not in manifest["upgrades"]
              and cid not in manifest["no_upgrade"]]
    assert silent == [], (
        f"{len(silent)} prototype row(s) ship with no upgrade path and no "
        f"stated reason: {silent}. Either the Prototype-stage rule should "
        f"reach the row (extend `upgrades.prototype_default_delta`), or the "
        f"row must carry `no_upgrade: <reason>` saying why it cannot.")
    for cid, reason in manifest["no_upgrade"].items():
        assert isinstance(reason, str) and len(reason.split()) >= 8, (
            f"{cid}: `no_upgrade:` must state the reason, not a phrase")


def test_the_gate_goes_red_on_a_row_with_no_path(monkeypatch, tmp_path):
    """Red-first, at the DERIVATION, because the assertion above reads a
    committed manifest and a green one proves only that today's surface is
    clean. Same question, asked of a synthetic row: an arm row that prints no
    number the rule can move, and no opt-out.
    """
    from tier0.content import upgrades

    row = dict(FIXTURE, id="proto_kk_silent", cost=0,
               effects=[{"op": "draw", "amount": 1}])
    genproto, plan, _ = _proto_plan(monkeypatch, tmp_path, [row])
    assert json.loads(plan.manifest_src)["upgrades"] == {}
    assert json.loads(plan.manifest_src)["no_upgrade"] == {}
    assert upgrades.prototype_default_delta(
        "proto_kk_silent", 0, row["effects"], False, []) == {}
    # ... and the SAME row with a Plan line is reached, which is the fix.
    assert upgrades.prototype_default_delta(
        "proto_kk_silent", 0, row["effects"], False,
        [{"op": "damage", "amount": 12, "target": "front_enemy"}]) == {
            "plan_damage": upgrades.PROTOTYPE_DAMAGE_DELTA}


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


def test_the_sim_honours_the_rows_no_upgrade_opt_out(tmp_path, monkeypatch):
    """`EB-315`. The opt-out is BOTH engines' or it is a divergence.

    A row that opts out is one the mod prints base-only, so a sim that still
    derived the default for it would smith a card the game cannot -- the exact
    class of defect `upgrades.py`'s own `exhaust` branch note describes ("a key
    live in one engine and dead in the other"). Proved on a row the rule WOULD
    otherwise reach (a printed Block), made reachable through the Kokomi arm's
    own door so the reachability filter is not what is answering.
    """
    from tier0 import constants as C
    from tier0.content import upgrades

    probe = dict(FIXTURE, id="proto_kk_optout",
                 effects=[{"op": "block", "amount": 5}])
    monkeypatch.setattr(C, "KOKOMI_OVERHAUL", True)
    monkeypatch.setattr(C, "KOKOMI_OVERHAUL_POOL_IDS", ("proto_kk_optout",))
    monkeypatch.setattr(C, "KOKOMI_OVERHAUL_STARTER_IDS", ())
    monkeypatch.setattr(loader, "PROTOTYPE_SHEET", _sheet(tmp_path, [probe]))
    loader.reset_caches()
    try:
        assert upgrades._prototype_deltas({}) == {
            "proto_kk_optout": {"block": upgrades.PROTOTYPE_BLOCK_DELTA}}
        monkeypatch.setattr(
            loader, "PROTOTYPE_SHEET",
            _sheet(tmp_path, [dict(probe, no_upgrade="the reason it cannot")]))
        loader.reset_caches()
        assert upgrades._prototype_deltas({}) == {}
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
    # BYTES, NOT TEXT (2026-09-02). This writes a TRACKED sheet in the real
    # checkout and puts it back, and `write_text` on Windows translates "\n"
    # into "\r\n" -- so the "restore" left the file byte-DIFFERENT from HEAD,
    # which `.gitattributes`' LF working tree reports as a standing
    # modification. Under `-n auto` it was worse than cosmetic while it lasted:
    # a tracked file flickering modified is a working tree flickering DIRTY,
    # and `test_manifest_version_gate` read exactly that flicker between two
    # `Get-AutoVersion` calls and went red once for it.
    raw = loader.PROTOTYPE_SHEET.read_bytes()
    try:
        loader.PROTOTYPE_SHEET.write_bytes(
            raw + b"\n# staged, for one assertion\n")
        assert lint_sheet_stamp.digest() == before
    finally:
        loader.PROTOTYPE_SHEET.write_bytes(raw)


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


# =============================================================================
# The 2026-09-02 live-defect burn: what a generated FACE and a generated
# TARGET TYPE must say. Both are read off the committed C#, because both
# defects were "the row is right and the emitted card is not".
# =============================================================================

_GENERATED = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
              / "Generated")


def _emitted_faces() -> dict[str, tuple[dict, str]]:
    """Every generated prototype card as `{id: (row, printed face)}`."""
    import re

    rows = {r["id"]: r for r in yaml.safe_load(
        loader.PROTOTYPE_SHEET.read_text(encoding="utf-8")) or []}
    out: dict[str, tuple[dict, str]] = {}
    for path in sorted(_GENERATED.glob("*.cs")):
        source = path.read_text(encoding="utf-8")
        ident = re.search(r"Sheet entry: id=(\S+)", source)
        face = re.search(r'\("description", "(.*)"\),', source)
        if ident is None or face is None:
            continue
        row = rows.get(ident.group(1))
        if row is not None:
            out[ident.group(1)] = (row, face.group(1))
    return out


def test_no_generated_face_prints_the_exhaust_keyword_twice():
    """`EB-293`. `exhaust: true` emits `CardKeyword.Exhaust` and the game's own
    auto-keyword pipeline prints the banner from there, so a face that ALSO
    writes the word prints it twice. [USER] read it off a reward screen --
    "Exhaust. The jellyfish carries out your front Plan now. Exhaust." -- and
    the r2 Opus seat read the same on Vanguard.

    Six rows carried both spellings across two arms. The generator strips the
    word now (`gen_klee_cards._dedupe_printed_exhaust`), so this is a class-wide
    assertion rather than six: a seventh row written next week cannot bring it
    back."""
    offenders = [cid for cid, (row, face) in _emitted_faces().items()
                 if row.get("exhaust") and "Exhaust." in face]
    assert offenders == [], (
        "these faces print the Exhaust banner the keyword rail already "
        f"prints: {offenders}")


def test_every_plan_only_row_prints_where_it_is_played():
    """`EB-293`. A row with a `plan:` and no now-line declares
    `KokomiTargets.PetOnly`, so the jellyfish is its ONLY legal target -- and
    the face used to say only what the Plan does. The r2 Opus seat: "Plan-only
    cards never say what happens if you play them normally... I never risked
    finding out."

    Read off the same test the target type is derived from, so the sentence and
    the target cannot disagree."""
    faces = _emitted_faces()
    plan_only = [cid for cid, (row, _) in faces.items()
                 if row.get("plan") and not row.get("effects")]
    assert plan_only, "the arm has no plan-only rows -- this pin is stale"
    for cid in plan_only:
        assert faces[cid][1].startswith(
            "Play on the [gold]Bake-Kurage[/gold]. "), (
            f"{cid} is plan-only and does not print where it is played")
    for cid, (row, face) in faces.items():
        if row.get("plan") and row.get("effects"):
            assert "Play on the [gold]Bake-Kurage[/gold]" not in face, (
                f"{cid} has a now-line, so the jellyfish is not its only "
                "target and the line would be false")


def test_every_kokomi_row_declares_the_target_type_the_slice_states():
    """`EB-296`, the codegen half, pinned per row for the WHOLE arm.

    The slice's rule (draft 6 rule 2): a card with only a `Plan` line targets
    the jellyfish alone; a card with both lines targets "an enemy or the
    jellyfish" when its now-line aims at an enemy and "you or the jellyfish"
    otherwise; a card with no `Plan` line is aimed the ordinary way. The Plan
    clause's own aim is resolved at CARRY-OUT and never at play, so a
    front-enemy Plan on a plan-only row must not pull the card's target toward
    the enemy.

    [USER] hit the three cases live in one session and they read as three
    different bugs ("'ambush' has no valid selector at all"; Slack Water
    "offers only the enemy"; Kurage's Oath fine), which is why the derivation
    is pinned here for every row rather than for the three."""
    import re

    checked = 0
    for path in sorted(_GENERATED.glob("*.cs")):
        source = path.read_text(encoding="utf-8")
        ident = re.search(r"Sheet entry: id=(\S+)", source)
        if ident is None:
            continue
        rows = {r["id"]: r for r in yaml.safe_load(
            loader.PROTOTYPE_SHEET.read_text(encoding="utf-8")) or []}
        row = rows.get(ident.group(1))
        if row is None or row.get("character") != "kokomi":
            continue
        if not row.get("plan"):
            assert "KokomiTargets." not in source, (
                f"{row['id']} has no Plan line and must not declare a "
                "pet-accepting target type")
            continue
        checked += 1
        aims_at_enemy = any(
            fx.get("target") in ("enemy", "front_enemy")
            for fx in row.get("effects") or [])
        expected = ("KokomiTargets.PetOnly" if not row.get("effects")
                    else "KokomiTargets.PetOrEnemy" if aims_at_enemy
                    else "KokomiTargets.PetOrSelf")
        assert expected in source, (
            f"{row['id']} should declare {expected}")
    assert checked >= 15, f"only {checked} Plan rows checked -- pin is stale"


# =============================================================================
# `EB-322`: NO PLAYER-FACING TITLE CARRIES THE SHADOW SUFFIX.
#
# A row that supersedes a shipped row keeps its name and declares the shadow
# with " (proto)" so the sheet namespace stays legible. That is a SHEET device
# -- the arm substitutes the shipped row out of the pool -- and the emitter
# printed it on the card face anyway: the round-7 seats read
# `Thoma - Blazing Barrier (proto)`, `Barbara - Let the Show Begin (proto)`
# and `Sparks 'n' Splash (proto)` as the cards' names.
# =============================================================================

def test_the_two_engines_spell_the_shadow_suffix_once():
    """The lint restates the suffix rather than importing it (it runs as a
    bare script), so the two spellings are pinned against each other here --
    the drift that would make the lint stop seeing a declaration while both
    engines kept stripping one."""
    import tools.lint_unique_names as lint

    assert lint.SHADOW_SUFFIX == loader.PROTOTYPE_SHADOW_SUFFIX


def test_display_name_strips_the_declaration_and_nothing_else():
    assert loader.display_name("Undertow (proto)") == "Undertow"
    assert loader.display_name("Undertow") == "Undertow"
    # Not a prefix rule and not a substring rule: only a trailing declaration.
    assert loader.display_name("(proto) Undertow") == "(proto) Undertow"
    assert loader.display_name("Undertow (proto) II") == "Undertow (proto) II"


def test_every_declared_shadow_names_a_row_that_really_ships():
    """The suffix is a CLAIM -- "this rewrites the shipped row of that name" --
    and a claim nothing checks is decoration. Read off the live surface and
    the six shipped sheets, so a row that keeps the suffix after its shipped
    twin is renamed or retired fails here."""
    shipped: dict[str, list[str]] = {}
    for sheet in loader.DOCS_CARD_SHEETS:
        for row in yaml.safe_load(
                (loader.DOCS_DIR / sheet).read_text(encoding="utf-8")) or []:
            shipped.setdefault(row["name"], []).append(row["id"])

    declared = 0
    for row in yaml.safe_load(
            loader.PROTOTYPE_SHEET.read_text(encoding="utf-8")) or []:
        name = row["name"]
        if not name.endswith(loader.PROTOTYPE_SHADOW_SUFFIX):
            continue
        declared += 1
        bare = loader.display_name(name)
        assert bare in shipped, (
            f"{row['id']} declares a shadow of {bare!r}, which no shipped "
            "row holds -- the suffix shadows nothing and the face prints "
            "the bare name unchecked")
    # Non-vacuous: the surface carries declared shadows today, and a sweep
    # over none of them is the dead-gate class this repo has been bitten by.
    assert declared >= 30, f"only {declared} declared shadows found"


def test_the_sim_carries_the_bare_title_for_a_declared_shadow():
    """The sim's half of "both engines print the same title", taken at the ONE
    seam: a `Card` the engine hands to a report, a draft or a seat page has
    the player's title on it, never the sheet's declaration."""
    rows = {r["id"]: r["name"] for r in yaml.safe_load(
        loader.PROTOTYPE_SHEET.read_text(encoding="utf-8")) or []}
    checked = 0
    for card in loader.prototype_cards():
        assert loader.PROTOTYPE_SHADOW_SUFFIX not in card.name, (
            f"{card.id} reaches the engine as {card.name!r}")
        if rows[card.id].endswith(loader.PROTOTYPE_SHADOW_SUFFIX):
            checked += 1
            assert card.name == loader.display_name(rows[card.id])
    assert checked >= 30, f"only {checked} shadowed rows checked"


def test_no_generated_prototype_face_prints_the_suffix():
    """The mod's half, read off the COMMITTED C# rather than off the emitter:
    the defect was "the row is right and the emitted card is not", and the
    card face is what the seat read."""
    import re

    titles = {}
    for path in sorted(_GENERATED.glob("*.cs")):
        source = path.read_text(encoding="utf-8")
        ident = re.search(r"Sheet entry: id=(\S+)", source)
        title = re.search(r'\("title", "(.*)"\),', source)
        if ident is None or title is None:
            continue
        titles[ident.group(1)] = title.group(1)

    assert titles, "no generated prototype titles found -- the sweep is dead"
    offenders = {cid: t for cid, t in titles.items()
                 if loader.PROTOTYPE_SHADOW_SUFFIX in t}
    assert not offenders, f"generated titles carrying the declaration: {offenders}"

    # And the positive half: the shadowed rows are still THERE, printing the
    # shipped row's title, which is what the arm is for.
    rows = {r["id"]: r["name"] for r in yaml.safe_load(
        loader.PROTOTYPE_SHEET.read_text(encoding="utf-8")) or []}
    checked = 0
    for cid, title in titles.items():
        if rows.get(cid, "").endswith(loader.PROTOTYPE_SHADOW_SUFFIX):
            checked += 1
            assert title == loader.display_name(rows[cid])
    assert checked >= 30, f"only {checked} shadowed faces checked"


def test_the_sheet_declares_a_shadow_only_with_the_suffix_both_engines_strip():
    """`EB-419`. The five Furina reframe copies declared their shadow with a
    SECOND spelling, ` (reframe)`, which `display_name` does not strip and no
    lint reads -- so the arm's starter printed "Aria of Recompense (reframe)"
    to the round-5 seat, and four offer rows carried the same tag.

    The rule is one spelling, not two: a row that ends its `name:` in
    parentheses is either declaring the ONE shadow both engines strip, or it
    is printing those parentheses on the card face. There is no third case,
    and this is the check that says so -- over the sheet, the sim's `Card`s
    and the committed C# alike, because that is the whole path the tag
    travelled."""
    import re

    rows = yaml.safe_load(
        loader.PROTOTYPE_SHEET.read_text(encoding="utf-8")) or []
    trailing = re.compile(r"\s\([^()]*\)$")
    for row in rows:
        name = row["name"]
        if name.endswith(loader.PROTOTYPE_SHADOW_SUFFIX):
            continue
        assert not trailing.search(name), (
            f"{row['id']}: {name!r} ends in a parenthesised tag that is not "
            f"{loader.PROTOTYPE_SHADOW_SUFFIX!r}, so nothing strips it and "
            "the card face prints it")

    # The two faces the seat actually read, checked as faces rather than as
    # sheet rows: the engine's `Card` and the committed C# title.
    for card in loader.prototype_cards():
        assert "(reframe)" not in card.name, card.id
    for path in sorted(_GENERATED.glob("*.cs")):
        title = re.search(r'\("title", "(.*)"\),',
                          path.read_text(encoding="utf-8"))
        assert title is None or "(reframe)" not in title.group(1), path.name


def test_the_lint_reads_a_declaration_as_a_shadow_and_a_bare_name_as_a_clash(
        tmp_path):
    """`EB-322`'s lint half, both directions, against the REAL relic sources.

    The relaxation has to be exactly as wide as the declaration: the shipped
    row and its declared rewrite pass, and two rows holding one bare name
    still fail -- which is the guarantee the suffix was standing in for."""
    import subprocess
    import sys

    lint = str(REPO / "tools" / "lint_unique_names.py")

    def run(body: str):
        sheet = tmp_path / f"s{abs(hash(body))}.yaml"
        sheet.write_text(body, encoding="utf-8")
        return subprocess.run([sys.executable, lint, str(sheet)],
                              capture_output=True, text=True)

    shadow = run(
        'cards:\n'
        '- {id: undertow, name: "Undertow", cost: 1, type: skill,\n'
        '   rarity: common}\n'
        '- {id: proto_kk_undertow, name: "Undertow (proto)", cost: 1,\n'
        '   type: skill, rarity: common}\n')
    assert shadow.returncode == 0, shadow.stdout + shadow.stderr

    clash = run(
        'cards:\n'
        '- {id: undertow, name: "Undertow", cost: 1, type: skill,\n'
        '   rarity: common}\n'
        '- {id: undertow_two, name: "Undertow", cost: 1, type: skill,\n'
        '   rarity: common}\n')
    assert clash.returncode == 1, clash.stdout + clash.stderr
    assert "DUPLICATE NAME" in clash.stdout

    twins = run(
        'cards:\n'
        '- {id: undertow, name: "Undertow", cost: 1, type: skill,\n'
        '   rarity: common}\n'
        '- {id: proto_a, name: "Undertow (proto)", cost: 1, type: skill,\n'
        '   rarity: common}\n'
        '- {id: proto_b, name: "Undertow (proto)", cost: 1, type: skill,\n'
        '   rarity: common}\n')
    assert twins.returncode == 1, twins.stdout + twins.stderr
    assert "DUPLICATE SHADOW" in twins.stdout

    orphan = run(
        'cards:\n'
        '- {id: proto_a, name: "Nothing Here (proto)", cost: 1, type: skill,\n'
        '   rarity: common}\n')
    assert orphan.returncode == 1, orphan.stdout + orphan.stderr
    assert "SHADOW OF NOTHING" in orphan.stdout


# --------------------- EB-403: the banner face and the Dexterity gloss ------

def _war_banner_row() -> dict:
    return next(r for r in yaml.safe_load(
        loader.PROTOTYPE_SHEET.read_text(encoding="utf-8")) or []
        if r["id"] == "proto_mi_gorou_war_banner")


def test_the_war_banner_face_says_the_banner_takes_the_dexterity_back():
    """`EB-403`, and the twin, C# side.

    The face printed "Gain 2 Dexterity for 2 turns" on a screen whose Dexterity
    gloss says "It does not decay" (Kokomi round 10, run 1, (c) 1). Both are
    true: the row grants real `DexterityPower`, and the `mi_war_banner` power
    it applies beside it is a clock that hands 2 of it back when it runs out
    (`WarBannerPower.Tick`). Nothing printed said so.

    The clause is now on the card face and on the power's own tip, and the two
    say the same thing.
    """
    row = _war_banner_row()
    assert "takes 2 back" in row["description"]
    emitted = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
               / "Generated" / "ProtoMiGorouWarBanner.cs").read_text(
                   encoding="utf-8")
    assert "for 2 turns, then the banner takes 2 back." in emitted
    power = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
             / "CompanionOverhaulInazuma.cs").read_text(encoding="utf-8")
    banner = power.split("class WarBannerPower")[1].split("class ")[0]
    assert '{Amount:plural:turn|turns}, then "' in banner
    assert '+ "[/blue] back."' in banner
    # ...and the number it hands back is the POWER's constant, not the card's
    # upgradeable amount: an upgraded banner grants 3 and gives 2 back.
    assert "CompanionOverhaulLaw.WarBannerDexterity" in banner
    assert row["upgrade"] is None if "upgrade" in row else True


def test_the_base_dexterity_gloss_is_still_the_base_rule():
    """The other half of the row, and the half it would have been easy to get
    wrong: Dexterity really does not decay, so the fix is a clause on the
    exception and NOT an edit to the base word's definition. Both copies of
    that definition -- the page's and the mod's hover tip -- are unchanged.
    """
    from understudy import blindplay_notes
    assert blindplay_notes.BASE_KEYWORDS["Dexterity"] == (
        "Adds its amount to every Block the wearer gains. It does not decay.")
    tips = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
            / "BaseKeywordTips.cs").read_text(encoding="utf-8")
    dexterity = tips.split("ForDexterity")[1].split("</summary>")[0]
    assert "It " in dexterity and "does not decay." in dexterity
