using System;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using HarmonyLib;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
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
    internal const string SetOffTrigger = "SetOff";
    internal const string JumpyTrigger = "Jumpy";
    internal const string AscensionTrigger = "Ascension";
    internal const string RejoiceTrigger = "Rejoice";

    /// <summary>
    /// Four Winds' Ascension plays Varka's Ascension clip: he jumps and drives
    /// one blade into the ground, and the ground burst plays at its point and,
    /// mirrored, under the target ([USER], 2026-10-13: "let's drop the twirl
    /// and instead show him jumping up and then driving one blade into the
    /// ground, with a mirrored ground particle effect on him and the target
    /// enemy"). Only that card: the visual paper names no other. A scene
    /// without an `ascension` state lunges as for an attack.
    /// </summary>
    internal static bool IsAscensionPlay(CardModel card)
        => card is ProtoVkFourWindsAscension;

    /// <summary>
    /// The wait after the Ascension trigger before the card's own play goes
    /// on. None: its attack command then waits Varka's AttackAnimDelay, which
    /// is his attack's main impact (0.6 s), so the hit lands just after the
    /// blade goes in at 0.5 s rather than a cast delay later.
    /// </summary>
    internal const float AscensionDelay = 0f;

    /// <summary>
    /// Let the People Rejoice plays Furina's Rejoice clip: she spins once and
    /// opens into the flourish, up on the front toe with both arms flung up
    /// and wide (review/active/furina-visual-paper-2026-10-13.md, the
    /// signature trigger; ruled with phase A, [USER]: "Furina looks good!").
    /// Only that card. A scene without a `rejoice` state lunges as for an
    /// attack.
    /// </summary>
    internal static bool IsRejoicePlay(CardModel card)
        => card is ProtoFsLetThePeopleRejoice;

    /// <summary>
    /// The wait after the Rejoice trigger before the card's own play goes
    /// on: its Spend (the gold burst, during the spin), then its attack
    /// command, which waits Furina's AttackAnimDelay (0.4 s). 0.2 + 0.4 puts
    /// the hit on the flourish, the clip's frame 12 at 0.6 s
    /// (tools/char_render/furina_frames.json, <c>rejoice.events.main</c>).
    /// </summary>
    internal const float RejoiceDelay = 0.2f;

    /// <summary>
    /// A Jumpy Dumpty card plays Klee's Jumpy Dumpty clip, whatever its type:
    /// she heaves the head-sized bomb with both hands ([USER], 2026-10-13:
    /// "I think the increased size would be fitting for her Jumpty Dumpty
    /// skill usage"; her normal attack's bomb is about 60% of her head). The
    /// starter, its Mk.III and the Archaic Tooth's Mk.Omega. Ahead of Set Off
    /// should a Jumpy Dumpty ever also set off. A scene without a `jumpy`
    /// state lunges as for an attack.
    /// </summary>
    internal static bool IsJumpyPlay(CardModel card)
        => card is ProtoKoJumpyDumpty or ProtoKoJumpyDumptyMkIii or JumpyDumptyMkOmega;

    /// <summary>
    /// A Set Off card of this mod plays Klee's Set Off clip, whatever its
    /// type: a hop with both fists thrown up, rendered from the model
    /// (review/active/klee-visual-paper-2026-10-12.md; the floating-bombs
    /// splash it replaced was retired 2026-10-13). Same delay as a cast. A
    /// scene without a `setoff` state lunges as for an attack.
    /// </summary>
    internal static bool IsSetOffPlay(CardModel card, bool definedByThisMod)
        => definedByThisMod && card is ISetOffCard;

    /// <summary>
    /// A SET OFF ATTACK KEEPS THE HOP TO ITS OWN HIT (in-game check
    /// 2026-10-16, `klee/09-setoff-dense-*`: Kaboom! played the throw). The
    /// card's own lunge is absorbed only while the tree is still in the
    /// setoff clip (0.85 s), and on a dense field the Bombs going off first
    /// outlast it, so the hit's "Attack" reached an idle tree and threw a
    /// bomb. For the rest of a Set off Attack's play, that "Attack" is sent
    /// as "SetOff" instead: absorbed while the hop still plays (travel to the
    /// current state is a no-op), a second hop on the hit if it has ended.
    /// Marked per creature at the play's start and cleared at the next play's
    /// start. Pure.
    /// </summary>
    internal static string RemapDuringPlay(string trigger, bool inSetOffAttackPlay)
        => inSetOffAttackPlay && trigger == "Attack" ? SetOffTrigger : trigger;

    private static readonly ConditionalWeakTable<Creature, object> SetOffAttackPlays = new();
    private static readonly object Marker = new();

    /// <summary>Whether this creature is inside a Set off Attack's play.</summary>
    internal static bool InSetOffAttackPlay(Creature? creature)
        => creature != null && SetOffAttackPlays.TryGetValue(creature, out _);

    private static void NoteSetOffAttackPlay(Creature creature, bool isSetOffAttack)
    {
        SetOffAttackPlays.Remove(creature);
        if (isSetOffAttack) SetOffAttackPlays.Add(creature, Marker);
    }

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

        // Varka's and Furina's element layer colours itself from the card
        // being played, so every play is noted, an Attack's too (its own
        // command lunges).
        ElementTrail.NotePlay(creature, card, cardPlay!.Target);

        var ours = DefinedByThisMod(card);
        var trigger = IsJumpyPlay(card) ? JumpyTrigger
            : IsAscensionPlay(card) ? AscensionTrigger
            : IsRejoicePlay(card) ? RejoiceTrigger
            : IsSetOffPlay(card, ours) ? SetOffTrigger
            : TriggerFor(card.Type, ours);
        NoteSetOffAttackPlay(creature,
            trigger == SetOffTrigger && card.Type == CardType.Attack);
        if (trigger == null) return;
        if (trigger == JumpyTrigger)
        {
            // the big bomb flies at the card's own target (the starter and
            // Mk.III aim at one enemy; Mk.Omega at all, so the side's centre)
            ThrownProjectile.NoteAim(creature, cardPlay!.Target);
        }
        var character = card.Owner!.Character;
        var delay = trigger == PowerUpTrigger ? character.PowerUpAnimDelay
            : trigger == AscensionTrigger ? AscensionDelay
            : trigger == RejoiceTrigger ? RejoiceDelay
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
