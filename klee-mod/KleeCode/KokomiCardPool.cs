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
/// Since legacy cleanup stage 4 (2026-10-01) the pool IS the current kit:
/// the `proto_kk_` rows are its members and the arm's roster its offer.
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

    /// <summary>
    /// THE OFFER (<c>GetUnlockedCards</c>, the sole door into reward rolls,
    /// the shop and transforms). Under the arm, her roster's pool, Ancients
    /// and co-op tier (<c>KokomiOverhaulRoster.OfferablePool</c>); with it off
    /// (the <c>-p:ShippedKits=true</c> gate only), the shipped offer less every
    /// prototype row and token.
    /// </summary>
    protected override IEnumerable<CardModel> FilterThroughEpochs(
        UnlockState unlockState, IEnumerable<CardModel> cards)
    {
#if PROTOTYPE_CARDS
        if (Powers.KokomiOverhaul.Enabled)
        {
            return Powers.KokomiOverhaulRoster.OfferablePool();
        }
#endif
        var current = PrototypeCards.Ids("kokomi");
        return base.FilterThroughEpochs(unlockState, cards)
            .Where(card => !KokomiOffPoolCards.Ids.Contains(card.Id)
                           && !current.Contains(card.Id));
    }

    /// <summary>
    /// MEMBERSHIP, the prototype rows first and as the pool (legacy cleanup
    /// stage 4, 2026-10-01): every `proto_` row she owns, then her Ancients
    /// (a character whose pool holds no Ancient softlocks Darv's Dusty Tome;
    /// <c>tools/lint_ancient_coverage.py</c>), then the never-offered members
    /// (<see cref="KokomiOffPoolCards"/>: the current kit's hand-written
    /// tokens and the shipped Burst). The shipped rows follow as members only
    /// until stage 5 deletes them.
    /// </summary>
    protected override CardModel[] GenerateAllCards() =>
        PrototypeCards.For("kokomi")
            .Concat(RosterAncientCards.Kokomi)
            .Concat(KokomiOffPoolCards.All)
            .Concat(Cards.Kokomi.Generated.KokomiCardRoster.All)
            .Distinct()
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
#if PROTOTYPE_CARDS
        // THE CASKET PASS (2026-09-28): the Tamakushi Casket's hand-written
        // token, dealt by the relic and in no pool -- Furina's Ethereal
        // Spotlight's footing.
        cards.Add(ModelDb.Card<Cards.Prototype.OpenTheCasket>());
        // THE STATUS BATCH (2026-10-01): Sea Glass Harvest's token, made only
        // by its Plan's transform and in no pool.
        cards.Add(ModelDb.Card<Cards.Prototype.SeaGlass>());
#endif
        return cards;
    }
}
