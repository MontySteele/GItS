using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// FURINA'S CARD VERBS THE SHEET'S GRAMMAR CANNOT SPELL (the pool to 75,
/// <c>review/active/furina-pool-growth-2026-10-09.md</c> sec.5): one method
/// per <c>{op: furina, kind: ...}</c>, Varka's and Kokomi's shape. The row's
/// one printed number is the card's <c>FsAmount</c> var, moved by the
/// <c>furina_amount</c> upgrade key. Each method is one call into
/// <see cref="FurinaStage"/>, whose rules are the director's. Sim twin:
/// <c>tier0/engine/furina_stage.py</c>'s <c>kind</c>.
/// </summary>
public static class FurinaCards
{
    /// <summary>The var a kind's printed number rides on.</summary>
    public const string AmountVar = "FsAmount";

    private const string Table = "cards";

    /// <summary>Casting Call's grid prompt (merged into the `cards` table by
    /// <c>KleeMod.InjectLocStrings</c>, `KleeExpansion`'s terms).</summary>
    public const string TutorPromptKey =
        "KLEEMOD-FURINA_CASTING_CALL.selectionScreenPrompt";

    public const string TutorPromptText =
        "Choose a Guest Star to put into your hand.";

    /// <summary>Final Bow's grid prompt, on the same terms.</summary>
    public const string BowPromptKey =
        "KLEEMOD-FURINA_FINAL_BOW.selectionScreenPrompt";

    public const string BowPromptText =
        "Choose a guest to take a Final Bow.";

    private static int Amount(CardModel card) =>
        card.DynamicVars[AmountVar].IntValue;

    /// <summary>Encore!: "Your oldest guest acts."</summary>
    public static Task ActOldest(PlayerChoiceContext choiceContext,
                                 CardModel card, CardPlay cardPlay) =>
        FurinaStage.ActOldest(choiceContext, card.Owner?.Creature);

    /// <summary>Tutti! and Bring the House Down: "Each guest acts."</summary>
    public static Task ActAll(PlayerChoiceContext choiceContext,
                              CardModel card, CardPlay cardPlay) =>
        FurinaStage.ActAll(choiceContext, card.Owner?.Creature);

    /// <summary>Final Bow: "Choose a guest. It acts twice, then leaves."
    /// [3 times]</summary>
    public static Task FinalBow(PlayerChoiceContext choiceContext,
                                CardModel card, CardPlay cardPlay) =>
        FurinaStage.FinalBow(choiceContext, card.Owner?.Creature,
                             Amount(card));

    /// <summary>The ledger source a card's own Fanfare gain is filed
    /// under.</summary>
    public const string CardGainSource = "card";

    /// <summary>Velvet Curtain (the block gap, 2026-10-09): "Gain 2
    /// Fanfare." [3] The ledger's gain, the path Universal Revelry's gain
    /// takes, so it counts as gained Fanfare.</summary>
    public static Task GainFanfare(PlayerChoiceContext choiceContext,
                                   CardModel card, CardPlay cardPlay) =>
        FurinaStage.Gain(choiceContext, card.Owner?.Creature, Amount(card),
                         CardGainSource);

    /// <summary>
    /// Casting Call: "Put a Guest Star from your draw pile into your hand."
    /// A TUTOR (the paper's "an Uncommon tutor, not a random guest"): with
    /// more than one in the pile the player picks off a grid, one is taken
    /// without a screen (<c>KleeExpansion.FetchFromDiscard</c>'s rule), none
    /// and the card plays on. TOP of the hand.
    /// </summary>
    public static async Task TutorGuest(PlayerChoiceContext choiceContext,
                                        CardModel card, CardPlay cardPlay)
    {
        if (card.Owner is not { } owner) return;
        if (!FurinaStage.LiveFor(owner.Creature)) return;
        var pile = CardPile.Get(PileType.Draw, owner);
        if (pile == null) return;
        var eligible = pile.Cards.Where(IsGuestStar).ToList();
        if (eligible.Count == 0) return;
        CardModel? pick;
        if (eligible.Count == 1)
        {
            pick = eligible[0];
        }
        else
        {
            pick = (await CardSelectCmd.FromSimpleGrid(
                choiceContext, eligible, owner,
                new CardSelectorPrefs(new LocString(Table, TutorPromptKey), 1)))
                .FirstOrDefault();
        }
        if (pick == null) return;
        await CardPileCmd.Add(pick, PileType.Hand, CardPilePosition.Top);
    }

    /// <summary>Final Bow's pick: the seat whose guest the player chose off a
    /// grid of the guests' own Guest Star cards (the card the seat holds, or
    /// a combat copy of its row when it holds none). Seat order.</summary>
    internal static async Task<int> ChooseSeat(
        PlayerChoiceContext choiceContext, Player player,
        FurinaStageLedger ledger)
    {
        var combat = player.Creature?.CombatState;
        var shown = new List<CardModel>();
        foreach (var seat in ledger.Seats)
        {
            var face = seat.Cards.FirstOrDefault();
            if (face == null && combat != null)
            {
                face = combat.CreateCard(GuestCardOf(seat.Who), player);
            }
            if (face == null) return 0;
            shown.Add(face);
        }
        var pick = (await CardSelectCmd.FromSimpleGrid(
            choiceContext, shown, player,
            new CardSelectorPrefs(new LocString(Table, BowPromptKey), 1)))
            .FirstOrDefault();
        var index = pick == null ? 0 : shown.IndexOf(pick);
        return index < 0 ? 0 : index;
    }

    /// <summary>Is <paramref name="card"/> a Guest Star? Its type is one of
    /// the eleven rows'. PURE.</summary>
    public static bool IsGuestStar(CardModel? card) =>
        card != null && GuestCardTypes.Contains(card.GetType());

    private static readonly HashSet<System.Type> GuestCardTypes = new()
    {
        typeof(ProtoFsGuestStarCharlotte),
        typeof(ProtoFsGuestStarWriothesley),
        typeof(ProtoFsGuestStarLynette),
        typeof(ProtoFsGuestStarClorinde),
        typeof(ProtoFsGuestStarLyney),
        typeof(ProtoFsGuestStarSigewinne),
        typeof(ProtoFsGuestStarChevreuse),
        typeof(ProtoFsGuestStarFreminet),
        typeof(ProtoFsGuestStarNavia),
        typeof(ProtoFsGuestStarNeuvillette),
        typeof(ProtoFsGuestStarEscoffier),
    };

    /// <summary>A guest's Guest Star row, canonical.</summary>
    public static CardModel GuestCardOf(StagePerformer who) => who switch
    {
        StagePerformer.Wriothesley => ModelDb.Card<ProtoFsGuestStarWriothesley>(),
        StagePerformer.Lynette => ModelDb.Card<ProtoFsGuestStarLynette>(),
        StagePerformer.Clorinde => ModelDb.Card<ProtoFsGuestStarClorinde>(),
        StagePerformer.Lyney => ModelDb.Card<ProtoFsGuestStarLyney>(),
        StagePerformer.Sigewinne => ModelDb.Card<ProtoFsGuestStarSigewinne>(),
        StagePerformer.Chevreuse => ModelDb.Card<ProtoFsGuestStarChevreuse>(),
        StagePerformer.Freminet => ModelDb.Card<ProtoFsGuestStarFreminet>(),
        StagePerformer.Navia => ModelDb.Card<ProtoFsGuestStarNavia>(),
        StagePerformer.Neuvillette => ModelDb.Card<ProtoFsGuestStarNeuvillette>(),
        StagePerformer.Escoffier => ModelDb.Card<ProtoFsGuestStarEscoffier>(),
        _ => ModelDb.Card<ProtoFsGuestStarCharlotte>(),
    };
}
