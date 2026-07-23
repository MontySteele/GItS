using System.Collections.Generic;
using System.Linq;
using Godot;
using KleeMod.Cards.Furina;
using KleeMod.Cards.Furina.Generated;
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

    protected override IEnumerable<CardModel> FilterThroughEpochs(
        UnlockState unlockState, IEnumerable<CardModel> cards)
    {
        return base.FilterThroughEpochs(unlockState, cards)
            .Where(card => !FurinaOffPoolCards.Ids.Contains(card.Id));
    }

    protected override CardModel[] GenerateAllCards() =>
        FurinaCardRoster.All.Concat(FurinaOffPoolCards.All).ToArray();
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
        var cards = new List<CardModel>(GuestStarRoster.All)
        {
            ModelDb.Card<LetThePeopleRejoice>(),
            ModelDb.Card<EtherealSpotlight>(),
            ModelDb.Card<CenterStageOption>(),
            ModelDb.Card<GuestCastOption>(),
        };
        return cards;
    }
}
