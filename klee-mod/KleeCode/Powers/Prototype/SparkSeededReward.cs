using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Characters;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Powers;

/// <summary>
/// `EB-577`. THE ARM'S FIRST CARD REWARDS EACH CARRY A SPARK-PRICED ROW.
///
/// THE READING SIX ROUNDS MADE. Sparks are inert until a sink is drafted --
/// r17, r18, r19, r20 and r21 all said it, and the r21 lane-2 seat ended
/// fights holding 3, 4 and 5 Sparks with Dig In the deck's only reader. The
/// resource this kit mints on every explosion did nothing at all for two acts,
/// because the reward screens that could have taught it never offered one.
///
/// AN OFFER RULE AND NOT A SHEET CHANGE, which is the whole shape of the
/// intervention (Klee r21 packet sec.5, a D default). No card's rarity, price
/// or face moves. What moves is which cards a reward screen may show while the
/// deck holds no reader, on floors 1 to
/// <see cref="KleeOverhaulLaw.SparkSeedFloors"/> -- the first two card rewards
/// of a run, which is where the reading forms.
///
/// A POSTFIX ON `CardFactory.CreateForReward`, which is the ONE place the base
/// game rolls the cards a reward screen shows. The sim's twin is
/// `tier05.rewards._spark_seed`, and it is the same rule read the same way: if
/// the roll already produced a Spark-priced offer the screen is untouched;
/// otherwise ONE offer is swapped for a Spark-priced row of the SAME rarity,
/// because the guarantee is about WHICH card and never about how good one is.
///
/// QUARANTINED, like everything else in this arm: <c>KleeOverhaul.Enabled</c>
/// off, or any character but Klee, and this patch returns having changed
/// nothing. Floor 4 on is untouched too, so the rule expires by itself rather
/// than becoming a permanent tax on the pool.
///
/// `EB-594`. TWO CORRECTIONS, BOTH FOUND LIVE ON `0.2.2817+proto`.
///
/// (1) THE SWAP HANDS BACK AN INSTANCE, never a canonical model. This first
/// shipped as <c>new CardCreationResult(Pick(...))</c> over a row taken
/// straight out of <c>options.GetPossibleCards(player)</c> -- which is the
/// game's REGISTRY, whose rows are canonical models. A canonical model put on
/// a screen survives until something asserts on it: on lane 1 the assert came
/// from <c>CardChoiceHistoryEntry..ctor</c> serialising the pick
/// (<c>AbstractModel.AssertMutable</c> ->
/// <c>CanonicalModelException: ... ProtoKoSugarRush used in incorrect
/// place</c>), which threw inside <c>HeftyTablet.AfterObtained</c> and left the
/// Neow screen with an empty option list and no legal verb -- a hard blocker,
/// not a cosmetic one. The base game's own reward path ends in
/// <c>((ICardScope)player.RunState).CreateCard(model, player)</c>
/// (<c>CompanionSlot.Roll</c> mirrors it for the same reason), so the swap
/// does too, and the row it substitutes is indistinguishable from the ones the
/// roll made.
///
/// (2) POST-FIGHT REWARDS ONLY. <c>CreateForReward</c> also rolls the cards for
/// Neow's options, for a relic's "choose one of three" (Hefty Tablet) and for
/// a shop's stock; a floor number does not tell those apart from the reward
/// after a fight, which is the only screen the rule was written about. The
/// gate is the same <c>CardCreationSource.Encounter</c> test the four reward
/// hooks in this mod already ask.
/// </summary>
[HarmonyPatch(typeof(CardFactory), nameof(CardFactory.CreateForReward),
    new[] { typeof(Player), typeof(int), typeof(CardCreationOptions) })]
internal static class CardFactory_CreateForReward_SparkSeed_Patch
{
    [HarmonyPostfix]
    public static void Postfix(Player player, CardCreationOptions options,
                               ref IEnumerable<CardCreationResult> __result)
    {
        if (!KleeOverhaul.Enabled || player?.Character is not IKleeCharacter)
        {
            return;
        }

        // `EB-594`. THE SCREEN, AND NOT THE FLOOR. Encounter is the enum's own
        // name for the reward after a fight; Neow, a relic's choose-one-of-
        // three and the shop all roll through this same factory and are none
        // of the rule's business.
        if (options == null || options.Source != CardCreationSource.Encounter)
        {
            return;
        }

        // MATERIALISED ONCE. The game hands back a lazy sequence and the
        // reward screen enumerates it; asking "does this hold a Spark row"
        // of a lazy sequence and then handing the same sequence on would
        // roll the screen twice.
        var rolled = __result?.ToList();
        if (rolled == null || rolled.Count == 0) return;

        var floor = player.RunState?.TotalFloor ?? 0;
        if (floor < 1 || floor > KleeOverhaulLaw.SparkSeedFloors) return;

        if (rolled.Any(r => IsSparkPriced(r?.Card))) return;

        var already = new HashSet<string>(
            rolled.Where(r => r?.Card?.Id.Entry != null)
                  .Select(r => r!.Card!.Id.Entry));
        var pool = options.GetPossibleCards(player)
            .Where(c => IsSparkPriced(c) && !already.Contains(c.Id.Entry))
            .ToList();
        if (pool.Count == 0) return;

        // THE SAME RARITY FIRST, so the swap costs the screen nothing in tier.
        for (var i = 0; i < rolled.Count; i++)
        {
            var offer = rolled[i]?.Card;
            if (offer == null) continue;
            var sameTier = pool.Where(c => c.Rarity == offer.Rarity).ToList();
            if (sameTier.Count == 0) continue;
            var swap = Instantiate(player, Pick(floor, sameTier));
            if (swap == null) return;
            rolled[i] = swap;
            __result = rolled;
            return;
        }

        var last = Instantiate(player, Pick(floor, pool));
        if (last == null) return;
        rolled[rolled.Count - 1] = last;
        __result = rolled;
    }

    /// <summary>
    /// `EB-594`. THE ROW A REWARD SCREEN MAY HOLD is an INSTANCE, and
    /// <see cref="CardCreationOptions.GetPossibleCards"/> hands back canonical
    /// models. Run scope, because a reward goes into the DECK and outlives the
    /// combat -- the same call <c>CardFactory.CreateForReward</c> ends in and
    /// the same one <c>CompanionSlot.Roll</c> makes for the appended companion
    /// offer, so the swapped row cannot be told from a rolled one.
    /// </summary>
    private static CardCreationResult? Instantiate(Player player, CardModel model)
    {
        var made = ((ICardScope)player.RunState).CreateCard(model, player);
        return made == null ? null : new CardCreationResult(made);
    }

    /// <summary>
    /// WHICH Spark row, and NO RNG IS CONSUMED DOING IT.
    ///
    /// `RunState.Rng` has no card-reward stream of its own -- the roll this
    /// postfix runs after has already been made -- so drawing here would have
    /// to spend one of the streams the base game owns (`UpFront`, `Niche`,
    /// `CombatCardGeneration`), and a seeded run would then diverge from the
    /// same seed played without the arm for a reason that has nothing to do
    /// with combat. So the pick is DERIVED: the eligible rows in a stable
    /// order, indexed by the floor. It is deterministic, it replays, and the
    /// run's two seeded screens get different cards, which is the whole of
    /// what a draw was wanted for.
    /// </summary>
    private static CardModel Pick(int floor, IReadOnlyList<CardModel> from)
    {
        var ordered = from.OrderBy(c => c.Id.Entry, System.StringComparer.Ordinal)
                          .ToList();
        return ordered[((floor - 1) % ordered.Count + ordered.Count)
                       % ordered.Count];
    }

    /// <summary>`ISparkPricedCard` is the arm's own declaration of a printed
    /// Spark price and the same one `SparkCost` and the playability gate read,
    /// so this rule and the refusal a player meets cannot disagree about which
    /// cards are Spark-priced.</summary>
    private static bool IsSparkPriced(CardModel? card) =>
        card is ISparkPricedCard priced && priced.PrintedSparkPrice > 0;
}
