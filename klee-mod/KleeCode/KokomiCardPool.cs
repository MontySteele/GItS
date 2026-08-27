using System.Collections.Generic;
using System.Linq;
using Godot;
using KleeMod.Cards.Kokomi;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod;

/// <summary>
/// Kokomi's complete personal pool.
///
/// Membership is a CORRECTNESS requirement, not bookkeeping: CardModel.Pool
/// walks ModelDb.AllCardPools and falls through to MockCardPool -- which
/// throws "You monster!" in a shipped build -- when nothing matches. That
/// fires when a card is DRAWN or previewed, not when it is played, so a
/// poolless card takes down whatever task owned the draw. See
/// tools/lint_pool_membership.py for the crash of record.
///
/// Every generated card is reward-eligible today. The off-pool split Klee and
/// Furina carry (kit cards, selector options, Guest Stars) has exactly one
/// member-in-waiting here: ceremonial_garment, her Burst, which is still
/// hand-write work. When it lands it goes in KokomiOffPoolCards, NOT in the
/// roster -- granted-not-drafted is the v1.9 kit invariant.
/// </summary>
public sealed class KokomiCardPool : CardPoolModel
{
    public override string Title => "kokomi";

    // Native frame borrowed while her art pass is outstanding, same standing
    // arrangement Furina shipped under. "silent" is the closest energy colour
    // to hydro in the base set.
    public override string EnergyColorName => "silent";

    public override string CardFrameMaterialPath => "card_frame_green";

    /// <summary>Watatsumi pearl-blue; also her NameColor and map colour, so
    /// the deck screen and the map read as the same character.</summary>
    public override Color DeckEntryCardColor => new("6FC8D6");

    public override Color EnergyOutlineColor => new("1E5A6B");

    public override bool IsColorless => false;

    protected override IEnumerable<CardModel> FilterThroughEpochs(
        UnlockState unlockState, IEnumerable<CardModel> cards)
    {
        return base.FilterThroughEpochs(unlockState, cards)
            .Where(card => !KokomiOffPoolCards.Ids.Contains(card.Id));
    }

    // RosterAncientCards.Kokomi: VISIBLE in the pool (Dusty Tome draws from
    // GetUnlockedCards) but never rolled, because generation filters Ancient
    // rarity upstream. A character whose pool holds no Ancient card softlocks
    // the act-2 Darv event on an empty draw -- that is the defect this concat
    // exists to prevent, and tools/lint_ancient_coverage.py is its gate.
    protected override CardModel[] GenerateAllCards() =>
        Cards.Kokomi.Generated.KokomiCardRoster.All
            .Concat(RosterAncientCards.Kokomi)
            .Concat(KokomiOffPoolCards.All)
            .ToArray();
}

/// <summary>
/// In the pool for Pool-lookup legality, filtered out of reward rolls.
///
/// Both halves are load-bearing. IN the pool, because CardModel.Pool falls
/// through to MockCardPool and throws the moment a poolless card is drawn --
/// and the kit card is drawn, into hand, every time the meter fills. OUT of
/// rewards, because granted-not-drafted is the v1.9 kit invariant: a Burst
/// you can take from a card reward is loot, and every number on her sheet was
/// measured against a Burst you cannot.
/// </summary>
public static class KokomiOffPoolCards
{
    private static List<CardModel>? _all;
    private static HashSet<ModelId>? _ids;

    public static IReadOnlyList<CardModel> All => _all ??= BuildAll();

    public static HashSet<ModelId> Ids =>
        _ids ??= All.Select(card => card.Id).ToHashSet();

    private static List<CardModel> BuildAll()
    {
        var cards = new List<CardModel>
        {
            // Kit Burst card: granted to hand by KokomiKitGrant when the
            // meter fills, never rollable.
            ModelDb.Card<CeremonialGarment>(),
        };
        // QUARANTINED prototype rows (R213 B, EB-147). Empty in every build
        // that did not set PrototypeCards=true -- the classes are not
        // compiled. Off-pool for the reason the Burst is: Pool must resolve
        // or the card throws "You monster!" on draw, and GetUnlockedCards
        // must not see it or a reward roll could offer a card nobody ruled.
        // See KleeMod.PrototypeCards.
        cards.AddRange(PrototypeCards.For("kokomi"));
        return cards;
    }
}
