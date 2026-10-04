using System.Collections.Generic;
using System.Linq;
using Godot;
using KleeMod.Cards.Furina;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod;

/// <summary>
/// Furina's complete personal pool. Generated cards are reward-eligible;
/// kit, selector, selector options, and Guest Stars are members only so their
/// CardModel.Pool lookups remain valid when they are created in combat.
/// </summary>
public sealed class FurinaCardPool : CardPoolModel
{
    public override string Title => "furina";

    // Temporary native frame while the Furina art pass is outstanding.
    public override string EnergyColorName => "silent";

    public override string CardFrameMaterialPath => "card_frame_green";

    public override Color DeckEntryCardColor => new("4AA6C8");

    public override Color EnergyOutlineColor => new("174B67");

    public override bool IsColorless => false;

    /// <summary>
    /// THE OFFER (<c>GetUnlockedCards</c>, the sole door into reward rolls,
    /// the shop and transforms): the slice's pool and her Ancients
    /// (<c>FurinaStageRoster.OfferablePool</c>).
    /// </summary>
    protected override IEnumerable<CardModel> FilterThroughEpochs(
        UnlockState unlockState, IEnumerable<CardModel> cards)
    {
        return Powers.FurinaStageRoster.OfferablePool();
    }

    /// <summary>
    /// MEMBERSHIP, the prototype rows first and as the pool (legacy cleanup
    /// stage 4, 2026-10-01): every `proto_` row she owns (the Stage's rows,
    /// its mode faces and the three Fontaine guest stars), then her Ancients
    /// (<c>tools/lint_ancient_coverage.py</c>), then the never-offered members
    /// (<see cref="FurinaOffPoolCards"/>). The shipped rows follow as members
    /// only until stage 5 deletes them.
    /// </summary>
    protected override CardModel[] GenerateAllCards() =>
        PrototypeCards.For("furina")
            .Concat(RosterAncientCards.Furina)
            .Concat(FurinaOffPoolCards.All)
            .Distinct()
            .ToArray();
}

public static class FurinaOffPoolCards
{
    private static List<CardModel>? _all;
    private static HashSet<ModelId>? _ids;

    public static IReadOnlyList<CardModel> All => _all ??= BuildAll();

    public static HashSet<ModelId> Ids =>
        _ids ??= All.Select(card => card.Id).ToHashSet();

    private static List<CardModel> BuildAll()
    {
        // The Salon's Tab (2026-10-05) makes no card outside her pool: the
        // performer picker, Arkhe Alignment's faces and Lyney's Trick went
        // with the v2 Stage. The list stays as the one door a future token
        // takes (EB-150: a card in no pool throws inside the chooser).
        var cards = new List<CardModel>();
        return cards;
    }
}
