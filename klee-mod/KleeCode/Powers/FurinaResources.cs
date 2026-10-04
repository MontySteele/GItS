using System;
using System.Collections.Generic;
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
/// Marker for Furina's CharacterModel, her identity gate: in co-op the other
/// seat is not hers, and every Stage rule asks this first.
/// </summary>
public interface IFurinaCharacter
{
}

/// <summary>
/// Furina's identity. Her shipped meters (Encore, the Fanfare meter and her
/// Burst) went with the shipped kits (legacy cleanup stage 5); the Stage's
/// Fanfare is one number on her (<see cref="FurinaStage"/>).
/// </summary>
public static class FurinaResources
{
    /// <summary>
    /// Is this creature Furina? THE QUESTION IS ANSWERED, never thrown.
    ///
    /// `EB-727`: this used to take a non-nullable <c>Creature</c> and
    /// dereference it, so a caller with no creature -- a compendium page, a
    /// card on a shelf, a hook fired on a board being torn down -- got a
    /// NullReferenceException where the honest answer is "no, that is not
    /// Furina". Several call sites already hold a <c>Creature?</c>, and two
    /// of them (<c>FurinaStage.LiveFor</c>)
    /// had each grown their own null test in front of this one. A predicate
    /// that cannot answer for the absent case makes every caller carry the
    /// guard, and the first caller that forgets it is a crash -- so the guard
    /// lives here, once, at the source.
    /// </summary>
    public static bool IsFurina(Creature? creature) =>
        creature?.Player?.Character is IFurinaCharacter;
}

/// <summary>
/// Furina's combat hooks: the Curtain Call windows (Quick Change's first
/// Attack, the per-turn HP lost). The Stage's own hooks are
/// <c>FurinaStageHooks</c>'s; since the re-founding no hit touches the stage.
/// </summary>
public sealed class FurinaResourceHooks : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static FurinaResourceHooks? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<FurinaResourceHooks>(
            ModelDb.GetId<FurinaResourceHooks>());
        yield return _instance;
    }

    /// <summary>Quick Change's first-Attack draw, for every seat.</summary>
    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await CurtainCallHooks.NoteCardPlayed(choiceContext, cardPlay);
    }

    /// <summary>Her per-turn windows open at the top of her turn.</summary>
    public override Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side != CombatSide.Player) return Task.CompletedTask;
        foreach (var creature in participants)
        {
            if (FurinaResources.IsFurina(creature))
            {
                CurtainCallHooks.ResetTurn(creature);
            }
        }
        return Task.CompletedTask;
    }

    /// <summary>The per-turn HP-lost window (Curtain Call's readers).</summary>
    public override Task AfterCurrentHpChanged(Creature creature, decimal delta)
    {
        if (delta < 0m && FurinaResources.IsFurina(creature))
        {
            CurtainCallHooks.NoteHpLost(creature, (int)Math.Ceiling(-delta));
        }
        return Task.CompletedTask;
    }
}
