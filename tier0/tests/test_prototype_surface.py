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


def test_shipped_surface_is_empty_and_loads(tmp_path):
    """The committed surface is EMPTY -- the R213 deletion rule's steady state."""
    assert loader.PROTOTYPE_SHEET.exists()
    assert yaml.safe_load(
        loader.PROTOTYPE_SHEET.read_text(encoding="utf-8")) in ([], None)
    assert loader.prototype_cards() == []


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
