using System;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using HarmonyLib;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Hooks;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Vfx;

/// <summary>
/// THE CAST AND POWER-UP MOTION on our own Skill and Power plays (motion
/// pass, 2026-10-02).
///
/// HOW THE BASE DOES IT. There is no engine-side hook: about 228 of the 596
/// base cards open their own <c>OnPlay</c> with
/// <c>CreatureCmd.TriggerAnim(Owner.Creature, "Cast", Owner.Character.CastAnimDelay)</c>
/// (a Skill, e.g. <c>Alchemize</c>) or the same call with "PowerUp" and
/// <c>PowerUpAnimDelay</c> (a Power, e.g. <c>Accelerant</c>). <c>OnPlay</c>
/// runs inside <c>CardModel</c>'s play loop straight after
/// <c>Hook.BeforeCardPlayed</c>, once per play in a series. None of our cards
/// make that call (0 hits under Cards/ and Powers/), so a Skill turn showed no
/// body motion at all.
///
/// WHAT THIS DOES. A postfix on <c>Hook.BeforeCardPlayed</c> chains exactly
/// that call onto the hook's task, for cards defined in THIS assembly only --
/// a base card already makes its own call, and doubling it would replay the
/// clip. Same trigger, same delay property, same moment (the hook's end is
/// <c>OnPlay</c>'s start), so the timing and the cast SFX path are the base's.
/// <c>TriggerAnim</c> lands in <see cref="CreatureAnimationRouter"/>, which
/// picks the scene's <c>cast</c>/<c>power</c> state or falls back silently.
/// Character-agnostic: it reads the card's own type and the owner's own
/// character, never a name.
///
/// It also refreshes the owner's low-HP idle on EVERY card play, ours or the
/// base's, so a fight that opens at a quarter HP slumps by the first play
/// rather than waiting for the first hit.
/// </summary>
internal static class CardPlayMotion
{
    internal const string CastTrigger = "Cast";
    internal const string PowerUpTrigger = "PowerUp";

    /// <summary>
    /// The trigger a play of this card should send, or null for none. Pure:
    /// Skill -> Cast, Power -> PowerUp (the base's own pairing), and nothing
    /// for an Attack (its <c>AttackCommand</c> already lunges), a Status, a
    /// Curse, or any card this mod did not define.
    /// </summary>
    internal static string? TriggerFor(CardType type, bool definedByThisMod)
    {
        if (!definedByThisMod) return null;
        return type switch
        {
            CardType.Skill => CastTrigger,
            CardType.Power => PowerUpTrigger,
            _ => null,
        };
    }

    internal static bool DefinedByThisMod(CardModel card)
        => card.GetType().Assembly == typeof(CardPlayMotion).Assembly;

    internal static async Task Then(Task hook, CardPlay cardPlay)
    {
        await hook;
        var card = cardPlay?.Card;
        var creature = card?.Owner?.Creature;
        if (card == null || creature == null || creature.IsDead) return;

        RefreshLowHealth(card);

        var trigger = TriggerFor(card.Type, DefinedByThisMod(card));
        if (trigger == null) return;
        var character = card.Owner!.Character;
        var delay = trigger == PowerUpTrigger
            ? character.PowerUpAnimDelay
            : character.CastAnimDelay;
        await CreatureCmd.TriggerAnim(creature, trigger, delay);
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    private static void RefreshLowHealth(CardModel card)
    {
        try
        {
            CreatureAnimationRouter.RefreshLowHealth(
                card.Owner?.Creature?.GetCreatureNode());
        }
        catch (Exception e)
        {
            // A pose must never cost a card play.
            Log.Warn($"[{KleeMod.ModId}] low-HP idle refresh skipped: {e.Message}");
        }
    }
}

[HarmonyPatch(typeof(Hook), nameof(Hook.BeforeCardPlayed))]
internal static class Hook_BeforeCardPlayed_CardPlayMotion
{
    [HarmonyPostfix]
    public static void Postfix(ref Task __result, CardPlay cardPlay)
        => __result = CardPlayMotion.Then(__result, cardPlay);
}
