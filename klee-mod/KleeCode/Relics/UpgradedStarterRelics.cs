using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Relics;

/// <summary>
/// G-C3: the upgraded forms Touch of Orobas hands out.
///
/// THE BUG. Touch of Orobas is an act-2 Ancient reward that replaces your
/// starting relic with an upgraded version. Vanilla resolves that through
/// <c>TouchOfOrobas.GetUpgradedStarterRelic</c>, which is a HARDCODED
/// dictionary of five base-game pairs (Burning Blood -> Black Blood, Ring of
/// the Snake -> Ring of the Drake, Divine Right -> Divine Destiny, Bound
/// Phylactery -> Phylactery Unbound, Cracked Core -> Infused Core) with a
/// fallback of <c>ModelDb.Relic&lt;Circlet&gt;()</c> -- the no-effect filler.
/// So on a modded character the "reward" swapped the starter for a relic that
/// does nothing: a strict DOWNGRADE dressed as an upgrade. Reported from the
/// 2026-07-25 co-op A0 playtest.
///
/// THE MECHANISM, found by decompile per the house norm rather than invented.
/// Vanilla itself is not extensible here -- the dictionary is a private static
/// property. But BaseLib already patches exactly this method:
///
///   [HarmonyPatch(typeof(TouchOfOrobas), "GetUpgradedStarterRelic")]
///   private static bool CustomStarterUpgrade(RelicModel starterRelic,
///                                            ref RelicModel? __result)
///   {
///       if (starterRelic is CustomRelicModel customRelicModel)
///       {
///           __result = customRelicModel.GetUpgradeReplacement();
///           return __result == null;
///       }
///       return true;
///   }
///
/// So the extension point is <c>CustomRelicModel.GetUpgradeReplacement()</c>,
/// which defaults to <c>null</c>. All three of our starters are
/// CustomRelicModels and none of them overrode it, so every one fell through
/// to the Circlet. The fix is to override it -- plugging into the mechanism,
/// not reinventing it. No Harmony patch of our own is needed or wanted.
///
/// NUMBERS ARE RATIFIED (red-pen 2026-07-26), not proposed. Worth recording
/// because the first attempt reasoned from the wrong precedent: Burning Blood
/// heals 6 and Black Blood heals 12, so the upgraded forms were drafted as
/// exact doublings of their starters. That works for a flat post-combat heal
/// and fails for an ENGINE INPUT -- doubling Klee's per-detonation Spark rate
/// compounds with every bomb in the deck, and it was rejected as "way too
/// good". The ratified shape is a fixed opening windfall instead. Ratio
/// precedents do not transfer across effect kinds.
///
/// FURINA'S ARRIVED AT THE RED-PEN. G-C3 declined to invent one because every
/// candidate broke either the sprint's "no new behaviour in a starter upgrade"
/// rule or her no-passive-accrual law. R2 (2026-07-26) overrides the FORMER by
/// user authority — see <see cref="CurtainNeverFalls"/>. The accrual law is
/// untouched: the upgrade grants no resource per turn, it removes a choice.
/// </summary>
internal static class UpgradedStarterRelics
{
}

/// <summary>
/// Klee's upgraded starter (Touch of Orobas), displayed as "Dodoco Tales".
/// RATIFIED 2026-07-26.
///
/// Her per-detonation Spark income is UNCHANGED at 1 -- this relic keeps the
/// base behaviour rather than replacing it -- and she banks a fixed windfall
/// of <see cref="OpeningSparks"/> at the start of every combat.
///
/// WHY A WINDFALL AND NOT A RATE. The first attempt doubled the per-detonation
/// grant, and that was rejected at red-pen as "way too good": a rate multiplies
/// with every bomb in the deck, so it compounds precisely where Klee is already
/// strongest, while a fixed opening bank dilutes across a long fight. The shape
/// mattered more than the number. Measured before ratification (act-2
/// acquisition, generous case): spark +2.3pt, demolition +7.1, reaction +5.0 --
/// strong for the slot, and the slot is an act-2 Ancient whose peers upgrade
/// six cards.
///
/// THE MEASUREMENT TABLE ABOVE GRADES THIS RELIC, NOT THE CARD. Red-pen Part 1
/// item 5 is titled "Explosive Frags", and until R69 that name belonged to two
/// different game objects reachable in the same run: this relic and the Rare
/// Power card `explosive_frags` (docs/klee-cards.yaml), which have
/// unrelated effects. The audit flagged the citation as ambiguous. It is
/// resolved here explicitly: the +2.3 / +7.1 / +5.0 figures are THIS object's,
/// measured as the Orobas upgrade, and item 5's ratification at 3 opening
/// Sparks is this object's ratification.
///
/// R69 (2026-07-26) settled the collision by renaming this side. The card was
/// the prior arrival and the ratified sheet artifact, so it keeps its name and
/// the relic yields. "Dodoco Tales" is Klee's signature catalyst, which keeps
/// the relic in her personal register alongside Pounding Surprise -- and it
/// still satisfies the base-game convention of a DISTINCT name for an upgraded
/// starter rather than a "+" suffix (Burning Blood -> Black Blood).
///
/// The C# TYPE is deliberately still `ExplosiveFrags`. R69 ruled that "no
/// mechanical change of any kind rides on this ruling", and a type rename is
/// not reliably cosmetic here: relic identity is BaseLib's, not this repo's,
/// so a renamed type risks moving the runtime relic id -- which in
/// deterministic-lockstep co-op is a desync, not a cosmetic diff. The
/// player-facing string is the thing the ruling renamed, and it is the thing
/// renamed below. Both names are reserved in docs/reserved-card-names.txt so
/// neither can be re-minted on the other side of the card/relic line.
///
/// Sim parity: tier05/content/relics.yaml `touch_of_orobas_klee`, whose
/// `combat_start_spark` hook is this class's opening bank. The per-detonation
/// half needs no sim entry because it is the starter's own hook, which the sim
/// never removes.
/// </summary>
public sealed class ExplosiveFrags : CustomRelicModel, IBombDetonationListener
{
    /// <summary>
    /// Sparks per detonation. UNCHANGED from the base relic -- the upgrade is
    /// the opening bank below, not this rate. Kept as a named constant rather
    /// than a literal 1 so that anyone tempted to raise it meets the ruling
    /// first.
    /// </summary>
    public const int SparksPerDetonation = 1;

    /// <summary>Sparks banked once, at the start of every combat.</summary>
    public const int OpeningSparks = 3;

    public ExplosiveFrags() : base(autoAdd: false)
    {
    }

    // Ancient, matching the reward tier that grants it -- Touch of Orobas is
    // itself RelicRarity.Ancient, and the five base-game upgraded forms are
    // not Starter-rarity either. Starter rarity here would also be actively
    // harmful: TouchOfOrobas.GetStarterRelic finds its target with
    // `p.Relics.FirstOrDefault(r => r.Rarity == RelicRarity.Starter)`, so a
    // Starter-rarity replacement could be picked up as the starter by a
    // second Orobas and upgraded again.
    public override RelicRarity Rarity => RelicRarity.Ancient;

    public override List<(string, string)>? Localization => new()
    {
        // R69 (2026-07-26): was "Explosive Frags", which collided with the
        // Rare Power card of that name. See the class summary.
        ("title", "Dodoco Tales"),
        ("description",
            $"At the start of combat, gain {OpeningSparks} "
          + "[gold]Spark[/gold]. Whenever a [gold]Bomb[/gold] detonates, gain "
          + $"{SparksPerDetonation} [gold]Spark[/gold]. "
          + CompanionSlot.RewardSlotDescription),
    };

    protected override string IconBaseName => "burning_blood";

    public override string PackedIconPath =>
        KleePck.Path("klee/relics/pounding_surprise.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("klee/relics/pounding_surprise.png") ?? base.BigIconPath;

    /// <summary>
    /// The companion reward slot rides along UNCHANGED. It is not part of the
    /// upgrade -- it is the fourth-offer hook that has to exist for the whole
    /// of every run, and losing it when Orobas fires would be a second
    /// instance of exactly the bug this class fixes.
    /// </summary>
    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (creationOptions.Source != CardCreationSource.Encounter) return false;
        if (player.Character is not Klee) return false;

        var companionRarity =
            creationOptions.RarityOdds == CardRarityOddsType.BossEncounter
                ? CardRarity.Rare
                : (CardRarity?)null;
        var offer = CompanionSlot.Roll(player, companionRarity);
        if (offer == null) return false;
        cardRewardOptions.Add(new CardCreationResult(offer));
        return true;
    }

    /// <summary>
    /// The opening bank.
    ///
    /// SITE CHOSEN FOR SIM PARITY, not convenience. `BeforeCombatStart()` is
    /// the obvious-sounding hook and is wrong here twice over: it carries no
    /// PlayerChoiceContext (which granting a power needs), and the sim fires
    /// its `combat_start_*` relic effects on TURN 1 after the block clear,
    /// energy reset and draw — not before the combat exists
    /// (combat.py `_player_turn`, `if state.turn == 1: apply_combat_start`).
    /// Turn 1 of `AfterPlayerTurnStart` is that same moment.
    ///
    /// `TurnNumber == 1` rather than `<= 1` so an extra first turn cannot pay
    /// the windfall twice, and per-PLAYER so a co-op partner's turn counter
    /// cannot trigger Klee's bank.
    /// </summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player != Owner || player.PlayerCombatState?.TurnNumber != 1) return;
        Flash();
        await SparkPower.Gain(
            choiceContext, Owner.Creature, OpeningSparks, cardSource: null);
    }

    public async Task OnBombDetonated(
        PlayerChoiceContext choiceContext, Creature? applier, Creature target,
        int damage)
    {
        // Own bombs only: in co-op another player's detonations are theirs.
        if (applier?.Player != Owner) return;

        Flash();
        await SparkPower.Gain(
            choiceContext, Owner.Creature, SparksPerDetonation,
            cardSource: null);
    }
}

/// <summary>
/// Kokomi's upgraded starter (Touch of Orobas). Same hook, doubled numbers.
///
/// Like the base relic this is the FICTION of the rule and the place the
/// tooltip lives, not the mechanism -- the exhaust funnel is keyed to her
/// character identity, so a player who loses the relic does not lose the
/// character. Which is precisely why the upgraded form has to declare its own
/// numbers rather than assume the funnel reads them from here.
///
/// PROPOSED. Included because G-C3(b) says Kokomi's rides along if her starter
/// relic already exists in-tree, and PearlOfWisdomRelic does. The tension with
/// the sprint's "Kokomi anything" non-goal is noted in the log; leaving her
/// starter to degrade into a Circlet while fixing exactly that bug for the
/// other two would have been knowingly shipping a known defect.
/// </summary>
public sealed class PearlOfInsightRelic : CustomRelicModel
{
    public const int ChargePerExhaust = KokomiConstants.ChargePerExhaust * 2;
    public const int BurstPerExhaust = KokomiConstants.BurstPerExhaust * 2;

    public PearlOfInsightRelic() : base(autoAdd: false)
    {
    }

    public override RelicRarity Rarity => RelicRarity.Ancient;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Pearl of Insight"),
        ("description",
            "Whenever a card is [gold]Exhausted[/gold], gain "
          + $"{ChargePerExhaust} [gold]Charge[/gold] "
          + $"and {BurstPerExhaust} Burst Energy."),
    };

    /// <summary>
    /// Kokomi's fourth companion reward option, carried forward from the base
    /// relic UNCHANGED.
    ///
    /// This is not part of the upgrade and must never be treated as optional.
    /// Companions are off every rollable pool, so the starter relic's reward
    /// slot is their ONLY door — and her Commander archetype is built entirely
    /// out of them. An upgraded starter that dropped this hook would not crash
    /// or warn; it would quietly delete one of her three archetypes the moment
    /// Touch of Orobas was taken, which is the same class of silent deletion
    /// the whole upgraded-starter track exists to prevent.
    ///
    /// It was in fact missing here for a day: this class was written before
    /// the base relic gained the hook, and the omission was caught by reading
    /// the two files side by side rather than by any check.
    /// </summary>
    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (creationOptions.Source != CardCreationSource.Encounter
            || player.Character is not Kokomi)
        {
            return false;
        }
        var rarity = creationOptions.RarityOdds == CardRarityOddsType.BossEncounter
            ? CardRarity.Rare
            : (CardRarity?)null;
        var offer = CompanionSlot.Roll(player, rarity);
        if (offer == null) return false;
        cardRewardOptions.Add(new CardCreationResult(offer));
        return true;
    }

    protected override string IconBaseName => "snake_ring";

    public override string PackedIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.BigIconPath;
}

/// <summary>
/// Furina's upgraded starter (Touch of Orobas). RATIFIED 2026-07-26 as red-pen
/// ruling R2, a [USER] design superseding all three worksheet options.
///
/// **Both Spotlight modes at once, permanently.** Her own cards generate
/// Fanfare (Center Stage's half) AND her Companions are multiplied (Guest
/// Cast's half), and conditions keying off "moved the Spotlight this turn" are
/// ALWAYS ON — which is what makes this relic the selector-payoff enabler
/// rather than merely a convenience.
///
/// THE UPGRADE REMOVES THE EXCLUSIVITY, NOT THE TARGETING (reading 1, ruled
/// during implementation). Each half still applies only to its own card class:
/// no numeric boost leaks onto Furina's cards, and her Companions still mint no
/// Fanfare. What she gains is that she never has to choose. Every gate lives in
/// <see cref="SpotlightSystem"/>, keyed off
/// <see cref="SpotlightSystem.BothModes"/>, so this class holds no logic of its
/// own beyond existing — which is the point: a relic that is a FLAG cannot
/// drift from the system that reads it.
///
/// **THE SELECTOR CARD STOPS ARRIVING.** With both modes always on it has
/// nothing left to choose, so this class deliberately does NOT override
/// AfterPlayerTurnStart the way <see cref="EtherealSpotlightRelic"/> does. That
/// touches Funnel Contract §3 (Spotlight is a designation event, one funnel):
/// the funnel is not removed, moved or renamed and every existing caller still
/// routes through it — but an upgraded Furina never FIRES it again, so the
/// Spotlight beam goes quiet for that run. The cross-session note was filed in
/// BOTH logs before this landed, per the contract's own rule:
/// docs/archive/animation-sprint-2-log.md and docs/archive/red-pen-2026-07-26.md.
///
/// THIS DELIBERATELY BREAKS the "no new behaviour in a starter upgrade" rule,
/// by user authority. The rule is OVERRIDDEN, not reinterpreted, and the
/// override is recorded rather than quietly absorbed. Her no-passive-accrual
/// law (kickoff §4) is NOT touched: this grants no resource per turn.
///
/// NAME is authored theatrical flavour like the rest of her sheet and rides the
/// pending v1.7 lore/constellation audit.
///
/// SIM PARITY: NOT MODELLED, recorded rather than silent. tier05 has no
/// Spotlight-mode model to make always-on, and the narrow relic-upgrade
/// approach ([USER], option 1) means there is no table to hang it off. So
/// Furina's Orobas variant has no row in tier05/content/relics.yaml, unlike
/// touch_of_orobas_klee. Consequence: a tier-0.5 Furina never receives this
/// upgrade, so no anchor or free-draft cell measures it, and its value is
/// unpriced. That is a real gap and belongs to the pool-sweep pass, where
/// Spotlight is already the subject.
/// </summary>
public sealed class CurtainNeverFalls : CustomRelicModel
{
    public CurtainNeverFalls() : base(autoAdd: false)
    {
    }

    // Ancient, never Starter -- see ExplosiveFrags for why that matters.
    public override RelicRarity Rarity => RelicRarity.Ancient;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "The Curtain Never Falls"),
        ("description",
            "[gold]Center Stage[/gold] and [gold]Guest Cast[/gold] are both "
          + "always active, and you always count as having moved the "
          + "[gold]Spotlight[/gold] this turn. "
          + CompanionSlot.RewardSlotDescription),
    };

    protected override string IconBaseName => "snake_ring";

    public override string PackedIconPath =>
        KleePck.Path("furina/relics/ethereal_spotlight.png")
        ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("furina/relics/ethereal_spotlight.png")
        ?? base.BigIconPath;

    /// <summary>
    /// Furina's companion reward slot, carried forward UNCHANGED from the base
    /// relic. Not part of the upgrade, and not optional: see
    /// <see cref="PearlOfInsightRelic.TryModifyCardRewardOptions"/> for the
    /// near-miss that put an invariant behind this.
    /// </summary>
    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (creationOptions.Source != CardCreationSource.Encounter
            || player.Character is not Furina)
        {
            return false;
        }
        var rarity = creationOptions.RarityOdds == CardRarityOddsType.BossEncounter
            ? CardRarity.Rare
            : (CardRarity?)null;
        var offer = CompanionSlot.Roll(player, rarity);
        if (offer == null) return false;
        cardRewardOptions.Add(new CardCreationResult(offer));
        return true;
    }
}
