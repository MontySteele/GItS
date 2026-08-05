"""Regression tests for the patch sentinel's diff core.

Everything here runs against SYNTHETIC records and synthetic decompiled
sources. No game install, no ilspycmd, no game_ref/, and no base-game data --
which is the point: the half of the sentinel that must be right is the half
that decides what counts as drift, and that half has to be testable on a fresh
clone where the sentinel itself can only say "skipped".
"""

from tools import patch_sentinel as ps


def test_no_findings_when_the_records_match():
    base = {"A": {"cost": 1, "rarity": "Common", "cmds": ["X.y"]}}
    assert ps.diff_records("cards/Test", base, dict(base)) == []


def test_a_changed_field_names_the_field_and_both_values():
    base = {"A": {"cost": 1, "rarity": "Common"}}
    cur = {"A": {"cost": 2, "rarity": "Common"}}
    findings = ps.diff_records("cards/Test", base, cur)
    assert len(findings) == 1
    f = findings[0]
    assert (f.kind, f.field, f.baseline, f.current) == ("changed", "cost", 1, 2)
    assert "baseline says 1, DLL says 2" in f.render()


def test_added_and_removed_entries_are_reported_by_key():
    base = {"A": {"cost": 1}, "B": {"cost": 1}}
    cur = {"A": {"cost": 1}, "C": {"cost": 1}}
    kinds = {(f.key, f.kind) for f in ps.diff_records("relics", base, cur)}
    assert kinds == {("C", "added"), ("B", "removed")}


def test_nested_var_maps_are_compared_by_value():
    base = {"A": {"vars": {"Damage": 6.0, "Block": 5.0}}}
    cur = {"A": {"vars": {"Block": 5.0, "Damage": 7.0}}}
    findings = ps.diff_records("cards/Test", base, cur)
    assert [f.field for f in findings] == ["vars"]
    # ... and key order alone is not a patch.
    assert ps.diff_records(
        "cards/Test", base, {"A": {"vars": {"Block": 5.0, "Damage": 6.0}}}) == []


def test_json_round_tripping_is_not_reported_as_drift():
    """A baseline read back from JSON has 3 where the parser produced 3.0, and
    tuples come back as lists. Neither is MegaCrit changing anything."""
    base = {"A": {"cost": 3, "cmds": ("X.y", "Z.w")}}
    cur = {"A": {"cost": 3.0, "cmds": ["X.y", "Z.w"]}}
    assert ps.diff_records("cards/Test", base, cur) == []


def test_a_shape_change_is_one_schema_finding_not_a_whole_pool_of_drift():
    """The failure mode this guards: an extractor that grew a field would
    otherwise report every entry as changed and bury the real finding."""
    base = {"A": {"cost": 1}, "B": {"cost": 2}}
    cur = {"A": {"cost": 1, "target": "Self"},
           "B": {"cost": 9, "target": "Self"}}
    findings = ps.diff_records("cards/Test", base, cur)
    schema = [f for f in findings if f.kind == "schema"]
    changed = [f for f in findings if f.kind == "changed"]
    assert len(schema) == 1 and "DLL-only: ['target']" in schema[0].note
    assert [(f.key, f.field) for f in changed] == [("B", "cost")]


def test_explicit_field_lists_ignore_everything_else():
    base = {"Ironclad": {"hp": 80, "note": "whatever"}}
    cur = {"Ironclad": {"hp": 75, "note": "different"}}
    findings = ps.diff_records("characters/Ironclad", base, cur,
                               fields=("hp",))
    assert [(f.field, f.baseline, f.current) for f in findings] == [
        ("hp", 80, 75)]


def test_redaction_hides_the_identifier_but_stays_stable():
    findings = ps.diff_records("relics", {"A": {"x": 1}}, {"A": {"x": 2}})
    rendered = findings[0].render(redact=True)
    assert "A" not in rendered.replace("PATCH", "")
    assert ps.digest("A") in rendered
    assert ps.digest("A") == ps.digest("A") != ps.digest("B")


def test_relic_parsing_reads_numbers_and_vocabulary_from_a_synthetic_model():
    src = (
        "namespace MegaCrit.Sts2.Core.Models.Relics;\n"
        "public sealed class Widget : RelicModel\n{\n"
        "  public override RelicRarity Rarity => RelicRarity.Uncommon;\n"
        "  protected override IEnumerable<DynamicVar> CanonicalVars =>\n"
        "    new DynamicVar(\"Sprockets\", 3m);\n"
        "  public override async Task Foo() {\n"
        "    await PowerCmd.Apply<FakePower>(ctx, owner, 2m);\n"
        "    await OrbCmd.Channel<FakeOrb>(ctx, owner);\n"
        "  }\n}\n")
    record = ps.parse_relic(src, "Widget")
    assert record["rarity"] == "Uncommon"
    assert record["vars"] == {"Sprockets": 3.0}
    assert "PowerCmd.Apply" in record["generic_cmds"]
    assert record["powers"] == ["FakePower"]
    assert record["orbs"] == ["FakeOrb"]


def test_relic_reader_skips_non_relic_types_and_records_pool_membership(
        tmp_path):
    (tmp_path / "Widget.cs").write_text(
        "namespace MegaCrit.Sts2.Core.Models.Relics;\n"
        "public sealed class Widget : RelicModel {\n"
        "  public override RelicRarity Rarity => RelicRarity.Rare;\n}\n",
        encoding="utf-8")
    # The abstract base lives in the same namespace and is not a relic.
    (tmp_path / "RelicModel.cs").write_text(
        "namespace MegaCrit.Sts2.Core.Models.Relics;\n"
        "public abstract class RelicModel : Model { }\n", encoding="utf-8")
    (tmp_path / "TestRelicPool.cs").write_text(
        "namespace MegaCrit.Sts2.Core.Models.RelicPools;\n"
        "public sealed class TestRelicPool : RelicPoolModel {\n"
        "  ModelDb.Relic<Widget>();\n}\n", encoding="utf-8")
    relics = ps.read_relics(tmp_path)
    assert set(relics) == {"Widget"}
    assert relics["Widget"]["pools"] == ["TestRelicPool"]


def test_character_facts_are_read_structurally(tmp_path):
    (tmp_path / "Testguy.cs").write_text(
        "namespace MegaCrit.Sts2.Core.Models.Characters;\n"
        "public sealed class Testguy : CharacterModel {\n"
        "  public override int StartingHp => 72;\n"
        "  public override int StartingGold => 99;\n"
        "  public override IEnumerable<CardModel> StartingDeck => new[] {\n"
        "    ModelDb.Card<Alpha>(), ModelDb.Card<Alpha>(),\n"
        "    ModelDb.Card<Beta>() };\n"
        "  public override IReadOnlyList<RelicModel> StartingRelics =>\n"
        "    ModelDb.Relic<Gizmo>();\n}\n", encoding="utf-8")
    facts = ps.read_character_facts(tmp_path, "Testguy")
    assert facts == {"hp": 72, "starting_gold": 99,
                     "starting_deck_size": 3, "starting_relic_count": 1}


def test_char_facts_baseline_sums_both_starting_relic_spellings(tmp_path):
    path = tmp_path / "x_char_facts.yaml"
    path.write_text(
        "id: real_x\nhp: 70\nstarting_deck: [a, b, c]\n"
        "relic_hooks: []\n"
        "starting_relic_effects:\n- {combat_start_draw: 2}\n", encoding="utf-8")
    assert ps.baseline_character_facts(path) == {
        "hp": 70, "starting_deck_size": 3, "starting_relic_count": 1}


def test_no_game_installed_is_a_skip_and_never_a_failure(monkeypatch):
    """The CI / fresh-clone contract. A sentinel that fails where the game is
    absent gets deleted the first week, so absence exits 0 even under
    --strict."""
    def no_game():
        raise SystemExit("sts2.dll not found")
    monkeypatch.setattr(ps.extract, "game_dll", no_game)
    assert ps.main([]) == 0
    assert ps.main(["--strict"]) == 0


def test_strict_is_the_only_way_to_a_nonzero_exit(monkeypatch, tmp_path):
    """Drift on a watched surface: advisory still exits 0, --strict does not.
    Driven through the dll surface alone so no decompilation is involved."""
    fake_dll = tmp_path / "sts2.dll"
    fake_dll.write_bytes(b"pretend this is an assembly")
    snapshot = tmp_path / "dll.json"
    monkeypatch.setattr(ps.extract, "game_dll", lambda: fake_dll)
    monkeypatch.setattr(ps, "DLL_SNAPSHOT", snapshot)
    monkeypatch.setattr(ps, "SNAP_DIR", tmp_path)
    monkeypatch.setattr(ps, "GAME_REF", tmp_path)

    assert ps.main(["--surfaces", "dll"]) == 0        # blesses, finds nothing
    fake_dll.write_bytes(b"pretend this is a PATCHED assembly")
    assert ps.main(["--surfaces", "dll"]) == 0        # advisory: still 0
    assert ps.main(["--surfaces", "dll", "--strict"]) == 1
