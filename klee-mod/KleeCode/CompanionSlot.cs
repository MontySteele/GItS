using System.Collections.Generic;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod;

/// <summary>
/// The companion reward slot -- tier05 rewards.roll_rewards, standard mode
/// (one offer; pity/choose-3 measured null and ruled OUT; the Featured
/// Banner is a no-op at current roster size and is skipped by ruling).
///
/// Law mirrored exactly: roll a rarity on RARITY_ODDS (5-star companions
/// ARE the rare tier), fall through rare -> uncommon -> common when a tier
/// is empty, pick uniformly inside the tier. Nation weighting
/// (SAME_NATION_REWARD_SHARE) reduces exactly to the uniform pick in a
/// single-nation world -- the sim's own note -- so it is deliberately not
/// mirrored until a second nation ships.
/// </summary>
public static class CompanionSlot
{
    // tier0 constants.RARITY_ODDS: common 0.60 / uncommon 0.35 / rare 0.05.
    private const float CommonOdds = 0.60f;
    private const float UncommonOdds = 0.35f;

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

        var pick = rng.NextItem(pool);
        if (pick == null) return null;
        // SpecialCardReward asserts mutability -- hand it a fresh instance.
        return ((ICardScope)player.RunState).CreateCard(pick, player);
    }
}
