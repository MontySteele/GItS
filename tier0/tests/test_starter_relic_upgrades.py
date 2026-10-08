"""G-C3(d): every roster starter relic has a registered upgraded form.

THE DEFECT THIS GUARDS is structurally invisible, which is why it needs a
curated list and a check rather than a code review.

Touch of Orobas (act-2 Ancient) replaces your starting relic with an upgraded
version. Vanilla resolves that through a HARDCODED dictionary of five
base-game pairs, falling back to `ModelDb.Relic<Circlet>()` -- the no-effect
filler relic. Nothing errors. Nothing logs. The reward screen looks normal,
the player takes it, and their character's talent relic is silently deleted.
Every modded character hit this, and it was found by playing the game.

BaseLib provides the extension point -- it patches
`TouchOfOrobas.GetUpgradedStarterRelic` with a prefix that calls
`CustomRelicModel.GetUpgradeReplacement()` and only falls through to vanilla
when that returns null. The default implementation returns null. So the bug is
an ABSENCE: a starter relic that simply never overrode a virtual method.

An absence is exactly what a compiler cannot see, so this asserts it.

Source-level, for the same reason as tier0/tests/test_coop_ownership.py: the
logic is C#, there is no C# test project, and the DLL only executes inside the
game. What is checkable from here is that the override exists on every starter
and points at a real Ancient-rarity class -- which is the whole of the defect.
"""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_RELICS = _ROOT / "klee-mod" / "KleeCode" / "Relics"

# Starter-relic class -> the upgraded class it must hand to Touch of Orobas.
STARTERS: dict[str, str] = {
    "PoundingSurprise": "ExplosiveFrags",          # Klee
    "PearlOfWisdomRelic": "PearlOfInsightRelic",   # Kokomi
    "EtherealSpotlightRelic": "CurtainNeverFalls", # Furina (red-pen R2)
    # The Stage arm's starter (FURINA_STAGE). Its curated absence
    # closed on 2026-09-27: The Curtain Never Falls was rebuilt for the Stage
    # (review/active/relics-potions-klee-furina-2026-09-27.md, pick 4 at its
    # default) and is Salon Solitaire's upgrade as it is the Spotlight's.
    "SalonSolitaire": "CurtainNeverFalls",
    # The prototype arms' starters (PROTOTYPE_CARDS). Built
    # 2026-09-30 from [USER]'s co-op playtest ("Varka and Kokomi need Ancient
    # relics for Orobas"), main-session design: each upgrade SUBCLASSES its
    # starter, so every reader that finds the starter by type finds it too.
    "BoreasFang": "WolfsGravestone",               # Varka
    "TamakushiCasket": "WatatsumiCasket",          # Kokomi (the overhaul)
}

# Starters KNOWINGLY without an upgraded form, each with the reason and the
# gate that clears it. A curated absence, never a silent one -- the point of
# this file is that a missing upgrade must be a decision on the record.
# Starters KNOWINGLY without an upgraded form, each with the reason and the
# gate that clears it. A curated absence, never a silent one.
#
# EMPTY since 2026-07-26. Furina was the sole entry and red-pen R2 closed it:
# her upgraded starter grants both Spotlight modes at once. G-C3 had declined
# to invent one because every candidate broke either the sprint's
# "no new behaviour in a starter upgrade" rule or her no-passive-accrual law,
# and the ruling OVERRODE the first of those by user authority rather than
# reinterpreting it. See docs/archive/red-pen-2026-07-26.md R2.
#
# Kept as an empty dict rather than deleted, per the standing curated-set
# discipline: the invariant is then asserted positively and the next gap has
# somewhere to be named instead of becoming a silent Circlet.
NO_UPGRADED_FORM: dict[str, str] = {
    # EMPTY again since 2026-09-30: the Tamakushi Casket and Boreas's Fang,
    # the two prototype starters curated here, gained the Watatsumi Casket
    # and Wolf's Gravestone.
}


_CLASS = re.compile(r"public (?:sealed )?class (\w+)\s*:\s*(\w+)")


def _declarations() -> dict[str, tuple[str, str]]:
    """Class name -> (its base class, its source text), across every relic
    file. A relic is a class whose base is `CustomRelicModel` or another relic
    here: the prototype upgrades (Wolf's Gravestone, the Watatsumi Casket)
    subclass their starters."""
    found: dict[str, tuple[str, str]] = {}
    for path in _RELICS.glob("*.cs"):
        src = path.read_text(encoding="utf-8")
        heads = list(_CLASS.finditer(src))
        for i, m in enumerate(heads):
            # Body runs to the next top-level class or EOF; good enough to
            # attribute members, since these files declare one class per
            # block and never nest them.
            end = heads[i + 1].start() if i + 1 < len(heads) else len(src)
            found[m.group(1)] = (m.group(2), src[m.start():end])
    relics = {"CustomRelicModel"}
    grew = True
    while grew:
        grew = False
        for name, (base, _) in found.items():
            if base in relics and name not in relics:
                relics.add(name)
                grew = True
    return {n: v for n, v in found.items() if n in relics}


def _classes() -> dict[str, str]:
    """Class name -> its source text, across every relic file."""
    return {name: body for name, (_, body) in _declarations().items()}


def test_every_starter_relic_is_accounted_for():
    """No starter may be neither upgraded nor curated.

    This is the assertion that makes the whole file work: without it, adding a
    fourth roster character with a starter relic would sail past every other
    check here.
    """
    classes = _classes()
    starters = {
        name for name, body in classes.items()
        if re.search(r"RelicRarity\s+Rarity\s*=>\s*RelicRarity\.Starter", body)
    }
    assert starters, "no starter relics found -- did the relic files move?"
    unaccounted = starters - set(STARTERS) - set(NO_UPGRADED_FORM)
    assert not unaccounted, (
        f"starter relic(s) {sorted(unaccounted)} are neither given an upgraded "
        "form nor curated in NO_UPGRADED_FORM. Touch of Orobas will replace "
        "them with the no-effect Circlet, silently.")


def test_curated_absences_still_apply():
    """A stale exemption reads as a considered decision while covering nothing."""
    classes = _classes()
    for name in NO_UPGRADED_FORM:
        assert name in classes, (
            f"NO_UPGRADED_FORM lists '{name}', which no longer exists -- "
            "remove it")
        assert "GetUpgradeReplacement" not in classes[name], (
            f"{name} now overrides GetUpgradeReplacement -- move it from "
            "NO_UPGRADED_FORM into STARTERS, the gap is closed")


# --- EPOCH 2 / D1: pool membership, made structural ----------------------

# Character -> the relic pool file that owns its membership. A curated map
# rather than a derived one: pool files are hand-written C# and the whole
# point of this check is that nothing in the compiler relates a relic class
# to the pool it belongs in.
RELIC_POOLS = {
    "PoundingSurprise": "KleeRelicPool.cs",
    "PearlOfWisdomRelic": "KokomiRelicPool.cs",
    "EtherealSpotlightRelic": "FurinaRelicPool.cs",
    "SalonSolitaire": "FurinaRelicPool.cs",
    # VARKA (prototype batch one).
    "BoreasFang": "VarkaRelicPool.cs",
    # The Kokomi overhaul's starter.
    "TamakushiCasket": "KokomiRelicPool.cs",
}

_CODE = _ROOT / "klee-mod" / "KleeCode"


def _pool_text(filename: str) -> str:
    return (_CODE / filename).read_text(encoding="utf-8")


def test_every_pool_file_is_named_by_the_map():
    """A new character's pool file must be added here, not discovered."""
    on_disk = {p.name for p in _CODE.glob("*RelicPool.cs")}
    assert on_disk == set(RELIC_POOLS.values()), (
        f"relic pool files on disk {sorted(on_disk)} do not match the curated "
        f"map {sorted(set(RELIC_POOLS.values()))}")


def test_r7_sweeps_the_upgraded_form_not_only_the_starter():
    """The boot-time half of the same invariant.

    R7 read `character.StartingRelics` only, so the grant path -- the one
    that actually crashes in act 2 -- was outside its sweep entirely.
    """
    self_check = (_CODE / "Diagnostics" / "KleeSelfCheck.cs").read_text(
        encoding="utf-8")
    assert "CheckRelicResolvesPool" in self_check
    assert "GetUpgradeReplacement() is { } upgraded" in self_check, (
        "R7 must reach the upgraded form through GetUpgradeReplacement rather "
        "than a hardcoded list, so a starter that gains an upgrade later is "
        "covered the day it does")


# --- EB-31: every upgraded starter is modelled in the sim too -------------

# Upgraded-form class -> the tier05 ancient-relic row that models it.
#
# WHY THIS MAP EXISTS. Touch of Orobas is modelled NARROWLY ([USER] ruling
# 2026-07-26, option 1): no relic-upgrade table, one owner-gated row per
# character. The cost of that shape is that "is this variant modelled?" has no
# structural answer -- a fourth character could ship an upgraded starter with
# no sim row and nothing would notice, which is exactly what happened to
# Furina and Kokomi for eleven days (EB-31). Klee's row landed at red-pen and
# theirs did not, and the C# recorded the gap against itself
# ("SIM PARITY: NOT MODELLED") rather than anything checking it.
#
# Read as: the sim ROW must exist and be owner-gated to the right character.
# What it DOES is asserted behaviourally in test_orobas_upgraded_starters.py;
# this is the membership gate, in the file that owns the Orobas invariants.
SIM_ROWS = {
    "ExplosiveFrags": ("touch_of_orobas_klee", "klee"),
    "PearlOfInsightRelic": ("touch_of_orobas_kokomi", "kokomi"),
    "CurtainNeverFalls": ("touch_of_orobas_furina", "furina"),
}


def _ancient_pool() -> dict:
    """The tier05 ancient pool, read as YAML rather than imported.

    Deliberately not `from tier05 import relics`: this is a tier0 test and the
    layer boundary runs the other way (tier05 imports tier0, never the
    reverse). test_relics_combat_start.py keeps the same discipline by
    inlining the effect dicts verbatim.
    """
    import yaml
    path = _ROOT / "tier05" / "content" / "relics.yaml"
    return (yaml.safe_load(path.read_text(encoding="utf-8"))
            or {}).get("ancient") or {}


def test_every_upgraded_starter_has_an_owner_gated_sim_row():
    pool = _ancient_pool()
    for upgraded, (relic_id, character) in SIM_ROWS.items():
        assert relic_id in pool, (
            f"{upgraded} is an upgraded starter with no row in "
            f"tier05/content/relics.yaml. A tier-0.5 {character} never "
            f"receives the upgrade, so no cell measures it and its value is "
            f"unpriced -- the EB-31 gap, reopened.")
        owner = pool[relic_id].get("owner")
        assert owner == [character], (
            f"{relic_id} must be owner-gated to [{character!r}]; got "
            f"{owner!r}. An ungated Orobas variant is offered to characters "
            f"whose kit it does not touch, which prices it against the wrong "
            f"runs.")


def test_no_upgraded_starter_is_modelled_without_being_declared_here():
    """The other direction: a sim row whose C# class this map does not know.

    Cheap, and it is the half that rots. Someone adding a fourth variant is
    far likelier to write the yaml row (visible, adjacent to its siblings)
    than to find this map.
    """
    modelled = {rid for rid in _ancient_pool()
                if rid.startswith("touch_of_orobas_")}
    declared = {relic_id for relic_id, _ in SIM_ROWS.values()}
    assert modelled == declared, (
        f"tier05 models {sorted(modelled - declared)} with no SIM_ROWS entry "
        f"(or SIM_ROWS claims {sorted(declared - modelled)} which is not "
        f"modelled). The map is the only thing relating the two.")


# Upgraded forms with NO tier05 row, each with its reason. A curated absence,
# the NO_UPGRADED_FORM discipline one level down.
#
# THE PROTOTYPE ARMS' UPGRADES (2026-09-30). tier05 does not run either arm:
# no pool offers a `proto_vk_` row (tier05/draft.py, VARKA_OPS) and the Kokomi
# overhaul's Casket has no tier05 Orobas row to sit beside the shipped Pearl's
# `touch_of_orobas_kokomi`, so a row would be offered to no seat that holds
# the starter. Measurement binds at Balance (docs/current/EXPERIMENTS.md); the
# row lands with the kit's Balance pass. tier0 twins where they exist:
# Wolf's Gravestone is `varka_oath.FANG_UPGRADED` (`boreas_fang+`).
SIM_ROWS_ABSENT = {
    "WolfsGravestone":
        "prototype arm (Varka) tier05 does not run; tier0 twin "
        "varka_oath.FANG_UPGRADED. Row lands at Balance.",
    "WatatsumiCasket":
        "prototype arm (the Kokomi overhaul) with no tier05 Orobas row. "
        "Row lands at Balance.",
}


def test_the_sim_row_set_matches_the_starter_set():
    """No starter may be upgraded C#-side and unmodelled sim-side.

    STARTERS is the C#-side curated set and SIM_ROWS the sim-side one; keeping
    them equal is what makes a fourth character's gap loud in both directions
    at once, instead of only in whichever file its author happened to open.
    """
    assert not set(SIM_ROWS) & set(SIM_ROWS_ABSENT)
    assert set(STARTERS.values()) == set(SIM_ROWS) | set(SIM_ROWS_ABSENT), (
        f"C# upgraded forms {sorted(set(STARTERS.values()))} and sim-modelled "
        f"forms {sorted(SIM_ROWS)} disagree.")
