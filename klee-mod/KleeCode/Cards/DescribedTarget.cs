using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// THE ENEMY A CARD'S FACE IS BEING WRITTEN AGAINST (Varka round 5,
/// 2026-10-13, "What to change" 1: a Swirl card whose target has lost its
/// aura should say so in hand).
///
/// The base game draws a hand card's face with
/// <c>CardModel.GetDescriptionForPile(pile, target)</c>, the target being the
/// enemy the card is aimed at while the player drags it (sts2.dll decompile:
/// <c>NCard</c> runs <c>UpdateDynamicVarPreview(mode, target)</c> and then
/// that call with the same target). <c>AddExtraArgsToDescription</c>, the
/// seam the in-combat lines ride, is called inside it but is not handed the
/// target. This prefix holds the target for the length of that one call, so
/// a line can read it; the postfix puts the previous value back (a face
/// written inside a face, a hover tip, restores its caller's).
///
/// Display only: it reads nothing and changes nothing but this field.
/// </summary>
[HarmonyPatch(typeof(CardModel), nameof(CardModel.GetDescriptionForPile),
    new[] { typeof(PileType), typeof(Creature) })]
internal static class DescribedTargetPatch
{
    [HarmonyPrefix]
    public static void Prefix(CardModel __instance, Creature? target,
                              out (CardModel? Card, Creature? Target) __state)
    {
        __state = (DescribedTarget.Card, DescribedTarget.Target);
        DescribedTarget.Card = __instance;
        DescribedTarget.Target = target;
    }

    [HarmonyFinalizer]
    public static void Finalizer((CardModel? Card, Creature? Target) __state)
    {
        DescribedTarget.Card = __state.Card;
        DescribedTarget.Target = __state.Target;
    }
}

/// <summary>The face being written now and its aimed enemy
/// (<see cref="DescribedTargetPatch"/>).</summary>
public static class DescribedTarget
{
    internal static CardModel? Card { get; set; }
    internal static Creature? Target { get; set; }

    /// <summary>The enemy <paramref name="card"/>'s face is being written
    /// against, or null when it is not aimed (or another card's face is being
    /// written).</summary>
    public static Creature? For(CardModel? card) =>
        card != null && ReferenceEquals(Card, card) ? Target : null;

    /// <summary>Test seam: write a face against <paramref name="target"/>.
    /// The mod never calls it.</summary>
    public static System.IDisposable Aim(CardModel card, Creature? target)
    {
        var was = (Card, Target);
        Card = card;
        Target = target;
        return new Restore(() => (Card, Target) = was);
    }

    private sealed class Restore : System.IDisposable
    {
        private System.Action? _undo;
        public Restore(System.Action undo) => _undo = undo;
        public void Dispose()
        {
            _undo?.Invoke();
            _undo = null;
        }
    }
}
