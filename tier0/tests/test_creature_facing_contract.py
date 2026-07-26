"""`CreatureFacing`'s load-bearing decisions, promoted from Log.Warn to pinned.

Audit sec.4 item 3. Every one of these was decided against a decompile of a
game that has **no facing concept at all** (v0.107.1: nothing in `NCreature`,
`NCreatureVisuals` or `CreatureAnimator` carries a flip). There is therefore no
upstream signal to check the mod against and no test that can execute any of
it — the whole feature is a gap this mod fills, and the only thing standing
behind the decisions today is a single `Log.Warn` on one reflection lookup.

Which makes the failure mode specific and nasty: every one of these reverts
LOOKS like a visual tweak and at least one of them is not. Mirroring
`Visuals.Scale` instead of `%Facing` inverts the hitbox `UpdateBounds` reads
back — a gameplay bug wearing a visual bug's clothes.

Source-text, in the `test_roster_runtime_contracts` idiom, for the same reason
that file gives: these fail inside a compiled Godot run while a scene tree is
being built, which is invisible to the simulator.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FACING = (
    ROOT / "klee-mod" / "KleeCode" / "Vfx" / "CreatureFacing.cs"
).read_text(encoding="utf-8")


def _code_only(source: str) -> str:
    """Strip doc comments so a prose mention is never mistaken for a call.

    This file argues its decisions at length in `///` blocks, and every token
    below appears in that prose as well as (or instead of) in the code. A
    naive `in FACING` check would pass on the strength of the comment
    explaining why the thing must NOT be done.
    """
    return "\n".join(
        line for line in source.splitlines()
        if not line.lstrip().startswith(("///", "//")))


CODE = _code_only(FACING)


# --- decision 1: the mirror rides %Facing --------------------------------

def test_the_mirror_is_applied_to_the_facing_node():
    assert '"%Facing"' in CODE, (
        "the mirror must be looked up on a %Facing node -- that is also what "
        "scopes the feature, since only our own convention combat scenes "
        "carry one and every base creature's lookup returns null")
    assert re.search(r"facing\.Scale\s*=\s*new\s+Vector2\(", CODE), CODE


def test_the_mirror_never_touches_visuals_scale():
    """The gameplay bug wearing a visual bug's clothes.

    NCreature owns `Visuals.Scale`: ScaleTo, SetDefaultScaleTo and
    OstyScaleToSize all write it, and UpdateBounds reads it back to place the
    hitbox and the intent. A sign flip there inverts the hitbox, which is not
    a rendering problem.
    """
    # Stated as "the only Scale assignment in the file is the facing node's"
    # rather than "Visuals.Scale never appears". The revert this guards writes
    # through the LOCAL (`visuals.Scale = ...`), which a check spelled against
    # the property name misses entirely -- confirmed by mutating the file.
    scale_writes = re.findall(r"(\w+)\.Scale\s*=(?!=)", CODE)
    assert scale_writes == ["facing"], scale_writes
    assert not re.search(r"\bScaleTo\b|\bSetDefaultScaleTo\b|\bOstyScaleToSize\b",
                         CODE), CODE


def test_the_mirror_never_rides_the_animated_rig():
    """%Rig carries the attack lunge in its own position track.

    A node's position track is expressed in its PARENT's space, so mirroring
    the rig flips the art while leaving the lunge travelling right -- a
    moonwalk. The mirror sits on a parent of the animated node so it mirrors
    the travel too, and nothing animates %Facing, so the two never fight.
    """
    assert '"%Rig"' not in CODE, CODE


# --- decision 2: the hook is AttackCommand.Execute -----------------------

def test_the_patch_prefixes_attack_command_execute():
    """Turn at the START of the attack, not when the damage lands.

    `AttackCommand.Execute` awaits `CreatureCmd.TriggerAnim` before dealing
    any damage, so hooking the damage funnel would flip the sprite at the
    moment of impact -- after the character had already lunged the wrong way.
    """
    assert re.search(
        r"\[HarmonyPatch\(typeof\(AttackCommand\),\s*nameof\(AttackCommand\.Execute\)\)\]",
        CODE), CODE
    assert "[HarmonyPrefix]" in CODE, CODE
    assert "[HarmonyPostfix]" not in CODE, (
        "a postfix runs after the damage has landed, which is the impact-time "
        "flip this patch exists to avoid")


def test_execute_is_the_only_thing_this_file_patches():
    """Stated as an enumeration so a SECOND patch cannot slip in beside it.

    The named alternative -- `CreatureCmd.Damage`, which every damage
    overload funnels into -- is the tempting one precisely because it is easy
    to reach. It is also the impact-time flip.
    """
    patched = re.findall(r"\[HarmonyPatch\(typeof\((\w+)\),\s*nameof\((\w+\.\w+)\)\)\]",
                         CODE)
    assert patched == [("AttackCommand", "AttackCommand.Execute")], patched


# --- decision 3: the reflection lookup degrades, never throws ------------

def test_the_private_target_accessor_is_null_guarded():
    """`AccessTools.Method` returns null on a rename; it does not throw.

    A game update that renames `GetPossibleTargets` must cost the mod its
    facing and nothing else. This is also the pattern the audit cites as
    correct against `KleeMod.PatchAll`'s all-or-nothing bootstrap -- so it has
    to keep working while that one is repaired.
    """
    assert re.search(r"MethodInfo\?\s+PossibleTargets", CODE), CODE
    assert re.search(r"if\s*\(\s*PossibleTargets\s*==\s*null\s*\)", CODE), CODE
    assert "catch (Exception)" in CODE, (
        "Invoke on a half-built command must degrade to no facing; Execute "
        "validates its own targets AFTER this prefix runs, so a command "
        "without targets is a normal state here, not an error")


def test_the_rename_warning_fires_once_not_per_attack():
    """A per-attack log line on a renamed method would flood the console."""
    assert "_warnedNoTargetAccessor" in CODE, CODE
    assert re.search(r"if\s*\(!\s*_warnedNoTargetAccessor\s*\)", CODE), CODE


# --- decision 4: the turn is aimed at the MEAN of the targets ------------

def test_facing_is_aimed_at_the_mean_of_the_targets():
    """A fully-centered encounter is exactly where an AoE spans both sides.

    Picking `targets[0]` there makes the turn depend on iteration order
    rather than on where the damage is going -- and centered encounters (the
    Act 2 Kaiser Crab, the only boss with FullyCenterPlayers) are the entire
    reason this file exists.
    """
    assert re.search(r"targetXs\.Average\(\)", CODE), CODE
    assert not re.search(r"targetXs\s*\[\s*0\s*\]", CODE), CODE


def test_dead_zone_and_self_target_are_excluded():
    """Below the dead zone "left" and "right" are not a distinction."""
    assert re.search(r"Mathf\.Abs\(delta\)\s*<\s*DeadZonePx", CODE), CODE
    assert re.search(r"target\s*!=\s*attacker", CODE), CODE
    assert "target.IsAlive" in CODE, (
        "a corpse must not drag the mean toward a side the attack is not "
        "going to")
