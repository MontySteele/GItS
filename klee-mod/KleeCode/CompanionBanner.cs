using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Random;

namespace KleeMod;

/// <summary>
/// The Featured Banner (principles §4.2, v1.8) -- port of tier05
/// rewards.roll_banner.
///
/// Each run features at most <see cref="FeaturedSlots"/> 5-star companions PER
/// NATION, drawn once and fixed for the run's duration; only featured 5-stars
/// appear in that run's companion offers. 4-stars are never gated.
///
/// WHY THIS EXISTS NOW AND NOT BEFORE. Both channels carried a written ruling
/// that the banner was skipped because it was EXACTLY a no-op -- no nation
/// designed more than <see cref="FeaturedSlots"/> Rares, so every 5-star was
/// featured in every run. CompanionPool.Eligible named the trigger for going
/// live: "when a nation ships a 4th Rare." R64 (2026-07-25) shipped Fontaine's
/// fourth, so it goes live in BOTH channels in the same change, exactly as
/// that ruling required -- wiring one alone would make the two disagree about
/// a rule neither could previously exercise.
///
/// NO PERSISTENCE, BY CONSTRUCTION. The banner is a pure function of the
/// player's own rng seed, so it is recomputed rather than stored. That is what
/// makes it survive save/load for free, and it is why nothing here needs to
/// hook the save system. The cache below is a speed optimisation, not the
/// source of truth: drop it and behaviour is identical.
///
/// PER PLAYER, NOT PER RUN. Keyed on PlayerRngSet.Seed, which is per player,
/// so in co-op each player rolls their own lineup and drafts from it --
/// divergent lineups are the point, per §4.2 and the sim's own docstring. This
/// is also why the seed comes from the PLAYER rather than from RunState.
///
/// PARITY IS STRUCTURAL, NOT NUMERIC. The sim and the game use different
/// generators, so WHICH three of Fontaine's four are featured will differ for
/// the same nominal seed. What is mirrored is the rule: per nation, feature
/// min(roster, slots) drawn without replacement, fixed for the run, 4-stars
/// never gated. <see cref="FeaturedSlots"/> is parity-lint watched.
/// </summary>
public static class CompanionBanner
{
    /// <summary>tier0 constants.BANNER_FEATURED_SLOTS.</summary>
    public const int FeaturedSlots = 3;

    /// <summary>
    /// Name of the derived rng stream. Rng(seed, name) mixes a deterministic
    /// hash of this string into the seed, giving the banner its own stream --
    /// the same reason tier05 draws it from random.Random(seed + 2e9) rather
    /// than the run's main rng. Drawing from a shared stream would advance it
    /// and silently renumber every measurement taken before the banner existed.
    /// </summary>
    private const string RngStream = "kleemod_featured_banner";

    // v0.111.0 (`EB-171`): the game widened its RNG seeds from uint to
    // ulong (`PlayerRngSet.Seed`, `Rng(ulong)`), so the cache key follows.
    private static readonly Dictionary<ulong, HashSet<string>> Cache = new();

    /// <summary>The featured 5-star card ids for this player's run.</summary>
    public static IReadOnlyCollection<string> Featured(Player player)
    {
        var seed = player.PlayerRng.Seed;
        if (Cache.TryGetValue(seed, out var cached)) return cached;

        var featured = Roll(seed, player);
        Cache[seed] = featured;
        return featured;
    }

    /// <summary>
    /// True if this card may be offered to this player. 4-stars and
    /// non-companions are never gated, mirroring _banner_filtered.
    /// </summary>
    public static bool IsOffered(CardModel card, Player player)
    {
        if (card is not ICompanionCard comp) return true;
        if (comp.Star != 5) return true;
        return Featured(player).Contains(card.Id.Entry);
    }

    private static HashSet<string> Roll(ulong seed, Player player)
    {
        // Grouped by nation and SORTED BY ID inside each group before the
        // draw. The roster has no guaranteed order, and an unsorted input
        // would make the "deterministic" draw depend on class-scan
        // order -- deterministic per build, and silently different after any
        // edit that reorders the roster. tier05's five_star_roster sorts for
        // the same reason.
        //
        // CompanionPool.All, not CompanionRoster.All: the pool class is the ONE
        // door to "which companions exist for this run" and the Mondstadt
        // companion overhaul (QUARANTINED, R213 B) redirects it. The banner has
        // to read the same roster the reward slot does or it would feature
        // five-stars that cannot be offered and gate out ones that can -- the
        // exact split R64 shipped this class to close.
        var byNation = new SortedDictionary<string, List<CardModel>>();
        foreach (var card in CompanionPool.All)
        {
            if (card is not ICompanionCard comp) continue;
            if (comp.Star != 5) continue;
            if (comp.PersonalPool is not null) continue;   // Prune is not a draw
            var nation = comp.Nation ?? "";
            if (!byNation.TryGetValue(nation, out var list))
            {
                byNation[nation] = list = new List<CardModel>();
            }
            list.Add(card);
        }

        var featured = new HashSet<string>();
        var rng = new Rng(seed, RngStream);
        foreach (var (_nation, roster) in byNation)
        {
            var ids = roster.Select(c => c.Id.Entry).OrderBy(e => e).ToList();
            if (ids.Count <= FeaturedSlots)
            {
                // A nation at or under the cap features everyone. The draw is
                // skipped entirely rather than shuffling and taking all of
                // them, so a nation growing past the cap does not retroactively
                // change what an under-cap nation featured.
                featured.UnionWith(ids);
                continue;
            }
            rng.Shuffle(ids);
            featured.UnionWith(ids.Take(FeaturedSlots));
        }
        return featured;
    }

    /// <summary>
    /// Test/diagnostic hook: forget cached banners. Not called in normal play
    /// -- the cache is keyed by seed, so a new run keys differently on its own.
    /// </summary>
    public static void ClearCache() => Cache.Clear();
}
