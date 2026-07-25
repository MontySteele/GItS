using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// The queryable companion surface: "which companions may be offered to THIS
/// player, in THIS nation, at THIS rarity". Track A of the §4.7 shop sprint.
///
/// WHY THIS IS NOT A CardPoolModel (read before "fixing" it).
///
/// §4.1/§4.7 describe companions as a colorless <c>CustomCardPoolModel</c>.
/// That description is now BUILDABLE but deliberately NOT built, and the
/// reasoning changed twice, so both halves are recorded here:
///
/// 1. The old blocker is GONE. KleeOffPoolCards documents an ATTEMPT 1 that a
///    standalone pool "could never work", because ModelDb.AllCardPools is
///    AllCharacterCardPools concat a HARDCODED array of 7 shared pools with no
///    registration hook. That was true when it was written and is now STALE:
///    BaseLib ships <c>ModelDbSharedCardPoolsPatch</c>, a postfix on the
///    shared-pools getter that appends any <c>CustomCardPoolModel</c> whose
///    <c>IsShared</c> is true (registered from its own constructor). A
///    companion pool WOULD resolve today.
///
/// 2. The reason not to do it anyway is cost, not feasibility. Registering a
///    real pool means MIGRATING all 47 companion models out of the three
///    character pools, because <c>CardModel.Pool</c> must resolve to exactly
///    one pool -- and Pool supplies the card FRAME, energy icon and deck-entry
///    colour. So the migration is a visual change to every companion card, it
///    touches the shared loader surface all three character workstreams sit
///    on, and it depends on our pool being constructed before the first
///    <c>ModelDb.AllCardPools</c> read (that property caches; AllSharedCardPools
///    does not). There is no C# test project, so none of that is verifiable
///    except by launching the game.
///
/// Nothing in this sprint NEEDS the pool object: <c>MerchantCardEntry</c> takes
/// a plain <c>IEnumerable&lt;CardModel&gt;</c>, so the shop reads this class
/// directly. The migration is therefore a de-risked follow-up, not a
/// prerequisite -- flagged for [USER] at sprint close-out.
///
/// HARD CONSTRAINT (sprint plan, Track A): the free reward slot is untouched.
/// CompanionSlot.Roll does not route through this class; it only delegates the
/// two identity lookups below, which are pure switches over Player.Character
/// and consume no rng. Reward-slot offers are byte-identical by construction.
/// </summary>
public static class CompanionPool
{
    /// <summary>
    /// Every companion card, canonical instances. Same list the reward slot
    /// draws from -- ONE roster, two channels (§4.7's whole point is that the
    /// channels differ in economy, not in contents).
    /// </summary>
    public static IReadOnlyList<CardModel> All => CompanionRoster.All;

    /// <summary>
    /// Does this player's character host the companion system at all? Base
    /// StS2 characters must see a completely unmodified shop, so every entry
    /// point gates on this first.
    /// </summary>
    public static bool HostsCompanions(Player player) => CharacterId(player) != null;

    /// <summary>
    /// tier05 rewards: personal_pool cards are only ever offered to their own
    /// character, and guest stars are generator-only (they are not in
    /// CompanionRoster at all, so no filter is needed for them here).
    /// </summary>
    public static bool IsOfferable(CardModel card, Player player)
    {
        if (card is not ICompanionCard comp) return false;
        return comp.PersonalPool is null || comp.PersonalPool == CharacterId(player);
    }

    /// <summary>
    /// The eligible set for one shop slot. <paramref name="nation"/> null means
    /// wildcard (slot 2); a nation string means the home-region filter (slot 1).
    ///
    /// NO BANNER GATING, mirroring the reward slot's standing ruling rather
    /// than inventing a second rule: BANNER_FEATURED_SLOTS is 3 and no nation
    /// designs more than 3 Rare companions (Mondstadt 3, Inazuma 2, Fontaine
    /// 0), so the Featured Banner currently features every 5-star in every
    /// nation and is EXACTLY a no-op. Wiring it into the shop alone would make
    /// the two channels disagree about a rule neither one can currently
    /// exercise. It goes live in both channels together, when a nation ships a
    /// 4th Rare.
    /// </summary>
    public static List<CardModel> Eligible(
        Player player, CardRarity rarity, string? nation)
    {
        return All
            .Where(c => c.Rarity == rarity)
            .Where(c => IsOfferable(c, player))
            .Where(c => nation == null || (c as ICompanionCard)?.Nation == nation)
            .ToList();
    }

    /// <summary>
    /// The mod character this player is playing, or null for a base-game
    /// character. Canonical home for the lookup: CompanionSlot delegates here
    /// so the reward slot and the shop can never drift about who is who.
    /// </summary>
    public static string? CharacterId(Player player) =>
        player.Character switch
        {
            Klee => "klee",
            Furina => "furina",
            Kokomi => "kokomi",
            _ => null,
        };

    /// <summary>Home nation, driving slot 1 and the reward slot's weighting.</summary>
    public static string? HomeNation(Player player) =>
        player.Character switch
        {
            Klee => "mondstadt",
            Furina => "fontaine",
            Kokomi => "inazuma",
            _ => null,
        };
}
