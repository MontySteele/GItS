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
}

# Starters KNOWINGLY without an upgraded form, each with the reason and the
# gate that clears it. A curated absence, never a silent one -- the point of
# this file is that a missing upgrade must be a decision on the record.
NO_UPGRADED_FORM: dict[str, str] = {
    "EtherealSpotlightRelic": (
        "RULED 2026-07-26 (red-pen R2) — this entry is now a QUEUED "
        "IMPLEMENTATION, not an open question. [USER] design: the upgraded "
        "relic grants the benefits of BOTH Spotlight selector effects at once, "
        "so conditions keying off 'moved the Spotlight this turn' are ALWAYS "
        "ON, making her starter upgrade the selector-payoff enabler. This "
        "deliberately overrides the sprint's 'no new behaviour in a starter "
        "upgrade' rule BY USER AUTHORITY -- the rule is overridden, not "
        "reinterpreted. Delete this entry when the class lands. "
        "See docs/red-pen-2026-07-26.md R2. "
        "Until then Touch of Orobas still hands Furina a Circlet. "
        "--- The original reasoning, kept because it is why the ruling had to "
        "come from the user rather than from an implementer: "
        "Ethereal Spotlight adds a one-use Spotlight selector to hand "
        "at the start of each turn. There is NO NUMBER in it to scale: the "
        "selector is a Token card with no upgrade, and the effect is binary "
        "(the card is added, or it is not). Every candidate tune-up is "
        "out of bounds for this sprint: adding a second designation or "
        "changing when the selector arrives is new BEHAVIOUR, which G-C3(b) "
        "forbids in a starter upgrade ('an upgraded starter that changes "
        "behavior is pool-sweep material'); and a per-turn Encore or Fanfare "
        "trickle is banned outright by her sheet's no-passive-accrual law "
        "(kickoff §4). The red-pen took the first branch and accepted a "
        "behaviour change as a deliberate exception."
    ),
}


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
