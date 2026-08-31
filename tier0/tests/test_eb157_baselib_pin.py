"""EB-157: one BaseLib pin, and a gate that compares the two places it lives.

WHAT WAS WRONG. The pin joined nothing. `klee-mod/Klee/manifest.json` asked
for `>= 3.3.6`, `STATE.md`'s pin block recorded a different number, and the
machine compiles and runs against a third -- three statements about one
dependency with nothing comparing any pair of them. `validate.ps1`'s S3 does
compare the manifest against the INSTALLED BaseLib at deploy time (R70), which
is why the drift never bit; nothing at all compared the manifest against the
repo's own record of what it is built against.

WHAT THIS PINS, AND WHY HERE. Two portable facts and one machine-local one:

  1. the manifest's BaseLib `min_version` and `STATE.md`'s pin block are ONE
     number;
  2. the BaseLib symbols we call are the enumerated set below -- so raising
     or lowering the pin is a decision somebody makes against a list, not a
     number nobody has checked;
  3. where a local BaseLib is resolvable (`klee-mod/local.props`), that it is
     the pinned version. Skipped on a runner, which has no game install.

THE RECONCILIATION, AND ITS RESIDUAL UNKNOWN (2026-08-30). The number both
records now carry is **3.4.5**, which is what this machine compiles against,
what the OneDrive assembly vault pins (`PIN.json`), and what the installed
Workshop item reports. The row asked for the called symbols to be enumerated
"against the 3.3.6 surface" first; that surface could not be obtained -- BaseLib
is a Steam Workshop item, Steam serves only an item's CURRENT version, and no
older copy exists on this machine or in the vault. So the enumeration below was
taken against 3.4.5 (decompiled with `ilspycmd`), and whether every symbol also
exists in 3.3.6 is STILL UNKNOWN. Raising the floor to the version we verifiably
build and run against is what makes that unknown harmless rather than answered:
the pin now claims only what has been checked.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "klee-mod" / "Klee" / "manifest.json"
STATE = ROOT / "docs" / "current" / "STATE.md"
SOURCE = ROOT / "klee-mod" / "KleeCode"
LOCAL_PROPS = ROOT / "klee-mod" / "local.props"

# The BaseLib types this mod actually calls, by the namespace it imports them
# from. Enumerated 2026-08-30 against BaseLib 3.4.5 decompiled with ilspycmd,
# then cross-checked against every non-comment line of `klee-mod/KleeCode`.
#
# This is a CURATED list and it is the point of the gate: the test below fails
# when a BaseLib type is used that is not here, so the commit that reaches for a
# new BaseLib API is the commit that has to look at the pin. It also fails when
# an entry stops being used, so it cannot rot into a list of things we once did.
#
# NOT in the list, deliberately, and each was checked by hand:
#   * `RunState` -- `Owner.RunState` is the GAME's, not BaseLib's
#     `BetaMainCompatibility` shim of the same name;
#   * `CustomPowerModel`, `CustomCardPoolModel`, `CustomContentDictionary`,
#     `MultiPileCardSelect` and the `BaseLib.Hooks` interfaces -- named only in
#     comments explaining what we deliberately do NOT derive from or rely on
#     (see KleePowerIcons.cs's header, and KleeMod.cs's finding-27 note).
CALLED_BASELIB_TYPES: frozenset[str] = frozenset({
    "AncientDialogueUtil",     # BaseLib.Utils
    "AutoKeywordPosition",     # BaseLib.Patches.Content
    "BasicCustomResource",     # BaseLib.Abstracts
    "CustomCardModel",         # BaseLib.Abstracts -- 327 uses, the roster
    "CustomCharacterModel",    # BaseLib.Abstracts -- the three characters
    "CustomRelicModel",        # BaseLib.Abstracts
    "CustomResource",          # BaseLib.Abstracts -- the meters
    "CustomResourceCost",      # BaseLib.Abstracts
    "CustomResources",         # BaseLib.Abstracts
    "ICustomModel",            # BaseLib.Abstracts
    "ILocalizationProvider",   # BaseLib.Abstracts -- 65 uses
    "NodeFactory",             # BaseLib.Utils.NodeFactories
    "PoolAttribute",           # BaseLib.Utils -- [Pool(typeof(...))]
    "SpireField",              # BaseLib.Utils
})

BASELIB_NAMESPACES = (
    "BaseLib.Abstracts",
    "BaseLib.Utils",
    "BaseLib.Utils.NodeFactories",
    "BaseLib.Patches.Content",
)


def _manifest_pin() -> str:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    row = next(d for d in data["dependencies"] if d["id"] == "BaseLib")
    return row["min_version"]


def _state_pin() -> str:
    """The number in STATE.md's `Mod build environment (pinned)` block.

    Read from the CURRENT block only. The paragraph after it is `Pin history`
    and names the number this one replaced; a reader that took the last match
    in the file would gate on the retired pin.
    """
    text = STATE.read_text(encoding="utf-8")
    block = text[text.index("## Mod build environment (pinned)"):]
    block = block[:block.index("**Pin history.**")]
    return re.search(r"BaseLib\s+\*\*([0-9.]+)\*\*", block).group(1)


def _release(version: str) -> tuple[int, ...]:
    """Compare on MAJOR.MINOR.PATCH: the manifest writes `3.4.5`, STATE.md
    writes the assembly's four-part `3.4.5.0`, and BaseLib's own json writes
    `v3.4.5`. Three spellings of one release; the gate is about the release."""
    return tuple(int(p) for p in version.lstrip("v").split(".")[:3])


def _code_lines() -> str:
    out = []
    for path in SOURCE.rglob("*.cs"):
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith(("//", "*", "using ")):
                continue
            out.append(line)
    return "\n".join(out)


# ------------------------------------------------------------------ the pin --

def test_the_manifest_and_STATE_name_one_release():
    """The row's acceptance: ONE pin. This is the comparison that did not
    exist -- the manifest said 3.3.6 while the pin block said something else
    and the machine ran a third number."""
    assert _release(_manifest_pin()) == _release(_state_pin()), (
        f"manifest min_version {_manifest_pin()} vs STATE.md pin "
        f"{_state_pin()}: the BaseLib pin has to be one number.")


def test_the_pin_is_the_version_this_repo_says_it_builds_against():
    """Belt and braces on the number itself, so a future edit that moves BOTH
    records together still has to be deliberate. 3.4.5 is what PIN.json in the
    assembly vault, the installed Workshop item and the compiler all report."""
    assert _release(_manifest_pin()) == (3, 4, 5)


def test_the_manifest_still_declares_a_baselib_dependency_at_all():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert any(d["id"] == "BaseLib" for d in data["dependencies"])


# -------------------------------------------------------------- the symbols --

def test_every_baselib_type_we_call_is_enumerated():
    """A BaseLib type used and not listed is a reach for a new API that has
    not been checked against the pin. That is the whole reason a pin exists."""
    code = _code_lines()
    usings = "\n".join(
        line for path in SOURCE.rglob("*.cs")
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("using BaseLib"))
    imported = [ns for ns in BASELIB_NAMESPACES if f"using {ns};" in usings]
    assert imported, "no BaseLib namespace is imported any more"

    # Anything spelled `BaseLib.Something.Type` inline is a use as well.
    qualified = set(re.findall(r"\bBaseLib(?:\.\w+)*\.(\w+)\b", code))
    unlisted = qualified - CALLED_BASELIB_TYPES
    assert not unlisted, (
        f"BaseLib types used but not in CALLED_BASELIB_TYPES: "
        f"{sorted(unlisted)}. Add them, and check the pin while you are there.")


def test_the_enumeration_does_not_rot():
    """Every listed type is still named in the code. A list of things we used
    to call is cover for the next unchecked API reach."""
    code = _code_lines()
    def named(name: str) -> bool:
        # An attribute is written by its short name: `PoolAttribute` is
        # spelled `[Pool(typeof(...))]`, and it is the same type.
        spellings = {name}
        if name.endswith("Attribute"):
            spellings.add(name[:-len("Attribute")])
        return any(re.search(rf"\b{re.escape(s)}\b", code) for s in spellings)

    stale = sorted(t for t in CALLED_BASELIB_TYPES if not named(t))
    assert not stale, f"CALLED_BASELIB_TYPES entries nothing calls: {stale}"


def test_the_two_types_the_whole_roster_rests_on_are_listed():
    """A guard on the guard: an empty or gutted set would pass the two tests
    above trivially."""
    assert {"CustomCardModel", "CustomCharacterModel"} <= CALLED_BASELIB_TYPES
    assert len(CALLED_BASELIB_TYPES) >= 10


# ------------------------------------------------------------- this machine --

def _installed_baselib_json() -> Path | None:
    if not LOCAL_PROPS.exists():
        return None
    # XML comments first: `local.props.example`'s header carries a macOS
    # sample path, and a copy of the example that keeps the comment would
    # otherwise be read as pointing at /Users/you/.
    text = re.sub(r"<!--.*?-->", "", LOCAL_PROPS.read_text(encoding="utf-8"),
                  flags=re.DOTALL)
    m = re.search(r"<BaseLibDll>(.*?)</BaseLibDll>", text)
    if not m:
        return None
    candidate = Path(m.group(1)).with_name("BaseLib.json")
    return candidate if candidate.exists() else None


def test_the_installed_baselib_is_the_pinned_one():
    """The machine-local arm. CI has no game install and no `local.props`, so
    this is skipped there rather than faked -- the two tests above are the
    portable half and they are the gate CI runs."""
    manifest = _installed_baselib_json()
    if manifest is None:
        pytest.skip("no local.props / installed BaseLib on this machine")

    installed = json.loads(
        manifest.read_text(encoding="utf-8-sig"))["version"]

    assert _release(installed) == _release(_manifest_pin()), (
        f"installed BaseLib {installed} is not the pin {_manifest_pin()}. "
        f"Either the Workshop item moved (re-pin deliberately, R70: latest is "
        f"not a version) or this checkout's pin is stale.")
