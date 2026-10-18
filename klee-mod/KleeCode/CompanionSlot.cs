using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod;

/// <summary>
/// The companion reward slot -- tier05 rewards.roll_rewards, standard mode
/// (one offer; pity/choose-3 measured null and ruled OUT). There is no
/// Featured Banner: every companion in the pool is offerable in every run
/// ([USER] 2026-10-18, "Agreed on (a)!" -- scrap the banner everywhere), in
/// this slot and in the shop alike.
///
/// THE COMPANION ROLLS LIKE THE CARDS BESIDE IT ([USER] 2026-10-18, legacy
/// review pick 3: "Agreed on all 6 legacy picks"). Its rarity is rolled by the
/// base game's own <c>CardFactory.RollForRarity</c> on the reward's own
/// <c>RarityOdds</c> -- regular, elite or boss odds and the run's rare pity
/// counter, exactly as each native reward card is rolled -- and it then gets
/// the native reward card's upgrade roll, <c>CardFactory.RollForUpgrade</c>
/// at base chance 0. After a boss it is a Rare, an Uncommon when no Rare
/// companion can be offered. Then a NATION-WEIGHTED pick inside the tier.
/// Rarity is the sheet's rarity field (codegen'd as CardRarity); Star is a
/// separate 4/5 label, and nothing here reads Star.
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
    // THE SLOT IS A FACT ABOUT THE MOD, NOT ABOUT A RELIC (`EB-346`, R249
    // pick 4). Every starting relic in the roster hosts this slot, so every
    // starting relic used to append one shared sentence describing it -- 59
    // characters of identical text on four relics, which is what pushed three
    // of them over the relic ceiling and bought the fourth a lint exception.
    // [USER], 2026-09-02: "it's universal to all of the modded characters, so
    // I would consider it a fact about the mod, not the relic." The sentence
    // is stated ONCE now, in klee-mod/Klee/manifest.json's `description` (the
    // Mods screen), and no relic prints it.
    //
    // The wording that moved there is load-bearing and moved intact: "a
    // fourth choice" -- not "an extra reward" -- because
    // TryModifyCardRewardOptions appends to the card reward's OWN option
    // list, so the companion COMPETES with the three cards rather than being
    // taken alongside them; and "after a fight" is the
    // CardCreationSource.Encounter gate, which the enum's own doc defines as
    // the post-fight reward -- shops and events get no companion.

    private delegate CardRarity RollForRarityFn(Player player,
        CardRarityOddsType rollMethod, CardCreationSource source,
        HashSet<CardRarity> allowedRarities, bool forceRarityOddsChange);

    private delegate void RollForUpgradeFn(Player player, CardModel card,
        decimal baseChance, Rng rng);

    /// <summary>
    /// The base game's own reward rarity roll and upgrade roll, both private
    /// to <c>CardFactory</c>. Reused, not re-implemented, so the companion's
    /// odds, pity and upgrade chance cannot drift from the native cards'.
    /// Resolved with their own catch so a renamed method degrades (logged)
    /// rather than throwing a TypeInitializationException into a reward
    /// screen -- the MerchantCompanionSlots F2 pattern.
    /// </summary>
    private static readonly Delegate? BaseRollForRarity = Resolve(
        "RollForRarity", typeof(RollForRarityFn),
        typeof(Player), typeof(CardRarityOddsType), typeof(CardCreationSource),
        typeof(HashSet<CardRarity>), typeof(bool));

    private static readonly Delegate? BaseRollForUpgrade = Resolve(
        "RollForUpgrade", typeof(RollForUpgradeFn),
        typeof(Player), typeof(CardModel), typeof(decimal), typeof(Rng));

    private static Delegate? Resolve(string name, Type delegateType, params Type[] args)
    {
        try
        {
            var method = AccessTools.Method(typeof(CardFactory), name, args);
            return method == null ? null : Delegate.CreateDelegate(delegateType, method);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] CardFactory.{name} did not resolve "
                    + $"({e.GetType().Name}); the companion reward slot falls back.");
            return null;
        }
    }

    /// <summary>tier0 SAME_NATION_REWARD_SHARE.</summary>
    private const double SameNationShare = 0.5;

    /// <summary>tier0 NATION_WEIGHTS -- every nation 1.0 today.</summary>
    private const double NationWeight = 1.0;

    /// <summary>
    /// Whether a host relic appends the slot to THIS reward: a post-fight
    /// reward, built for the relic's own owner, who is on the host's
    /// character. The base game's <c>Hook.TryModifyCardRewardOptions</c> runs
    /// every active player's relics over every player's reward
    /// (<c>RunState.IterateHookListeners</c> gathers all seats), passing the
    /// reward's player. A gate on the character alone therefore let two Klees
    /// in co-op each add a companion to BOTH rewards -- five options, two of
    /// them companions. The owner test makes it one per reward.
    /// </summary>
    public static bool OffersTo(RelicModel host, Player player,
        CardCreationOptions creationOptions, bool homeCharacter) =>
        creationOptions.Source == CardCreationSource.Encounter
        && homeCharacter
        && ReferenceEquals(host.Owner, player);

    public static CardModel? Roll(Player player, CardCreationOptions creationOptions)
    {
        // rarity tier -> canonical companion models. personal_pool cards are
        // only offered to their own character (tier05: "load-bearing the
        // moment a second character exists"). It has: five characters host
        // this slot now, each from its own starter relic, so the filter is
        // doing real work.
        var tiers = new Dictionary<CardRarity, List<CardModel>>();
        // CompanionPool.All, not CompanionRoster.All: the pool class is the ONE
        // door to "which companions exist for this run", and the Mondstadt
        // companion overhaul roster is what it returns, on every build.
        foreach (var canonical in CompanionPool.All)
        {
            // The one offerability rule the shop's Eligible uses too: personal
            // pools AND IsHiddenFrom (Yae is never offered Sesshou Sakura, her
            // card paper pick 5 (a)). This loop used to test PersonalPool alone,
            // so Yae's reward slot could still offer it (audit 2026-10-18).
            if (!CompanionPool.IsOfferable(canonical, player)) continue;
            if (!tiers.TryGetValue(canonical.Rarity, out var tier))
            {
                tiers[canonical.Rarity] = tier = new List<CardModel>();
            }
            tier.Add(canonical);
        }
        if (tiers.Count == 0) return null;

        var rarity = RollRarity(player, creationOptions, tiers);
        if (!tiers.TryGetValue(rarity, out var pool)) return null;

        var rng = creationOptions.RngOverride ?? player.PlayerRng.Rewards;
        var pick = NationWeightedChoice(rng, pool, HomeNation(player));
        if (pick == null) return null;
        // Same instantiation the native reward path uses for its own rolled
        // cards (CardFactory.CreateForReward ends in exactly this call), then
        // the same upgrade roll it gives each of them, on the same stream and
        // under the same NoUpgradeRoll flag.
        var card = ((ICardScope)player.RunState).CreateCard(pick, player);
        if (!creationOptions.Flags.HasFlag(CardCreationFlags.NoUpgradeRoll)
            && BaseRollForUpgrade is RollForUpgradeFn upgrade)
        {
            upgrade(player, card, 0m, rng);
        }
        return card;
    }

    /// <summary>
    /// The reward's own rarity roll (<c>CardFactory.RollForRarity</c>), over
    /// the tiers this player can be offered: an Encounter reward on regular,
    /// elite or boss odds rolls with the pity counter and moves it, exactly
    /// as a native reward card does, and an empty tier wraps the way the base
    /// game's <c>GetNextAllowedRarity</c> does. After a boss the slot is a
    /// Rare, or an Uncommon when no Rare companion can be offered.
    /// </summary>
    private static CardRarity RollRarity(Player player,
        CardCreationOptions creationOptions,
        Dictionary<CardRarity, List<CardModel>> tiers)
    {
        var odds = creationOptions.RarityOdds;
        CardRarity rarity;
        if (BaseRollForRarity is RollForRarityFn roll)
        {
            rarity = roll(player, odds, creationOptions.Source,
                tiers.Keys.ToHashSet(),
                creationOptions.Flags.HasFlag(CardCreationFlags.ForceRarityOddsChange));
        }
        else
        {
            rarity = player.PlayerOdds.CardRarity.Roll(odds);
            if (!tiers.ContainsKey(rarity)) rarity = CardRarity.Uncommon;
            if (!tiers.ContainsKey(rarity)) rarity = CardRarity.Common;
        }
        if (odds == CardRarityOddsType.BossEncounter)
        {
            rarity = tiers.ContainsKey(CardRarity.Rare)
                ? CardRarity.Rare
                : CardRarity.Uncommon;
        }
        return rarity;
    }

    // Delegated to CompanionPool (§4.7 shop sprint, Track A) so the reward
    // slot and the shop channel can never drift about which character is which
    // or where they are from. Pure switches over Player.Character: no rng, no
    // ordering, so the offers this slot produces are unchanged by the move.
    private static string? CharacterId(Player player) =>
        CompanionPool.CharacterId(player);

    private static string? HomeNation(Player player) =>
        CompanionPool.HomeNation(player);

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

        // Weighted draw off the reward's own stream (Rewards unless the
        // reward overrides it), the stream the native card draw uses.
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
