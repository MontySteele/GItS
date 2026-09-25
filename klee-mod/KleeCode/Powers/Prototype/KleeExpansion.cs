using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// THE POOL EXPANSION (R276): the thirty rows' shared reads and the three
/// card verbs that are not about a Bomb.
///
/// WHAT A COMPANION CARD IS is <c>CompanionHexerei.CountsAsCompanion</c>'s
/// answer (R276 pick 2), read through <see cref="IsCompanionCard"/> so
/// Playdate's discount, Friendship Bracelet and the discard/hand verbs cannot
/// disagree with Klee's Spark rule or with Team Effort's ledger read. What IS
/// a Set off card is the codegen's <see cref="ISetOffCard"/> stamp, which Boom
/// Badge and Treasure Map read the same way Where Did I Put It? does.
/// </summary>
public static class KleeExpansion
{
    /// <summary>What <see cref="FetchFromDiscard"/> looks for.</summary>
    public enum FetchKind
    {
        /// <summary>Treasure Map: a card that says Set off.</summary>
        SetOff,

        /// <summary>Come Back and Play!: a Companion card.</summary>
        Companion,
    }

    private const string Table = "cards";

    /// <summary>The Set off pick's prompt, keyed on the VERB (one screen, one
    /// string, the <c>ScryTake</c> discipline). Merged into the `cards` table
    /// by <c>KleeMod.InjectLocStrings</c>, which is its only source.</summary>
    public const string SetOffPromptKey =
        "KLEEMOD-FETCH_SET_OFF.selectionScreenPrompt";

    public const string SetOffPromptText =
        "Choose a Set off card to put into your hand.";

    /// <summary>The Companion pick's prompt, on the same terms.</summary>
    public const string CompanionPromptKey =
        "KLEEMOD-FETCH_COMPANION.selectionScreenPrompt";

    public const string CompanionPromptText =
        "Choose a Companion card to put into your hand.";

    /// <summary>Is <paramref name="card"/> a Companion card?
    /// <c>CompanionHexerei.CountsAsCompanion</c>, the one reader. PURE.
    /// </summary>
    public static bool IsCompanionCard(CardModel? card) =>
        CompanionHexerei.CountsAsCompanion(card);

    /// <summary>
    /// R276 (Alice's Detonator): the card it adds, previewed as a hover tip,
    /// the base game's shape for a card that makes another (Blade Dance and
    /// Infinite Blades show a Shiv through <c>HoverTipFactory.FromCard</c>).
    /// The upgraded Detonator previews the upgraded Ka-pow!, which is the one
    /// its Power adds. Appended after <paramref name="tips"/>.
    /// </summary>
    public static IEnumerable<IHoverTip> WithKapowPreview(
        IEnumerable<IHoverTip> tips, CardModel card)
    {
        foreach (var tip in tips) yield return tip;
        yield return HoverTipFactory.FromCard<ProtoKoKapow>(card.IsUpgraded);
    }

    /// <summary>Does this card say Set off? The stamp, read. PURE.</summary>
    public static bool IsSetOffCard(CardModel? card) => card is ISetOffCard;

    /// <summary>Does this card cost Sparks -- Party Poppers' "a card that
    /// costs Sparks"? The price the cost BADGE renders (`SparkCost.PriceOf`),
    /// so an X-priced card (Fireworks Finale, Stoke the Fuse) counts and a
    /// card with no badge does not. PURE.</summary>
    public static bool CostsSparks(CardModel? card) =>
        card != null && SparkCost.PriceOf(card) > 0;

    /// <summary>The cards of <paramref name="kind"/> in
    /// <paramref name="discard"/>, in pile order. PURE -- the half of
    /// <see cref="FetchFromDiscard"/> a headless pin can read.</summary>
    public static List<CardModel> Eligible(
        IEnumerable<CardModel> discard, FetchKind kind) =>
        discard.Where(card => kind == FetchKind.SetOff
                                  ? IsSetOffCard(card)
                                  : IsCompanionCard(card))
               .ToList();

    /// <summary>
    /// Treasure Map and Come Back and Play!: the player picks ONE card of the
    /// kind out of the discard pile and it goes to the hand.
    ///
    /// NONE OF THE KIND AND THE CARD PLAYS ON: the spec's note ("if none
    /// qualifies the card still plays"), and Treasure Map's growth is a second
    /// op that runs whatever happened here. ONE CANDIDATE IS TAKEN WITHOUT A
    /// SCREEN, <c>ScryTake.Choose</c>'s rule: a choice of one is not a choice,
    /// and a screen with one card in it is a click the player owes nothing
    /// for. TOP of the hand, <c>KokomiPlan.Replay</c>'s position.
    /// </summary>
    public static async Task FetchFromDiscard(
        PlayerChoiceContext choiceContext, Player? owner, FetchKind kind)
    {
        if (owner == null) return;
        var pile = CardPile.Get(PileType.Discard, owner);
        if (pile == null) return;
        var eligible = Eligible(pile.Cards, kind);
        if (eligible.Count == 0) return;

        CardModel? pick;
        if (eligible.Count == 1)
        {
            pick = eligible[0];
        }
        else
        {
            var prompt = new LocString(
                Table, kind == FetchKind.SetOff
                           ? SetOffPromptKey : CompanionPromptKey);
            pick = (await CardSelectCmd.FromSimpleGrid(
                choiceContext, eligible, owner,
                new CardSelectorPrefs(prompt, 1))).FirstOrDefault();
        }
        if (pick == null) return;
        await CardPileCmd.Add(pick, PileType.Hand, CardPilePosition.Top);
    }

    /// <summary>
    /// The Companion cards a random draw may produce for
    /// <paramref name="owner"/>: the run's companion pool
    /// (<see cref="CompanionPool.All"/>, the one door the reward slot reads),
    /// less every Personal that is someone else's -- the predicate every other
    /// door applies (<see cref="CompanionPool.IsOfferable"/>). Sorted by id so
    /// the roll is reproducible. PURE.
    /// </summary>
    public static List<CardModel> RandomCompanionPool(Player owner) =>
        CompanionPool.All
            .Where(card => CompanionPool.IsOfferable(card, owner))
            .OrderBy(card => card.Id.ToString())
            .ToList();

    /// <summary>
    /// Tag Along and Adventure Club: <paramref name="amount"/> random Companion
    /// cards into the hand, each costing 0 this turn.
    ///
    /// A COMBAT-SCOPE COPY (<c>CombatState.CreateCard</c>), the rule
    /// <c>KokomiConscript.RollRecruit</c> records at length: a run-scope card
    /// is refused by the pile it is added to. EACH ROLLS ITS OWN, so two can be
    /// the same friend. THE STAND-IN HAND-OFF APPLIES, as it does to the reward
    /// slot: Klee is dealt her caretaker where a named Universal comes up.
    /// "Costs 0 this turn" is the base game's own temporary cost
    /// (<c>EnergyCost.SetThisTurn</c>, the Guest Star generator's call).
    /// </summary>
    public static async Task AddRandomCompanions(
        PlayerChoiceContext choiceContext, Player? owner, int amount)
    {
        var combat = owner?.Creature?.CombatState;
        if (owner == null || combat == null || amount <= 0) return;
        var pool = RandomCompanionPool(owner);
        if (pool.Count == 0) return;

        for (var i = 0; i < amount; i++)
        {
            var canonical = owner.RunState.Rng.CombatTargets.NextItem(pool);
            if (canonical == null) break;
            canonical = CompanionStandIns.HandOff(canonical, owner);
            var card = combat.CreateCard(canonical, owner);
            if (card == null) continue;
            card.EnergyCost.SetThisTurn(0);
            await CardPileCmd.AddGeneratedCardToCombat(
                card, PileType.Hand, owner);
        }
    }

    /// <summary>
    /// R276, THE START-OF-TURN PLACEMENTS IN ONE FIXED ORDER: Klee's Secret
    /// Base asks its question ("no enemy has a Bomb of yours") of the board as
    /// the growth left it, and only then does Dodoco's Mine land. Both Powers
    /// call this from <c>AfterPlayerTurnStart</c> -- after the draw and after
    /// rule 1's growth -- and the ledger's per-turn latch makes the second call
    /// a no-op, so the order is this method's and not the broadcast's. Sim
    /// twin: <c>klee_overhaul._turn_start_expansion</c>, same order.
    ///
    /// SPARKS 'N' SPLASH GOES FIRST (2026-09-25): its echo reads the Bombs
    /// the growth just grew, before anything new is placed, and it is the
    /// third Power that calls in here.
    /// </summary>
    public static async Task RunTurnStartPlacements(
        PlayerChoiceContext choiceContext, Player player)
    {
        var klee = player.Creature;
        if (klee == null) return;
        if (!KleeOverhaulLedger.For(klee).TakeTurnStartPlacements()) return;
        var echoes = klee.Powers.OfType<BombEchoPower>().Sum(p => p.Amount);
        if (echoes > 0) await BombEchoPower.Fire(choiceContext, klee, echoes);
        foreach (var secretBase in klee.Powers.OfType<SecretBasePower>().ToList())
        {
            if (ProtoBombPower.AnyPlacedBy(klee)) break;
            await ProtoBombPower.PlaceOnRandom(choiceContext, klee,
                                               secretBase.Amount, isMine: false,
                                               payloadMineAll: 0,
                                               cardSource: null);
        }
        foreach (var dodoco in klee.Powers.OfType<DodocoPower>().ToList())
        {
            await ProtoBombPower.PlaceOnRandom(choiceContext, klee,
                                               dodoco.Amount, isMine: true,
                                               payloadMineAll: 0,
                                               cardSource: null);
        }
    }

    /// <summary>
    /// ONE EXPLOSION, SEEN WITH ITS CHARGE. Called by
    /// <c>ProtoBombPower.Explode</c> after the explosion bus, for the four
    /// Powers whose trigger needs what the bus does not carry -- whether the
    /// charge was a MINE (Look Out!, Second Surprise), and the charge's own
    /// size and a once-per-turn latch (Aftershock), and a one-shot window
    /// (Wait For It...).
    ///
    /// A SECOND DOOR AND NOT A WIDER <c>IProtoExplosionListener</c>, for the
    /// reason <c>CompanionStandIns.OnExplosion</c> gives one call up: widening
    /// the arm's own interface for these four would re-sign every existing
    /// listener. Each Power owns its rule; this only walks them.
    /// </summary>
    internal static async Task AfterChargeExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        ProtoBombPower.ProtoCharge charge, bool reacted)
    {
        foreach (var power in applier.Powers.ToList())
        {
            if (power is IProtoChargeListener listener)
            {
                await listener.AfterChargeExploded(
                    choiceContext, applier, target, charge, reacted);
            }
        }
    }
}

/// <summary>
/// R276: a Power that answers ONE explosion with the charge in hand. See
/// <see cref="KleeExpansion.AfterChargeExploded"/>.
/// </summary>
public interface IProtoChargeListener
{
    Task AfterChargeExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        ProtoBombPower.ProtoCharge charge, bool reacted);
}
