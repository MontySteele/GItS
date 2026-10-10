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

from tier0 import constants as C  # noqa: E402

CS_ROOT = REPO / "klee-mod" / "KleeCode"


def _stage(name: str):
    """A number out of the Furina STAGE's quarantined engine module.

    The brief's own decision: the sim keeps these
    in `tier0/engine/furina_stage.py` rather than in `constants.py`, so that a
    prototype moves neither the constant census nor the world stamp. Mirroring
    is a different question from stamping -- the C# arm PLAYS these numbers and
    its keyword tips PRINT them -- and reading them from where the sim keeps
    them is what lets both facts be true at once.
    """
    from tier0.engine import furina_stage as _fs
    return getattr(_fs, name)


def _varka(name: str):
    """A number out of VARKA's Oath module, `_stage`'s case one character
    over: the sim keeps his rule numbers in `tier0/engine/varka_oath.py`
    rather than in `constants.py`, so the prototype moves neither the constant
    census nor the world stamp, and the C# `VarkaLaw` is mirrored against
    them where they live."""
    from tier0.engine import varka_oath as _vo
    return getattr(_vo, name)


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
    # Klee's upgraded starter (Touch of Orobas -> Dodoco Tales): the opening
    # bank, live again under the current kit (Klee finish-line batch,
    # 2026-10-03).
    "ExplosiveFrags.OpeningSparks":
        _ancient_hook("touch_of_orobas_klee", "combat_start_spark"),
    # Shared elemental table (tier0/constants.py, reaction block).
    "ReactionConstants.AuraDurationTurns": C.AURA_DURATION_TURNS,
    "ReactionConstants.OverloadSplash": C.OVERLOAD_SPLASH,
    "ReactionConstants.OverloadWeak": C.OVERLOAD_WEAK,
    "ReactionConstants.SuperconductVuln": C.SUPERCONDUCT_VULN,
    "ReactionConstants.ElectroChargedDot": C.ELECTROCHARGED_DOT,
    "ReactionConstants.CrystallizeBlock": C.CRYSTALLIZE_BLOCK,
    "ReactionConstants.SwirlDamage": C.SWIRL_DAMAGE,     # the element port, sec.4 A
    "ReactionConstants.ShatterDamage": C.SHATTER_DAMAGE,
    "ReactionConstants.FrozenBossVuln": C.FROZEN_BOSS_VULN,
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
    # New to the map on 2026-08-13 (EB-97), and the reason it is here is the
    # gate's own blind spot: the fraction was an inline `/ 2` in FanfareCap,
    # so it appeared in neither MIRRORED nor UNMIRRORED and the lint's
    # "every balance number in the mod lives twice" promise did not cover
    # the Furina identity record's headline "%maxHP". Naming it on the C# side is what makes
    # it visible here.

    # Klee.
    "CompanionConstants.MasqueBondBlock": C.MASQUE_BOND_BLOCK,
    "CompanionBanner.FeaturedSlots": C.BANNER_FEATURED_SLOTS,

    # Furina.
    # RE-CLASSIFIED by the Fanfare rework (2026-07-28). FanfarePerEncoreGained
    # and both FanfareFloorPerPower* left this map because they left BOTH
    # engines -- a retired constant must be deleted from the map, never left
    # pointing at a deleted C.* (which raises) and never quietly stubbed to a
    # literal (which would assert parity between two things that no longer
    # exist). FanfarePerEncoreAbsorbed is new on both sides and joins here.

    # Kokomi.
    # The Kurage's memory (R213 B / EB-147 -- the C# rule lives
    # under klee-mod/KleeCode/Powers/Prototype and is Compile Remove'd out of a
    # release build). Quarantined is not exempt: a prototype arm measured on a
    # number the sim never chose is exactly the failure this lint exists for,
    # and these three are the only numeric constants the rule has. Spec:
    # review/ruled/kokomi-kurage-memory-2026-08-29.md sec.11.4.
    # The Klee overhaul, slice one (R213 B -- the rules engine
    # lives under klee-mod/KleeCode/Powers/Prototype and is Compile Remove'd
    # out of a release build). Quarantined is not exempt, for the same reason
    # the Kurage's three above are not: these four numbers ARE the rules
    # (`review/active/klee-brief-2026-09-01.md` sec.3), and a prototype played
    # on a number the sim never declared is exactly this lint's failure. They
    # are placeholders and not claims -- but they are the placeholders both
    # sides have to agree on.
    "KleeOverhaulLaw.BombGrowth": C.KLEE_OVERHAUL_BOMB_GROWTH,
    "KleeOverhaulLaw.AliceMultiplier": C.KLEE_OVERHAUL_ALICE_MULTIPLIER,
    "KleeOverhaulLaw.SparkPerExplosion": C.KLEE_OVERHAUL_SPARK_PER_EXPLOSION,
    # SIX now: R242 pick 1 gave rule 4 a second number, the opening bank, and
    # R248 (`EB-344`) a third -- the Spark Grounded pays on a held turn, which
    # is the one turn rule 4's per-explosion rate mints nothing.
    "KleeOverhaulLaw.OpeningSpark": C.KLEE_OVERHAUL_OPENING_SPARK,
    "KleeOverhaulLaw.GroundedSpark": C.KLEE_OVERHAUL_GROUNDED_SPARK,
    "KleeOverhaulLaw.DamageReportSpark": C.KLEE_OVERHAUL_DAMAGE_REPORT_SPARK,
    "KleeOverhaulLaw.SparkSeedFloors": C.KLEE_OVERHAUL_SPARK_SEED_FLOORS,
    # R276, Wait For It...'s printed payout, on the same terms.
    "WaitForItPower.ReactionEnergy": C.KLEE_OVERHAUL_WAIT_FOR_IT_ENERGY,
    # THE MONDSTADT COMPANION OVERHAUL (`C.COMPANION_OVERHAUL`).
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
    "CompanionOverhaulLaw.LightningRoseDamage": C.MC_LIGHTNING_ROSE_DMG,
    "CompanionOverhaulLaw.LightningRoseVulnerable": C.MC_LIGHTNING_ROSE_VULN,
    # The same arm's SECOND WAVE -- the seven numbers its thirteen new rows
    # hand to a POWER rather than print on a card. Same terms again.
    "CompanionOverhaulLaw.ShowerDamage": C.MC_SHOWER_DMG,
    "CompanionOverhaulLaw.LightningFangDamage": C.MC_LIGHTNING_FANG_BONUS,
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
    # KLEE'S COVEN PERSONALS (R236), same flag and same terms:
    # three numbers a POWER carries, mirrored by value because both engines
    # play these four rows.
    "CompanionCovenLaw.HeraldBlock": C.CVN_HERALD_BLOCK,
    "CompanionCovenLaw.HeraldApplications": C.CVN_HERALD_APPLICATIONS,
    # THE KOKOMI OVERHAUL (`C.KOKOMI_OVERHAUL`). Same terms again
    # and for the same reason: quarantined is not exempt. Draft 6 left the arm
    # with exactly ONE rule number -- Tamakushi Casket's Hydro strike, printed
    # on the relic and on no card -- because its rules are structural and every
    # other figure is a CARD's, on its own row. The six draft 2 declared went
    # with the pulse, the Garment and the Tide.
    # THE CASKET PASS (2026-09-28) retired the strike; the relic now counts
    # carried-out Plans and Open the Casket turns the count into Strength.
    "KokomiOverhaulLaw.CasketPerPlan": C.KOKOMI_OVERHAUL_CASKET_PER_PLAN,
    "KokomiOverhaulLaw.CasketStrengthPerPoint":
        C.KOKOMI_OVERHAUL_CASKET_STRENGTH_PER_POINT,
    # THE EXPANSION, BATCH ONE (2026-09-29): The Long Game's threshold.
    "KokomiOverhaulLaw.LongGameWaiting":
        C.KOKOMI_EXPANSION_LONG_GAME_WAITING,
    # THE STATUS BATCH (2026-10-01): Abyssal Salvage+'s Block per stack.
    "AbyssalSalvagePlusPower.BlockPerStack":
        C.KOKOMI_ABYSSAL_SALVAGE_PLUS_BLOCK,
    # POOL COMPLETION (2026-10-01): the hand limit Kurage School, Casting
    # Agent and Watatsumi Resistance stop at.
    "KokomiPoolCompletion.MaxHandSize": C.MAX_HAND_SIZE,
    # THE FURINA STAGE (`furina_stage.FURINA_STAGE`; `EB-723` /
    # `EB-724` / `EB-725`, R269). Same terms as every arm above and for the
    # same reason -- quarantined is not exempt. These NINE numbers ARE the
    # brief's sec.3 rules: the seat count, the relic's opening bar, what a
    # summon arrives at, the lead's regen, the starter Refill, the three acts
    # and the fade's threshold (draft 3, 2026-09-25, which also retired the
    # two bow numbers: a Bow is the act once more). The sim declared them
    # first (`EB-724` is the sim engine and `EB-725` the C#), and the C# side
    # reads them for its keyword tips, so a pair that drifted would print a
    # retired number under a card the seat is grading.
    "FurinaStageLaw.Seats": _stage("SEATS"),
    # THE SALON'S TAB (2026-10-05, review/active/furina-research-proposal-
    # 2026-10-05.md sec.16): the Singer's Repay (the starter and its Orobas
    # upgrade) and the four guests' lines and acts. The v2 Stage's numbers
    # (the trio, the stars' prices, the Bow's Fanfare, Rehearsal, Sold Out,
    # Casting Agent, Pneuma) retired with it.
    "FurinaStageLaw.SingerRepay": _stage("SINGER_REPAY"),
    "FurinaStageLaw.SingerRepayUpgraded": _stage("SINGER_REPAY_UPGRADED"),
    "FurinaStageLaw.CharlotteActRepay": _stage("CHARLOTTE_ACT_REPAY"),
    "FurinaStageLaw.CharlotteLineDraw": _stage("CHARLOTTE_LINE_DRAW"),
    "FurinaStageLaw.WriothesleyActDamage": _stage("WRIOTHESLEY_ACT_DAMAGE"),
    "FurinaStageLaw.LynetteActDamage": _stage("LYNETTE_ACT_DAMAGE"),
    "FurinaStageLaw.ClorindeActDamage": _stage("CLORINDE_ACT_DAMAGE"),
    "FurinaStageLaw.ClorindePerRepay": _stage("CLORINDE_PER_REPAY"),
    # THE POOL TO 39 (review/active/furina-pool-40-2026-10-05.md sec.3): the
    # three new guests' lines and acts, A Five-Century Act's line and
    # Fountain of Lucine's three turns.
    "FurinaStageLaw.LyneyLineDrop": _stage("LYNEY_LINE_DROP"),
    "FurinaStageLaw.LyneyActDrain": _stage("LYNEY_ACT_DRAIN"),
    "FurinaStageLaw.LyneyActDamage": _stage("LYNEY_ACT_DAMAGE"),
    "FurinaStageLaw.SigewinneActRepay": _stage("SIGEWINNE_ACT_REPAY"),
    "FurinaStageLaw.ChevreuseActDamage": _stage("CHEVREUSE_ACT_DAMAGE"),
    "FurinaStageLaw.ChevreuseLineVulnerable": _stage("CHEVREUSE_LINE_VULNERABLE"),
    "FurinaStageLaw.DrainFloor": _stage("DRAIN_FLOOR"),
    "FurinaStageLaw.FountainTurns": _stage("FOUNTAIN_TURNS"),
    # THE POOL TO 75 (review/active/furina-pool-growth-2026-10-09.md, ruled
    # 2026-10-09): the guests' upgraded lines and acts (sec.3), the four new
    # guests and the new Powers' numbers (sec.5).
    "FurinaStageLaw.CharlotteActRepayUpgraded": _stage("CHARLOTTE_ACT_REPAY_UPGRADED"),
    "FurinaStageLaw.SigewinneActRepayUpgraded": _stage("SIGEWINNE_ACT_REPAY_UPGRADED"),
    "FurinaStageLaw.WriothesleyActDamageUpgraded": _stage("WRIOTHESLEY_ACT_DAMAGE_UPGRADED"),
    "FurinaStageLaw.LyneyActDamageUpgraded": _stage("LYNEY_ACT_DAMAGE_UPGRADED"),
    "FurinaStageLaw.LynetteActDamageUpgraded": _stage("LYNETTE_ACT_DAMAGE_UPGRADED"),
    "FurinaStageLaw.ChevreuseLineWeakUpgraded": _stage("CHEVREUSE_LINE_WEAK_UPGRADED"),
    "FurinaStageLaw.ClorindeActDamageUpgraded": _stage("CLORINDE_ACT_DAMAGE_UPGRADED"),
    "FurinaStageLaw.FreminetActDamage": _stage("FREMINET_ACT_DAMAGE"),
    "FurinaStageLaw.FreminetActDamageUpgraded": _stage("FREMINET_ACT_DAMAGE_UPGRADED"),
    # The pool-75 round's card numbers and the Drain line rule (ruled
    # 2026-10-09): Freminet's act's Block and the line's quarter of Max HP.
    "FurinaStageLaw.FreminetActBlock": _stage("FREMINET_ACT_BLOCK"),
    "FurinaStageLaw.FreminetActBlockUpgraded": _stage("FREMINET_ACT_BLOCK_UPGRADED"),
    "FurinaStageLaw.LineMaxHpDivisor": _stage("LINE_MAX_HP_DIVISOR"),
    "FurinaStageLaw.NaviaLineDiscount": _stage("NAVIA_LINE_DISCOUNT"),
    "FurinaStageLaw.NaviaLineDiscountUpgraded": _stage("NAVIA_LINE_DISCOUNT_UPGRADED"),
    "FurinaStageLaw.NeuvilletteHydroBonus": _stage("NEUVILLETTE_HYDRO_BONUS"),
    "FurinaStageLaw.NeuvilletteHydroBonusUpgraded": _stage("NEUVILLETTE_HYDRO_BONUS_UPGRADED"),
    "FurinaStageLaw.EscoffierActDamage": _stage("ESCOFFIER_ACT_DAMAGE"),
    "FurinaStageLaw.EscoffierActDamageUpgraded": _stage("ESCOFFIER_ACT_DAMAGE_UPGRADED"),
    "FurinaStageLaw.EscoffierLineRepay": _stage("ESCOFFIER_LINE_REPAY"),
    "FurinaStageLaw.EnsembleSeats": _stage("ENSEMBLE_SEATS"),
    "FurinaStageLaw.ShowstopperSpend": _stage("SHOWSTOPPER_SPEND"),
    "FurinaStageLaw.NearLine": _stage("NEAR_LINE"),
    # High Stakes' divisor (the Spend round, 2026-10-10).
    "FurinaStageLaw.HighStakesEvery": _stage("HIGH_STAKES_EVERY"),
    "FurinaStageLaw.HighStakesEveryUpgraded": _stage("HIGH_STAKES_EVERY_UPGRADED"),
    "FurinaStageLaw.HymnThreshold": _stage("HYMN_THRESHOLD"),
    "FurinaStageLaw.PrimaDonnaFanfare": _stage("PRIMA_DONNA_FANFARE"),
    "FurinaStageLaw.ReginaDrain": _stage("REGINA_DRAIN"),
    "FurinaStageLaw.StarTurnFanfarePer": _stage("STAR_TURN_FANFARE_PER"),
    # VARKA, THE OATH REWORK (review/active/varka-paper-kit-2026-09-28.md,
    # ruled 2026-09-29): the Swirl payout of each current element. (Stormward
    # Stance's Oath bar left in Varka round 3, 2026-10-10.) Sim twins in
    # `tier0/engine/varka_oath.py`.
    "VarkaLaw.SwirlPyroDamage": _varka("SWIRL_PYRO_DAMAGE"),
    "VarkaLaw.SwirlHydroBlock": _varka("SWIRL_HYDRO_BLOCK"),
    "VarkaLaw.SwirlCryoVulnerable": _varka("SWIRL_CRYO_VULNERABLE"),
    "VarkaLaw.SwirlElectroDamageAll": _varka("SWIRL_ELECTRO_DAMAGE_ALL"),
    # THE EXPANSION (2026-10-01): Eye of Stormterror's Swirls a turn.
    "VarkaLaw.EyeOfStormterrorSwirls": _varka("EYE_OF_STORMTERROR_SWIRLS"),
    # THE REBALANCE (2026-10-03): Whisper of Water's later turns.
    "VarkaLaw.EchoBlockTurns": _varka("ECHO_BLOCK_TURNS"),
}

# --------------------------------------------------------------------------
# UNMIRRORED: C# constants with no tier0 counterpart, each with its reason.
#
# "The sim does not model this" is a legitimate answer and always has been --
# relics, Ancients and the run layer are game-side content. What is not
# legitimate is leaving the question unanswered.
# --------------------------------------------------------------------------

#: The Klee and Furina arms' own relics and potions, and the two Ancient
#: repairs (review/active/relics-potions-klee-furina-2026-09-27.md, ruled
#: 2026-09-27). C# first: the arms are Prototype, the sim is brought up at
#: Balance, and tier 0.5 models no relic or potion of either arm yet.
_ARM_ITEMS_REASON = (
    "THE ARMS' OWN RELICS AND POTIONS (review/active/relics-potions-klee-"
    "furina-2026-09-27.md). A printed number on a Prototype-stage relic or "
    "potion of the Klee arm or the Stage, built C# first "
    "(operations/prototype.md); no sim twin exists until Balance.")

#: Varka's own relics and potions (review/active/varka-expansion-2026-10-01.md
#: sec.4), built C# first like the arms' above: tier0's Varka twin
#: (`tier0/engine/varka_oath.py`) models no relic but the Fang.
_VARKA_ITEMS_REASON = (
    "VARKA'S OWN RELICS AND POTIONS (review/active/varka-expansion-2026-10-01.md "
    "sec.4). A printed number on a Prototype-stage relic or potion of his, "
    "built C# first (operations/prototype.md); no sim twin exists until "
    "Balance.")

UNMIRRORED: dict[str, str] = {
    "AlicesGuidebook.Growth": _ARM_ITEMS_REASON,
    "BottledResolve.Oath": _VARKA_ITEMS_REASON,
    "KnightsCommission.Oath": _VARKA_ITEMS_REASON,
    "WindblumeGarland.Block": _VARKA_ITEMS_REASON,
    "BlastingPowder.Growth": _ARM_ITEMS_REASON,
    "BottledApplause.Fanfare": _ARM_ITEMS_REASON,
    "BottledSparks.Sparks": _ARM_ITEMS_REASON,
    "CloverCharm.Block": _ARM_ITEMS_REASON,
    "DodocoArmy.MineSize": _ARM_ITEMS_REASON,
    "DodocoCharm.Bonus": _ARM_ITEMS_REASON,
    "ExplosiveFrags.FirstExplosionSparks": _ARM_ITEMS_REASON,
    "FireworksStand.Energy": _ARM_ITEMS_REASON,
    "FireworksStand.Threshold": _ARM_ITEMS_REASON,
    "OperaGlasses.Fanfare": _ARM_ITEMS_REASON,
    "GrandTheaterProgram.Fanfare": _ARM_ITEMS_REASON,
    "WatatsumiCasket.WatatsumiOpeningCount":
        "THE KOKOMI OVERHAUL'S TOUCH OF OROBAS UPGRADE (2026-09-30, main-"
        "session design from the co-op playtest). A Prototype-stage relic "
        "number built C# first; tier05 has no Orobas row for the arm, and "
        "the sim twin lands at Balance.",
    "ShrapnelPower.Shred":
        "THE CO-OP SET, SECOND BATCH (review/active/coop-concepts-2026-09-27.md). "
        "Shrapnel's printed '50% more': the multiplier another player's Attack "
        "takes on an enemy holding Klee's Mine. Only ANOTHER player's hit can "
        "take it, and tier 0 seats one player (`tier0/engine/coop.py`), so the "
        "sim has no hit this number could ever apply to and no counterpart.",
    "PunchOffMirror.MaxHitSparksPerVisit":
        "`EB-769`. AN ALLOCATION BOUND on a decoration, not balance: how many "
        "`NHitSparkVfx` nodes one visit to the Punch-Off may add to the combat "
        "VFX container. The base event spawns one per swing paced only by "
        "`Cmd.Wait(1.2f)`, which is fine at the player's own speed and "
        "unbounded once a harness collapses the wait -- the deploy proofs of "
        "2026-09-15 measured 34,501 `Element limit reached at _allocate_rid` "
        "and a 2.56 GB `godot.log` from this one call site. Nothing a card, a "
        "rule or a reward reads is priced in it: the anims, "
        "`vfx_attack_blunt`, the waits, the options and the gold roll are all "
        "untouched, and a player at the game's own speed never reaches the "
        "cap. tier0 draws nothing and has no counterpart.",
    "PunchOffMirror.MaxBluntVfxPerVisit":
        "`EB-769`, the sibling of the line above and the same kind of number: "
        "how many `vfx/vfx_attack_blunt` scenes one visit to the Punch-Off may "
        "instantiate. `VfxCmd.PlayOnCreatureCenter` reaches "
        "`PackedScene.Instantiate` through `VfxCmd.PlayVfx`, so it is exactly "
        "as unbounded as the spark was once the 1.2 s wait collapses -- with "
        "the sparks capped and absent from every log, the proofs of 2026-09-16 "
        "found the process still dying under `FastMode = Instant` with "
        "`PackedScene.Instantiate` at the top of the backtrace. Its own "
        "constant rather than a shared one because the blunt impact is the "
        "blow a player reads and the spark is decoration on top of it. Nothing "
        "a card, a rule or a reward is priced in it, and tier0 has no "
        "counterpart.",
    "PunchOffMirror.MaxSwingsUnderInstant":
        "`EB-769`. A LOOP BOUND on a decoration, and only under "
        "`FastModeType.Instant`. `Cmd.Wait` creates no timer at all at that "
        "setting, so every `await` in the punching loop completes "
        "synchronously and the loop never yields; capping what a pass "
        "allocates makes each pass cheap but does not make a spinning loop "
        "stop. At `Normal` and `Fast` -- every speed a person plays at -- the "
        "constructs punch until the player leaves the room exactly as the base "
        "event has them do, so this number cannot be reached by play. tier0 "
        "has no event loop and no counterpart.",
    "ModdedPlayerDeathSeam.FallbackDeathAnimLength":
        "`EB-159`. A PRESENTATION DURATION, not balance: how long a spine-less "
        "player body with no death clip to measure is reported to be dying for, "
        "so the death sound has room and `Hook.AfterDeath` waits something "
        "instead of nothing. The number is one of the mod's own authored clips "
        "(`pck-src/klee/model/combat.tscn`, `Animation_death` `length = 1.0`), "
        "and a body that HAS a clip is measured rather than given this. tier0 "
        "has no animations, no clock the player sees and no counterpart.",
    "ModdedPlayerDeathSeam.MaxDeathAnimLength":
        "`EB-159`. THE BASE GAME'S OWN CEILING, copied from it rather than "
        "chosen here: `NCreature.StartDeathAnim` returns `Mathf.Min(a, 30f)` "
        "(0.111.0 decompile, `NCreature.cs:945`), and the seam that fills in "
        "the length the spine gate skipped keeps the same cap so it can never "
        "report a longer death than the base could. tier0 has no counterpart.",
    "ModdedDeathWaitSeam.MaxDeathWait":
        "`EB-797`. THE BASE GAME'S OWN CEILING AGAIN, copied rather than "
        "chosen: the private `NCreature.AnimDie` waits "
        "`Math.Min(GetCurrentAnimationTimeRemaining() + 0.5f, 20f)` (0.111.0 "
        "decompile, `NCreature.cs:1006-1010`), and the seam that reports a "
        "spine-less body's remaining keeps the same cap so it can never hand "
        "the engine a longer wait than the base could reach. The engine still "
        "applies its own pad and its own ceiling on top. tier0 has no "
        "animations, no clock the player sees and no counterpart.",
    "IdleDesync.MinSpeedScale":
        "`EB-816`. A PRESENTATION BAND, not balance: the slowest an individual "
        "dressed enemy's idle may run so that a pack of identical bodies does "
        "not read as one metronome ([USER] look, 2026-09-17). It scales a clip "
        "the eye sees and nothing else -- no intent, no number, no timing any "
        "rule reads (the death seams read the clip's own length and the tree's "
        "own remaining, so both follow it). tier0 has no animations, no clock "
        "the player sees and no counterpart.",
    "IdleDesync.MaxSpeedScale":
        "`EB-816`. The other end of the same presentation band, and UNMIRRORED "
        "for the same reason as `IdleDesync.MinSpeedScale` directly above.",
    "KleeOverhaulLedger.LineCap":
        "`EB-318`. A MEMORY BOUND on a diagnostic, not balance: how many lines the arm's per-combat log holds before it drops the oldest. Nothing a card, a rule or a face reads is priced in it -- the lines are prose written for a run record and mirrored to `godot.log`, and the only thing the number can change is how far back a long fight's log reaches. tier0 keeps its own events in `CombatState.log`, which is a per-run list with no cap and no counterpart to this.",
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
    "RosterArt.CacheCapacity":
        "`EB-158`. A MEMORY BOUND, not balance: how many decoded card "
        "portraits the LRU in `KleeArt.cs` holds before it evicts the least "
        "recently used one. Sized off what the UI can want AT ONCE -- a "
        "browsed end-of-run deck alongside a hand, a shop row and a reward "
        "screen -- and the only thing it can change is whether a re-shown "
        "card costs one PNG decode. tier0 draws nothing, loads no textures "
        "and has no counterpart.",
    "RosterArt.PortraitBytes":
        "`EB-158`. DERIVED, and read by no code: `PortraitWidth * "
        "PortraitHeight * 4` is the decoded RGBA8 size of one portrait, "
        "written down so the arithmetic behind `RosterArt.CacheCapacity` is "
        "checkable instead of asserted in a comment. Both of its inputs are "
        "UNMIRRORED directly above, for the same reason.",
    "NonFiniteCardGuard.MaxTrailTravelPx":
        "`EB-292`. A SCENE BOUND, not balance: how far a followed node may "
        "travel in one frame before the base game's card-trail gap-fill loop "
        "is refused. That loop walks the gap at a fixed 48 px and is bounded "
        "by the travel, so an infinite -- or merely enormous -- position asks "
        "it for unbounded work and takes the process's memory. 100,000 px is "
        "far past anything a real flight produces on a 1920x1080 design "
        "resolution. It touches no card, no meter and no number the sim can "
        "see: tier0 draws nothing.",
    "NonFiniteCardGuard.MaxTrackedNodes":
        "`EB-292`. A LOG BOUND, not balance: how many nodes the guard's "
        "rate limiter remembers before it forgets the lot. Every card play "
        "builds a fresh trail node, so the limiter's keys are transient and "
        "the map needs a bound of its own -- the file's whole subject is an "
        "unbounded allocation, and a diagnostic that leaked would be the same "
        "defect in a smaller font. Forgetting costs at most one extra log "
        "line. The sim writes no godot.log and has nothing to limit.",
    "NonFiniteCardGuard.ExtrapolationReportT":
        "`EB-292`. A CURVE DOMAIN, not balance: how far past the end of its "
        "own Bezier a card flight has to run before the clamp SAYS so in "
        "godot.log. The clamp itself bites at t = 1, where the quadratic stops "
        "interpolating and starts extrapolating as t^2; the last iteration of "
        "`NCardFlyVfx.PlayAnim`'s loop overshoots a little by construction, so "
        "the reporting threshold sits above the worst ordinary frame and below "
        "a stall. It is a parameter of the base game's animation curve. The "
        "sim animates nothing and has no counterpart.",
    "NonFiniteCardGuard.MaxNodesScanned":
        "`EB-292`. A WALK BUDGET, not balance: how many scene nodes the "
        "clamp's report visits looking for the flight that owns the curve it "
        "caught. The clamp is a prefix on a static helper and has no node, so "
        "the card is found by matching the flight's own start and end; the "
        "walk is bounded because it runs on a frame the engine is already "
        "struggling with. The sim has no scene tree.",
    "RewardRowProbe.SettleSeconds":
        "A UI TIMER, not balance: how long the card reward row probe waits "
        "before measuring the row, chosen to land after the base screen's "
        "0.5 s placement tween. It only decides when a godot.log line is "
        "written. The sim has no screen.",
    # THE FURINA STAGE ARM'S ELEVEN ARE NOT HERE, and their absence is the
    # `EB-723` / `EB-725` reconciliation. This branch declared them UNMIRRORED
    # on the reading that the arm was C#-first; the sim leg had in fact
    # declared them FIRST, in `tier0/engine/furina_stage.py`, and ships the
    # mirrored `FurinaStageLaw.cs` beside it. So the C# copy was deleted rather
    # than reconciled -- two declarations of one number is exactly the drift
    # this gate exists to refuse -- and the MIRRORED table above carries the
    # pairs.
    # The placement pass's two, which are a different kind of number entirely:
    # scene offsets. The Y is the BASE GAME's own, lifted out of
    # `NCombatRoom.AddCreature`'s pet layout (`owner.Y + 10`); the X is no
    # longer the engine's `owner.X - 20`, which stood the back performer on
    # Furina's legs (2026-09-26 smoke), but a floor gap measured out from her
    # hitbox edge, Osty's reference point. The sim draws nothing.
    "FurinaStagePlacement.Gap":
        "A SCENE OFFSET, not balance: the floor between Furina's hitbox edge "
        "and the first performer, and between every two performers, so the "
        "line stands clear of her the way Osty stands clear of the "
        "Necrobinder. The sim has no scene tree.",
    "FurinaStagePlacement.OwnerYOffset":
        "A SCENE OFFSET, not balance: the base game's own pet placement "
        "constant, lifted from `NCombatRoom.AddCreature` (`owner.Y + 10`) so "
        "a performer stands on the line the engine's own layout would give it.",
    "MeterLedger.MaxRows":
        "`EB-216`. INSTRUMENT, not balance: how many per-play ledger rows the "
        "mod keeps before dropping the oldest. It touches no game number, no "
        "card and no meter -- it is the size of a diagnostic buffer, and the "
        "sim has no ledger to size. R225 filed the ledger as instrument work "
        "that does not gate an arm; this is the only number it has.",
    "ResolutionLedger.MaxRows":
        "`EB-349` / `EB-611`. INSTRUMENT, not balance, on "
        "`MeterLedger.MaxRows`' own terms one reader over: how many resolved "
        "cards the per-turn ledger will file before it stops minting rows. It "
        "touches no game number, no card and no meter -- it is the size of a "
        "diagnostic buffer read by a PAGE rather than by a grader, so the only "
        "growth it guards against is a single pathological turn. The sim has "
        "no ledger to size.",
    "ResolutionLedger.MaxHits":
        "`EB-611`. INSTRUMENT, not balance: how many hits one resolved card "
        "will file before the row says it overflowed. The same diagnostic "
        "buffer as the row directly above, one level down, and said rather "
        "than silently truncated because a reader adding up forty lines that "
        "should be forty-three has been handed `EB-518`'s error in a new "
        "place. The sim has no ledger to size.",
    "ExplosiveFrags.SparksPerDetonation":
        "the BASE starter's rate, carried forward unchanged by the upgrade -- "
        "the doubling of this rate was rejected at the 2026-07-26 red-pen. Its "
        "sim counterpart is a literal at the detonation site in effects.py "
        "(`gain_sparks(state, 1)` under spark_on_detonation), not a named "
        "constant, so there is nothing to compare against by value. The "
        "opening windfall beside it (`OpeningSparks`) is MIRRORED above.",
    # The two PearlOfInsightRelic rates USED TO LIVE HERE, as derived
    # expressions this lint could not read. R190 ratified the 2x relationship
    # as a standing invariant and they moved to MIRRORED above, with INVARIANTS
    # below carrying the half MIRRORED cannot express. The old entry's own
    # note said this was the fix; it was taken.

    # --- surfaced by widening the lint past `int` (§4.7 shop sprint) ---
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
    # The Kurage memory card (sec.14). Every number below is SCREEN GEOMETRY or
    # a font size for a HUD element the sim has no notion of: tier0 has no
    # display at all, so there is nothing to compare by value. The affordability
    # rule the element draws IS mirrored, and it carries no constant -- it is a
    # running subtraction over prices the queue already holds.
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
    "KokomiPlanStrip.LineFontSize":
        "presentation: the Plan line / Now-line caption's font size (pick 5a).",
    "KokomiPlanStrip.MaxDrawn":
        "presentation: how many pending Plans get a picture before the column "
        "runs off the band. Not a cap on the queue -- nothing limits how many "
        "Plans she may write -- and the overflow is printed as `+N`, so the "
        "sim has nothing to compare and no rule is hiding here.",
    # The Spark counter in the energy area (`EB-621`), on the same terms. Its
    # A POSITION is deliberately not here: the element derives its placement
    # from `%EnergyCounterContainer`'s own rect at runtime rather than writing
    # a screen position down (`EB-815`). What is left is a font size, a
    # fallback square for the case where the star counter cannot be measured,
    # a margin expressed in the panel's own units, and the energy orb's
    # displacement -- the base game's own line, kept as a fallback anchor and
    # classified below. The number the badge DRAWS is `SparkPower`'s stack,
    # which is a rule and is mirrored as the Spark bank elsewhere in this file.
    "SparkCounter.FallbackSide":
        "presentation: the badge's square in pixels when `%StarCounter` "
        "reports no size yet, so the element still lands somewhere rather "
        "than collapsing to nothing.",
    "SparkCounter.CountFontSize":
        "presentation: the Spark count's font size.",
    # Furina's "Drained N" counter (the Salon's Tab, 2026-10-05): its slot in
    # the row above the energy orb, after the Fanfare gauge.
    "DrainedCounter.Slot":
        "presentation: the counter's place in the row above the energy orb "
        "(after the Fanfare gauge). The number it draws is the ledger's "
        "drained HP, which the sim keeps as `Ftd.drained`.",
    "SparkCounter.PanelMargin":
        "presentation: the gap the badge keeps from the energy panel, in the "
        "panel's own units. It is a MARGIN rather than a position -- it is "
        "added to the panel's own edge at runtime -- and the sim has no "
        "energy panel, no viewport and nothing that could overlap.",
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
    # EB-248's price band. The SENTENCE it prints is `KurageMemory.PriceText`'s
    # and its multiplier is the law constant, interpolated -- pinned in
    # KleeTests and in tier0/tests/test_kurage_base_kit.py. These three are
    # where the band sits on the card and how big its type is, and the sim has
    # no card to sit on.
    # EB-214's header. The SENTENCE is what R224 ruled and it is pinned in
    # KleeTests and in tier0/tests/test_kurage_base_kit.py; where it sits and
    # how big it is are presentation, and the sim has no screen to compare
    # them against.
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
    "ReactionFx.FlashSeconds":
        "presentation: a reaction's body-flash length in seconds; nothing "
        "waits on it, and the sim draws nothing.",
    "KleeCombatVfx.LobDuration":
        "presentation: bomb-toss animation length in seconds.",
    "KleeCombatVfx.MaxConcurrentPops":
        "presentation: how many pop effects may overlap before they are "
        "dropped. A frame-rate guard, not a rule -- the sim resolves every "
        "detonation regardless of what is drawn.",
    "CreatureAnimationRouter.LowHealthFraction":
        "presentation: the HP fraction at or under which a combat body plays "
        "its slumped idle -- the base game's own CharacterModel.IsLowHealth "
        "line (0.25). It picks a pose and moves no number; the sim draws no "
        "bodies.",
    "StagePerformerBeat.ActSeconds":
        "presentation: how long a Furina performer's lunge holds before its "
        "act resolves (motion pass, 2026-10-02). Screen time only -- the act "
        "resolves the same either way, and the sim draws no bodies.",
    # EB-38, the rest-site and merchant breathe. All four are the SHAPE of one
    # loop -- two of them seconds, two of them the size of the move -- on a
    # portrait the sim does not draw, at two rooms the sim does not render. A
    # rest site's RULES (the heal, the enchant) are mirrored elsewhere and none
    # of them is here; nothing in this file can change a number a run reads.
    "StaticPortraitIdle.PeriodSeconds":
        "presentation: one full breath, in seconds.",
    "StaticPortraitIdle.HalfPeriodSeconds":
        "presentation: the swell and the settle are half a breath each, in "
        "seconds. Derived from PeriodSeconds by the pin, not by the compiler.",
    "StaticPortraitIdle.ScaleYPeak":
        "presentation: peak vertical scale of the portrait at the top of the "
        "breath. A multiplier on drawn pixels, not on any quantity.",
    "StaticPortraitIdle.RiseYPixels":
        "presentation: how far the portrait lifts at the top of the breath, "
        "in pixels, so the feet stay planted while the head moves.",
    # RibbonFullWidth and RibbonVisualSpan retired with D7 (salon UI sprint,
    # 2026-07-28): the ribbon no longer has a display span at all. A segment
    # is one TURN of upkeep at the current stage, which is a derived quantity
    # (members x TickEncoreCost), so the only constants left are the count of
    # segment NODES and the geometry they sit in.
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
    "FurinaStageCueNodes.HeadGap":
        "presentation: the pixels between a performer's hitbox and the "
        "bottom of its cue card (2026-09-26, the Furina cues). Geometry; the "
        "sim draws nothing.",
    "TurnEndPreviewBridge.SpriteScaleMax":
        "presentation: the largest scale a docket entity is drawn at. A "
        "rendering ratio; the sim has no sprites.",
    # ------------------------------------------------------------------
    # The Teyvat map overlay (2026-09-17). Three numbers about where a
    # decoration is DRAWN, on a screen the sim has never modelled -- tier0.5
    # generates a map graph and has no map SCREEN at all, so none of the three
    # can be mirrored and none of them prices anything.
    # ------------------------------------------------------------------
    "MapOverlay.TintAlpha":
        "`EB-818`. The alpha of the nation colour grade drawn over the map "
        "screen: a look, chosen against [USER]'s read that the dressed map was "
        "harder to read than the base game's, and held in the 10-15% band by "
        "`KleeTests/TeyvatMapOverlayTests`. Nothing a card, a rule, a reward or "
        "a route reads is priced in it; the sim has no map screen to draw it "
        "on.",
    "MapOverlay.WordmarkTopMargin":
        "`EB-818`. Pixels of clear air between the top of the map screen and "
        "the nation emblem strip, so the mark sits under the act banner the "
        "screen draws for itself rather than on it. A layout offset in screen "
        "pixels; tier0 has no counterpart and could not have one.",
    "MapOverlay.GroundChildIndex":
        "`EB-818`. The child index the overlay is moved to when it hangs off "
        "the map screen's root -- 1, i.e. directly above whatever is drawn "
        "first. A Godot draw-order position and not a quantity: `game_ref/` "
        "holds no decompile of `NMapScreen`, so this is the one number the "
        "arm's `teyvat:maptree` log line exists to confirm or move.",
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
# SWITCHES: build switches whose C# default is an MSBuild property in
# `klee-mod/Directory.Build.props` and whose sim twin is a tier0 bool. A
# `const bool` is not a number, so CONST_RE cannot see it; this table is how
# the sim's default stays the game's. SWIRL_PAYS sat False in the sim for ten
# days while every build Swirled for damage (fixed 2026-10-08).
# --------------------------------------------------------------------------
PROPS = REPO / "klee-mod" / "Directory.Build.props"

SWITCHES: dict[str, str] = {
    "SwirlPays": "SWIRL_PAYS",     # the element port, sec.4 A
}


def msbuild_bool_default(prop: str) -> bool:
    """The default `Directory.Build.props` gives an MSBuild bool property."""
    m = re.search(rf"<{prop}\s+Condition=\"[^\"]*\"\s*>\s*(true|false)\s*</{prop}>",
                  PROPS.read_text(encoding="utf-8"), re.IGNORECASE)
    if m is None:
        raise SystemExit(f"FINDING: no default for <{prop}> in {PROPS}; the "
                         "switch table names a property the props file does "
                         "not declare.")
    return m.group(1).lower() == "true"


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
    # Empty since 2026-10-08. Its two entries tied Kokomi's Pearl of Insight
    # rates (`charge_per_exhaust` / `burst_per_exhaust` on
    # `touch_of_orobas_kokomi`) to 2 x `CHARGE_PER_EXHAUST` and
    # `KOKOMI_BURST_PER_EXHAUST`. The Charge and Burst meters left the sim
    # with the rest of the shipped-kit machinery, the base constants with
    # them, and the relic's two hooks are inert (`tier0.engine.relics`).
    return []


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

    for prop, name in sorted(SWITCHES.items()):
        cs, sim = msbuild_bool_default(prop), getattr(C, name)
        if cs is not sim:
            findings.append(
                f"switch {prop}: the mod builds with {cs}, but tier0 "
                f"C.{name} is {sim}. A plain sim run would not model the "
                f"shipped game; make them agree.")

    for finding in findings:
        print(f"FINDING: {finding}")
    if findings:
        return 1
    print(f"constant parity: OK ({len(MIRRORED)} mirrored, "
          f"{len(UNMIRRORED)} declared unmirrored, {len(SWITCHES)} switch, "
          f"{len(_invariants())} ratified invariants held)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
