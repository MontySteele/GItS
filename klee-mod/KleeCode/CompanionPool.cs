using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// The queryable companion surface: "which companions may be offered to THIS
/// player, in THIS nation, at THIS rarity". Track A of the §4.7 shop sprint.
///
/// NOT THE POOL OBJECT. The shared companions' <c>CardPoolModel</c> is
/// <see cref="CompanionCardPool"/> (legacy review pick 4, [USER] 2026-10-18:
/// "Shared companions move to their own pool with a neutral frame, out of
/// Klee's"); it holds them so <c>CardModel.Pool</c> resolves and gives them
/// the Colorless frame. This class is the OFFER question, which a pool cannot
/// answer because it is not told the player: <c>MerchantCardEntry</c> takes a
/// plain <c>IEnumerable&lt;CardModel&gt;</c>, so the shop reads this class
/// directly.
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
    ///
    /// AND IT IS THE ONE DOOR. <see cref="CompanionSlot"/> and the shop's
    /// <see cref="Eligible"/> read this property rather than
    /// <c>CompanionRoster.All</c> directly, so "which companions exist for this
    /// run" has a single definition and the reward slot and the shop cannot be
    /// given different answers. That was already true by coincidence -- both
    /// read the same generated list -- and it is now
    /// true by construction, because the Mondstadt companion overhaul
    /// (R213 B) redirects exactly this property.
    /// </summary>
    public static IReadOnlyList<CardModel> All =>
        Powers.CompanionOverhaulRoster.Roster();

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
        if (IsHiddenFrom(card, CharacterId(player))) return false;
        return comp.PersonalPool is null || comp.PersonalPool == CharacterId(player);
    }

    /// <summary>
    /// A Universal that is never offered to one character: the Inazuma
    /// roster's "Yae Miko -- Sesshou Sakura" stays for the others and is
    /// hidden from Yae's own offers (her card paper, pick 5 (a), ruled
    /// 2026-10-13: "her Sakura are her kit's"). Her second card, Sacred
    /// Sakura's Favor, is offered to her (the Inazuma review, 2026-10-18).
    /// Sim twin: <c>yae_shrine.hidden_from</c>. PURE.
    /// </summary>
    public static bool IsHiddenFrom(CardModel card, string? characterId) =>
        characterId == Powers.YaePrototype.CharacterId
        && card is Cards.Prototype.Generated.ProtoMiYaeSesshouSakura;

    /// <summary>
    /// The eligible set for one shop slot. <paramref name="nation"/> null means
    /// wildcard (slot 2); a nation string means the home-region filter (slot 1).
    ///
    /// NO BANNER. Every offerable companion is eligible in every run: the
    /// Featured Banner, which once let only three five-stars per nation be
    /// offered in a given run, was scrapped everywhere ([USER] 2026-10-18,
    /// "Agreed on (a)!"). Personal pools and <see cref="IsHiddenFrom"/> still
    /// apply through <see cref="IsOfferable"/>.
    ///
    /// §4.7: if the nation has no card at this rarity, slot 1 falls through on
    /// the merchant patch's ladder -- that is the ladder's job, not this
    /// method's; Eligible just returns fewer cards.
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
            // VARKA (prototype batch one): a roster character, so the reward
            // clamp, the companion shop and his Knights' personal pool all
            // know him. Matched on the identity interface, which compiles
            // with the surface, as the class does.
            Powers.IVarkaCharacter => Powers.VarkaPrototype.CharacterId,
            // YAE MIKO (2026-10-13): a roster character, Varka's terms.
            Powers.IYaeCharacter => Powers.YaePrototype.CharacterId,
            _ => null,
        };

    /// <summary>Home nation, driving slot 1 and the reward slot's weighting.</summary>
    public static string? HomeNation(Player player) =>
        player.Character switch
        {
            Klee => "mondstadt",
            Furina => "fontaine",
            Kokomi => "inazuma",
            Powers.IVarkaCharacter => "mondstadt",
            Powers.IYaeCharacter => "inazuma",
            _ => null,
        };
}
