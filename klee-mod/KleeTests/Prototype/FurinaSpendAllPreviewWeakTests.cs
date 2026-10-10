using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>The collection for pins that put
/// <c>CombatManager.Instance</c> into a combat for a moment. The game reads
/// that one static everywhere, so nothing else may run alongside.</summary>
[CollectionDefinition(Name, DisableParallelization = true)]
public sealed class CombatInProgressSwitch
{
    public const string Name = "CombatInProgressSwitch";
}

/// <summary>
/// The Block-card round (<c>review/records/furina-block-round-2026-10-10.md</c>,
/// "What to change" 1): "Bravura and Let the People Rejoice previews (164 and
/// 152) ignored Weak 2."
///
/// THE SEAT'S SCREEN. The transcript shows both numbers on a "Choose up to 2
/// cards to put into your Hand" grid, not in her hand. The base game runs the
/// damage hooks only for a card in the Hand or Play pile
/// (<c>CardModel.UpdateDynamicVarPreview</c>: <c>runGlobalHooks</c> is
/// <c>Pile.Type is Hand or Play</c>). Anywhere else
/// <c>CalculatedDamageVar</c> prints its formula, Fanfare included, with no
/// Weak, Strength or Vulnerable. That is every calculated attack's
/// convention, the base game's included.
///
/// IN HER HAND the Spend-all face runs the game's own
/// <c>CalculatedDamageVar.UpdateCardPreview</c>, which hands
/// <c>Hook.ModifyDamage</c> her creature as the dealer, so Weak folds. These
/// pins run that preview for real on a real Bravura, Weak 2 on Furina and
/// 38 Fanfare (the seat's count), and compare it with the engine's own
/// composition of the same hit (<see cref="HitOrder.Compose"/>, pinned pair
/// by pair in <c>HitOrderPinTests</c>).
///
/// HOW THE PREVIEW IS REACHED HEADLESS. Three things a live combat supplies
/// are supplied here and nothing else: a run state and a combat state that
/// answer only <c>IterateHookListeners</c> (her powers and the target's), the
/// card placed in her real Hand pile (or Draw pile, for the grid case), and <c>CombatManager.Instance</c> marked in progress so
/// <c>CalculatedVar.Calculate</c> reads the multiplier. The last is a
/// process-wide static, put back in a finally, in a collection that runs
/// alone.
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class FurinaSpendAllPreviewWeakTests
{
    private const int SeatFanfare = 38;

    /// <summary>A run state and a combat state that answer one question:
    /// who listens to hooks.</summary>
    public class ListenerProxy : DispatchProxy
    {
        public List<AbstractModel> Listeners = new();

        protected override object? Invoke(MethodInfo? m, object?[]? args)
        {
            if (m!.Name == "IterateHookListeners") return Listeners;
            if (m.Name == "get_HittableEnemies") return Array.Empty<Creature>();
            if (m.Name == "get_Enemies") return Array.Empty<Creature>();
            throw new NotSupportedException(m.Name);
        }
    }

    internal sealed class Board
    {
        public required Seat Furina;
        public required Creature Enemy;
        public required CardModel Card;
    }

    internal static Board Build(CardModel card, Action<Seat>? furinaPowers = null,
                               Action<Seat>? enemyPowers = null,
                               bool inHand = true,
                               Func<Seat>? owner = null)
    {
        FurinaStageLedger.ResetAll();
        // `owner` seats another character with the card in hand (the
        // null-target preview pins); the board's field keeps its name.
        var furina = (owner?.Invoke() ?? Seat.Furina(66)).WithCombatState();
        furinaPowers?.Invoke(furina);
        var enemySeat = Seat.Klee(234);
        enemyPowers?.Invoke(enemySeat);
        var enemy = enemySeat.Creature;

        var listeners = furina.Creature.Powers.Concat(enemy.Powers)
            .Cast<AbstractModel>().ToList();
        var run = DispatchProxy.Create<IRunState, ListenerProxy>();
        ((ListenerProxy)(object)run).Listeners = listeners;
        var combat = DispatchProxy.Create<ICombatState, ListenerProxy>();
        ((ListenerProxy)(object)combat).Listeners = listeners;

        Seat.Force(furina.Player, "RunState", run);
        furina.Creature.CombatState = combat;

        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", furina.Player);
        // The card sits in a real combat pile, so `card.Pile` and
        // `card.CombatState` answer as they do in a fight. The run deck is
        // left empty (an uninitialised Player has none).
        Seat.Force(furina.Player, "RunPiles", Array.Empty<CardPile>());
        var state = furina.Player.PlayerCombatState!;
        var pile = inHand ? state.Hand : state.DrawPile;
        ((List<CardModel>)typeof(CardPile)
            .GetField("_cards", HeadlessGame.All)!.GetValue(pile)!).Add(card);

        FurinaStageLedger.For(furina.Creature).Gain(SeatFanfare);
        return new Board { Furina = furina, Enemy = enemy, Card = card };
    }

    /// <summary>Run <paramref name="body"/> with the combat manager in a
    /// combat, and put it back.</summary>
    internal static void InCombat(Action body)
    {
        var field = typeof(CombatManager).GetField("_turnState", HeadlessGame.All)!;
        var saved = field.GetValue(CombatManager.Instance);
        var turn = RuntimeHelpers.GetUninitializedObject(field.FieldType);
        Seat.Set(turn, "IsInProgress", true);
        field.SetValue(CombatManager.Instance, turn);
        try
        {
            Assert.True(CombatManager.Instance.IsInProgress);
            body();
        }
        finally
        {
            field.SetValue(CombatManager.Instance, saved);
            FurinaStageLedger.ResetAll();
        }
    }

    internal static decimal Preview(CardModel card, Creature? target, bool inHand)
    {
        var var = card.DynamicVars.CalculatedDamage;
        var.UpdateCardPreview(card, CardPreviewMode.Normal, target,
                              runGlobalHooks: inHand);
        return var.PreviewValue;
    }

    /// <summary>Bravura's formula at the seat's Fanfare: 6 + 2 x 38.</summary>
    private const decimal BravuraFormula = 6m + 2m * SeatFanfare;

    [Fact]
    public void Bravura_in_hand_under_weak_2_previews_the_weakened_hit()
    {
        InCombat(() =>
        {
            var b = Build(new ProtoFsBravura(),
                          f => f.WithPower<WeakPower>(2));
            Assert.Equal(BravuraFormula,
                         b.Card.DynamicVars.CalculatedDamage.Calculate(null));

            var preview = Preview(b.Card, null, inHand: true);

            // 82 x 0.75 = 61.5, printed 61: Weak folded, once.
            Assert.Equal(61.5m, preview);
            Assert.Equal(HitOrder.Compose(b.Furina.Creature, null,
                                          BravuraFormula, ValueProp.Move,
                                          b.Card),
                         preview);
            Assert.NotEqual(BravuraFormula, preview);
        });
    }

    [Fact]
    public void Bravura_aimed_folds_strength_weak_and_the_targets_vulnerable()
    {
        InCombat(() =>
        {
            var b = Build(new ProtoFsBravura(),
                          f => f.WithPower<WeakPower>(2).WithPower<StrengthPower>(3),
                          e => e.WithPower<VulnerablePower>(2));

            var preview = Preview(b.Card, b.Enemy, inHand: true);

            // (82 + 3) x 0.75 x 1.5 = 95.625: the engine's order, one product.
            Assert.Equal(95.625m, preview);
            Assert.Equal(HitOrder.Compose(b.Furina.Creature, b.Enemy,
                                          BravuraFormula, ValueProp.Move,
                                          b.Card),
                         preview);
        });
    }

    [Fact]
    public void Let_the_people_rejoice_in_hand_under_weak_2_previews_the_weakened_hit()
    {
        InCombat(() =>
        {
            var b = Build(new ProtoFsLetThePeopleRejoice(),
                          f => f.WithPower<WeakPower>(2));
            const decimal formula = 0m + 2m * SeatFanfare;

            var preview = Preview(b.Card, null, inHand: true);

            Assert.Equal(formula * 0.75m, preview);
            Assert.Equal(HitOrder.Compose(b.Furina.Creature, null, formula,
                                          ValueProp.Move, b.Card),
                         preview);
        });
    }

    [Fact]
    public void Off_her_hand_the_face_prints_the_formula_as_every_calculated_attack_does()
    {
        // The seat's screen: a card grid, so the game passes
        // runGlobalHooks false and no hook runs -- the base game's own
        // CalculatedDamageVar, unchanged by this mod.
        InCombat(() =>
        {
            var b = Build(new ProtoFsBravura(),
                          f => f.WithPower<WeakPower>(2), inHand: false);
            Assert.Equal(PileType.Draw, b.Card.Pile!.Type);

            Assert.Equal(BravuraFormula, Preview(b.Card, null, inHand: false));
        });
    }
}
