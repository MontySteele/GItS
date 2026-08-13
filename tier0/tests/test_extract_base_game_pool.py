"""Regression tests for the local base-game extraction plumbing.

These tests use tiny synthetic source trees. They never read or reproduce
base-game data, and they do not require ilspycmd or a game installation.
"""

import dataclasses
from pathlib import Path
from types import SimpleNamespace

import pytest

from tier0.content import loader
from tier0.engine.state import SLY_AUTOPLAY, Card
from tools import build_official_sheet as build
from tools import extract_base_game_pool as extract


def test_the_required_layer_lists_agree_between_loader_and_builder():
    """A reviewed layer listed in one place and not the other is a pool that
    loads at the wrong size -- silently, because both sides fail closed only
    against their OWN list.

    Lives HERE, not in test_real_silent.py: it compares two committed Python
    lists and needs no game_ref, and the environment that most needs it is
    the fresh clone (CI) where a game_ref skip guard would blind it."""
    checked = 0
    for name, spec in build.CHARACTERS.items():
        sheet = f"{name}_pool.yaml"
        if sheet not in loader.EXTERNAL_CARD_SHEETS:
            continue
        assert tuple(p.name for p in spec.supplements) == \
            loader.EXTERNAL_CARD_LAYERS.get(sheet, ())
        checked += 1
    # The loop must never quietly check nobody.
    assert checked >= 2


def test_id_prefixes_are_pairwise_distinct_across_registered_characters():
    """id_prefix guards a derived prefix against the PINNED table at
    derivation time, but two derived prefixes can only collide across runs
    (Watcher/Warden -> wa_). The registry is the one place every character
    is known at once, so distinctness is pinned here."""
    prefixes = {name: extract.id_prefix(name) for name in build.CHARACTERS}
    assert len(set(prefixes.values())) == len(prefixes), prefixes


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
    path.write_text(f"namespace {namespace};\n\n{body}\n", encoding="utf-8")
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
        "</PropertyGroup></Project>",
        encoding="utf-8")
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


def test_declared_keywords_refuses_a_token_free_declaration():
    """A declaration that MATCHES but names no keyword -- e.g. delegating to
    a cached field -- must exclude, not read as empty. Only an explicit
    empty collection may say `no keywords` out loud."""
    with pytest.raises(extract._Untranslatable, match="no CardKeyword token"):
        extract._declared_keywords(
            "IEnumerable<CardKeyword> CanonicalKeywords => _keywords;")
    empty = ("IEnumerable<CardKeyword> CanonicalKeywords => "
             "new HashSet<CardKeyword>();")
    assert extract._declared_keywords(empty) == []
    braces = ("IEnumerable<CardKeyword> CanonicalKeywords => "
              "new HashSet<CardKeyword> { };")
    assert extract._declared_keywords(braces) == []


def test_a_keyword_with_no_tier0_field_excludes_the_card():
    """Keywords are RULES ON THE CARD. tier0 has fields for four of them;
    a fifth must take the card out of the sheet, not ride along invisibly."""
    assert set(extract.CARD_KEYWORDS) == {"Exhaust", "Innate", "Retain", "Sly"}
    assert set(extract.CARD_KEYWORDS.values()) <= {
        f.name for f in dataclasses.fields(Card)}
    # EB-71 (R174): Sly maps onto the ONE `sly` field, and emits the reserved
    # auto-play rider rather than an authored effect list. Emitting a bare
    # list here (or `true`, which `sly` cannot carry) would print a keyword
    # that did nothing -- the dropped-rule defect wearing a new costume (ask
    # A4, ruled 2026-07-27). The tool cannot import the engine, so its mirror
    # of the rider is pinned against the engine's own constant here.
    assert extract.CARD_KEYWORDS["Sly"] == "sly"
    assert extract.SLY_AUTOPLAY_ROW == [SLY_AUTOPLAY]
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
    row, _ = extract._sheet_row(card, body % "Sly", "xx_")
    assert row["sly"] == [SLY_AUTOPLAY]  # the rider, never an authored list
    assert "sly_keyword" not in row      # the retired field
    with pytest.raises(extract._Untranslatable, match="CardKeyword.Ethereal"):
        extract._sheet_row(card, body % "Ethereal", "xx_")


def test_an_animation_delay_branch_does_not_exclude_a_card():
    """A local holding an anim delay, plus the Fast-Mode PREFERENCE branch
    that bumps it, is cosmetic in both halves -- and cosmetic-ness has to
    propagate from the declaration to the statements that feed it, or the
    `if` survives and the card leaves the sheet over an animation timer."""
    stmts = [
        "float num = base.Owner.Character.AttackAnimDelay;",
        "if (SaveManager.Instance.PrefsSave.FastMode == FastModeType.Normal) {",
        "num += 0.2f;",
        "}",
        "await CardPileCmd.Draw(choiceContext, 1m, base.Owner);",
    ]
    kept = extract._drop_cosmetic_blocks(extract._drop_cosmetic_locals(stmts))
    assert kept == ["await CardPileCmd.Draw(choiceContext, 1m, base.Owner);"]


def test_a_real_branch_still_excludes_the_card():
    """The propagation must not become a general `if`-eraser: an unrelated
    local keeps its branch, and the card stays out."""
    stmts = [
        "float num = base.Owner.Character.AttackAnimDelay;",
        "if (cardPlay.Target.HasPower<PoisonPower>()) {",
        "await PowerCmd.Apply<PoisonPower>(choiceContext, cardPlay.Target);",
        "}",
    ]
    kept = extract._drop_cosmetic_blocks(extract._drop_cosmetic_locals(stmts))
    assert any(extract.CONTROL_FLOW.match(s) for s in kept)


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


def test_parse_card_records_the_tokens_a_card_makes_and_names():
    """`EB-63`. Both facts existed and both were thrown away.

    The create call was matched by TOKEN_CREATE (which `read_pool` already
    used to find the pool's token TYPES) and then not written down, so nobody
    could ask which CARD made the token. The hover-tip is the other spelling:
    the card names the token without making one, which is a mention and never
    a generation.
    """
    source = """
    public sealed class Fake : CardModel {
        IEnumerable<IHoverTip> ExtraHoverTips => HoverTipFactory.FromCard<Tok>();
        public Fake() : base(1, CardType.Skill, CardRarity.Common) { }
        async Task OnPlay() { await Tok.CreateInHand(base.Owner); }
    }
    """
    card = extract.parse_card(source, "Fake")
    assert card["creates"] == ["Tok"]
    assert card["card_refs"] == ["Tok"]


def test_parse_card_records_what_a_computed_magnitude_counts():
    """`EB-63`, the other half: a CalculatedVar's ARGUMENTS.

    The census's P2 predicate says "this card's number is computed at play
    time" from the presence of the var. What the number is computed FROM lives
    in the constructor argument and the multiplier lambda, and without those
    the card is a payoff of nothing nameable -- which is how 24 of the five
    pools' payoff-shaped cards ended up unattributed.
    """
    source = """
    public sealed class Fake : CardModel {
        IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[2] {
            new CalculationBaseVar(0m),
            new CalculatedVar("CalculatedToks").WithMultiplier(
                (CardModel card, Creature? _) =>
                    PileType.Exhaust.GetPile(card.Owner).Cards.Count(
                        (CardModel c) => c.Tags.Contains(CardTag.Tok)))
        };
        public Fake() : base(2, CardType.Skill, CardRarity.Rare) { }
    }
    """
    calc, = extract.parse_card(source, "Fake")["calc_vars"]
    assert calc["var"] == "CalculatedVar"
    assert calc["args"] == ['"CalculatedToks"']
    assert calc["reads"] == ["CardTag.Tok", "PileType.Exhaust"]


def test_a_longer_fluent_chain_still_yields_its_reads():
    """The multiplier is not always the first link after the constructor.

    Four cards put a marker call in front of it. Matching only
    `.WithMultiplier(` dropped their reads silently, which is the worst shape
    of extraction bug: the card still appears, with a state of nothing.
    """
    source = """
    public sealed class Fake : CardModel {
        IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[1] {
            new CalculatedDamageVar(ValueProp.Move).FromOsty().WithMultiplier(
                delegate(CardModel card, Creature? _) {
                    return card.Owner.AllCards.Count(
                        (CardModel c) => c.Tags.Contains(CardTag.Tok)
                                         || c is Widget);
                })
        };
        public Fake() : base(1, CardType.Attack, CardRarity.Rare) { }
    }
    """
    calc, = extract.parse_card(source, "Fake")["calc_vars"]
    assert calc["reads"] == ["CardTag.Tok", "is Widget"]


def test_a_calculated_var_without_a_multiplier_reads_nothing():
    """Fail EMPTY, not wrong. A var whose shape changed must not silently
    inherit the reads of the next var in the file."""
    source = """
    public sealed class Fake : CardModel {
        IEnumerable<DynamicVar> CanonicalVars => new DynamicVar[1] {
            new CalculatedDamageVar(ValueProp.Move)
        };
        public Fake() : base(1, CardType.Attack, CardRarity.Common) { }
        async Task OnPlay() { var x = card.Tags.Contains(CardTag.Tok); }
    }
    """
    calc, = extract.parse_card(source, "Fake")["calc_vars"]
    assert calc["args"] == ["ValueProp.Move"]
    assert calc["reads"] == []


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
    first.write_text("- {id: two}\n", encoding="utf-8")
    second.write_text("- {id: three}\n", encoding="utf-8")
    spec = _spec(tmp_path, supplements=(first, second))
    monkeypatch.setattr(build, "_doc1_cards", lambda _spec: [{"id": "one"}])

    assert [row["id"] for row in build._validated_pool_cards(spec)] == [
        "one", "three", "two",
    ]


def test_builder_rejects_cross_layer_overlap(tmp_path, monkeypatch):
    first = tmp_path / "pass4.yaml"
    second = tmp_path / "pass5.yaml"
    first.write_text("- {id: repeated}\n", encoding="utf-8")
    second.write_text("- {id: repeated}\n", encoding="utf-8")
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
    present.write_text("- {id: two}\n", encoding="utf-8")
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
    (tmp_path / "pool.yaml").write_text("- {id: one}\n", encoding="utf-8")
    monkeypatch.setattr(loader, "GAME_REF_DIR", tmp_path)
    monkeypatch.setattr(loader, "EXTERNAL_CARD_SHEETS",
                        {"pool.yaml": "reference"})
    monkeypatch.setattr(loader, "EXTERNAL_CARD_LAYERS",
                        {"pool.yaml": ("missing.yaml",)})

    with pytest.raises(ValueError, match="missing required local layer"):
        loader._external_cards()


def test_builder_rejects_partial_upgrade_coverage(tmp_path):
    (tmp_path / "upgrades.yaml").write_text("one: {damage: 1}\n",
                                            encoding="utf-8")
    spec = _spec(tmp_path)

    with pytest.raises(SystemExit, match="missing upgrades for.*two"):
        build._validated_upgrades(spec, [{"id": "one"}, {"id": "two"}])


def test_the_tag_scoped_dial_commits_only_a_prefix():
    """The finished `tag_damage_<tag>` name embeds a base-game CardTag, so
    it may exist only in the gitignored output, never in the committed
    dial -- the payload rule (sprint log 2026-07-27 s14.1), applied to a
    power NAME. `decompile_character` completes the entry at run time."""
    assert extract.TAG_SCOPED_POWERS      # the category must not vanish
    for power_cls, prefix in extract.TAG_SCOPED_POWERS.items():
        assert prefix.endswith("_")
        assert power_cls not in extract.SUPPORTED_POWERS
    assert all(not name.startswith("tag_damage_")
               for name in extract.SUPPORTED_POWERS.values())
    assert all(not key.startswith("tag_damage_")
               for key in extract.UPGRADE_POWER_KEY)


def test_single_card_tag_requires_exactly_one_tag():
    # One tag, referenced twice, is one tag. (The tag here is fictional:
    # this test may not carry base-game data either.)
    src = ("if (!card.HasTag(CardTag.Ember)) return num;\n"
           "// scoped to CardTag.Ember\n")
    assert extract._single_card_tag(src, "EmberPower") == "ember"
    with pytest.raises(SystemExit):
        extract._single_card_tag("no tag reference at all", "EmberPower")
    with pytest.raises(SystemExit):
        extract._single_card_tag("CardTag.Ember CardTag.Ash", "EmberPower")


def test_read_decompiled_short_fails_closed(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "a" / "FooPower.cs").write_text("x", encoding="utf-8")
    assert extract._read_decompiled_short(tmp_path, "FooPower") == "x"
    with pytest.raises(SystemExit):
        extract._read_decompiled_short(tmp_path, "MissingPower")
    # An ambiguous match is a real error, same as _read_decompiled_type.
    (tmp_path / "b" / "FooPower.cs").write_text("y", encoding="utf-8")
    with pytest.raises(SystemExit):
        extract._read_decompiled_short(tmp_path, "FooPower")


def test_an_unimportable_tier0_is_reported_as_such_not_as_a_dial_verdict(
        monkeypatch):
    """Tooling-hardening sprint item 4, red demonstration.

    `_power_gap` wrapped `from tier0.engine import refpowers` in
    `except Exception` and answered "{power} is not on the SUPPORTED_POWERS
    dial" -- a claim about the dial's CONTENTS, made by code that had just
    failed to open the dial. The blocker manifest then recorded an adjudicated
    verdict where the truth was "unknown, the engine was unreachable", and the
    two want opposite repairs (implement the power vs fix the import).

    Simulated by making the import raise, which is the only way to reach the
    branch in a repo where tier0 imports fine.
    """
    import builtins

    real_import = builtins.__import__

    def boom(name, *a, **kw):
        if name.startswith("tier0.engine"):
            raise ImportError("no module named tier0.engine (simulated)")
        return real_import(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", boom)
    reason = extract._power_gap("BarricadePower")
    assert "could not be imported" in reason
    assert "UNKNOWN" in reason
    assert "SUPPORTED_POWERS dial" not in reason, (
        "an unreachable engine must not be reported as a verdict on the dial")
    assert "ImportError" in reason and "simulated" in reason


def test_a_real_dial_gap_still_reads_as_a_dial_gap():
    """The other half: with tier0 importable, an unsupported power keeps its
    original message. Separating the two reasons must not lose either one."""
    reason = extract._power_gap("NoSuchInventedPower")
    assert "is not on the SUPPORTED_POWERS dial" in reason
    assert "could not be imported" not in reason
