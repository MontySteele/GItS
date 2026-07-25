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
/// !!! CARRIES A REJECTED NUMBER — DO NOT SHIP WITHOUT READING THIS !!!
///
/// The doubling below was **REJECTED** at the 2026-07-26 red-pen ("way too
/// good"). The ratified design is different in kind, not just in magnitude:
/// **"Gain 3 additional Sparks at the start of combat"** — a one-off windfall,
/// not a permanent rate increase. See docs/red-pen-2026-07-26.md item 5.
///
/// It is left standing rather than half-replaced because the ratified version
/// needs its sim counterpart (a real `starter_upgraded` hook; the red-pen
/// harness used a throwaway) and the two must land together or the C# and the
/// sim disagree about what Klee's upgraded starter does. That is queue item 2.
///
/// **Until then this relic is live in any build cut from this tree**, and a
/// playtester who takes Touch of Orobas gets the rejected design. That is the
/// same failure this whole track exists to prevent — a build implementing a kit
/// that is not the design of record — so it is flagged loudly rather than left
/// to a reader of the git log.
///
/// ---
///
/// Klee's upgraded starter (Touch of Orobas). Same hook, doubled number:
/// 2 Sparks per Bomb detonation instead of 1.
///
/// Named for her C2 constellation. The base-game convention is a DISTINCT
/// name rather than a "+" suffix (Burning Blood -> Black Blood), so this
/// follows it.
///
/// PROPOSED, and the most aggressive number in this sprint: Sparks are Klee's
/// core economy -- three make the next real Attack free -- so doubling
/// detonation income roughly halves the time to every free attack. It is the
/// Burning Blood -> Black Blood ratio applied faithfully, which is the
/// argument FOR it; that the base-game starter it copies is a flat post-combat
/// heal rather than an engine input is the argument against. Red-pen decides.
/// </summary>
public sealed class ExplosiveFrags : CustomRelicModel, IBombDetonationListener
{
    /// <summary>Sparks per detonation. Base relic grants 1.</summary>
    public const int SparksPerDetonation = 2;

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
            $"Whenever a [gold]Bomb[/gold] detonates, gain "
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

    protected override string IconBaseName => "snake_ring";

    public override string PackedIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.BigIconPath;
}
