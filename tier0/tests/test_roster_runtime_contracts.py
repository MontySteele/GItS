"""Static regressions for roster-only runtime contracts.

These are intentionally source-level checks. The failures they guard happen
after C# compilation, while Godot preloads a run or ModHelper registers hook
delegates, and therefore are invisible to the simulator.
"""

from pathlib import Path
import re


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


def test_pck_builder_authors_every_character_scene_and_material():
    for character, source in CHARACTERS.items():
        resources = re.findall(
            r'KleePck\.Path\("([^"]+\.(?:tscn|tres))"\)',
            source,
        )
        assert resources, f"{character} has no packaged scene resources"
        for resource in resources:
            windows_path = resource.replace("/", "\\")
            assert windows_path in PCK_BUILDER, (
                f"{character} references {resource}, but build_pck.ps1 "
                "does not author it"
            )
            assert f"resource=res://{resource}" in PCK_BUILDER


def test_deploy_rejects_an_old_or_mismatched_pck():
    deploy = (ROOT / "klee-mod" / "build" / "deploy.ps1").read_text()
    validate = (ROOT / "klee-mod" / "build" / "validate.ps1").read_text()

    assert '$contract = "$out.contract.txt"' in PCK_BUILDER
    assert "contract=roster-pck-v2" in PCK_BUILDER
    assert "Get-FileHash" in PCK_BUILDER
    assert "pck.contract.txt" in deploy
    assert "contract=roster-pck-v2" in validate
    assert "Get-FileHash" in validate


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
