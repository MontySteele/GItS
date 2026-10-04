using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE STAGE'S CLOCKS AND LINES (v2): the turn's flow counts reset at its top
/// (sec.8), Charlotte's draw and the turn-start powers after the draw, the
/// acts at its end (rule 1), the card-play counts, the free cards
/// (Escoffier's and Lyney's lines, The Last Act), Neuvillette's Hydro line on
/// her cards, and Sigewinne's and Wriothesley's readings.
///
/// ITS OWN LISTENER, concatenated behind the one
/// <c>SubscribeForCombatStateHooks</c> call like every other tenant, AFTER the
/// shipped end-of-turn sequencer, and a walk over nothing on a board with no
/// stage: every method's first question is <see cref="FurinaStage.LiveFor"/>.
/// </summary>
public sealed class FurinaStageHooks : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static FurinaStageHooks? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<FurinaStageHooks>(
            ModelDb.GetId<FurinaStageHooks>());
        yield return _instance;
    }

    /// <summary>
    /// THE CARDS THAT PRICE THEMSELVES OFF THE STAGE. PURE, floored at 0, and
    /// asked of the holder through <c>SparkCost.OwnerCreatureOf</c> (a
    /// canonical card has no owner):
    ///   * The Last Act: "Costs 1 less for each empty seat."
    ///   * Escoffier on stage: the first Salon summon card each turn costs 0.
    ///   * Lyney on stage: the first Cue card each turn costs 0.
    /// </summary>
    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (originalCost <= 0m) return false;
        var owner = SparkCost.OwnerCreatureOf(card);
        if (!FurinaStage.LiveFor(owner)) return false;
        if (FurinaStage.PlaysFree(owner, card))
        {
            modifiedCost = 0m;
            return true;
        }
        if (card is not Cards.Prototype.Generated.ProtoFsTheLastAct) return false;
        var empty = FurinaStage.EmptySeats(owner);
        if (empty <= 0) return false;
        modifiedCost = System.Math.Max(0m, originalCost - empty);
        return modifiedCost != originalCost;
    }

    /// <summary>NEUVILLETTE'S LINE, on her cards: "Your Hydro damage deals 2
    /// more", per hit of a Hydro card while he is on stage.</summary>
    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (target == null || dealer == null || target == dealer) return 0m;
        if (!target.IsEnemy) return 0m;
        return FurinaStage.HydroBonus(dealer, cardSource);
    }

    /// <summary>The top of her turn, before the draw: the flow counts reset,
    /// so they held through the whole end-of-turn sequence (sec.8).</summary>
    public override Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side != CombatSide.Player) return Task.CompletedTask;
        foreach (var creature in participants)
        {
            FurinaStage.OpenTurn(creature);
        }
        return Task.CompletedTask;
    }

    /// <summary>After her draw: the badge, Charlotte's extra card and the
    /// turn-start powers (<see cref="FurinaStage.TurnStart"/>), then the
    /// cues go up for the turn they forecast.</summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (!FurinaStage.LiveFor(player.Creature)) return;
        await FurinaStage.InstallBadge(player.Creature);
        await FurinaStage.TurnStart(choiceContext, player.Creature);
        Vfx.FurinaStageCues.CurtainUp(player.Creature);
    }

    /// <summary>
    /// RULE 1: the performers act at the end of her turn, front to back.
    /// <c>BeforeSideTurnEnd</c>, the broadcast the shipped end-of-turn work
    /// runs in, before the discard flush. The log clears just before the
    /// sweep it is about (`EB-735`), and the cues come down as the acts
    /// begin.
    /// </summary>
    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        foreach (var creature in participants.ToList())
        {
            if (!FurinaStage.LiveFor(creature)) continue;
            FurinaStageLedger.For(creature).ClearBeats();
            Vfx.FurinaStageCues.CurtainDown(creature);
            await FurinaStage.EndOfTurnActs(choiceContext, creature);
        }
    }

    /// <summary>A fresh per-play spend record (`stage_spent`).</summary>
    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        FurinaStage.BeginPlay(cardPlay.Card?.Owner?.Creature);
        return Task.CompletedTask;
    }

    /// <summary>The play closed: Opening Number's count, and the Salon
    /// summon and Cue cards Escoffier's and Lyney's lines count.</summary>
    public override Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        FurinaStage.NoteCardPlayed(cardPlay.Card?.Owner?.Creature,
                                   cardPlay.Card);
        return Task.CompletedTask;
    }

    /// <summary>Wriothesley's reading: what her Block stopped of a hit.
    /// </summary>
    public override Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target,
        DamageResult result, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (FurinaStage.LiveFor(target))
        {
            FurinaStage.NoteBlocked(target, result.BlockedDamage);
            Vfx.FurinaStageCues.Refresh(target);
        }
        return Task.CompletedTask;
    }

    /// <summary>Sigewinne's reading: each time Furina loses HP.</summary>
    public override Task AfterCurrentHpChanged(Creature creature, decimal delta)
    {
        if (delta < 0m && FurinaStage.LiveFor(creature))
        {
            FurinaStage.NoteHpLoss(creature);
        }
        return Task.CompletedTask;
    }
}
