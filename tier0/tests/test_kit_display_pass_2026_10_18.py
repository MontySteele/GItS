"""Kit display pass, 2026-10-18: one pin per BACKLOG line fixed under
"Kits and display". Text, previews and display only; the C# halves are in
`klee-mod/KleeTests/Prototype/KitDisplayPassTests.cs`."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHEET = ROOT / "docs" / "prototype-surface.yaml"
GENERATED = ROOT / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"
CODE = ROOT / "klee-mod" / "KleeCode"


def _row(card_id: str) -> str:
    sheet = SHEET.read_text(encoding="utf-8")
    row = sheet[sheet.index(f"id: {card_id},"):]
    return row[:row.index("\n\n")]


def test_chain_fuse_names_mines_and_hovers_the_mine_tip():
    # Klee suite 6 lane 2: Chain Fuse grows Mines too (a Mine is a Bomb,
    # `ProtoBombPower.GrowOn`), and the face did not say so.
    assert ("Each [gold]Bomb[/gold] and [gold]Mine[/gold] on the enemy"
            in _row("proto_ko_chain_fuse"))
    face = (GENERATED / "ProtoKoChainFuse.cs").read_text(encoding="utf-8")
    assert "ArmKeywordTips.ForMine(" in face


def test_mikas_discount_is_printed_as_energy():
    # Klee suite 6 lane 3: the discount is Energy, so a Spark-cost Attack
    # gets nothing from it. The face and the badge print the Energy icon.
    assert ("costs {energyPrefix:energyIcons(1)} less"
            in _row("proto_mc_mika_starfrost_swirl"))
    hooks = (CODE / "Powers" / "Prototype" / "CompanionOverhaulHooks.cs"
             ).read_text(encoding="utf-8")
    assert "costs {Amount:energyIcons()} less." in hooks


def test_the_big_ones_bombs_line_is_a_live_preview():
    # A bare `{SetOffBombs}` formats from the var's BaseValue (0).
    row = _row("proto_ko_the_big_one")
    assert "{SetOffBombs:diff()}" in row
    assert "{SetOffBombs}" not in row


def test_the_bomb_number_folds_hardened_shell():
    bomb = (CODE / "Powers" / "Prototype" / "ProtoBombPower.cs"
            ).read_text(encoding="utf-8")
    assert "return ShellCapped(target, total);" in bomb
    assert "OfType<HardenedShellPower>()" in bomb


def test_the_reaction_preview_says_an_artifact_blocks_the_debuff():
    # Varka combo round (2026-10-05) item 4: Artifact silently ate
    # Overloaded's Weak and Electro-Charged's Poison. Frozen already said so.
    tips = (CODE / "Cards" / "KleeCardTooltips.cs").read_text(encoding="utf-8")
    assert "ReactionEffects.ArtifactWillBlock(reaction, enemy)" in tips
    assert "DebuffArtifactSentence(" in tips
    effects = (CODE / "Powers" / "ReactionEffects.cs").read_text(
        encoding="utf-8")
    note = effects.index("ReactionLog.Note(reaction, target, dealer, cardSource);")
    assert "DebuffBlockedByArtifact(debuff)" in effects[note - 800:note]
