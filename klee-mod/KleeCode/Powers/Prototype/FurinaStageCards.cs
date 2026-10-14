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
using MegaCrit.Sts2.Core.Models.Powers;

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
    /// random guest."</summary>
    public static Task SummonRandom(PlayerChoiceContext choiceContext,
                                    CardModel card, CardPlay cardPlay) =>
        FurinaStage.SummonRandom(choiceContext, card.Owner?.Creature);

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

    // ---- THE SWEEP (review/active/furina-sweep-2026-10-14.md sec.3) -----
    // Seven base-game verbs, each one base card's command calls (decompiled
    // sts2.dll). None needs her stage, so none is gated on it: a card of
    // hers played by anyone does what it prints. The three that change when
    // upgraded read IsUpgraded (`furina_upgraded`). Sim twin:
    // `furina_stage.kind`.

    /// <summary>Read the Script's grid prompt.</summary>
    public const string LookPromptKey =
        "KLEEMOD-FURINA_READ_THE_SCRIPT.selectionScreenPrompt";

    public const string LookPromptText =
        "Choose a card to put into your [gold]Hand[/gold]. The rest are discarded.";

    /// <summary>Mise en Scene's hand prompt.</summary>
    public const string FreePromptKey =
        "KLEEMOD-FURINA_MISE_EN_SCENE.selectionScreenPrompt";

    public const string FreePromptText = "Choose a card to cost 0.";

    /// <summary>Second Act's discard-pile prompt.</summary>
    public const string ReturnPromptKey =
        "KLEEMOD-FURINA_SECOND_ACT.selectionScreenPrompt";

    public const string ReturnPromptText =
        "Choose a card to put into your [gold]Hand[/gold].";

    /// <summary>Stand-In's hand prompt.</summary>
    public const string CopyPromptKey =
        "KLEEMOD-FURINA_STAND_IN.selectionScreenPrompt";

    public const string CopyPromptText = "Choose a card to copy.";

    private static List<CardModel> HandOf(Player owner) =>
        CardPile.Get(PileType.Hand, owner)?.Cards.ToList()
        ?? new List<CardModel>();

    /// <summary>Costume Fitting: "Upgrade a card in your Hand for this
    /// combat." [ALL cards] Armaments' body: <c>FromHandForUpgrade</c>, or
    /// every upgradable hand card upgraded.</summary>
    public static async Task UpgradeInHand(PlayerChoiceContext choiceContext,
                                           CardModel card, CardPlay cardPlay)
    {
        if (card.Owner is not { } owner) return;
        if (card.IsUpgraded)
        {
            foreach (var c in HandOf(owner).Where(c => c.IsUpgradable))
            {
                CardCmd.Upgrade(c);
            }
            return;
        }
        var pick = await CardSelectCmd.FromHandForUpgrade(
            choiceContext, owner, card);
        if (pick != null) CardCmd.Upgrade(pick);
    }

    /// <summary>Quick Change: "Discard your Hand, then draw that many
    /// cards." [plus 1] Calculated Gamble's body.</summary>
    public static async Task DiscardHandRedraw(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        if (card.Owner is not { } owner) return;
        var hand = HandOf(owner);
        var count = hand.Count + (card.IsUpgraded ? 1 : 0);
        if (hand.Count == 0)
        {
            if (count > 0) await CardPileCmd.Draw(choiceContext, count, owner);
            return;
        }
        await CardCmd.DiscardAndDraw(choiceContext, hand, count);
    }

    /// <summary>Read the Script: "Look at the top 4 cards of your Draw Pile.
    /// Put 1 into your Hand; discard the rest." One seen card is taken
    /// without a screen (<see cref="ScryTake"/>'s rule).</summary>
    public static async Task LookTakeDiscard(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        if (card.Owner is not { } owner) return;
        var top = CardPile.Get(PileType.Draw, owner)?.Cards
                      .Take(Amount(card)).ToList()
                  ?? new List<CardModel>();
        if (top.Count == 0) return;
        CardModel? pick = top.Count == 1
            ? top[0]
            : (await CardSelectCmd.FromSimpleGrid(
                choiceContext, top, owner,
                new CardSelectorPrefs(new LocString(Table, LookPromptKey), 1)))
                .FirstOrDefault();
        if (pick != null)
        {
            await CardPileCmd.Add(pick, PileType.Hand, CardPilePosition.Top);
        }
        var rest = top.Where(c => !ReferenceEquals(c, pick)).ToList();
        if (rest.Count > 0) await CardCmd.Discard(choiceContext, rest);
    }

    /// <summary>Mise en Scene: "Choose a card in your Hand. It costs 0 this
    /// turn." [until played] Enlightenment's cost calls, reduce-only, on one
    /// chosen card that costs Energy.</summary>
    public static async Task FreeInHand(PlayerChoiceContext choiceContext,
                                        CardModel card, CardPlay cardPlay)
    {
        if (card.Owner is not { } owner) return;
        var pick = (await CardSelectCmd.FromHand(
            choiceContext, owner,
            new CardSelectorPrefs(new LocString(Table, FreePromptKey), 1),
            c => !c.EnergyCost.CostsX && c.EnergyCost.GetResolved() > 0,
            card)).FirstOrDefault();
        if (pick == null) return;
        if (card.IsUpgraded)
        {
            pick.EnergyCost.SetUntilPlayed(0, reduceOnly: true);
        }
        else
        {
            pick.EnergyCost.SetThisTurn(0, reduceOnly: true);
        }
    }

    /// <summary>Intermission: "Retain your Hand this turn." Equilibrium's
    /// call: the base game's <c>RetainHandPower</c>, 1.</summary>
    public static async Task RetainHand(PlayerChoiceContext choiceContext,
                                        CardModel card, CardPlay cardPlay)
    {
        if (card.Owner?.Creature is not { } creature) return;
        await PowerCmd.Apply<RetainHandPower>(
            choiceContext, creature, 1m, creature, card);
    }

    /// <summary>Second Act: "Put a card from your Discard Pile into your
    /// Hand." Hologram's body.</summary>
    public static async Task DiscardToHand(PlayerChoiceContext choiceContext,
                                           CardModel card, CardPlay cardPlay)
    {
        if (card.Owner is not { } owner) return;
        var pile = CardPile.Get(PileType.Discard, owner);
        if (pile == null || pile.Cards.Count == 0) return;
        var pick = (await CardSelectCmd.FromCombatPile(
            choiceContext, pile, owner,
            new CardSelectorPrefs(new LocString(Table, ReturnPromptKey), 1)))
            .FirstOrDefault();
        if (pick != null) await CardPileCmd.Add(pick, PileType.Hand);
    }

    /// <summary>Stand-In: "Choose a card in your Hand. Add a copy of it to
    /// your Hand. The copy Exhausts." Dual Wield's clone, any card type, with
    /// Exhaust added to the copy (Wolfpack's <c>AddKeyword</c>).</summary>
    public static async Task CopyInHand(PlayerChoiceContext choiceContext,
                                        CardModel card, CardPlay cardPlay)
    {
        if (card.Owner is not { } owner) return;
        var pick = (await CardSelectCmd.FromHand(
            choiceContext, owner,
            new CardSelectorPrefs(new LocString(Table, CopyPromptKey), 1),
            null, card)).FirstOrDefault();
        if (pick == null) return;
        var copy = pick.CreateClone();
        copy.AddKeyword(CardKeyword.Exhaust);
        await CardPileCmd.AddGeneratedCardToCombat(copy, PileType.Hand, owner);
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
