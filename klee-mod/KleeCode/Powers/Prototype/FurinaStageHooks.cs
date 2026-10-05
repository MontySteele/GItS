using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE KIT'S CLOCKS AND LINES (the Salon's Tab, 2026-10-05): the turn's flow
/// counts reset at its top, Grand Theater Program after the draw, the guests
/// and the Singer at its end, the HP-loss hooks that print Fanfare (rule 3)
/// and Lynette's line, and the curtain call when the combat ends.
///
/// ITS OWN LISTENER, concatenated behind the one
/// <c>SubscribeForCombatStateHooks</c> call like every other tenant, and a
/// walk over nothing on a board with no Furina: every method's first question
/// is <see cref="FurinaStage.LiveFor"/>.
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

    /// <summary>The top of her turn, before the draw: the flow counts reset,
    /// so they held through the whole end-of-turn sequence and the enemies'
    /// turn (Lynette's line reads its latch across it).</summary>
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

    /// <summary>After her draw: the badge, then Grand Theater Program, then
    /// the cues go up for the turn they forecast.</summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (!FurinaStage.LiveFor(player.Creature)) return;
        await FurinaStage.InstallBadge(player.Creature);
        await FurinaStage.TurnStart(choiceContext, player.Creature);
        Vfx.FurinaStageCues.CurtainUp(player.Creature);
    }

    /// <summary>Rule 5 and rule 4: the guests act at the end of her turn,
    /// front to back, then the Singer Repays. <c>BeforeSideTurnEnd</c>, the
    /// broadcast the shipped end-of-turn work runs in. The log clears just
    /// before the sweep it is about (`EB-735`).</summary>
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

    /// <summary>The play is over: the per-play spend record closes, so a
    /// spend-all face in hand previews her Fanfare and not the last play's
    /// spend (the Salon's Tab seat round, 2026-10-05).</summary>
    public override Task AfterCardPlayed(PlayerChoiceContext choiceContext,
                                         CardPlay cardPlay)
    {
        FurinaStage.EndPlay(cardPlay.Card?.Owner?.Creature);
        return Task.CompletedTask;
    }

    /// <summary>Rule 3: every HP she loses prints 1 Fanfare -- a hit past
    /// Block, a status, a card's own HP cost. A Drain counts its own loss
    /// (the ledger's <c>Draining</c> latch).</summary>
    public override Task AfterCurrentHpChanged(Creature creature, decimal delta)
    {
        if (delta < 0m && FurinaStage.LiveFor(creature))
        {
            FurinaStage.NoteHpLost(creature,
                                   (int)System.Math.Ceiling(-delta));
        }
        return Task.CompletedTask;
    }

    /// <summary>Lynette's line: an enemy's hit that reached her HP.</summary>
    public override Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target,
        DamageResult result, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (FurinaStage.LiveFor(target) && dealer != null && dealer.IsEnemy)
        {
            FurinaStage.NoteEnemyHit(target, (int)result.UnblockedDamage);
            Vfx.FurinaStageCues.Refresh(target);
        }
        return Task.CompletedTask;
    }

    /// <summary>THE CURTAIN CALL (sec.16): every drained HP returns when the
    /// combat ends, before the rewards, and the HP carries into the run.
    /// <c>AfterCombatEnd</c> runs inside <c>EndCombatInternal</c>, which the
    /// loss path never reaches (`PlayTelemetry.CombatEnded`).</summary>
    public override async Task AfterCombatEnd(CombatRoom room)
    {
        foreach (var furina in FurinaStageLedger.Furinas.ToList())
        {
            await FurinaStage.CurtainCall(furina);
        }
    }
}
