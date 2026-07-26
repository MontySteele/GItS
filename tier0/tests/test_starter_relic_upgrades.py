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
# reinterpreting it. See docs/red-pen-2026-07-26.md R2.
#
# Kept as an empty dict rather than deleted, per the standing curated-set
# discipline: the invariant is then asserted positively and the next gap has
# somewhere to be named instead of becoming a silent Circlet.
NO_UPGRADED_FORM: dict[str, str] = {}


def _classes() -> dict[str, str]:
    """Class name -> its source text, across every relic file."""
    out: dict[str, str] = {}
    for path in _RELICS.glob("*.cs"):
        src = path.read_text(encoding="utf-8")
        for m in re.finditer(
                r"public sealed class (\w+)\s*:\s*CustomRelicModel", src):
            # Body runs to the next top-level class or EOF; good enough to
            # attribute members, since these files declare one class per
            # block and never nest them.
            start = m.start()
            nxt = src.find("public sealed class ", m.end())
            out[m.group(1)] = src[start:nxt if nxt != -1 else len(src)]
    return out


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


def test_starters_override_the_baselib_hook():
    classes = _classes()
    for starter, upgraded in STARTERS.items():
        assert starter in classes, f"{starter} not found"
        body = classes[starter]
        assert "GetUpgradeReplacement" in body, (
            f"{starter} does not override GetUpgradeReplacement() -- BaseLib's "
            "StarterUpgradePatches prefix will fall through to vanilla's "
            "hardcoded table, which does not know us, and Touch of Orobas will "
            "hand out a Circlet")
        assert upgraded in body, (
            f"{starter}.GetUpgradeReplacement() does not name {upgraded}")


def test_upgraded_forms_exist_and_are_not_starter_rarity():
    """The upgraded form must be a real class, and must NOT be Starter rarity.

    Rarity is load-bearing rather than cosmetic. `TouchOfOrobas.GetStarterRelic`
    finds its target with
    `p.Relics.FirstOrDefault(r => r.Rarity == RelicRarity.Starter)`, so an
    upgraded form that kept Starter rarity could be found and upgraded AGAIN by
    a second Orobas -- and the second pass would find no entry for it and hand
    back the Circlet. The bug would come back through the fix.
    """
    classes = _classes()
    for starter, upgraded in STARTERS.items():
        assert upgraded in classes, (
            f"{upgraded} (the upgraded form of {starter}) does not exist")
        body = classes[upgraded]
        assert not re.search(
            r"RelicRarity\s+Rarity\s*=>\s*RelicRarity\.Starter", body), (
            f"{upgraded} is Starter rarity; a second Touch of Orobas would "
            "treat it as the starter and replace it with a Circlet")
        assert re.search(
            r"RelicRarity\s+Rarity\s*=>\s*RelicRarity\.Ancient", body), (
            f"{upgraded} should be Ancient rarity, matching the reward tier "
            "that grants it")


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


def test_upgraded_forms_carry_forward_their_base_reward_hook():
    """An upgraded starter must not silently drop the companion reward slot.

    THE NEAR-MISS THIS ENCODES (2026-07-26). `PearlOfInsightRelic` was written
    before `PearlOfWisdomRelic` gained its reward hook, so for a day the
    upgraded form did not carry it. Nothing would have crashed or warned:
    companions are off every rollable pool, so the starter relic's fourth
    reward option is their ONLY door, and Kokomi's Commander archetype is built
    entirely out of them. Taking Touch of Orobas would have quietly deleted one
    of her three archetypes.

    That is the same silent-deletion class the whole upgraded-starter track
    exists to prevent, reappearing one level up -- in the FIX rather than in
    the bug. It was caught by reading two files side by side, which is exactly
    the kind of catch that does not survive contact with a busy week.
    """
    classes = _classes()
    hook = "TryModifyCardRewardOptions"
    for starter, upgraded in STARTERS.items():
        if hook not in classes[starter]:
            continue        # base has no reward slot; nothing to carry
        assert hook in classes[upgraded], (
            f"{starter} hosts the companion reward slot but its upgraded form "
            f"{upgraded} does not. Taking Touch of Orobas would remove the "
            "only door companions have into the deck -- silently.")


# --- EPOCH 2 / D1: pool membership, made structural ----------------------

# Character -> the relic pool file that owns its membership. A curated map
# rather than a derived one: pool files are hand-written C# and the whole
# point of this check is that nothing in the compiler relates a relic class
# to the pool it belongs in.
RELIC_POOLS = {
    "PoundingSurprise": "KleeRelicPool.cs",
    "PearlOfWisdomRelic": "KokomiRelicPool.cs",
    "EtherealSpotlightRelic": "FurinaRelicPool.cs",
}

_CODE = _ROOT / "klee-mod" / "KleeCode"


def _pool_text(filename: str) -> str:
    return (_CODE / filename).read_text(encoding="utf-8")


def test_every_upgraded_starter_is_in_its_characters_relic_pool():
    """audit sec.1.2. All three shipped in NO pool, and that is a crash.

    `RelicModel.Pool` is a non-virtual `First()` over `AllRelicPools` and
    throws `InvalidOperationException` for a relic in none. That is finding
    27's crash class -- Pounding Surprise shipped poolless and made Klee look
    selected while the run started as somebody else -- reappearing one door
    over, at the mid-run Touch of Orobas grant instead of at character select.
    Act 2 rather than the menu: later, and much worse.

    KleeSelfCheck R7 now sweeps the upgrade replacement too, so this is
    belt-and-braces on purpose: R7 fires at BOOT, on the machine running the
    game, and reaches a Log line. This fires at commit time, on any machine,
    and is the reason a fourth character cannot repeat it.
    """
    for starter, upgraded in STARTERS.items():
        pool = _pool_text(RELIC_POOLS[starter])
        assert f"ModelDb.Relic<Relics.{upgraded}>()" in pool, (
            f"{upgraded} is in no relic pool. RelicModel.Pool throws for a "
            f"poolless relic, and Touch of Orobas hands this one over mid-run. "
            f"Append it in {RELIC_POOLS[starter]}.")


def test_the_base_starter_is_still_pooled_too():
    """Non-vacuity: the assertion above is only meaningful while the pool
    file is the thing that declares membership at all."""
    for starter in STARTERS:
        pool = _pool_text(RELIC_POOLS[starter])
        assert f"ModelDb.Relic<Relics.{starter}>()" in pool


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


def test_the_kokomi_exhaust_funnel_reads_the_relic_not_the_base_constant():
    """audit sec.1.1: the relic was a no-op with a lying tooltip.

    `PearlOfInsightRelic` declared `ChargePerExhaust = base * 2` and
    `BurstPerExhaust = base * 2`, and those constants were read by NOTHING
    except the relic's own description string. The funnel granted the base
    1/2 unconditionally. So the relic panel promised doubled per-exhaust
    accrual, and the red-pen record ("shipped as doubled per-exhaust")
    described a game that was never built.

    Pinned on the SHAPE rather than on the numbers: the grant site must go
    through the relic-aware helpers, and must not hand the base constants
    straight to the grant. Restating the numbers at the grant site is exactly
    how the description and the funnel came to disagree.
    """
    resources = (_CODE / "Powers" / "KokomiResources.cs").read_text(
        encoding="utf-8")
    hook = resources[resources.index("AfterCardExhausted"):]
    hook = hook[:hook.index("</summary>")] if "</summary>" in hook else hook

    assert "ExhaustCharge(owner)" in hook, hook[:800]
    assert "ExhaustBurst(owner)" in hook, hook[:800]
    assert "GainCharge(owner, KokomiConstants.ChargePerExhaust)" not in hook, (
        "the exhaust funnel is granting the base constant directly again; "
        "PearlOfInsightRelic's doubled numbers become decorative the moment "
        "it does")
    assert "PearlOfInsightRelic.ChargePerExhaust" in resources
    assert "PearlOfInsightRelic.BurstPerExhaust" in resources
