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
        var offered = base.FilterThroughEpochs(unlockState, cards)
            .Where(card => !FurinaOffPoolCards.Ids.Contains(card.Id));
#if PROTOTYPE_CARDS
        // QUARANTINED, THE FURINA REFRAME'S ONE POOL SEAM (round 2 pick 1 at
        // its default, 2026-09-04). Sim twin
        // `tier0.content.loader._pool_substitutions`, read at the one door
        // `tier05.rewards.character_pool` already reads.
        //
        // THE SAME PLACE KOKOMI'S OATH SWAP SITS, and for the same reason:
        // this method feeds GetUnlockedCards, which is the SOLE path into
        // reward rolls, the shop and card transforms, so a substitution made
        // here reaches every surface that can offer her a card and no list of
        // surfaces has to be kept in step. Four shipped rows gate on a Fanfare
        // bar (12, 12, 15 and 20) that this arm's performance-only meter does
        // not reach; the arm's copies read 6, 6, 8 and 10 at the same
        // rarities, so the offer odds are untouched.
        //
        // With `FurinaReframe.Enabled` off this returns `offered` unchanged,
        // which the method checks itself rather than leaving to this call.
        offered = Powers.FurinaReframeRoster.SwapOfferedRiders(offered);
#endif
        return offered;
    }

    // RosterAncientCards.Furina: visible (Dusty Tome draws from
    // GetUnlockedCards) but never rolled -- generation filters Ancient
    // rarity upstream. Gate: tools/lint_ancient_coverage.py.
    protected override CardModel[] GenerateAllCards() =>
        FurinaCardRoster.All
            .Concat(RosterAncientCards.Furina)
            .Concat(FurinaOffPoolCards.All)
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
        var cards = new List<CardModel>(GuestStarRoster.All)
        {
            ModelDb.Card<LetThePeopleRejoice>(),
            ModelDb.Card<EtherealSpotlight>(),
            ModelDb.Card<CenterStageOption>(),
            ModelDb.Card<GuestCastOption>(),
        };
        // EB-150: the GENERATED mode faces, on the same footing as the two
        // hand-written selector options above. A choose-one option card that
        // is in no pool does not read as null on CardModel.Pool -- the getter
        // falls through to MockCardPool, whose GenerateAllCards throws
        // "You monster!" inside NChooseACardSelectionScreen._Ready(), leaving
        // the overlay's buttons unfetched; the NullReferenceException the
        // 2026-08-26 playtest logged in AfterOverlayShown() is that, and the
        // awaited selection never returns. The roster is emitted by
        // tools/gen_klee_cards.py, so a new modal card joins this list
        // without anyone having to remember to add it.
        cards.AddRange(FurinaModalOptions.All);
        // QUARANTINED prototype rows (R213 B, EB-147). Empty in every
        // build that did not set PrototypeCards=true -- the classes are not
        // compiled. Off-pool for the reason everything else here is: Pool
        // must resolve or the card throws "You monster!" on draw, and
        // GetUnlockedCards must not see it or a reward roll could offer a
        // card nobody ruled. See KleeMod.PrototypeCards.
        cards.AddRange(PrototypeCards.For("furina"));
        return cards;
    }
}
