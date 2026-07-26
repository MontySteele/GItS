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
    /// Is this one of OUR characters? The mod must not change anything for a
    /// base StS2 character, so every entry point that alters behaviour gates
    /// on this first.
    ///
    /// C2 named this. The predicate already existed as `HostsCompanions`, and
    /// the reward-draw clamp needed the same question asked for an unrelated
    /// reason -- nothing to do with companions. A gate named for one of its two
    /// callers is how a later reader concludes the other caller is a mistake.
    /// One predicate, two names, the general one primary.
    /// </summary>
    public static bool IsRosterCharacter(Player player) => CharacterId(player) != null;

    /// <summary>
    /// Does this player's character host the companion system at all? Base
    /// StS2 characters must see a completely unmodified shop, so every entry
    /// point gates on this first. Identical to <see cref="IsRosterCharacter"/>
    /// by construction: the roster and the companion hosts are the same set,
    /// and if they ever diverge this is the line that splits.
    /// </summary>
    public static bool HostsCompanions(Player player) => IsRosterCharacter(player);

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
    /// BANNER GATING WENT LIVE 2026-07-25 (R64). This used to read "NO BANNER
    /// GATING", because BANNER_FEATURED_SLOTS is 3 and no nation designed more
    /// than 3 Rare companions (Mondstadt 3, Inazuma 2, Fontaine 0) -- the
    /// Featured Banner featured every 5-star in every nation and was EXACTLY a
    /// no-op. That ruling named its own trigger: "It goes live in both channels
    /// together, when a nation ships a 4th Rare." Fontaine shipped its fourth,
    /// so it does, and the reward slot gained the same filter in the same
    /// change -- wiring the shop alone is precisely what that ruling forbade.
    ///
    /// §4.7: if the banner has emptied the nation's Rare tier, slot 1 falls
    /// through to Uncommon exactly as the reward slot does. That fallthrough is
    /// the ladder's job, not this method's -- Eligible just returns fewer cards.
    /// </summary>
    public static List<CardModel> Eligible(
        Player player, CardRarity rarity, string? nation)
    {
        return All
            .Where(c => c.Rarity == rarity)
            .Where(c => IsOfferable(c, player))
            .Where(c => CompanionBanner.IsOffered(c, player))
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
