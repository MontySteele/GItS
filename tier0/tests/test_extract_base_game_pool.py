"""Regression tests for the local base-game extraction plumbing.

These tests use tiny synthetic source trees. They never read or reproduce
base-game data, and they do not require ilspycmd or a game installation.
"""

import dataclasses
from pathlib import Path
from types import SimpleNamespace

import pytest

from tier0.content import loader
from tier0.engine.state import Card
from tools import build_official_sheet as build
from tools import extract_base_game_pool as extract


def _spec(tmp_path: Path, **overrides) -> build.CharacterSpec:
    """An Ironclad-shaped spec pointed at a scratch directory.

    Built by REPLACING fields on the real registry entry, so a field added to
    CharacterSpec cannot be quietly missing from these tests.
    """
    return dataclasses.replace(build.CHARACTERS["ironclad"],
                               **{**{
                                   "extractor_sheet": tmp_path / "cards.yaml",
                                   "supplements": (),
                                   "char_facts": tmp_path / "facts.yaml",
                                   "pool": tmp_path / "pool.yaml",
                                   "upgrades": tmp_path / "upgrades.yaml",
                                   "char_out": tmp_path / "char.yaml",
                               }, **overrides})


def _write_type(root: Path, relative: str, namespace: str, body: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"namespace {namespace};\n\n{body}\n")
    return path


def test_game_dll_finds_macos_app_layout(tmp_path, monkeypatch):
    install = tmp_path / "Slay the Spire 2"
    dll = (install / "SlayTheSpire2.app" / "Contents" / "Resources"
           / "data_sts2_macos_arm64" / "sts2.dll")
    dll.parent.mkdir(parents=True)
    dll.touch()
    props = tmp_path / "local.props"
    props.write_text(
        f"<Project><PropertyGroup><GameDir>{install}</GameDir>"
        "</PropertyGroup></Project>"
    )
    monkeypatch.setattr(extract, "LOCAL_PROPS", props)

    assert extract.game_dll() == dll


def test_project_mode_passes_reference_path_and_runs_once(
        tmp_path, monkeypatch):
    dll = tmp_path / "data_sts2_macos_arm64" / "sts2.dll"
    dll.parent.mkdir()
    dll.touch()
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(extract.shutil, "which", lambda _name: "/fake/ilspycmd")
    monkeypatch.setattr(extract.subprocess, "run", fake_run)
    extract._run_ilspy_project(dll, tmp_path / "out")

    assert len(calls) == 1
    command, kwargs = calls[0]
    assert command[0] == "/fake/ilspycmd"
    assert command[command.index("-r") + 1] == str(dll.parent)
    assert "--project" in command
    assert "--nested-directories" in command
    assert kwargs["timeout"] == 300


def test_decompile_character_reads_pool_and_cards_from_one_project(
        tmp_path, monkeypatch):
    dll = tmp_path / "sts2.dll"
    dll.touch()
    calls = []

    def fake_project(_dll, root):
        calls.append(_dll)
        _write_type(
            root, "pool/IroncladCardPool.cs",
            "MegaCrit.Sts2.Core.Models.CardPools",
            "class IroncladCardPool { object Cards => "
            "ModelDb.Card<Bash>(); }",
        )
        _write_type(
            root, "cards/Bash.cs", "MegaCrit.Sts2.Core.Models.Cards",
            "class Bash { }",
        )
        # A same-named type in another namespace must not be selected.
        _write_type(root, "other/Bash.cs", "Example.Other", "class Bash { }")

    monkeypatch.setattr(extract, "_run_ilspy_project", fake_project)

    names, sources = extract.decompile_character(dll, "Ironclad")

    assert calls == [dll]
    assert names == ["Bash"]
    assert "MegaCrit.Sts2.Core.Models.Cards" in sources["Bash"]
    assert "Example.Other" not in sources["Bash"]


def test_id_prefix_is_per_character_and_pins_ironclad():
    """Two base-game pools share card NAMES (Strike, Defend); if they shared
    an id prefix the second extraction would silently overwrite the first in
    the loader. `ic_` is pinned because artifacts this tool cannot rewrite
    already depend on it."""
    assert extract.id_prefix("Ironclad") == "ic_"
    assert extract.id_prefix("ironclad") == "ic_"
    assert extract.id_prefix("Silent") == "si_"
    assert extract.id_prefix("Defect") == "de_"
    assert len({extract.id_prefix(name)
                for name in ("Ironclad", "Silent", "Defect")}) == 3


def test_id_prefix_refuses_a_collision_with_a_pinned_prefix(monkeypatch):
    monkeypatch.setattr(extract, "ID_PREFIXES", {"ironclad": "si_"})
    with pytest.raises(SystemExit, match="collides with"):
        extract.id_prefix("Silent")


def test_emitted_upgrade_delta_supports_energy_and_hit_count():
    assert extract._delta_key({"op": "energy"}, "amount") == "energy"
    assert extract._delta_key({"op": "damage"}, "times") == "times"


def test_declared_keywords_reads_the_single_element_list_shape():
    """ilspy renders a one-keyword list as a compiler-generated type, NOT a
    `{ ... }` initialiser. The brace-shaped reader found nothing on exactly
    the cards that carry one keyword, which is most of them."""
    single = ("public override IEnumerable<CardKeyword> CanonicalKeywords => "
              "new global::_003C_003Ez__ReadOnlySingleElementList"
              "<CardKeyword>(CardKeyword.Sly);")
    assert extract._declared_keywords(single) == ["Sly"]
    braces = ("public override IEnumerable<CardKeyword> CanonicalKeywords => "
              "new HashSet<CardKeyword> { CardKeyword.Exhaust, "
              "CardKeyword.Innate };")
    assert extract._declared_keywords(braces) == ["Exhaust", "Innate"]
    assert extract._declared_keywords("class Plain { }") == []


def test_declared_keywords_refuses_an_unreadable_declaration():
    """An unparsed keyword line looks exactly like an empty one. Guessing
    empty is how five Sly cards were emitted as vanilla rows."""
    with pytest.raises(extract._Untranslatable,
                       match="unrecognised CanonicalKeywords"):
        extract._declared_keywords(
            "IEnumerable<CardKeyword> CanonicalKeywords { get { yield break }")


def test_a_keyword_with_no_tier0_field_excludes_the_card():
    """Keywords are RULES ON THE CARD. tier0 has fields for three of them;
    a fourth must take the card out of the sheet, not ride along invisibly."""
    assert set(extract.CARD_KEYWORDS) == {"Exhaust", "Innate", "Retain"}
    assert set(extract.CARD_KEYWORDS.values()) <= {
        f.name for f in dataclasses.fields(Card)}
    body = """
class SyntheticCard
{
    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new global::_003C_003Ez__ReadOnlySingleElementList<CardKeyword>(
            CardKeyword.%s);

    protected override async Task OnPlay(PlayerChoiceContext c, CardPlay p)
    {
        await CreatureCmd.GainBlock(base.Owner.Creature, 5m);
    }
}
"""
    card = {"name": "SyntheticCard", "cost": 1, "type": "Skill",
            "rarity": "Common"}
    row, _ = extract._sheet_row(card, body % "Retain", "xx_")
    assert row["retain"] is True
    with pytest.raises(extract._Untranslatable, match="CardKeyword.Sly"):
        extract._sheet_row(card, body % "Sly", "xx_")


def test_canonical_tags_reads_only_the_declared_tag_property():
    source = """
    HashSet<CardTag> CanonicalTags => new HashSet<CardTag> {
        CardTag.Strike
    };
    bool ReadsOtherCards => card.Tags.Contains(CardTag.Skill);
    """
    assert extract._canonical_tags(source) == ["strike"]
    assert extract._canonical_tags(
        "bool ReadsOtherCards => card.Tags.Contains(CardTag.Strike);") == []


def test_supplement_upgrade_uses_row_shape_not_card_identity():
    row = {"effects": [
        {"op": "conditional", "then": [
            {"op": "gain_max_hp", "amount": 2},
        ]},
        {"op": "upgrade_in_hand", "scope": "chosen"},
        {"op": "exhaust_from", "amount": 1},
    ]}
    source = """
class SyntheticCard
{
    bool Preview => base.IsUpgraded;

    void OnUpgrade()
    {
        base.DynamicVars.MaxHp.UpgradeValueBy(1m);
    }
}
"""

    assert extract._supplement_upgrade_delta(row, source) == {
        "max_hp": 1,
        "upgrade_scope": "all",
        "exhaust_select": "chosen",
    }


def test_supplement_upgrade_keys_cover_runtime_formula_shapes():
    assert extract._row_delta_key({"effects": [{
        "op": "damage", "target": "enemy",
        "amount_formula": {"base": 1, "per": 2, "count": "pile"},
    }]}, "ExtraDamage") == "formula_per"
    assert extract._row_delta_key({"effects": [{
        "op": "damage", "amount": 1, "target": "enemy",
        "bonus_per_target_power": {"power": "vulnerable", "per": 2},
    }]}, "ExtraDamage") == "target_power_per"
    # Standard DLL variable names take precedence over the structural
    # fallback when a future formula card upgrades more than one field.
    assert extract._row_delta_key({"effects": [
        {"op": "damage", "target": "enemy",
         "amount_formula": {"base": 1, "per": 2, "count": "pile"}},
        {"op": "block", "amount": 4},
    ]}, "Block") == "block"
    assert extract._row_delta_key({"effects": [{
        "op": "damage", "amount": 1, "target": "enemy",
        "bonus_per_target_power": {"power": "vulnerable", "per": 2},
    }]}, "Damage") == "damage"
    assert extract._row_delta_key({"effects": [{
        "op": "conditional", "if": "ready", "then": [
            {"op": "damage", "amount": 3, "target": "enemy"},
        ], "else": [
            {"op": "damage", "amount": 3, "target": "enemy"},
        ],
    }]}, "Damage") == "conditional_damage"
    assert extract._row_delta_key({"effects": [
        {"op": "apply_power", "power": "vulnerable", "amount": 1,
         "target": "enemy"},
        {"op": "apply_power", "power": "strength", "amount": 1,
         "target": "self"},
    ]}, "VulnerablePower") == "vulnerable"


def test_supplement_upgrade_keys_cover_bounded_history_shapes():
    assert extract._row_delta_key({
        "effects": [{"op": "draw", "amount": 2}],
        "on_exhaust_energy": 2,
    }, "Energy") == "on_exhaust_energy"
    assert extract._row_delta_key({"effects": [{
        "op": "conditional", "if": "ready",
        "then": [{"op": "block", "amount": 4},
                 {"op": "block", "amount": 4}],
        "else": [{"op": "block", "amount": 4}],
    }]}, "Block") == "conditional_block"
    assert extract._row_delta_key({"effects": [
        {"op": "damage", "amount": 3, "target": "enemy"},
        {"op": "grow_damage", "amount": 2},
    ]}, "Increase") == "damage_growth"


def test_builder_merges_required_supplement_layers(tmp_path, monkeypatch):
    first = tmp_path / "pass4.yaml"
    second = tmp_path / "pass5.yaml"
    first.write_text("- {id: two}\n")
    second.write_text("- {id: three}\n")
    spec = _spec(tmp_path, supplements=(first, second))
    monkeypatch.setattr(build, "_doc1_cards", lambda _spec: [{"id": "one"}])

    assert [row["id"] for row in build._validated_pool_cards(spec)] == [
        "one", "three", "two",
    ]


def test_builder_rejects_cross_layer_overlap(tmp_path, monkeypatch):
    first = tmp_path / "pass4.yaml"
    second = tmp_path / "pass5.yaml"
    first.write_text("- {id: repeated}\n")
    second.write_text("- {id: repeated}\n")
    spec = _spec(tmp_path, supplements=(first, second))
    monkeypatch.setattr(build, "_doc1_cards", lambda _spec: [{"id": "one"}])

    with pytest.raises(SystemExit, match="overlaps earlier layers"):
        build._validated_pool_cards(spec)


def test_builder_fails_closed_on_a_missing_required_layer(tmp_path,
                                                          monkeypatch):
    """The guarantee the registry exists to keep: a REQUIRED layer that is
    absent is an error, never a quietly smaller pool. game_ref/ has been
    destroyed twice; a glob would have made both losses silent."""
    present = tmp_path / "pass4.yaml"
    present.write_text("- {id: two}\n")
    spec = _spec(tmp_path, supplements=(present, tmp_path / "pass5.yaml"))
    monkeypatch.setattr(build, "_doc1_cards", lambda _spec: [{"id": "one"}])

    with pytest.raises(SystemExit, match="refusing to write a partial pool"):
        build._validated_pool_cards(spec)


def test_every_registered_character_derives_the_same_path_convention():
    """The registry's only per-character fact is which layers are required;
    everything else follows the naming convention the loader and the
    distinctness report already glob for."""
    for name, spec in build.CHARACTERS.items():
        assert spec.character == name
        assert spec.char_id == f"real_{name}"
        assert spec.pool.name == f"{name}_pool.yaml"
        assert spec.upgrades.name == f"{name}-upgrades.yaml"
        assert spec.extractor_sheet.name == f"{name}-cards.yaml"
        assert spec.char_out.name == f"char_real_{name}.yaml"
        assert all(p.name.startswith(f"{name}_pool_pass")
                   for p in spec.supplements)


def test_loader_rejects_a_missing_required_external_layer(
        tmp_path, monkeypatch):
    (tmp_path / "pool.yaml").write_text("- {id: one}\n")
    monkeypatch.setattr(loader, "GAME_REF_DIR", tmp_path)
    monkeypatch.setattr(loader, "EXTERNAL_CARD_SHEETS",
                        {"pool.yaml": "reference"})
    monkeypatch.setattr(loader, "EXTERNAL_CARD_LAYERS",
                        {"pool.yaml": ("missing.yaml",)})

    with pytest.raises(ValueError, match="missing required local layer"):
        loader._external_cards()


def test_builder_rejects_partial_upgrade_coverage(tmp_path):
    (tmp_path / "upgrades.yaml").write_text("one: {damage: 1}\n")
    spec = _spec(tmp_path)

    with pytest.raises(SystemExit, match="missing upgrades for.*two"):
        build._validated_upgrades(spec, [{"id": "one"}, {"id": "two"}])
