"""THE roster registry. One place a character is declared. (F1, audit sec.5.)

Adding character #4 touches roughly **26 scattered edit sites, 4 of them gated
and 22 silent**. That is the audit's single highest-leverage finding and the
reason this file exists: not because the duplication is ugly, but because the
failure mode of missing one is invisible. Kokomi shipped with an archetype
registry naming three tags that existed on zero cards (R66) and every adaptive
number ever taken for her was measured through it. Her card art shipped
unstaged because `deploy.ps1`'s directory list did not know about her. Neither
failed anything.

**This registry is the pre-Zhongli gate.** Slot 4 does not open until a
character can be declared once and have every consumer either read it or fail
loudly.

WHAT THIS FILE IS AND IS NOT
----------------------------
It is the single source of truth for **what characters exist and where their
parts live**. Consumers that can import Python read it directly. The C# mod and
the PowerShell build scripts cannot, so for them the registry is enforced
rather than consumed: `tools/lint_roster_registry.py` sweeps every site named
below and fails if a registered character is missing from any of them. That is
the S6c pattern -- a closed list that a lint holds shut -- extended from one
rule to the whole roster surface.

It is NOT a place for balance numbers. HP, burst_max, decks and bands stay in
`tier0/content/characters/*.yaml`, which is the ratified artifact. Duplicating
them here would create exactly the two-registries-disagreeing failure this file
exists to end -- R66 is the worked example. Two fields look like exceptions and
are not:

  * `plans` is a plan->pilot ROUTING table, not a design fact, and
    `runner.resolve_plan` has owned it since R68.
  * `archetypes` is R66's own defect, brought here on purpose and held shut by
    a cross-check against the cards themselves (see the field's note).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Character:
    """One playable character, and every file that has to know about them."""

    id: str                       # sim id, sheet filename stem, pck namespace
    display: str                  # player-facing name
    cs_class: str                 # KleeCode/<cs_class>.cs
    nation: str                   # companion-pool home nation
    default_plan: str
    plans: dict[str, str]         # plan name -> combat pilot id

    # The drafter's archetype vocabulary for this character, in DECLARED
    # order (not alphabetical, not plan order -- Kokomi's plans run
    # commander/priest/assist and her archetypes run priest/commander/assist).
    #
    # This is the R66 defect's home, and it is here rather than derived for
    # one reason: deriving it from card tags would let a TYPO'D tag on one
    # card silently invent an archetype. So it stays declared, and
    # `test_roster_registry` asserts it equals the set of tags her cards
    # actually carry (minus `generic`, which every character has and no
    # character is). Declared plus cross-checked makes both directions of
    # R66 impossible: a registry naming a tag that exists on zero cards
    # fails, and a card tag no registry knows about fails too.
    archetypes: tuple[str, ...] = ()

    # --- content the sim reads -------------------------------------------
    @property
    def character_yaml(self) -> Path:
        return REPO / "tier0" / "content" / "characters" / f"{self.id}.yaml"

    @property
    def card_sheet(self) -> Path:
        return REPO / "docs" / f"{self.id}-cards.yaml"

    @property
    def upgrade_sheet(self) -> Path:
        return REPO / "docs" / f"{self.id}-upgrades.yaml"

    # --- the mod --------------------------------------------------------
    @property
    def character_cs(self) -> Path:
        return REPO / "klee-mod" / "KleeCode" / f"{self.cs_class}.cs"

    @property
    def card_pool_cs(self) -> Path:
        return REPO / "klee-mod" / "KleeCode" / f"{self.cs_class}CardPool.cs"

    @property
    def relic_pool_cs(self) -> Path:
        return REPO / "klee-mod" / "KleeCode" / f"{self.cs_class}RelicPool.cs"

    # --- art ------------------------------------------------------------
    @property
    def card_art_dir(self) -> Path:
        return REPO / "ImageGen" / "images" / "cards" / self.id

    @property
    def pck_namespace(self) -> str:
        """res:// prefix for this character's packed resources."""
        return self.id


# Order is stable and meaningful: it is ship order, and several reports print
# the roster in it. Append; never reorder.
ROSTER: tuple[Character, ...] = (
    Character(
        id="klee", display="Klee", cs_class="Klee", nation="mondstadt",
        default_plan="demolition",
        plans={"generic": "generic", "demolition": "demolition",
               "spark": "spark", "reaction": "reaction"},
        archetypes=("demolition", "spark", "reaction"),
    ),
    Character(
        id="furina", display="Furina", cs_class="Furina", nation="fontaine",
        default_plan="salon",
        plans={"salon": "salon", "spotlight": "spotlight",
               "fanfare": "fanfare"},
        archetypes=("salon", "spotlight", "fanfare"),
    ),
    Character(
        id="kokomi", display="Sangonomiya Kokomi", cs_class="Kokomi",
        nation="inazuma", default_plan="priest",
        # v0.2 sheet pass (2026-07-24): plans mirror her tier0 archetype
        # pilots. Requires DRAFTER_VERSION >= 7 -- the v6 scorer read her
        # conscript/gain_charge/Sly verbs as literal zero.
        plans={"generic": "generic", "commander": "commander",
               "priest": "priest", "assist": "assist"},
        # R66: was ("garment", "ward", "conscript"), which matched nothing.
        # The tuple predated the v0.2 sheet pass that tagged her cards
        # priest/commander/assist/generic, and "conscript" had independently
        # been retired by the lore pass. Two registries in one repo disagreed
        # about her vocabulary and EVERY adaptive Kokomi number ever taken was
        # measured through the wrong one.
        archetypes=("priest", "commander", "assist"),
    ),
)

BY_ID: dict[str, Character] = {c.id: c for c in ROSTER}
IDS: tuple[str, ...] = tuple(c.id for c in ROSTER)


def get(character_id: str) -> Character:
    """Registered character, or a loud failure naming the whole roster.

    Deliberately not `.get()`-shaped: an unregistered id reaching this
    function is the exact defect the registry exists to make impossible, and
    returning None would let it travel one more layer.
    """
    try:
        return BY_ID[character_id]
    except KeyError:
        raise KeyError(
            f"{character_id!r} is not a registered character. The roster is "
            f"{', '.join(IDS)}. Adding a character means adding a row to "
            "tier0/roster.py -- and tools/lint_roster_registry.py will then "
            "tell you every other file that has to learn about them."
        ) from None


# Reference characters are NOT roster members. They are measurement anchors
# with no art, no pool, no C# class and no plans beyond `generic`, and folding
# them in would make every roster sweep below either wrong or full of
# exceptions. Named here so the distinction is on record rather than implied
# by their absence.
REFERENCE_IDS: tuple[str, ...] = ("ref_ironclad", "real_ironclad",
                                  "ref_silent", "real_silent")
