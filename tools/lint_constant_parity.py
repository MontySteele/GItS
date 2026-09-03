#!/usr/bin/env python3
"""Parity lint: C# mirrored constants vs tier0, the single source of truth.

WHY THIS EXISTS. Every balance number in the mod lives twice -- once in
tier0 (constants.py, the character yamls) where it was MEASURED, and once in
C# where it is PLAYED. The C# copies carry doc comments swearing they mirror
the sim and must never be re-derived, and until now that promise was kept by
discipline alone. Discipline is not a gate: a sim-side retune that nobody
mirrors produces a mod that plays to numbers no simulation ever endorsed, and
it does so SILENTLY -- the build is green, the tests pass, the tuning report
describes a game nobody is playing.

There is no C# test project (and no cheap way to add one against a Godot game
assembly), so a running fixture is not available. This is the static form of
the same guarantee, and it is strictly the more valuable half: a fixture pins
behaviour at the numbers it was written with, while this pins the numbers
themselves against the model that chose them.

DISCIPLINE (tier0's UNAPPLIABLE, applied to linting). Every `public const int`
in the mod must be classified: either MIRRORED (with the tier0 expression it
copies, compared by value) or UNMIRRORED (with a written reason it has no sim
counterpart). A constant in neither map is a FINDING, not a skip. That is what
makes the lint survive contact with future work -- adding a C# balance number
forces a decision about where it came from, at the moment the author still
knows the answer.

Run: python tools/lint_constant_parity.py
Exit 1 with findings on stdout when a mirror has drifted or is unclassified.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import yaml  # noqa: E402

from tier0 import constants as C  # noqa: E402

CS_ROOT = REPO / "klee-mod" / "KleeCode"


def _char(name: str, key: str):
    """A value from a tier0 character sheet (burst_max and friends live there,
    not in constants.py, because they are per-character statline)."""
    path = REPO / "tier0" / "content" / "characters" / f"{name}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))[key]


def _salon(member: str, phase: str, key: str):
    """A number out of the SALON_MEMBERS table. Furina's members are typed, so
    their tick/bow numbers are table entries rather than named constants."""
    return C.SALON_MEMBERS[member][phase][key]


def _reframe(name: str):
    """A number out of the Furina reframe's quarantined engine module.

    NOT `constants.py`, and that is the countersigned packet's own decision
    (its sec.6.1): the reframe's flags and seeds are "a module constant in the
    reframe module, **not** in `constants.py`", so that a quarantined slice
    moves neither the constant census nor the world stamp. Mirroring is a
    different question from stamping -- the C# arm PLAYS these numbers, so the
    two engines have to agree on them by value or a seat grades a rule the sim
    never scored. Reading them from where the sim keeps them is what lets both
    facts be true at once.
    """
    from tier0.engine import furina_reframe as _fr
    return getattr(_fr, name)


# --------------------------------------------------------------------------
# MIRRORED: C# constant -> the tier0 value it copies.
#
# The right-hand side is evaluated here, so this table doubles as the written
# record of WHERE each C# number came from -- which is the question that is
# expensive to answer six months later and free to answer today.
# --------------------------------------------------------------------------
def _ancient_hook(relic_id: str, hook: str) -> int:
    """A number out of tier05's ancient-relic table.

    Relic effects are DATA rather than named constants, so the sim's copy of an
    Ancient's number lives in tier05/content/relics.yaml. Reading it here is
    what makes a relic number mirrorable at all -- the alternative was to file
    every Ancient under UNMIRRORED as "the sim does not model relics", which
    stopped being true the day the starter-upgrade hook landed.
    """
    from tier05 import relics as _relics
    for fx in _relics.ancient_pool()[relic_id]["effects"]:
        if fx.get("hook") == hook:
            return int(fx["amount"])
    raise KeyError(f"{relic_id} has no {hook} effect")


MIRRORED: dict[str, object] = {
    # Klee's upgraded starter (Touch of Orobas -> Dodoco Tales). The sim's
    # copy is a relic row, not a constant; see _ancient_hook. The key below
    # is the C# TYPE name, which R69 deliberately left as ExplosiveFrags:
    # only the player-facing string was renamed, so relic ids stay put.
    "ExplosiveFrags.OpeningSparks":
        _ancient_hook("touch_of_orobas_klee", "combat_start_spark"),
    # Kokomi's upgraded starter (Touch of Orobas -> Pearl of Insight). Both
    # were UNMIRRORED until 2026-08-13 because the C# side was the EXPRESSION
    # `KokomiConstants.X * 2`, which parse_number cannot read. R190 ratified
    # the doubling as a standing invariant, the C# side became a literal on
    # OpeningSparks's precedent, and INVARIANTS below asserts the 2x itself --
    # which is the half a by-value mirror cannot express.
    "PearlOfInsightRelic.ChargePerExhaust":
        _ancient_hook("touch_of_orobas_kokomi", "charge_per_exhaust"),
    "PearlOfInsightRelic.BurstPerExhaust":
        _ancient_hook("touch_of_orobas_kokomi", "burst_per_exhaust"),
    # Shared elemental table (tier0/constants.py, reaction block).
    "ReactionConstants.AuraDurationTurns": C.AURA_DURATION_TURNS,
    "ReactionConstants.OverloadSplash": C.OVERLOAD_SPLASH,
    "ReactionConstants.OverloadWeak": C.OVERLOAD_WEAK,
    "ReactionConstants.SuperconductVuln": C.SUPERCONDUCT_VULN,
    "ReactionConstants.ElectroChargedDot": C.ELECTROCHARGED_DOT,
    "ReactionConstants.ElectroChargedDotTurns": C.ELECTROCHARGED_DOT_TURNS,
    "ReactionConstants.CrystallizeBlock": C.CRYSTALLIZE_BLOCK,
    "ReactionConstants.ShatterDamage": C.SHATTER_DAMAGE,
    "ReactionConstants.FrozenBossVuln": C.FROZEN_BOSS_VULN,
    "ReactionKitConstants.CatalyticBurstPerReaction":
        C.CATALYTIC_BURST_PER_REACTION,
    # Non-integer members of the same table. These were invisible until the
    # lint was widened past `int` during the §4.7 shop sprint -- and they are
    # the amplifier numbers, i.e. the single most consequential multipliers in
    # the mod. AMP_STACK_LIMIT is the provenance-log tripwire guardrail (§7.1).
    "ReactionConstants.VaporizeMult": C.VAPORIZE_MULT,
    "ReactionConstants.MeltMult": C.MELT_MULT,
    "ReactionConstants.FrozenDamageMult": C.FROZEN_DAMAGE_MULT,
    "ReactionConstants.VulnerableTakenMult": C.VULNERABLE_TAKEN_MULT,
    "ReactionConstants.AmpStackLimit": C.AMP_STACK_LIMIT,

    # Companion reward slot (§4.1) -- the rarity walk and the nation weighting
    # CompanionSlot ports from tier05 rewards.
    "CompanionSlot.CommonOdds": C.RARITY_ODDS["common"],
    "CompanionSlot.UncommonOdds": C.RARITY_ODDS["uncommon"],
    "CompanionSlot.SameNationShare": C.SAME_NATION_REWARD_SHARE,
    "CompanionSlot.NationWeight": C.NATION_WEIGHTS["mondstadt"],
    # §4.7 shop channel. BOTH slots read the reward odds CONDITIONED on
    # >= Uncommon since [USER] restored slot 2's floor on 2026-08-10
    # (CONSTANTS_VERSION 9), so both mirrors point at the same tier0 entry.
    #
    # SlotTwoUncommonOdds has now held both readings: the conditioned value
    # before R116, the unconditioned 0.35 between R116 and the restoration,
    # and the conditioned value again. `SlotTwoCommonOdds` was its companion
    # in the middle period and is DELETED from the patch -- a Common is no
    # longer a reachable shop draw, so a mirror for it would pin a number the
    # mod does not use.
    "MerchantInventory_CompanionColorlessSlots_Patch.SlotOneUncommonOdds":
        C.SHOP_COMPANION_RARITY_ODDS["uncommon"],
    "MerchantInventory_CompanionColorlessSlots_Patch.SlotTwoUncommonOdds":
        C.SHOP_COMPANION_RARITY_ODDS["uncommon"],

    # Furina.
    "FurinaResourceConstants.FanfareDecayFraction": C.FANFARE_DECAY_FRACTION,
    # New to the map on 2026-08-13 (EB-97), and the reason it is here is the
    # gate's own blind spot: the fraction was an inline `/ 2` in FanfareCap,
    # so it appeared in neither MIRRORED nor UNMIRRORED and the lint's
    # "every balance number in the mod lives twice" promise did not cover
    # the Furina identity record's headline "%maxHP". Naming it on the C# side is what makes
    # it visible here.
    "FurinaResourceConstants.FanfareCapFraction": C.FANFARE_CAP_FRACTION,
    "SalonConstants.DryDamageMultiplier": C.SALON_DRY_DAMAGE_MULT,
    "SpotlightSystem.GuestCastBaseMultiplier": C.SPOTLIGHT_BASE_MULT,

    # Klee.
    "BurstConstants.PerSkillTag": C.BURST_PER_SKILL_TAG,
    "BurstConstants.PerReaction": C.BURST_PER_REACTION,
    "BurstConstants.KleeMax": _char("klee", "burst_max"),
    "KitBurstConstants.VolleyHits": C.SPARKS_N_SPLASH_HITS,
    "KitBurstConstants.VolleyHitDamage": C.SPARKS_N_SPLASH_HIT_DMG,
    "SparkPower.Threshold": C.SPARKS_FOR_FREE_ATTACK,
    # The Sparks alternative-cost arm (review/ruled/klee-sparks-2026-08-29.md
    # sec.5). MIRRORED and not UNMIRRORED even though the class is
    # quarantined: the tier0 counterpart exists and is the SAME number, and
    # this pairing is the only thing that would catch one side being repriced
    # without the other. The row above is the threshold this one retires;
    # both stay, because the flag runs the two economies as two arms.
    "SparkAttackCostPower.Price": C.SPARK_ATTACK_POWER_PRICE,
    "DemolitionConstants.SplashBurst": C.DETONATION_SPLASH_BURST,
    "DemolitionConstants.SplashProcCapPerTurn": C.DETONATION_SPLASH_PROC_CAP,
    "DemolitionConstants.PlaytimeBombDamage": C.PLAYTIME_BOMB_DAMAGE,
    # EB-219 / LAW:145 -- "Little Hexenzirkul", Klee's kit answering a PERSONAL
    # Companion play. These four ARE the declaration the clause requires, so a
    # drift between the engines would be a drift in a rule, not in a tunable.
    "KleeCompanionSpark.Base": C.KLEE_COMPANION_SPARK_BASE,
    "KleeCompanionSpark.ReactionBonus": C.KLEE_COMPANION_SPARK_REACTION_BONUS,
    "KleeCompanionSpark.UpgradedBonus": C.KLEE_COMPANION_SPARK_UPGRADED_BONUS,
    "KleeCompanionSpark.MaxPerPlay": C.KLEE_COMPANION_SPARK_MAX_PER_PLAY,
    "CompanionConstants.OzDamage": C.OZ_DMG,
    "CompanionConstants.WitchsFlameBurst": C.WITCHS_FLAME_BURST,
    "CompanionConstants.SolarIsotomaBlock": C.SOLAR_ISOTOMA_BLOCK,
    "CompanionConstants.CelestialGiftBlock": C.CELESTIAL_GIFT_BLOCK,
    "CompanionConstants.MasqueBondBlock": C.MASQUE_BOND_BLOCK,
    "CompanionBanner.FeaturedSlots": C.BANNER_FEATURED_SLOTS,

    # Furina.
    # RE-CLASSIFIED by the Fanfare rework (2026-07-28). FanfarePerEncoreGained
    # and both FanfareFloorPerPower* left this map because they left BOTH
    # engines -- a retired constant must be deleted from the map, never left
    # pointing at a deleted C.* (which raises) and never quietly stubbed to a
    # literal (which would assert parity between two things that no longer
    # exist). FanfarePerEncoreAbsorbed is new on both sides and joins here.
    "FurinaResourceConstants.FanfarePerHpLost": C.FANFARE_PER_HP_LOST,
    "FurinaResourceConstants.FanfarePerEncoreSpent":
        C.FANFARE_PER_ENCORE_SPENT,
    "FurinaResourceConstants.FanfarePerEncoreAbsorbed":
        C.FANFARE_PER_ENCORE_ABSORBED,
    "FurinaResourceConstants.BurstPerSkillTag": C.BURST_PER_SKILL_TAG,
    "FurinaResourceConstants.BurstPerReaction": C.BURST_PER_REACTION,
    "FurinaResourceConstants.BurstPerEncoreSpent": C.BURST_PER_ENCORE_SPENT,
    "FurinaResourceConstants.BurstPerSalonTick": C.SALON_TICK_BURST,
    "FurinaResourceConstants.BurstMax": _char("furina", "burst_max"),
    "SpotlightSystem.FanfarePerCenterStagePlay": C.FANFARE_PER_SPOTLIGHT_CARD,
    "SalonConstants.MemberSlots": C.SALON_MEMBER_SLOTS,
    "SalonConstants.FocusPerFanfare": C.SALON_FOCUS_PER,
    "SalonConstants.ReplacementNumericMultiplier": C.SALON_REPLACE_NUMERIC_MULT,
    "SalonConstants.ReplacementDamageMultiplier": C.SALON_REPLACE_DAMAGE_MULT,
    "SalonConstants.TickEncoreCost": C.SALON_TICK_ENCORE_COST,
    "SalonConstants.CrabalettaTick": _salon("crabaletta", "tick", "damage"),
    "SalonConstants.CrabalettaBow": _salon("crabaletta", "bow", "damage"),
    "SalonConstants.UsherTick": _salon("usher", "tick", "block"),
    "SalonConstants.UsherBow": _salon("usher", "bow", "block"),
    "SalonConstants.ChevalmarinTick": _salon("chevalmarin", "tick", "damage"),
    "SalonConstants.ChevalmarinBowEncore": _salon("chevalmarin", "bow", "encore"),

    # Kokomi.
    "KokomiConstants.ChargePerExhaust": C.CHARGE_PER_EXHAUST,
    "KokomiConstants.BurstPerExhaust": C.KOKOMI_BURST_PER_EXHAUST,
    "KokomiConstants.BurstPerReaction": C.BURST_PER_REACTION,
    "KokomiConstants.KurageDuration": C.KURAGE_DURATION,
    "KokomiConstants.KuragePulseBase": C.KURAGE_PULSE_BASE,
    "KokomiConstants.KuragePulsePerCharge": C.KURAGE_PULSE_PER_CHARGE,
    "KokomiConstants.KuragePulseBlock": C.KURAGE_PULSE_BLOCK,
    "KokomiConstants.GarmentAttackBlock": C.GARMENT_ATTACK_BLOCK,
    "KokomiConstants.GarmentTurns": C.CEREMONIAL_GARMENT_TURNS,
    "KokomiConstants.GarmentChargeDivisor": C.GARMENT_CHARGE_DIVISOR,
    "KokomiConstants.ConscriptCostDelta": C.CONSCRIPT_COST_DELTA,
    "KokomiConstants.BurstMax": _char("kokomi", "burst_max"),
    # The Kurage's memory (QUARANTINED, R213 B / EB-147 -- the C# rule lives
    # under klee-mod/KleeCode/Powers/Prototype and is Compile Remove'd out of a
    # release build). Quarantined is not exempt: a prototype arm measured on a
    # number the sim never chose is exactly the failure this lint exists for,
    # and these three are the only numeric constants the rule has. Spec:
    # review/ruled/kokomi-kurage-memory-2026-08-29.md sec.11.4.
    "KurageMemoryLaw.CostPerEnergy": C.KURAGE_MEMORY_COST_PER_ENERGY,
    "KurageMemoryLaw.PulseBlock": C.KURAGE_MEMORY_PULSE_BLOCK,
    "KurageMemoryLaw.QueueCap": C.KURAGE_QUEUE_CAP,
    # The Klee overhaul, slice one (QUARANTINED, R213 B -- the rules engine
    # lives under klee-mod/KleeCode/Powers/Prototype and is Compile Remove'd
    # out of a release build). Quarantined is not exempt, for the same reason
    # the Kurage's three above are not: these four numbers ARE the rules
    # (`review/active/klee-brief-2026-09-01.md` sec.3), and a prototype played
    # on a number the sim never declared is exactly this lint's failure. They
    # are placeholders and not claims -- but they are the placeholders both
    # sides have to agree on.
    "KleeOverhaulLaw.BombGrowth": C.KLEE_OVERHAUL_BOMB_GROWTH,
    "KleeOverhaulLaw.WorkshopGrowth": C.KLEE_OVERHAUL_WORKSHOP_GROWTH,
    "KleeOverhaulLaw.AliceMultiplier": C.KLEE_OVERHAUL_ALICE_MULTIPLIER,
    "KleeOverhaulLaw.SparkPerExplosion": C.KLEE_OVERHAUL_SPARK_PER_EXPLOSION,
    # FIVE now: R242 pick 1 gave rule 4 a second number, the opening bank.
    "KleeOverhaulLaw.OpeningSpark": C.KLEE_OVERHAUL_OPENING_SPARK,
    # THE MONDSTADT COMPANION OVERHAUL (QUARANTINED, `C.COMPANION_OVERHAUL`).
    # Same terms as the four above and for the same reason: quarantined is not
    # exempt. Every number here is the approved workshop's own printed text
    # (its sec.3, re-priced in its sec.8), and BOTH engines play these cards --
    # so the two implementations have to agree on them by value, or a seat is
    # grading a different card from the one the sim scored.
    "CompanionOverhaulLaw.SignatureMixBlock": C.MC_SIGNATURE_MIX_BLOCK,
    "CompanionOverhaulLaw.GlacialWaltzDamage": C.MC_GLACIAL_WALTZ_DMG,
    "CompanionOverhaulLaw.IsotomaDamage": C.MC_ISOTOMA_DMG,
    "CompanionOverhaulLaw.IsotomaBlock": C.MC_ISOTOMA_BLOCK,
    "CompanionOverhaulLaw.DandelionBreezeBlock": C.MC_DANDELION_BREEZE_BLOCK,
    "CompanionOverhaulLaw.OzDamage": C.MC_OZ_DMG,
    "CompanionOverhaulLaw.RevelationBlock": C.MC_REVELATION_BLOCK,
    "CompanionOverhaulLaw.RevelationStrength": C.MC_REVELATION_STRENGTH,
    "CompanionOverhaulLaw.OmenVulnerable": C.MC_OMEN_VULNERABLE,
    "CompanionOverhaulLaw.LightningRoseDamage": C.MC_LIGHTNING_ROSE_DMG,
    "CompanionOverhaulLaw.LightningRoseVulnerable": C.MC_LIGHTNING_ROSE_VULN,
    # The same arm's SECOND WAVE -- the seven numbers its thirteen new rows
    # hand to a POWER rather than print on a card. Same terms again.
    "CompanionOverhaulLaw.ShowerDamage": C.MC_SHOWER_DMG,
    "CompanionOverhaulLaw.BinaryWhiteReactionMult":
        C.MC_BINARY_WHITE_REACTION_MULT,
    "CompanionOverhaulLaw.LightningFangDamage": C.MC_LIGHTNING_FANG_BONUS,
    "CompanionOverhaulLaw.BaronBunnyReduction": C.MC_BARON_BUNNY_REDUCTION,
    "CompanionOverhaulLaw.BaronBunnyDamage": C.MC_BARON_BUNNY_DMG,
    "CompanionOverhaulLaw.LightfallBase": C.MC_LIGHTFALL_BASE,
    "CompanionOverhaulLaw.LightfallPerAttack": C.MC_LIGHTFALL_PER_ATTACK,
    # THE SAME ARM'S SECOND NATION -- the twenty numbers the approved Inazuma
    # workshop hands to a POWER rather than prints on a card. Same terms again,
    # and the same reason: BOTH engines play these cards, so the two
    # implementations have to agree on them by value or a seat is grading a
    # different card from the one the sim scored.
    "CompanionOverhaulLaw.WarBannerDexterity": C.MI_WAR_BANNER_DEXTERITY,
    "CompanionOverhaulLaw.JuugaDamage": C.MI_JUUGA_DMG,
    "CompanionOverhaulLaw.DarumaDamage": C.MI_DARUMA_DMG,
    "CompanionOverhaulLaw.DarumaBlock": C.MI_DARUMA_BLOCK,
    "CompanionOverhaulLaw.SanctifyingRingDamage": C.MI_SANCTIFYING_RING_DMG,
    "CompanionOverhaulLaw.SanctifyingRingBlock": C.MI_SANCTIFYING_RING_BLOCK,
    "CompanionOverhaulLaw.BlazingBarrierBlock": C.MI_BLAZING_BARRIER_BLOCK,
    "CompanionOverhaulLaw.OoyoroiDamage": C.MI_OOYOROI_DMG,
    "CompanionOverhaulLaw.OoyoroiBlock": C.MI_OOYOROI_BLOCK,
    "CompanionOverhaulLaw.StormcallBonus": C.MI_STORMCALL_BONUS,
    "CompanionOverhaulLaw.SakuraDamage": C.MI_SAKURA_DMG,
    "CompanionOverhaulLaw.SakuraBonus": C.MI_SAKURA_BONUS,
    "CompanionOverhaulLaw.SakuraCap": C.MI_SAKURA_CAP,
    "CompanionOverhaulLaw.AurousBlazeDamage": C.MI_AUROUS_BLAZE_DMG,
    "CompanionOverhaulLaw.SoumetsuDamage": C.MI_SOUMETSU_DMG,
    "CompanionOverhaulLaw.SoumetsuFinale": C.MI_SOUMETSU_FINALE,
    "CompanionOverhaulLaw.KyoukaDamage": C.MI_KYOUKA_BONUS,
    "CompanionOverhaulLaw.KyoukaFinale": C.MI_KYOUKA_FINALE,
    "CompanionOverhaulLaw.SurpriseDispatchDamage": C.MI_SURPRISE_DISPATCH_DMG,
    "CompanionOverhaulLaw.TamotoDamage": C.MI_TAMOTO_DMG,
    # THE KOKOMI OVERHAUL (QUARANTINED, `C.KOKOMI_OVERHAUL`). Same terms again
    # and for the same reason: quarantined is not exempt. Draft 6 left the arm
    # with exactly ONE rule number -- Tamakushi Casket's Hydro strike, printed
    # on the relic and on no card -- because its rules are structural and every
    # other figure is a CARD's, on its own row. The six draft 2 declared went
    # with the pulse, the Garment and the Tide.
    "KokomiOverhaulLaw.CasketStrike": C.KOKOMI_OVERHAUL_CASKET_STRIKE,
    # THE FURINA REFRAME, SLICE ONE (QUARANTINED -- the C# arm lives under
    # klee-mod/KleeCode/Powers/Prototype and is Compile Remove'd out of a
    # release build; the sim half is tier0/engine/furina_reframe.py, every flag
    # False). Same terms as the four arms above and for the same reason:
    # quarantined is not exempt. These FIVE numbers ARE the slice's rules --
    # the two mint amounts, the LAW:145 bound, the Evoke's Focus multiplier and
    # the one-mode selector's price -- and the sim declared every one of them
    # first, because R220 B sequenced the C# leg last. See `_reframe` for why
    # they are read out of the reframe module rather than constants.py.
    "FurinaReframeLaw.FanfarePerTrigger": _reframe("FANFARE_PER_TRIGGER"),
    "FurinaReframeLaw.FanfarePerEvoke": _reframe("FANFARE_PER_EVOKE"),
    "FurinaReframeLaw.FanfarePerCompanionTriggerMax":
        _reframe("FANFARE_PER_COMPANION_TRIGGER_MAX"),
    "FurinaReframeLaw.EvokeFocusMult": _reframe("EVOKE_FOCUS_MULT"),
    "FurinaReframeLaw.SpotlightDesignateEncoreCost":
        _reframe("SPOTLIGHT_DESIGNATE_ENCORE_COST"),
    # A SENTINEL rather than a balance number, and mirrored anyway because it
    # HAS a sim counterpart -- "the named member is not on the stage" is a
    # value both engines return and both engines test against, so filing it
    # UNMIRRORED as "not balance" would be true and useless. The classification
    # this table asks for is where the number came from.
    "FurinaReframe.EvokeTargetAbsent": _reframe("EVOKE_TARGET_ABSENT"),
    # Rally prints "costs 1 less" but the op carries no amount (it is one
    # whole printed clause), so the number lives on the power and is
    # mirrored like every other rule number.
    "NextCompanionDiscountPower.Discount": C.KOKOMI_OVERHAUL_RALLY_DISCOUNT,
}

# --------------------------------------------------------------------------
# UNMIRRORED: C# constants with no tier0 counterpart, each with its reason.
#
# "The sim does not model this" is a legitimate answer and always has been --
# relics, Ancients and the run layer are game-side content. What is not
# legitimate is leaving the question unanswered.
# --------------------------------------------------------------------------
UNMIRRORED: dict[str, str] = {
    "RosterArt.PortraitWidth":
        "`EB-275`. AN IMAGE SIZE, not balance: the card-art window's authored "
        "pixel width, used to build the flat blank an uncovered row's portrait "
        "resolves to instead of null -- which is what stops the game falling "
        "through to its own atlas and logging a missing sprite on every draw. "
        "The number is the art pipeline's: `tools/art_lint.py` bills every "
        "portrait against 500x380 and `tools/art_coverage.py` reads the same "
        "shape off disk. tier0 draws nothing and has no counterpart.",
    "RosterArt.PortraitHeight":
        "`EB-275`. The other half of the card-art window's authored size; see "
        "`RosterArt.PortraitWidth` for the whole of it.",
    "NonFiniteCardGuard.MaxTrailTravelPx":
        "`EB-292`. A SCENE BOUND, not balance: how far a followed node may "
        "travel in one frame before the base game's card-trail gap-fill loop "
        "is refused. That loop walks the gap at a fixed 48 px and is bounded "
        "by the travel, so an infinite -- or merely enormous -- position asks "
        "it for unbounded work and takes the process's memory. 100,000 px is "
        "far past anything a real flight produces on a 1920x1080 design "
        "resolution. It touches no card, no meter and no number the sim can "
        "see: tier0 draws nothing.",
    "MeterLedger.MaxRows":
        "`EB-216`. INSTRUMENT, not balance: how many per-play ledger rows the "
        "mod keeps before dropping the oldest. It touches no game number, no "
        "card and no meter -- it is the size of a diagnostic buffer, and the "
        "sim has no ledger to size. R225 filed the ledger as instrument work "
        "that does not gate an arm; this is the only number it has.",
    "ExplosiveFrags.SparksPerDetonation":
        "the BASE starter's rate, carried forward unchanged by the upgrade -- "
        "which is the ratified design (the windfall is OpeningSparks; the "
        "doubling of this rate was rejected at the 2026-07-26 red-pen). Its "
        "sim counterpart is a literal at the detonation site in effects.py "
        "(`gain_sparks(state, 1)` under spark_on_detonation), not a named "
        "constant, so there is nothing to compare against by value. "
        "NOTE: this entry used to read 'tier0 has no relic-upgrade layer', "
        "which stopped being true when combat_start_spark and "
        "touch_of_orobas_klee landed -- OpeningSparks is now MIRRORED against "
        "that row.",
    # The two PearlOfInsightRelic rates USED TO LIVE HERE, as derived
    # expressions this lint could not read. R190 ratified the 2x relationship
    # as a standing invariant and they moved to MIRRORED above, with INVARIANTS
    # below carrying the half MIRRORED cannot express. The old entry's own
    # note said this was the fix; it was taken.

    # --- surfaced by widening the lint past `int` (§4.7 shop sprint) ---
    "FurinaParityVectors.DecayFraction":
        "derived: it IS FurinaResourceConstants.FanfareDecayFraction, by "
        "reference rather than by literal. The compiler enforces the link and "
        "the target is MIRRORED, so comparing here would only add a second "
        "place to forget.",
    "KleeSelfCheck.RuleCount":
        "diagnostic bookkeeping: how many self-check rules exist. It counts "
        "this file's own contents, not anything the sim models.",
    "ExhaustSelection.XCost":
        "a SENTINEL, not a balance number (EB-118): the cost recorded for an "
        "X-cost victim, negative so no derived total can sum it by accident. "
        "tier0 expresses the same fact differently -- the descriptor keeps "
        "`cost` raw as the string 'X' and the total skips non-ints "
        "(effects.exhaust_selection_counts) -- so there is no sim VALUE to "
        "compare against. The BEHAVIOUR is pinned on both sides instead, by "
        "the X-cost tests in test_exhaust_context.py and "
        "ExhaustSelectionTests.cs.",

    # Presentation layer. These are pixels, seconds and sprite orientation --
    # tier0 models no geometry and no time, so there is nothing to mirror. They
    # are listed rather than pattern-skipped on purpose: a rule that skipped
    # everything under Vfx/ would also skip a balance number that someone
    # parked there, which is precisely how numbers go missing.
    "CreatureFacing.AuthoredFacing":
        "presentation: which way the source art is drawn. No sim counterpart.",
    "CreatureFacing.DeadZonePx":
        "presentation: pixel threshold below which a creature is not re-aimed.",
    "GaugeBridge.BarFullWidth":
        "presentation: meter bar width in pixels.",
    # The Kurage memory card (sec.14). Every number below is SCREEN GEOMETRY or
    # a font size for a HUD element the sim has no notion of: tier0 has no
    # display at all, so there is nothing to compare by value. The affordability
    # rule the element draws IS mirrored, and it carries no constant -- it is a
    # running subtraction over prices the queue already holds.
    "KurageMemoryCard.EdgeMargin":
        "presentation: distance from the left edge of the screen, in pixels.",
    "KurageMemoryCard.ThumbWidth":
        "presentation: card-thumbnail width in pixels.",
    "KurageMemoryCard.ThumbHeight":
        "presentation: thumbnail height, derived from the width by NCard's own "
        "300x422 aspect so the portrait is not stretched.",
    "KurageMemoryCard.RingWidth":
        "presentation: affordability ring thickness on the HUD thumbnail.",
    "KurageMemoryCard.CountFontSize":
        "presentation: the Charge count's font size.",
    "KurageMemoryCard.BadgeFontSize":
        "presentation: the price badge's font size.",
    # The Kokomi Plan strip (`EB-216`), on the same terms one element over:
    # every number is SCREEN GEOMETRY or a font size for a HUD element the sim
    # has no notion of. The one that is nearly a rule -- how many Plans get a
    # picture -- is still presentation: the queue's LENGTH is the rule and the
    # element prints the overflow as "+N" rather than dropping it.
    "KokomiPlanStrip.EdgeMargin":
        "presentation: distance from the left edge of the screen, in pixels.",
    "KokomiPlanStrip.ThumbWidth":
        "presentation: card-thumbnail width in pixels.",
    "KokomiPlanStrip.ThumbHeight":
        "presentation: thumbnail height, on the same 300x422 aspect the memory "
        "card's is, so a Plan and a memory draw the same size card.",
    "KokomiPlanStrip.ThumbGap":
        "presentation: vertical gap between stacked thumbnails, in pixels.",
    "KokomiPlanStrip.CountFontSize":
        "presentation: the overflow count's font size.",
    "KokomiPlanStrip.MaxDrawn":
        "presentation: how many pending Plans get a picture before the column "
        "runs off the band. Not a cap on the queue -- nothing limits how many "
        "Plans she may write -- and the overflow is printed as `+N`, so the "
        "sim has nothing to compare and no rule is hiding here.",
    # The Bake-Kurage's beat (`EB-316`, `EB-317`). Both numbers are SCREEN
    # TIME. They decide how long an animation and a speech bubble occupy the
    # frame and nothing else: no hit is added, removed, resized or reordered by
    # either, and every rule they sit between resolves in the same order for the
    # same amounts with them set to zero. The sim has no frames, no animation
    # and nobody to read a bubble, so there is nothing to compare by value.
    "KurageBeat.ActSeconds":
        "presentation: how long the jellyfish's attack animation holds before "
        "the hit behind it lands, in seconds. It IS `EB-316`'s repair -- the "
        "casket's strike used to arrive in the same frame as the card that "
        "caused it, so the two damage numbers read as one -- and it moves no "
        "number: the same damage lands either way. tier0 resolves a turn with "
        "no frames in it.",
    "KurageBeat.LineSeconds":
        "presentation: how long the carry-out line stays on screen, in "
        "seconds. Long enough to read, short enough that four Plans in one "
        "morning do not stack their bubbles. The sim has no screen.",
    "KurageMemoryPileRing.RingWidth":
        "presentation: ring thickness on a full-size card in the pile viewer, "
        "thicker than the HUD's because the card is.",
    # EB-214's header. The SENTENCE is what R224 ruled and it is pinned in
    # KleeTests and in tier0/tests/test_kurage_base_kit.py; where it sits and
    # how big it is are presentation, and the sim has no screen to compare
    # them against.
    "KurageMemoryPileRing.HeaderFontSize":
        "presentation: font size of the Charge-source line at the head of the "
        "pile view.",
    "KurageMemoryPileRing.HeaderTop":
        "presentation: the header line's inset from the top of the pile "
        "screen, in pixels.",
    "KurageMemoryPileRing.HeaderHeight":
        "presentation: the header line's own height, in pixels.",
    "KleeCombatVfx.LobApexLift":
        "presentation: bomb-toss arc height in pixels.",
    # The element indicator ([USER], 2026-09-01: "instead of saying 'applies
    # pyro' - maybe make it a card indicator as well to remove text overhead").
    # Both numbers are the gem's rect against the type plaque it hangs on, and
    # they are the ONLY geometry in that file -- everything else about where it
    # sits is anchors, resolved by the engine's own layout pass. The sim has no
    # card face, so there is nothing to compare by value; what the gem MEANS is
    # the element keyword, which IS mirrored (the sheet's cadence decides it)
    # and carries no constant of its own.
    "ElementBadge.Side":
        "presentation: the element gem's side in card pixels, against NCard's "
        "own 300x422 face.",
    "ElementBadge.Gap":
        "presentation: pixels between the gem's right edge and the type "
        "plaque's left, so the pair reads as one row.",
    "KleeCombatVfx.LobDuration":
        "presentation: bomb-toss animation length in seconds.",
    "KleeCombatVfx.MaxConcurrentPops":
        "presentation: how many pop effects may overlap before they are "
        "dropped. A frame-rate guard, not a rule -- the sim resolves every "
        "detonation regardless of what is drawn.",
    # RibbonFullWidth and RibbonVisualSpan retired with D7 (salon UI sprint,
    # 2026-07-28): the ribbon no longer has a display span at all. A segment
    # is one TURN of upkeep at the current stage, which is a derived quantity
    # (members x TickEncoreCost), so the only constants left are the count of
    # segment NODES and the geometry they sit in.
    "SalonVisualsBridge.RunwaySegments":
        "presentation: how many runway segments the ribbon can draw before it "
        "shows the overflow cue. A node count, not a rule -- Encore is "
        "uncapped, so no sim number corresponds and a sixth turn of runway "
        "is real whether or not it is drawn.",
    "SalonVisualsBridge.SceneSlots":
        "presentation: how many slot nodes salon_stage.tscn ships. The RULE "
        "is SalonConstants.MemberSlots plus the cap-raise power, which is "
        "mirrored; this is the ceiling on what the scene can draw.",
    "SalonVisualsBridge.SpriteScaleMax":
        "presentation: the largest scale the member art is drawn at, half the "
        "144px master. A rendering ratio; the sim has no sprites.",
    "SalonVisualsBridge.SlotHalfSpan":
        "presentation: how far from centre a slot may sit, in pixels, before "
        "it overhangs the stage arc.",
    "SalonVisualsBridge.SlotSpacingMax":
        "presentation: the shipped three-slot pitch in pixels, kept as the "
        "maximum gap so a cap raise tightens the row instead of widening it.",
    # EB-53/N1, the end-of-turn attribution docket. The whole widget is a
    # READ: every number it prints comes from the accessor the resolution
    # itself calls (KurageSummonPower.PulseDamage, KitBurstConstants.*,
    # CompanionConstants.*), and those are classified above where they live.
    # What is left here is geometry, and geometry has no sim counterpart --
    # the same classification the two sibling bridges carry.
    "TurnEndPreviewBridge.SceneSlots":
        "presentation: how many slot nodes shared/turn_end_docket.tscn ships. "
        "The RULE is the length of TurnEndAttribution.Order, which IS the "
        "sim's player_turn_end_triggers sequence; this is the ceiling on what "
        "the scene can draw, and the bridge logs the excess rather than "
        "hiding it.",
    "TurnEndPreviewBridge.SlotSpacing":
        "presentation: docket slot pitch in pixels.",
    "TurnEndPreviewBridge.SpriteScaleMax":
        "presentation: the largest scale a docket entity is drawn at. A "
        "rendering ratio; the sim has no sprites.",
}

CLASS_RE = re.compile(
    r"^\s*(?:public|internal)\s+(?:static\s+|sealed\s+|abstract\s+|partial\s+)*"
    r"(?:class|record|struct)\s+(\w+)")
# Non-integer balance numbers count too. The gate shipped int-only, and the
# docstring's promise ("every balance number in the mod lives twice") quietly
# did not cover them -- eight constants were escaping when this was widened
# during the §4.7 shop sprint, and they were not marginal ones: the Vaporize
# and Melt amplifier multipliers, AMP_STACK_LIMIT, Frozen's damage multiplier,
# Furina's Fanfare decay fraction, the Salon dry multiplier and the Spotlight
# Guest Cast multiplier. Every one of those is a headline tuning number, and a
# sim-side retune of any of them would have drifted silently -- the exact
# failure this file exists to prevent.
#
# `private` is included for the same reason. Visibility is a C# concern; a
# balance number is a balance number whether or not another class can read it.
CONST_RE = re.compile(
    r"^\s*(?:public|internal|private)\s+const\s+"
    r"(?:int|float|double|decimal)\s+(\w+)\s*=\s*([^;]+);")

# C# numeric literal suffixes (1.5m, 0.875f, 12L) -- stripped before parsing.
NUM_SUFFIX_RE = re.compile(r"^([-+0-9.eE]+)[mMfFdDlLuU]?$")

# Floating-point mirrors compare within this tolerance rather than exactly:
# 0.875f round-trips through binary32 and will not equal Python's 0.875.
FLOAT_TOLERANCE = 1e-6


def parse_number(raw: str) -> float | None:
    """A C# numeric literal as a Python number, or None if it is not one."""
    m = NUM_SUFFIX_RE.match(raw.strip())
    if m is None:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def collect() -> dict[str, tuple[str, Path]]:
    """Every declared numeric `const` in the mod, keyed Class.Member.

    The enclosing class is the most recent class declaration above the line.
    That is a lexical approximation rather than a parse, and it is exact for
    this codebase because constant blocks are always declared at the top of
    their own class; a nested-class constant would need a real parse, and the
    duplicate-key guard below is what would catch the confusion.
    """
    found: dict[str, tuple[str, Path]] = {}
    for path in sorted(CS_ROOT.rglob("*.cs")):
        cls = None
        for line in path.read_text(encoding="utf-8").splitlines():
            if (m := CLASS_RE.match(line)) is not None:
                cls = m.group(1)
                continue
            if (m := CONST_RE.match(line)) is None:
                continue
            key = f"{cls}.{m.group(1)}"
            if key in found:
                raise SystemExit(
                    f"FINDING: duplicate constant key {key} "
                    f"({found[key][1]} and {path}); the lint's class "
                    "attribution is ambiguous and must be fixed before it can "
                    "be trusted.")
            found[key] = (m.group(2).strip(), path)
    return found


# --------------------------------------------------------------------------
# INVARIANTS: ratified RELATIONSHIPS between two numbers.
#
# MIRRORED compares a C# number against a sim number BY VALUE. That cannot
# express "this number is twice that one" -- and a ratio that a [USER] ruling
# made permanent is exactly the kind of thing that decays silently, because
# both halves keep passing their own checks while the relationship between
# them quietly stops being true.
#
# Each entry is (label, left, right, reason). The check is left == right.
# --------------------------------------------------------------------------
def _invariants() -> list[tuple[str, float, float, str]]:
    return [
        (
            "PearlOfInsight.charge_per_exhaust == 2 x CHARGE_PER_EXHAUST",
            _ancient_hook("touch_of_orobas_kokomi", "charge_per_exhaust"),
            2 * C.CHARGE_PER_EXHAUST,
            "RATIFIED INVARIANT (R190, 2026-08-13): Pearl of Insight's "
            "upgraded rates are exactly 2x their base rates in BOTH engines, "
            "permanently. The sim's copy is a LITERAL in "
            "tier05/content/relics.yaml, so nothing but this check ties it to "
            "the base constant -- bump CHARGE_PER_EXHAUST alone (EB-74's "
            "lever-2 candidate B is the live example) and the relic keeps "
            "granting the OLD doubled rate while the tooltip and the C# "
            "literal say otherwise. Move all of them, or move none.",
        ),
        (
            "PearlOfInsight.burst_per_exhaust == 2 x KOKOMI_BURST_PER_EXHAUST",
            _ancient_hook("touch_of_orobas_kokomi", "burst_per_exhaust"),
            2 * C.KOKOMI_BURST_PER_EXHAUST,
            "Same ratified invariant, other currency. Note A9's warning "
            "applies to the base pair independently: CHARGE_PER_EXHAUST and "
            "KOKOMI_BURST_PER_EXHAUST are one wage in two currencies and move "
            "together or the reason moves with them. This check is about the "
            "UPGRADE's ratio, not about that pairing.",
        ),
    ]


def main() -> int:
    findings: list[str] = []
    found = collect()

    for label, got, want, reason in _invariants():
        if abs(float(got) - float(want)) > FLOAT_TOLERANCE:
            findings.append(
                f"INVARIANT BROKEN -- {label}: reads {got}, requires {want}. "
                f"{reason}")

    if not found:
        print("FINDING: no numeric `const` found -- the lint's pattern or "
              "the source layout changed, and a lint that passes because it "
              "read nothing is not a gate.")
        return 1

    for key, (raw, path) in sorted(found.items()):
        rel = path.relative_to(REPO)
        if key in UNMIRRORED:
            continue
        if key not in MIRRORED:
            findings.append(
                f"{rel}: {key} = {raw} is classified nowhere. Add it to "
                f"MIRRORED with the tier0 value it copies, or to UNMIRRORED "
                f"with the reason the sim has no counterpart.")
            continue
        got = parse_number(raw)
        if got is None:
            findings.append(
                f"{rel}: {key} = {raw} is in MIRRORED but is not a numeric "
                f"literal, so its value cannot be compared. Make it a literal "
                f"or move it to UNMIRRORED as derived.")
            continue
        want = float(MIRRORED[key])
        if abs(got - want) > FLOAT_TOLERANCE:
            findings.append(
                f"{rel}: {key} = {raw}, but tier0 says {MIRRORED[key]}. The "
                f"sim is the source of truth: the mod would play to a number "
                f"no simulation endorsed. Mirror it, or re-measure and move "
                f"both.")

    for key in sorted(MIRRORED):
        if key not in found:
            findings.append(
                f"MIRRORED lists {key}, but no such constant exists in the "
                f"mod. It was renamed or deleted -- update the table so the "
                f"gate keeps covering what it claims to cover.")
    for key in sorted(UNMIRRORED):
        if key not in found:
            findings.append(
                f"UNMIRRORED lists {key}, but no such constant exists in the "
                f"mod. Drop the entry.")

    for finding in findings:
        print(f"FINDING: {finding}")
    if findings:
        return 1
    print(f"constant parity: OK ({len(MIRRORED)} mirrored, "
          f"{len(UNMIRRORED)} declared unmirrored, "
          f"{len(_invariants())} ratified invariants held)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
