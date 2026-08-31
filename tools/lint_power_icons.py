#!/usr/bin/env python3
"""EB-153: every power this mod ships is either ICONED, EXEMPT, or NAMED DEBT.

WHY A LINT AND NOT THE BOOT CHECK. `KleeSelfCheck.CheckPowerIcons` (rule R13)
already asks this question at runtime, and it is the better instrument: it
holds the live `PowerModel` instances and can ask the merged PCK whether the
file is actually there. It has one property this repo cannot live with alone --
**it only speaks inside a running game**. Its findings land in `godot.log` on
one machine, after a deploy, in front of whoever happened to be playing. Seven
powers had no icon case and no exemption for months with every gate green,
because no gate could see the question. That is LAW's invisible-defect shape
exactly: the check needs data the repo cannot see (which PNGs exist -- Tier F
art is gitignored), so the answer is a CURATED list plus a lint over it.

THE TWO SHAPES IT BITES ON, which are the two halves of `EB-153`:

  1. **A concrete `PowerModel` subclass with no `KleePowerIcons.PathFor` case,
     no `IconExempt` entry, and no row in `ICON_DEBT` below.** A power in that
     state renders the base-game placeholder badge, silently, forever.

  2. **A concrete `AuraPower` subclass whose element has no declared icon.**
     `PathFor` builds the aura path by CONCATENATION --
     `"klee/powers/aura_" + Element.ToString().ToLowerInvariant() + ".png"` --
     so a new aura element compiles, matches the case, produces a path, and
     resolves to nothing. There is no case to forget, which is why nothing
     catches it: the switch is already "covered". `AURA_ICONS` below is that
     concatenation's coverage list, joined to `art/plan.tsv`, the one ledger
     of produced art that IS tracked.

WHAT IT DOES NOT CLAIM. Not that a PNG exists on this machine (it cannot see
Tier F art), not that an icon is the RIGHT icon, and not that `ICON_DEBT` is
complete -- no tool knows about a power nobody has written down. It checks the
one mechanical property: nothing is missing from all three lists at once.

`ICON_DEBT` ROTS ON PURPOSE, the semantics `lint_register_ids.OPEN_IDS` and
`lint_face_defects` already carry: an entry that has SINCE been given a case or
an exemption FAILS and must be deleted. The set can only shrink, so it cannot
become cover for the next missing icon. It ships non-empty, which is the honest
state -- these seven powers have no art, and missing art is a named fact here
rather than a silent pass.

Run: python tools/lint_power_icons.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "klee-mod" / "KleeCode"
ICONS = SOURCE / "Powers" / "KleePowerIcons.cs"
ART_PLAN = REPO / "art" / "plan.tsv"

# ---------------------------------------------------------------- curation --

# THE DEBT (2026-08-30, EB-153). Seven concrete powers with no `PathFor` case
# and no `IconExempt` entry, found by the D25 / lane-B F5 sweep and confirmed
# against HEAD when this lint was written. Every one of them renders the
# base-game placeholder badge in a live run TODAY. They are debt and not
# exemptions: an exemption says "this power needs no icon", and each of these
# wants one. No path is wired ahead of the art for them -- that policy (see
# KleePowerIcons.cs, the companion-summon block) is for paths whose PNG is
# planned, and none of these seven is in `art/plan.tsv`.
#
# TO CLOSE ONE: make the art, add the case, DELETE the row here. Leaving the
# row behind fails this lint.
ICON_DEBT: dict[str, str] = {
    "AncientSeaAuthorityPower":
        "Fontaine ancient payoff; no icon planned, renders the placeholder",
    "CannonFireSupportPower":
        "Fontaine companion payoff; no icon planned, renders the placeholder",
    "ExplosivesWorkshopPower":
        "Klee demolition payoff; no icon planned, renders the placeholder",
    "MasqueRedDeathPower":
        "Bond of Life carrier; the end-of-turn docket titles it, the badge does not",
    "MetallicizePower":
        "base-game-shaped block power; no icon planned, renders the placeholder",
    "NightVigilPower":
        "Fontaine ancient payoff; no icon planned, renders the placeholder",
    "SalonCapUpPower":
        "Casting Call's cap raise; no icon planned, renders the placeholder",
}

# THE AURA CONCATENATION'S COVERAGE LIST (shape 2). `Element` -> the
# `art/plan.tsv` out-path the concatenated `klee/powers/aura_<element>.png`
# is built from. An element reaching `PathFor`'s `AuraPower` case with no row
# here is the invisible half of EB-153: the switch matches, a path is built,
# and nothing exists at the end of it.
AURA_ICONS: dict[str, str] = {
    "Pyro": "ImageGen/images/powers/aura_pyro.png",
    "Hydro": "ImageGen/images/powers/aura_hydro.png",
    "Electro": "ImageGen/images/powers/aura_electro.png",
    "Cryo": "ImageGen/images/powers/aura_cryo.png",
}

# ------------------------------------------------------------------ parsing --

CLASS = re.compile(
    r"^\s*(?:public|internal)\s+(?P<mods>(?:sealed\s+|abstract\s+|static\s+|partial\s+)*)"
    r"class\s+(?P<name>\w+)\s*:\s*(?P<bases>[^{\r\n]+)")

# A switch arm in PathFor: `SomePower => ...` or `AuraPower aura => ...`.
ARM = re.compile(r"^\s*(?P<type>\w+)(?:\s+\w+)?\s*=>")

EXEMPT = re.compile(r"\[typeof\((?P<type>\w+)\)\]")

# `public override Element Element => Element.Pyro;`
AURA_ELEMENT = re.compile(r"Element\s+Element\s*=>\s*Element\.(?P<element>\w+)")


def _cs_files() -> list[Path]:
    return sorted(SOURCE.rglob("*.cs"))


def classes() -> dict[str, dict]:
    """Every class declaration in the mod, by name, with bases and modifiers.

    Text-scanned rather than compiled, for the same reason
    `test_repo_python_convention` reads PowerShell as text: the lane that must
    run this has no game assemblies to compile against.
    """
    out: dict[str, dict] = {}
    for path in _cs_files():
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        for i, line in enumerate(lines):
            m = CLASS.match(line)
            if not m:
                continue
            bases = [b.strip().split("<")[0]
                     for b in m.group("bases").split(",")]
            body = "\n".join(lines[i:i + 40])
            out[m.group("name")] = {
                "bases": bases,
                "abstract": "abstract" in m.group("mods"),
                "static": "static" in m.group("mods"),
                "file": path,
                "element": (e.group("element")
                            if (e := AURA_ELEMENT.search(body)) else None),
            }
    return out


def _derives(name: str, target: str, known: dict[str, dict],
             seen: set[str] | None = None) -> bool:
    seen = seen or set()
    if name in seen:
        return False
    seen.add(name)
    row = known.get(name)
    if row is None:
        return False
    if target in row["bases"]:
        return True
    return any(_derives(b, target, known, seen) for b in row["bases"])


def _ancestors(name: str, known: dict[str, dict],
               seen: set[str] | None = None) -> set[str]:
    """Every base type reachable from `name`, transitively."""
    seen = seen if seen is not None else set()
    for base in known.get(name, {}).get("bases", []):
        if base in seen:
            continue
        seen.add(base)
        _ancestors(base, known, seen)
    return seen


def switch_arms(text: str | None = None) -> set[str]:
    """The type names `KleePowerIcons.PathFor` matches, one arm each."""
    body = ICONS.read_text(encoding="utf-8") if text is None else text
    start = body.index("PathFor(PowerModel power)")
    end = body.index("IconExempt", start)
    return {m.group("type") for line in body[start:end].splitlines()
            if (m := ARM.match(line)) and m.group("type") != "_"}


def exempt(text: str | None = None) -> set[str]:
    body = ICONS.read_text(encoding="utf-8") if text is None else text
    start = body.index("IconExempt")
    return {m.group("type") for m in EXEMPT.finditer(body[start:])}


def planned_art(path: Path = ART_PLAN) -> set[str]:
    """The out-paths `art/plan.tsv` declares a producer for.

    CRLF + UTF-8, read the way the art pipeline's own rule says to (see
    OPERATIONS.md, "Art pipeline"): the last column stops matching otherwise.
    """
    with path.open(encoding="utf-8", newline="") as fh:
        return {row[1].strip() for row in csv.reader(fh, delimiter="\t")
                if len(row) > 1 and row[1].strip()}


# ----------------------------------------------------------------- findings --

def findings(known: dict[str, dict] | None = None,
             arms: set[str] | None = None,
             exemptions: set[str] | None = None,
             plan: set[str] | None = None,
             debt: dict[str, str] | None = None,
             aura_icons: dict[str, str] | None = None) -> list[str]:
    """Every finding, over injected inputs or over HEAD.

    The parameters exist so the two shapes can be SEEN TO BITE against
    synthetic input -- a gate is not trusted until it has been watched fail
    (`docs/current/LAW.md`, and the Klee protocol's "a lock is trusted only
    once seen to FAIL"). Nothing production passes them.
    """
    known = classes() if known is None else known
    arms = switch_arms() if arms is None else arms
    exemptions = exempt() if exemptions is None else exemptions
    plan = planned_art() if plan is None else plan
    debt = ICON_DEBT if debt is None else debt
    aura_icons = AURA_ICONS if aura_icons is None else aura_icons
    out: list[str] = []

    def _has_icon(name: str) -> bool:
        return (name in arms or name in exemptions
                or any(a in arms for a in _ancestors(name, known)))

    concrete = {name: row for name, row in known.items()
                if not row["abstract"] and not row["static"]
                and _derives(name, "PowerModel", known)}

    # --- shape 1: a power covered by nothing at all ------------------------
    #
    # An ARM on an ancestor counts: C# pattern matching matches base types, so
    # the four `*AuraPower`s are covered by the `AuraPower` arm (which is
    # shape 2's whole problem, and is checked there). An EXEMPTION on an
    # ancestor deliberately does NOT count -- `SpotlightPower` is exempt as an
    # abstract base precisely so that a new subclass of it has to answer for
    # itself, which is the failure the 2026-07-24 sweep was cleaning up.
    for name in sorted(concrete):
        if not (_has_icon(name) or name in debt):
            out.append(
                f"{name}: no KleePowerIcons.PathFor case, no IconExempt entry "
                f"and no ICON_DEBT row -- it renders the base-game placeholder "
                f"and nothing says so. Add a case, an exemption with its "
                f"reason, or a debt row naming the missing art "
                f"({concrete[name]['file'].relative_to(REPO)}).")

    for name, why in sorted(debt.items()):
        if name not in known:
            out.append(f"ICON_DEBT[{name}]: no such power class in the mod. "
                       f"The class was renamed or deleted; drop the row.")
        elif _has_icon(name):
            out.append(
                f"ICON_DEBT[{name}]: this power now HAS a case or an exemption "
                f"({why}). The debt is paid -- delete the row, which is the "
                f"only way this set is allowed to change.")

    # --- shape 2: the concatenated aura path -------------------------------
    if "AuraPower" not in arms:
        out.append("KleePowerIcons.PathFor no longer has an AuraPower arm; "
                   "AURA_ICONS below is guarding a concatenation that has "
                   "moved. Re-read the switch before editing this lint.")
    aura_powers = {name: row for name, row in concrete.items()
                   if _derives(name, "AuraPower", known)}
    for name in sorted(aura_powers):
        element = aura_powers[name]["element"]
        if element is None:
            out.append(
                f"{name}: derives from AuraPower but declares no "
                f"`Element Element => Element.X`, so the icon path this lint "
                f"cannot compute is one the game builds anyway.")
            continue
        if element not in aura_icons:
            out.append(
                f"{name}: element {element} has no AURA_ICONS row. PathFor "
                f"builds \"klee/powers/aura_{element.lower()}.png\" by "
                f"concatenation, so this compiles, matches the AuraPower arm "
                f"and resolves to nothing -- invisible to every other gate. "
                f"Add the art and the row, or exempt the power by name.")
            continue
        declared = aura_icons[element]
        if declared not in plan:
            out.append(
                f"{name}: AURA_ICONS names {declared}, which art/plan.tsv "
                f"declares no producer for. The concatenated path "
                f"\"klee/powers/aura_{element.lower()}.png\" has nothing "
                f"behind it.")

    for element in sorted(aura_icons):
        if not any(row["element"] == element for row in aura_powers.values()):
            out.append(
                f"AURA_ICONS[{element}]: no concrete AuraPower subclass "
                f"declares this element any more. The coverage row outlived "
                f"its power; drop it.")

    return out


def main() -> int:
    problems = findings()
    for line in problems:
        print(line)
    if problems:
        print(f"\npower icons: {len(problems)} finding(s)")
        return 1
    print(f"power icons: OK ({len(ICON_DEBT)} debt row(s), "
          f"{len(AURA_ICONS)} aura element(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
