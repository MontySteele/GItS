#nullable enable

using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using HarmonyLib;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

// THE KOKOMI CARD PAPER V2 (2026-10-18, review/active/kokomi-cards-2026-10-18.md
// sec.2, picks 1 (b), 2 (a), 3 (a)). Draft the Orders' discount, Tidal
// Rebuke's Block spend and Tidal Riposte's stored bonus. Endless Shoal's and
// Kurage Canopy's Sting-or-Ward clause is on their own classes
// (KokomiRefounding.OnCarriedOut, KurageCanopyBasePower). Sim twins in
// tier0/engine/kokomi_plan.py, same names.

public static partial class KokomiCards
{
    private static readonly Dictionary<CardModel, int> _blockLost = new();

    /// <summary>Tidal Rebuke: "Lose all your Block." The amount is kept for
    /// the damage clause after it ("Deal twice that"), which reads it through
    /// <see cref="BlockLostThisPlay"/>. Sim twin: the `lose_all_block`
    /// kind.</summary>
    public static async Task LoseAllBlock(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var kokomi = card.Owner?.Creature;
        if (kokomi == null) return;
        var lost = (int)kokomi.Block;
        _blockLost[card] = lost;
        if (lost > 0)
        {
            await CreatureCmd.LoseBlock(choiceContext, kokomi, lost, kokomi);
        }
    }

    /// <summary>The Block Tidal Rebuke's play just lost; in a preview (the
    /// card still in hand, nothing lost yet) the Block she stands behind, so
    /// the face's "(Deals N damage)" reads what playing it would do.</summary>
    public static int BlockLostThisPlay(CardModel card)
    {
        var kokomi = SparkCost.OwnerCreatureOf(card);
        if (kokomi == null) return 0;
        if (card.Pile?.Type == PileType.Hand) return (int)kokomi.Block;
        return _blockLost.TryGetValue(card, out var lost)
            ? lost : (int)kokomi.Block;
    }
}

/// <summary>
/// Draft the Orders (Kokomi card paper v2, sec.2 change 1): "The next card you
/// plan this turn costs 1 less."
///
/// THE COST SEAM CANNOT SEE THE TARGET. <c>TryModifyEnergyCostInCombat</c> is
/// handed a card and no play (`EB-668`), and "plan" is a fact about the play:
/// the card is dragged onto the Bake-Kurage. So the discount is shown on every
/// card in hand that has a Plan line (each one could be the card planned), and
/// <see cref="KokomiPlanCost"/> takes it back off a play aimed anywhere else:
/// <c>PlayCardAction.ExecuteAction</c> knows its target before it checks the
/// price and spends the Energy, and the patch below records it. A card the
/// discount alone made affordable, played normally, is refused, as any card is
/// whose Energy is short.
///
/// SPENT BY THE FIRST CARD PLANNED THAT IT CHEAPENED: a planned 0-cost card
/// (a Sting, a Ward) does not spend it. Copies add to the one discount, which
/// is spent whole (Playdate's rule). Gone at the end of the turn either way.
/// Sim twin: <c>kokomi_plan.DRAFT_THE_ORDERS</c>.
/// </summary>
public sealed class DraftTheOrdersPower : PowerModel, ILocalizationProvider
{
    private CardPlay? _spendingOn;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Draft the Orders"),
        ("description",
            "The next card you [gold]plan[/gold] this turn costs "
          + "[blue]{Amount}[/blue] less."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Can this card be planned at all (a printed Plan line)?</summary>
    public static bool Plannable(CardModel? card) =>
        card is IPlannedCard { PlanClauses.Count: > 0 };

    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (SparkCost.OwnerCreatureOf(card) != Owner) return false;
        if (originalCost <= 0m || !Plannable(card)) return false;
        if (KokomiPlanCost.PlayedOffThePet(card)) return false;
        modifiedCost = System.Math.Max(0m, originalCost - Amount);
        return true;
    }

    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        _spendingOn = null;
        var card = cardPlay.Card;
        if (card?.Owner?.Creature != Owner) return Task.CompletedTask;
        if (cardPlay.IsAutoPlay || !KokomiPlan.PlayedOnPet(cardPlay))
        {
            return Task.CompletedTask;
        }
        if (!Plannable(card)) return Task.CompletedTask;
        if (card!.EnergyCost.GetWithModifiers(CostModifiers.Local) <= 0)
        {
            return Task.CompletedTask;
        }
        _spendingOn = cardPlay;
        return Task.CompletedTask;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!ReferenceEquals(_spendingOn, cardPlay)) return;
        _spendingOn = null;
        await PowerCmd.Remove(this);
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// The one card play the game is pricing right now, and whether it is aimed
/// at the Bake-Kurage. Written by the <c>PlayCardAction.ExecuteAction</c>
/// patch before the action checks the price and spends the Energy, cleared
/// when the action is over. Read only by <see cref="DraftTheOrdersPower"/>.
/// </summary>
public static class KokomiPlanCost
{
    private static CardModel? _card;
    private static bool _onPet;

    /// <summary>Is <paramref name="card"/> being played right now, and NOT
    /// on the Bake-Kurage?</summary>
    public static bool PlayedOffThePet(CardModel card) =>
        ReferenceEquals(_card, card) && !_onPet;

    internal static CardModel? Capture(PlayCardAction action)
    {
        var card = action.NetCombatCard.ToCardModelOrNull();
        if (!DraftTheOrdersPower.Plannable(card))
        {
            return null;
        }
        _card = card;
        _onPet = BakeKuragePet.Is(action.Target);
        return card;
    }

    internal static async Task ReleaseAfter(Task inner, CardModel? card)
    {
        try
        {
            await inner;
        }
        finally
        {
            if (card != null && ReferenceEquals(_card, card)) _card = null;
        }
    }
}

// lint: no-seat: records which card a play action is about and whether its
// target is the Bake-Kurage, for Draft the Orders' cost hook; only a card with
// a Plan line (Kokomi's) is recorded. It resolves no seat and changes nothing
// about the play itself.
[HarmonyPatch(typeof(PlayCardAction), "ExecuteAction")]
internal static class PlayCardAction_PlanTarget_Patch
{
    [HarmonyPrefix]
    private static void Prefix(PlayCardAction __instance, out CardModel? __state)
    {
        __state = null;
        try
        {
            __state = KokomiPlanCost.Capture(__instance);
        }
        catch (System.Exception)
        {
            // A card the net table cannot resolve yet: no discount decision.
        }
    }

    [HarmonyPostfix]
    private static void Postfix(ref Task __result, CardModel? __state)
    {
        if (__state == null) return;
        __result = KokomiPlanCost.ReleaseAfter(__result, __state);
    }
}

/// <summary>
/// Tidal Riposte's stored bonus (Kokomi card paper v2, sec.2 change 4): "your
/// next Attack deals N more damage."
///
/// VIGOR'S SHAPE, ONE CARD WIDE. The base game's <c>VigorPower</c> latches the
/// first powered attack and adds its Amount to that attack's hits, then spends
/// it. This latches the next Attack CARD she plays face-up
/// (<c>BeforeCardPlayed</c>) and adds the whole stack to every powered hit
/// that card deals, then spends it (<c>AfterCardPlayed</c>), the
/// <see cref="NextAttackRiderPower"/> latch. Two things it will not be spent
/// by: an Attack written on the Bake-Kurage (no hit now), and a Plan the
/// Bake-Kurage carries out (its hits are unpowered, and a flipped now-line is
/// no card play). Until it is latched, the bonus is shown on the hand's
/// previews only. Sim twin: <c>kokomi_plan.TIDAL_RIPOSTE_CHARGE</c>.
/// </summary>
public sealed class TidalRiposteChargePower : PowerModel, ILocalizationProvider
{
    private CardPlay? _spendingOn;
    private int _spending;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Riposte"),
        ("description",
            "Your next Attack deals [blue]{Amount}[/blue] additional damage. A "
          + "carried-out [gold]Plan[/gold] does not spend it."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        _spendingOn = null;
        _spending = 0;
        if (cardPlay.Card?.Type != CardType.Attack) return Task.CompletedTask;
        if (cardPlay.Card?.Owner?.Creature != Owner) return Task.CompletedTask;
        if (KokomiPlan.PlayedOnPet(cardPlay)) return Task.CompletedTask;
        _spendingOn = cardPlay;
        _spending = (int)Amount;
        return Task.CompletedTask;
    }

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        if (_spendingOn != null)
        {
            return ReferenceEquals(cardSource, _spendingOn.Card) ? Amount : 0m;
        }
        // Not latched: the hand's preview (no play) shows it; a hit with a
        // play attached that never latched (a flipped Plan) gets nothing.
        return cardPlay == null ? Amount : 0m;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!ReferenceEquals(_spendingOn, cardPlay)) return;
        _spendingOn = null;
        var spent = _spending;
        _spending = 0;
        if (spent <= 0) return;
        if (Amount <= spent)
        {
            await PowerCmd.Remove(this);
            return;
        }
        await PowerCmd.ModifyAmount(
            choiceContext, this, -spent,
            applier: Owner, cardSource: null, silent: true);
    }
}
