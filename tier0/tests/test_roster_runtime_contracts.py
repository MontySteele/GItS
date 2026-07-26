"""Static regressions for roster-only runtime contracts.

These are intentionally source-level checks. The failures they guard happen
after C# compilation, while Godot preloads a run or ModHelper registers hook
delegates, and therefore are invisible to the simulator.
"""

from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "klee-mod" / "KleeCode"
PCK_BUILDER = (ROOT / "tools" / "build_pck.ps1").read_text()

CHARACTERS = {
    "Klee": (SOURCE / "Klee.cs").read_text(),
    "Furina": (SOURCE / "Furina.cs").read_text(),
}

REQUIRED_PRELOAD_OVERRIDES = {
    "CustomVisualPath",
    "CustomIconPath",
    "CustomEnergyCounterPath",
    "CustomTrailPath",
    "CustomRestSiteAnimPath",
    "CustomMerchantAnimPath",
}

CONVERTED_PATH_PROPERTIES = {
    "CustomVisualPath",
    "CustomRestSiteAnimPath",
    "CustomMerchantAnimPath",
}


def _pck_path(source: str, property_name: str) -> str:
    match = re.search(
        rf"{property_name}\s*=>\s*KleePck\.Path\(\"([^\"]+)\"\)",
        source,
    )
    assert match, f"{property_name} must use a character-specific KleePck.Path"
    return match.group(1)


def test_every_character_redirects_the_id_derived_preload_scenes():
    for character, source in CHARACTERS.items():
        for property_name in REQUIRED_PRELOAD_OVERRIDES:
            assert re.search(
                rf"override\s+string\?\s+{property_name}\b",
                source,
            ), f"{character} is missing {property_name}"


def test_scene_conversion_paths_are_unique_across_the_roster():
    owners: dict[str, str] = {}
    for character, source in CHARACTERS.items():
        for property_name in CONVERTED_PATH_PROPERTIES:
            path = _pck_path(source, property_name)
            assert path not in owners, (
                f"{character}.{property_name} reuses {path}, already owned by "
                f"{owners[path]}; BaseLib's conversion registry is path-keyed"
            )
            owners[path] = f"{character}.{property_name}"


CONTRACT = ROOT / "klee-mod" / "assets" / "klee.pck.contract.txt"


def test_pck_builder_authors_every_character_scene_and_material():
    # Two authoring channels (animation sprint 1): heredoc text inside
    # build_pck.ps1, or a git-tracked scene source under klee-mod/pck-src/
    # that the build overlays into the pck work dir.
    pck_src = ROOT / "klee-mod" / "pck-src"
    for character, source in CHARACTERS.items():
        resources = re.findall(
            r'KleePck\.Path\("([^"]+\.(?:tscn|tres))"\)',
            source,
        )
        assert resources, f"{character} has no packaged scene resources"
        for resource in resources:
            windows_path = resource.replace("/", "\\")
            assert windows_path in PCK_BUILDER or (pck_src / resource).is_file(), (
                f"{character} references {resource}, but build_pck.ps1 "
                "does not author it and klee-mod/pck-src does not carry it"
            )


def test_the_pck_contract_is_derived_from_the_build_not_written_by_hand():
    """C4 (audit sec.3.2). The contract must MEASURE the pck, not assert it.

    Until this sprint the builder appended a hand-written list of ~45
    `resource=` lines after the export, and this file asserted against THAT
    list -- an assertion checking an assertion, with the actual pack contents
    untouched by either. Every copy block in the builder skips on a missing
    source, so the contract named `res://furina/salon/member_usher.png`
    whether or not that file existed; missing salon art shipped with all
    gates green.

    Pinned on the mechanism rather than on any resource name, because a
    derived list has no fixed contents.
    """
    assert '$contract = "$out.contract.txt"' in PCK_BUILDER
    assert "contract=roster-pck-v3" in PCK_BUILDER
    assert "Get-FileHash" in PCK_BUILDER
    # Derived: enumerate the work directory, do not restate a literal.
    assert "Get-ChildItem $work -Recurse -File" in PCK_BUILDER
    assert "Contract would be empty" in PCK_BUILDER, (
        "an empty derived contract must throw -- a zero-length measurement is "
        "the failure mode a derived list introduces, and it has to be loud")
    # No resource literal may reappear: that is the hand-written list coming
    # back, and it would silently outrank the derived one. Matched as a quoted
    # string with a PATH inside it -- the derived line is the bare prefix
    # `'resource=res://' + $_.FullName...`, which is the one legal occurrence.
    literals = re.findall(r"'resource=res://[^']+'", PCK_BUILDER)
    assert not literals, (
        f"literal resource lines are back in the builder: {literals[:3]}. The "
        "contract is derived; a literal beside it is the sec.3.2 defect "
        "returning, and it would assert what the build did not do.")


def test_deploy_rejects_an_old_or_mismatched_pck():
    deploy = (ROOT / "klee-mod" / "build" / "deploy.ps1").read_text()
    validate = (ROOT / "klee-mod" / "build" / "validate.ps1").read_text()

    assert "pck.contract.txt" in deploy
    # v2 is stale BY DEFINITION, not merely by age: a v2 contract is a
    # hand-written one, so reading it as current reads an assertion as a
    # measurement.
    assert "contract=roster-pck-v3" in validate
    assert "roster-pck-v2" not in validate
    assert "Get-FileHash" in validate


@pytest.mark.skipif(
    not CONTRACT.exists(),
    reason="*.pck.contract.txt is a gitignored build artifact; only present "
           "where the pck has been built")
def test_the_built_contract_names_every_referenced_scene():
    """The assertion that moved out of the builder's source and onto its OUTPUT.

    This is the half that can actually fail when a copy block skips: the
    resource is missing from the work directory, so it is missing from the
    derived contract, so this fails -- where the old source-text check passed
    because the literal was still typed in the script.
    """
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "contract=roster-pck-v3" in contract, "rebuild with build_pck.ps1"
    for character, source in CHARACTERS.items():
        for resource in re.findall(
                r'KleePck\.Path\("([^"]+\.(?:tscn|tres))"\)', source):
            assert f"resource=res://{resource}" in contract, (
                f"{character} references {resource}, and the built pck "
                "contract does not list it -- a copy block skipped, or the "
                "pck is stale. Rebuild with tools/build_pck.ps1.")


def test_roster_uses_one_combined_combat_hook_subscription():
    entry = (SOURCE / "KleeMod.cs").read_text()
    calls = re.findall(
        r"(?m)^\s*ModHelper\.SubscribeForCombatStateHooks\(",
        entry,
    )
    assert len(calls) == 1, "ModHelper rejects a duplicate subscription id"
    assert "KleeElementalHooks.Subscribe" in entry
    assert "FurinaResourceHooks.Subscribe" in entry


def test_runtime_self_check_sweeps_resolved_character_assets():
    self_check = (SOURCE / "Diagnostics" / "KleeSelfCheck.cs").read_text()
    assert "character.AssetPaths" in self_check
    assert "character.AssetPathsCharacterSelect" in self_check
    assert "ResourceLoader.Exists(path)" in self_check
    assert 'Fail("R9"' in self_check


def test_frozen_power_supplies_the_localization_checked_by_r8():
    frozen = (SOURCE / "Powers" / "FrozenPower.cs").read_text()
    assert "FrozenPower : PowerModel, ILocalizationProvider" in frozen
    assert '("title", "Frozen")' in frozen
    assert '("description",' in frozen


def test_bomb_suppression_latch_is_per_creature_and_snapshotted():
    """Armed-Bomb suppression, C# side (sim law: combat.py snapshots
    eligibility BEFORE the enemy action resolves; state.py keeps the spent
    latch on the enemy). The port once re-derived eligibility live per hit
    and kept the latch in process-global statics keyed by combat reference
    equality, which reload or a second live combat silently reset."""
    bomb = (SOURCE / "Powers" / "BombPower.cs").read_text()
    # Spent latch lives on the enemy creature, not in combat-keyed statics.
    assert "SpireField<Creature, bool> SuppressionSpent" in bomb
    assert "_suppressionCombat" not in bomb
    assert "HashSet<Creature>" not in bomb
    # The multiplier honors the BeforeAttack snapshot for the whole action
    # instead of re-reading _damages per hit.
    assert re.search(
        r"_suppressionAttack != null\s*\?\s*_suppressionArmedForAttack",
        bomb,
    )


def test_beetle_swarm_snapshots_bombed_state_at_cast():
    """R72 (2026-07-26), C# side. The sim pin lives in test_klee.py; this is
    the parity half, and it is a source-text check for the same reason the
    suppression latch above is -- the divergence is a phase question (WHEN the
    bomb state is read), and no simulator run can observe the port's phase.

    The failure it guards is a silent revert to the live per-hit read: that
    version compiles, plays, and differs from the sim by exactly the +6 the
    ruling restored."""
    card = (SOURCE / "Cards" / "KaboomBeetleSwarm.cs").read_text()
    # The snapshot is taken in OnPlay, before the damage series is executed.
    play = card.split("protected override async Task OnPlay", 1)[1]
    snapshot_at = play.index("_bombedAtCast =")
    assert snapshot_at < play.index("DamageCmd.Attack"), (
        "the bombed-state snapshot must be taken before the first hit")
    # ...and the per-hit modifier consults the snapshot, not live Powers.
    assert re.search(
        r"_bombedAtCast is \{ \} snap\s*\?\s*snap\.Any\(", card)
    # Cleared on the way out, so no play can inherit another's snapshot.
    assert re.search(r"finally\s*\{[^}]*_bombedAtCast = null;", card,
                     re.DOTALL)
