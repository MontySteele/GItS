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
            rolled[i] = new CardCreationResult(Pick(floor, sameTier));
            __result = rolled;
            return;
        }

        rolled[rolled.Count - 1] = new CardCreationResult(Pick(floor, pool));
        __result = rolled;
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
