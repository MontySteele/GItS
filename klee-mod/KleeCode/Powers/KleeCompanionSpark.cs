using System.Threading.Tasks;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;

namespace KleeMod.Powers;

/// <summary>
/// "Little Hexenzirkul" -- Klee's kit answering a PERSONAL Companion play, and
/// the only place in this assembly where a Companion play mints Sparks.
///
/// LAW:145, countersigned R224 (2026-08-30): "Companion cards may not
/// themselves grant signature resources. A character-owned engine may respond
/// to a Companion play and generate its resource where that character's kit
/// explicitly declares the trigger and bounds the amount generated per
/// Companion play." So the grant lives HERE, in Klee's kit, and
/// <c>PruneWitchHunt</c> -- which used to print two <c>SparkPower.Gain</c>
/// calls -- prints none (EB-219).
///
/// SIM MIRROR: <c>tier0/engine/effects.py klee_personal_companion_spark</c>,
/// called from <c>combat._finish_play</c>. Numbers are LAW from tier0
/// (<c>constants.KLEE_COMPANION_SPARK_*</c>) and are mirrored below, never
/// re-derived.
///
/// PARITY IS THE WHOLE SPEC. Prune's shipped face paid 1 / 2 / 2 / 3 Sparks
/// across (base, no reaction) / (base, reaction) / (upgraded, no reaction) /
/// (upgraded, reaction), because she printed <c>gain_spark 1</c> inside a
/// reaction conditional AND <c>gain_spark 1</c> unconditionally, upgrading the
/// second. BASE + REACTION + UPGRADED reproduces all four, and the cap is their
/// sum rather than a fifth number.
///
/// ONCE PER PLAY, WHICH IS THE BOUND ITSELF. The trigger is armed in
/// <c>KleeElementalHooks.BeforeCardPlayed</c> and fires in
/// <c>AfterCardPlayed</c>, both gated on <c>IsFirstInSeries</c> -- the same
/// gate <c>CompanionPlays.Record</c> uses, and the phase that means "once per
/// play_card call" rather than once per replay. A replay (Study Buddy) is one
/// card being resolved twice, and a per-play bound a replay can double is not a
/// bound. This is the one place the re-authored card diverges from the face it
/// replaces, and it diverges in the direction the clause exists to enforce.
/// </summary>
public static class KleeCompanionSpark
{
    /// <summary>Any Personal Companion play. tier0 KLEE_COMPANION_SPARK_BASE.</summary>
    public const int Base = 1;

    /// <summary>...that triggered a reaction. tier0 KLEE_COMPANION_SPARK_REACTION_BONUS.</summary>
    public const int ReactionBonus = 1;

    /// <summary>...and/or is upgraded. tier0 KLEE_COMPANION_SPARK_UPGRADED_BONUS.</summary>
    public const int UpgradedBonus = 1;

    /// <summary>The bound LAW:145 requires. tier0 KLEE_COMPANION_SPARK_MAX_PER_PLAY.</summary>
    public const int MaxPerPlay = 3;

    /// <summary>
    /// The reaction count observed when the Companion's play began, or null
    /// when the play in flight is not one this trigger answers.
    ///
    /// A single field rather than a per-card map: card plays do not interleave
    /// -- <c>BeforeCardPlayed</c> and <c>AfterCardPlayed</c> bracket one
    /// resolution -- and a map keyed on a card that can be replayed is a leak
    /// waiting for the first Study Buddy. Cleared in <see cref="Settle"/>
    /// whether or not it mints, so an unarmed play can never inherit an armed
    /// one's snapshot.
    /// </summary>
    private static int? _reactionsAtPlayStart;

    /// <summary>
    /// Is this card a Personal Companion of the character playing it?
    ///
    /// Both halves matter. PERSONAL, because the declaration is over the pool
    /// and a shared companion's Swirl mints nothing. OF THE CHARACTER PLAYING
    /// IT, because it is Klee's KIT that declared the trigger -- the sim asks
    /// the identical question (<c>card.personal_pool ==
    /// state.player.character_id</c>).
    /// </summary>
    public static bool IsOwnPersonalCompanion(CardModel? card)
    {
        if (card is not ICompanionCard comp || comp.PersonalPool is null) return false;
        var owner = card.Owner;
        if (owner == null) return false;
        return comp.PersonalPool == CompanionPool.CharacterId(owner);
    }

    /// <summary>
    /// Arm the trigger, pre-resolution. Called once per PLAY from
    /// <c>KleeElementalHooks.BeforeCardPlayed</c>, beside
    /// <c>CompanionPlays.Record</c>.
    /// </summary>
    public static void Arm(CardPlay cardPlay)
    {
        _reactionsAtPlayStart = IsOwnPersonalCompanion(cardPlay.Card)
            ? ReactionEffects.TotalResolved
            : null;
    }

    /// <summary>
    /// Mint, post-resolution. Called once per PLAY from
    /// <c>KleeElementalHooks.AfterCardPlayed</c>.
    ///
    /// The reaction limb is a DIFF around the play, which is how the sim's
    /// <c>reactions_this_card</c> reads and how Prune's own face used to read
    /// it before EB-219 moved the grant -- so the question being asked has not
    /// changed, only who asks it.
    /// </summary>
    public static async Task Settle(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var start = _reactionsAtPlayStart;
        _reactionsAtPlayStart = null;
        if (start is not { } reactionsAtStart) return;
        if (cardPlay.Card?.Owner?.Creature is not { } creature) return;

        var amount = Base;
        if (ReactionEffects.TotalResolved > reactionsAtStart) amount += ReactionBonus;
        if (cardPlay.Card.IsUpgraded) amount += UpgradedBonus;
        if (amount > MaxPerPlay) amount = MaxPerPlay;
        if (amount <= 0) return;

        await SparkPower.Gain(choiceContext, creature, amount, cardPlay.Card,
            source: "companion:prune/play");
    }
}
