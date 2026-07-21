using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod;

/// <summary>
/// The companion reward slot -- tier05 rewards.roll_rewards, standard mode
/// (one offer; pity/choose-3 measured null and ruled OUT; the Featured
/// Banner is a no-op at current roster size and is skipped by ruling).
///
/// Law mirrored exactly: roll a rarity on RARITY_ODDS (5-star companions
/// ARE the rare tier), fall through rare -> uncommon -> common when a tier
/// is empty, then a NATION-WEIGHTED pick inside the tier.
///
/// Nation weighting went live with the Fontaine roster (2026-07-21 ruling:
/// "it's fine for Fontaine companions to show up as long as the 50%
/// nationality weighting is respected... it's probably best to have some
/// non-Mondstadt cards in the pool to make sure Klee doesn't inadvertently
/// overperform with a 100% Mondstadt roster"). It was previously and
/// correctly a no-op -- with one nation in the pool the weighting reduces
/// exactly to a uniform pick -- so this is the first build where it bites.
/// </summary>
public static class CompanionSlot
{
    // tier0 constants.RARITY_ODDS: common 0.60 / uncommon 0.35 / rare 0.05.
    private const float CommonOdds = 0.60f;
    private const float UncommonOdds = 0.35f;

    /// <summary>tier0 SAME_NATION_REWARD_SHARE.</summary>
    private const double SameNationShare = 0.5;

    /// <summary>tier0 NATION_WEIGHTS -- every nation 1.0 today.</summary>
    private const double NationWeight = 1.0;

    public static CardModel? Roll(Player player)
    {
        // rarity tier -> canonical companion models. personal_pool cards are
        // only offered to their own character (tier05: "load-bearing the
        // moment a second character exists") -- the call site already gates
        // on Klee, so "klee" is the only id that can match today.
        var tiers = new Dictionary<CardRarity, List<CardModel>>();
        foreach (var canonical in CompanionRoster.All)
        {
            if (canonical is not ICompanionCard comp) continue;
            if (comp.PersonalPool is not null && comp.PersonalPool != "klee") continue;
            if (!tiers.TryGetValue(canonical.Rarity, out var tier))
            {
                tiers[canonical.Rarity] = tier = new List<CardModel>();
            }
            tier.Add(canonical);
        }
        if (tiers.Count == 0) return null;

        // Sim _roll_rarity: cumulative walk of RARITY_ODDS in sheet order.
        var rng = player.PlayerRng.Rewards;
        var roll = rng.NextFloat();
        var rarity = roll < CommonOdds ? CardRarity.Common
            : roll < CommonOdds + UncommonOdds ? CardRarity.Uncommon
            : CardRarity.Rare;
        // Fall-through when a tier is empty (tier0 roll_rewards).
        if (!tiers.ContainsKey(rarity)) rarity = CardRarity.Uncommon;
        if (!tiers.ContainsKey(rarity)) rarity = CardRarity.Common;
        if (!tiers.TryGetValue(rarity, out var pool)) return null;

        var pick = NationWeightedChoice(rng, pool, HomeNation);
        if (pick == null) return null;
        // Same instantiation the native reward path uses for its own rolled
        // cards (CardFactory.CreateForReward ends in exactly this call), so
        // the appended 4th option is indistinguishable from the other three.
        // No upgrade roll here: the native path rolls one per reward card,
        // and the sim's companion slot does not.
        return ((ICardScope)player.RunState).CreateCard(pick, player);
    }

    /// <summary>Klee's home nation (tier0 loader.character_nation).</summary>
    private const string HomeNation = "mondstadt";

    /// <summary>
    /// Port of tier05 rewards._nation_weighted_choice. SAME_NATION_REWARD_SHARE
    /// of the slot's weight is split evenly across the home-nation cards; the
    /// remaining (1 - share) spreads across ALL cards in proportion to
    /// NATION_WEIGHTS (all 1.0 today, so: evenly).
    ///
    /// With no home-nation card in the tier the sim falls back to the plain
    /// weights, which is a uniform pick -- mirrored exactly, because that is
    /// the case a Fontaine-only rare tier actually hits.
    /// </summary>
    private static CardModel? NationWeightedChoice(
        Rng rng, List<CardModel> cards, string? homeNation)
    {
        if (cards.Count == 0) return null;

        var homeCount = homeNation == null
            ? 0
            : cards.Count(c => (c as ICompanionCard)?.Nation == homeNation);

        double[] weights;
        if (homeCount == 0)
        {
            weights = cards.Select(_ => NationWeight).ToArray();
        }
        else
        {
            var total = cards.Count * NationWeight;
            weights = cards
                .Select(c => (1.0 - SameNationShare) * NationWeight / total
                    + ((c as ICompanionCard)?.Nation == homeNation
                        ? SameNationShare / homeCount
                        : 0.0))
                .ToArray();
        }

        // Weighted draw off the same Rewards stream the rarity roll used, so
        // the slot still consumes exactly two numbers per offer.
        var cutoff = rng.NextFloat() * weights.Sum();
        double running = 0;
        for (var i = 0; i < cards.Count; i++)
        {
            running += weights[i];
            if (cutoff < running) return cards[i];
        }
        return cards[cards.Count - 1];   // float slop: last card owns the tail
    }
}
