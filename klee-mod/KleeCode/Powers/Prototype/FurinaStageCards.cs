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
/// <c>review/ruled/furina-pool-growth-2026-10-09.md</c> sec.5): one method
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
        "Choose a Guest Star to put into your [gold]Hand[/gold].";

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

    /// <summary>Ensemble Cast (the diversity pass, 2026-10-11): "Summon a
    /// random guest." [2 random guests] (the upgrade census, 2026-10-23: its
    /// <c>FsAmount</c>, was cost -1). Each is one not on stage when it
    /// comes.</summary>
    public static async Task SummonRandom(PlayerChoiceContext choiceContext,
                                          CardModel card, CardPlay cardPlay)
    {
        for (var i = 0; i < Amount(card); i++)
        {
            await FurinaStage.SummonRandom(choiceContext, card.Owner?.Creature);
        }
    }

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
    /// Casting Call: "Put a Guest Star from your draw pile into your hand. If
    /// you can't, draw 2 cards." A TUTOR (the paper's "an Uncommon tutor, not
    /// a random guest"): with more than one in the pile the player picks off
    /// a grid, one is taken without a screen
    /// (<c>KleeExpansion.FetchFromDiscard</c>'s rule). TOP of the hand. With
    /// none in the pile it draws its <c>FsAmount</c> instead (the diversity
    /// pass, 2026-10-11: the floor).
    /// </summary>
    public static async Task TutorGuest(PlayerChoiceContext choiceContext,
                                        CardModel card, CardPlay cardPlay)
    {
        if (card.Owner is not { } owner) return;
        if (!FurinaStage.LiveFor(owner.Creature)) return;
        var pile = CardPile.Get(PileType.Draw, owner);
        var eligible = pile?.Cards.Where(IsGuestStar).ToList()
                       ?? new List<CardModel>();
        if (eligible.Count == 0)
        {
            await CardPileCmd.Draw(choiceContext, Amount(card), owner);
            return;
        }
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

    // ---- THE SWEEP, SECOND SET (review/active/furina-sweep-2026-10-14.md
    // sec.3) -------------------------------------------------------------
    // Five verbs the grammar cannot spell. None needs her stage except
    // Verdict, which reads her Fanfare (zero for anyone else). Sim twin:
    // `furina_stage.kind`.

    /// <summary>Stage Directions' hand prompt.</summary>
    public const string DirectionsPromptKey =
        "KLEEMOD-FURINA_STAGE_DIRECTIONS.selectionScreenPrompt";

    public const string DirectionsPromptText =
        "Choose a card to put on top of your [gold]Draw Pile[/gold].";

    /// <summary>Ousia / Pneuma: "Flip." The card turns to its other face
    /// (<see cref="FurinaFlip"/>), after the face it was played on has
    /// resolved.</summary>
    public static Task Flip(PlayerChoiceContext choiceContext,
                            CardModel card, CardPlay cardPlay)
    {
        FurinaFlip.Turn(card);
        return Task.CompletedTask;
    }

    /// <summary>Stage Directions: "Put a card from your Hand on top of your
    /// Draw Pile. It costs 0 next turn." Headbutt's move, from the hand; the
    /// cost is set at the start of her next turn
    /// (<see cref="FurinaSweep.CostZeroNextTurn"/>), as the base game's
    /// "this turn" (this turn or until played). One card is taken without a
    /// screen.</summary>
    public static async Task StageDirections(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        if (card.Owner is not { } owner) return;
        var hand = CardPile.Get(PileType.Hand, owner)?.Cards
                       .Where(c => !ReferenceEquals(c, card)).ToList()
                   ?? new List<CardModel>();
        if (hand.Count == 0) return;
        var pick = hand.Count == 1
            ? hand[0]
            : (await CardSelectCmd.FromHand(
                choiceContext, owner,
                new CardSelectorPrefs(new LocString(Table, DirectionsPromptKey), 1),
                c => !ReferenceEquals(c, card), card)).FirstOrDefault();
        if (pick == null) return;
        await CardPileCmd.Add(pick, PileType.Draw, CardPilePosition.Top);
        FurinaSweep.CostZeroNextTurn(owner.Creature, pick);
    }

    /// <summary>Facade: "Gain Block equal to the HP you have lost this
    /// combat, up to 12." [16] Any HP loss, a Drain included
    /// (<see cref="FurinaSweep.LostThisCombat"/>); card Block, so Dexterity
    /// and Frail fold it.</summary>
    public static async Task Facade(PlayerChoiceContext choiceContext,
                                    CardModel card, CardPlay cardPlay)
    {
        if (card.Owner?.Creature is not { } creature) return;
        var amount = System.Math.Min(FurinaSweep.LostThisCombat(creature),
                                     Amount(card));
        if (amount <= 0) return;
        await CreatureCmd.GainBlock(
            creature,
            new MegaCrit.Sts2.Core.Localization.DynamicVars.BlockVar(
                amount, MegaCrit.Sts2.Core.ValueProps.ValueProp.Move),
            cardPlay);
    }

    /// <summary>Encore Performance: "Play the top card of your Discard Pile
    /// for free. Exhaust it." Havoc's body off the Discard Pile
    /// (<c>CardPileCmd.AutoPlayFromDrawPile</c>: to the play pile, then
    /// <c>CardCmd.AutoPlay</c> with <c>ExhaustOnNextPlay</c>). The top card
    /// is the last one discarded.</summary>
    public static async Task EncorePerformance(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        if (card.Owner is not { } owner) return;
        var top = CardPile.Get(PileType.Discard, owner)?.Cards.LastOrDefault();
        if (top == null || ReferenceEquals(top, card)) return;
        await CardPileCmd.Add(top, PileType.Play);
        top.ExhaustOnNextPlay = true;
        await CardCmd.AutoPlay(choiceContext, top, null);
    }

    /// <summary>Verdict of the Oratrice: "Choose an enemy. If its HP is no
    /// higher than your Fanfare, it dies. Otherwise deal damage equal to your
    /// Fanfare." It does not spend her Fanfare. The death is
    /// <c>CreatureCmd.Kill</c>, the base game's Doom execute, so it reaches a
    /// boss as Doom does. The damage is a Skill's card damage
    /// (<c>ValueProp.Move</c>: her Strength counts), not an Attack.</summary>
    public static async Task Verdict(PlayerChoiceContext choiceContext,
                                     CardModel card, CardPlay cardPlay)
    {
        if (card.Owner?.Creature is not { } creature) return;
        if (cardPlay.Target is not { IsAlive: true } target) return;
        var fanfare = FurinaStage.FanfareOf(creature);
        if (fanfare <= 0) return;
        if (target.CurrentHp <= fanfare)
        {
            await CreatureCmd.Kill(target);
            return;
        }
        await CreatureCmd.Damage(choiceContext, target, fanfare,
                                 MegaCrit.Sts2.Core.ValueProps.ValueProp.Move,
                                 creature, card, cardPlay);
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

    /// <summary>The eleven Guest Stars, canonical, in her pool's order: what
    /// "Choose 1 of 3 random Guest Stars" (her story, A Steambird Clipping)
    /// draws from. A list, not <see cref="GuestCardTypes"/>, so the draw's
    /// order is fixed on every client.</summary>
    public static IReadOnlyList<CardModel> GuestStars() => new CardModel[]
    {
        ModelDb.Card<ProtoFsGuestStarCharlotte>(),
        ModelDb.Card<ProtoFsGuestStarWriothesley>(),
        ModelDb.Card<ProtoFsGuestStarLynette>(),
        ModelDb.Card<ProtoFsGuestStarClorinde>(),
        ModelDb.Card<ProtoFsGuestStarLyney>(),
        ModelDb.Card<ProtoFsGuestStarSigewinne>(),
        ModelDb.Card<ProtoFsGuestStarChevreuse>(),
        ModelDb.Card<ProtoFsGuestStarFreminet>(),
        ModelDb.Card<ProtoFsGuestStarNavia>(),
        ModelDb.Card<ProtoFsGuestStarNeuvillette>(),
        ModelDb.Card<ProtoFsGuestStarEscoffier>(),
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
