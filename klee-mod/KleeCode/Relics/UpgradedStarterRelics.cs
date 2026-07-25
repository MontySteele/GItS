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
/// NUMBERS ARE PROPOSED, pending the single red-pen session (G-D). The
/// magnitude precedent is the base game's own: Burning Blood heals 6 after
/// combat, Black Blood heals 12 -- an exact doubling of the starter's effect.
/// These follow that, and the doubling is called out per relic because it is
/// the most aggressive thing in this sprint.
///
/// FURINA IS DELIBERATELY ABSENT. See the G-C3 findings in
/// docs/ship-what-we-know-sprint-log.md: Ethereal Spotlight has no number to
/// scale, and every candidate tune-up is either a new mechanic (which this
/// sprint's own rule forbids in a starter upgrade) or a per-turn Encore
/// trickle, which her sheet law bans outright. That is a [USER] decision, not
/// an implementation gap, and it is named in a curated set rather than filled
/// with an invention.
/// </summary>
internal static class UpgradedStarterRelics
{
}

/// <summary>
/// Klee's upgraded starter (Touch of Orobas). RATIFIED 2026-07-26.
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
/// Named for her C2 constellation. The base-game convention is a DISTINCT name
/// rather than a "+" suffix (Burning Blood -> Black Blood), so this follows it.
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
        ("title", "Explosive Frags"),
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
