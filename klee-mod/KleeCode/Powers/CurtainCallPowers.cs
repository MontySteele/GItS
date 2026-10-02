using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// The Curtain Call sweep's surviving activity windows (R85): Courtroom
/// Drama's first reaction each turn, Quick Change's first Attack each turn,
/// and the per-turn HP-lost and intent reads their callers ask. The Salon and
/// Encore halves went with the shipped kits (legacy cleanup stage 5).
/// Mirrors: cross_examination -> reactions.py resolve_hit; first_attack_draw
/// -> refpowers.py after_card_played.
/// </summary>
public static class CurtainCallHooks
{
    // Per-turn windows, keyed by owner. Cleared at the top of Furina's turn;
    // a key whose combat is gone is dropped on every reset.
    private static readonly Dictionary<Creature, int> AttacksPlayed = new();
    private static readonly Dictionary<Creature, int> HpLost = new();

    private static int Get(Dictionary<Creature, int> map, Creature creature) =>
        map.TryGetValue(creature, out var value) ? value : 0;

    private static int PowerAmount<T>(Creature creature) where T : PowerModel =>
        creature.Powers.OfType<T>().FirstOrDefault()?.Amount ?? 0;

    public static void ResetTurn(Creature creature)
    {
        AttacksPlayed.Remove(creature);
        HpLost.Remove(creature);
        Purge();
    }

    public static void NoteHpLost(Creature creature, int amount)
    {
        if (amount <= 0) return;
        HpLost[creature] = Get(HpLost, creature) + amount;
    }

    public static bool HpLostThisTurn(Creature creature) =>
        Get(HpLost, creature) > 0;

    public static bool EnemyIntendsAttack(Creature owner)
    {
        var enemies = owner.CombatState?.HittableEnemies;
        if (enemies == null) return false;
        return enemies.Any(IntendsAttack);
    }

    public static bool IntendsAttack(Creature enemy) =>
        enemy.Monster != null
        && !enemy.IsStunned
        && enemy.Monster.NextMove.Intents.Any(
            intent => intent.IntentType == IntentType.Attack);

    private static void Purge()
    {
        foreach (var stale in AttacksPlayed.Keys
                     .Concat(HpLost.Keys)
                     .Where(creature => creature.CombatState == null)
                     .Distinct()
                     .ToList())
        {
            AttacksPlayed.Remove(stale);
            HpLost.Remove(stale);
        }
    }

    /// <summary>Quick Change: the first Attack a creature plays each turn
    /// draws (sim twin refpowers.after_card_played).</summary>
    public static async Task NoteCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var owner = cardPlay.Card?.Owner?.Creature;
        if (owner == null) return;
        if (cardPlay.Card!.Type != CardType.Attack) return;

        var played = Get(AttacksPlayed, owner) + 1;
        AttacksPlayed[owner] = played;
        if (played != 1) return;

        var draw = PowerAmount<FirstAttackDrawPower>(owner);
        if (draw <= 0) return;
        if (owner.Player is not { } player) return;
        await CardPileCmd.Draw(choiceContext, draw, player);
    }

    public static bool CourtroomDramaWillAmplify(Creature? dealer) =>
        dealer != null
        && PowerAmount<CrossExaminationPower>(dealer) > 0
        && ReactionEffects.NextReactionIsFirstFor(dealer);

    public static async Task NoteFirstReaction(
        PlayerChoiceContext choiceContext, Creature target, Creature? dealer,
        CardModel? cardSource)
    {
        if (dealer == null) return;
        var amount = PowerAmount<CrossExaminationPower>(dealer);
        if (amount <= 0) return;

        await PowerCmd.Apply<VulnerablePower>(
            choiceContext, target, amount, applier: dealer,
            cardSource: cardSource);
        await PowerCmd.Apply<WeakPower>(
            choiceContext, target, amount, applier: dealer,
            cardSource: cardSource);
    }
}

/// <summary>Courtroom Drama: the first reaction each turn applies Vulnerable
/// and Weak to its target. Activity-gated on the reaction, so a silent turn
/// pays nothing and a reaction storm pays once.
///
/// `EB-591`. THE ORDER IS ON THE FACE NOW, and on this badge as well because
/// the two must not fork. The r15 lane-2 seat watched one 1-cost card take a
/// body from 50 to 19 and could not find the reason: the debuff lands INSIDE
/// the reaction (<see cref="CurtainCallHooks.NoteFirstReaction"/>, reached
/// from <c>ReactionEffects.Resolve</c>) one hook before the triggering hit's
/// number is final, so the hit that applied the Vulnerable is itself moved by
/// it. THE ENGINE IS NOT WHAT MOVED: that phase is RULED and pinned in both
/// engines -- `tier0/tests/test_reaction_phase_parity.py`'s
/// "courtroom-drama-vulnerable-is-multiplicative" row, EB-19/M1, which exists
/// BECAUSE the mod once landed it a hook late and paid two different numbers
/// for one reaction. What was missing was the sentence. The opening clause
/// tightened to "Your first ... each turn" to pay for it under the ceiling;
/// it is the same per-dealer window it always was.</summary>
public sealed class CrossExaminationPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Courtroom Drama"),
        ("description",
            "Your first [gold]Elemental Reaction[/gold] each turn applies "
          + "{Amount} [gold]Vulnerable[/gold] and {Amount} [gold]Weak[/gold] "
          + "to its target before the hit lands."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}


/// <summary>Quick Change: the first Attack you play each turn draws.</summary>
public sealed class FirstAttackDrawPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Quick Change"),
        ("description",
            "The first Attack you play each turn draws "
          + "{Amount} card{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}
