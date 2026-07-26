"""F2's Harmony bootstrap, pinned where the suite can hold it.

Serenitea Sweep II, Track A. The defect F2 closed was not a bug in any one
patch: it was `harmony.PatchAll(assembly)`, which walks the assembly's patch
classes in reflection order and abandons the walk at the first one that
throws. Every patch after that point is never applied, and the single
try/catch around the call logged one line naming the patch that threw -- not
the ones that consequently never armed.

Two of this assembly's patches are softlock guards (`CreateForMerchant` type
fallback, finding 24 -- entering ANY shop black-screens the run; and the
`CreateForReward` clamp, finding 22). Reflection order is neither source order
nor stable across builds, so a dead lookup in a cosmetic VFX patch could
disarm the shop guard, and the run would then die in a shop hours later for a
reason nothing in the log pointed at.

WHY SOURCE-TEXT. Same reason `test_creature_facing_contract` gives: this code
runs inside a compiled Godot process during mod initialization, which the
simulator cannot execute and the Python suite cannot import. There is no C#
test project. So the suite pins the SHAPE, and the behaviour was verified by
running it -- see the bite-check in the sprint log, which loads the built
klee.dll outside Godot, breaks one lookup at a time and reads the boot report.
That bite-check is a manual gate; these rules are the automated half, and they
exist so a later edit cannot quietly reintroduce the batch-abort shape.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KLEECODE = ROOT / "klee-mod" / "KleeCode"
BOOTSTRAP = KLEECODE / "KleePatchBootstrap.cs"


def _code_only(source: str) -> str:
    """Strip comments so prose about a call is never read as the call.

    These files argue at length in `///` blocks and name the very constructs
    they exist to forbid -- `PatchAll` appears in three comments explaining
    why it is gone. A naive substring check would fail on the documentation.
    """
    return "\n".join(
        line for line in source.splitlines()
        if not line.lstrip().startswith(("///", "//")))


def _cs_files() -> list[Path]:
    return sorted(p for p in KLEECODE.rglob("*.cs")
                  if "obj" not in p.parts and "bin" not in p.parts)


def test_patchall_is_not_called_anywhere() -> None:
    """The batch-abort shape must not come back.

    `PatchAll` in any of its overloads re-creates the exact failure F2 closed.
    """
    offenders = []
    for path in _cs_files():
        code = _code_only(path.read_text(encoding="utf-8"))
        if re.search(r"\.PatchAll\s*\(", code):
            offenders.append(path.relative_to(ROOT).as_posix())

    assert not offenders, (
        "harmony.PatchAll aborts the whole patch walk on the first failure, "
        "silently disarming every later patch including the shop softlock "
        "guards. Use KleePatchBootstrap.ApplyAll instead. Offenders: "
        f"{offenders}")


def test_bootstrap_is_the_single_entry_point() -> None:
    """Exactly one ApplyAll call, and it is in the mod initializer."""
    calls = {
        path.relative_to(ROOT).as_posix(): len(
            re.findall(r"KleePatchBootstrap\.ApplyAll\s*\(",
                       _code_only(path.read_text(encoding="utf-8"))))
        for path in _cs_files()
    }
    calling = {name: n for name, n in calls.items() if n}

    assert calling == {"klee-mod/KleeCode/KleeMod.cs": 1}, (
        "ApplyAll should be called exactly once, from KleeMod.Initialize. "
        f"Found: {calling}")


def test_target_methods_resolve_through_the_bootstrap() -> None:
    """No bare AccessTools lookups inside a [HarmonyTargetMethods] body.

    `AccessTools.Method` and `AccessTools.PropertyGetter` return null for a
    name that stopped resolving. Yielding that null makes Harmony throw about
    a null element rather than about the name that died, and filtering it out
    silently makes the patch inert. Routing through KleePatchBootstrap records
    the miss BY NAME so the boot report can attribute it.
    """
    offenders = []
    for path in _cs_files():
        code = _code_only(path.read_text(encoding="utf-8"))
        if "[HarmonyTargetMethods]" not in code:
            continue
        # From the attribute to the end of its method body. Brace-matching is
        # overkill here: the next attribute or the class close is a fine
        # terminator, and over-reading only makes this rule stricter.
        body = code.split("[HarmonyTargetMethods]", 1)[1]
        body = re.split(r"\n\s*\[Harmony", body)[0]
        for bare in re.findall(r"(?<!Bootstrap\.)\bAccessTools\.(Method|PropertyGetter)\s*\(",
                               body):
            offenders.append(f"{path.relative_to(ROOT).as_posix()}: AccessTools.{bare}")

    assert not offenders, (
        "TargetMethods must resolve via KleePatchBootstrap.ResolveMethod / "
        "ResolvePropertyGetter so a dead lookup names itself at boot. "
        f"Offenders: {offenders}")


def test_no_reflection_lookup_in_a_static_field_initializer() -> None:
    """A throwing lookup in a field initializer becomes a softlock.

    `AccessTools.FieldRefAccess` THROWS (it does not return null). In a static
    field initializer that surfaces as a TypeInitializationException on first
    use -- and for MerchantCompanionSlots, first use was a player walking into
    a shop. A renamed private field therefore black-screened the run: the very
    failure class the surrounding patches exist to prevent, produced by the
    guard itself. Resolve in a method with its own catch and hold the result
    nullable, which is the CreatureFacing pattern.
    """
    offenders = []
    for path in _cs_files():
        for line in _code_only(path.read_text(encoding="utf-8")).splitlines():
            stripped = line.strip()
            # A field initializer: an assignment whose right-hand side is the
            # throwing lookup. Inside a method body the call is fine, because
            # the method can catch.
            if re.search(r"=\s*AccessTools\.FieldRefAccess", stripped):
                offenders.append(
                    f"{path.relative_to(ROOT).as_posix()}: {stripped[:90]}")

    # The one legitimate site is inside ResolveColorlessEntries(), which wraps
    # it in try/catch -- that reads `return AccessTools.FieldRefAccess...`, not
    # `= AccessTools.FieldRefAccess...`, so it does not match.
    assert not offenders, (
        "AccessTools.FieldRefAccess throws on a dead name; in a field "
        "initializer that becomes a TypeInitializationException at the point "
        "of use. Wrap it in a method with a catch and return null. "
        f"Offenders: {offenders}")


def test_softlock_guard_list_is_compile_checked() -> None:
    """Every SoftlockGuards entry is `nameof`, never a string literal.

    A literal survives the rename or deletion of the class it names and then
    guards nothing, silently -- an exemption outliving its reason (the B6
    ledger lesson). `nameof` turns that into a compile error.
    """
    code = _code_only(BOOTSTRAP.read_text(encoding="utf-8"))
    block = re.search(r"SoftlockGuards\s*=\s*new\([^)]*\)\s*\{(.*?)\};",
                      code, re.S)
    assert block, "could not find the SoftlockGuards initializer"

    entries = [e.strip() for e in block.group(1).split(",") if e.strip()]
    assert entries, "SoftlockGuards is empty; the escalation path is dead"

    literals = [e for e in entries if not e.startswith("nameof(")]
    assert not literals, (
        "SoftlockGuards entries must be nameof(...) so a renamed or deleted "
        f"patch class fails the build instead of silently losing its guard. "
        f"String literals found: {literals}")


def test_every_patch_class_declares_a_class_level_attribute() -> None:
    """A patch class without [HarmonyPatch] is skipped in total silence.

    True of Harmony's PatchAll and of our bootstrap alike -- the bootstrap logs
    it at boot, and this rule catches it before boot. The failure mode is a
    file full of [HarmonyPostfix] methods that never run and never complain.
    """
    method_attrs = ("[HarmonyPrefix]", "[HarmonyPostfix]", "[HarmonyTranspiler]",
                    "[HarmonyFinalizer]", "[HarmonyTargetMethods]",
                    "[HarmonyTargetMethod]")
    offenders = []
    for path in _cs_files():
        code = _code_only(path.read_text(encoding="utf-8"))
        if not any(a in code for a in method_attrs):
            continue
        if "[HarmonyPatch" not in code:
            offenders.append(path.relative_to(ROOT).as_posix())

    assert not offenders, (
        "these files declare Harmony patch methods but no class-level "
        f"[HarmonyPatch], so nothing in them is ever applied: {offenders}")
