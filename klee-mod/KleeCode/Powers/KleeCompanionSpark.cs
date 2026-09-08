using System.Threading.Tasks;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;

namespace KleeMod.Powers;

/// <summary>
/// "Little Hexenzirkul" -- Klee's kit answering a HEXEREI Companion play, and
/// the only place in this assembly where a Companion play mints Sparks.
///
/// `EB-642`, R265 pick 1: WHAT THE KIT DECLARES IS THE PRINTED WORD. [USER]
/// played act 1 and read the second mark as noise -- "the 'Klee's own' text on
/// the Personals is not needed" -- so a Universal printing <c>Hexerei</c> now
/// grants exactly as a Personal printing it does, and the ownership mark leaves
/// the faces in the same commit (<c>gen_klee_cards._family_tags</c>). One word,
/// one rule: the mark and the payment say the same thing, or the r20 defect
/// returns pointing the other way.
///
/// LAW:145, countersigned R224 (2026-08-30): "Companion cards may not
/// themselves grant signature resources. A character-owned engine may respond
/// to a Companion play and generate its resource where that character's kit
/// explicitly declares the trigger and bounds the amount generated per
/// Companion play." So the grant lives HERE, in Klee's kit, and
/// <c>PruneWitchHunt</c> -- which used to print two <c>SparkPower.Gain</c>
/// calls -- prints none (EB-219).
///
/// SIM MIRROR: <c>tier0/engine/effects.py klee_companion_spark</c>,
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
    /// <summary>Any paying Companion play. tier0 KLEE_COMPANION_SPARK_BASE.</summary>
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
    /// Does this Companion play pay Klee a Spark? The kit's own question, and
    /// the sim asks it in the same three steps
    /// (<c>effects.klee_companion_spark</c>).
    ///
    /// A COMPANION ONLY OFF THE ARM (`EB-663`, r24 lane 1). The old test was
    /// COMPANION *and* Hexerei, so a Klee card carrying the mark -- Alice's
    /// Introduction Magic itself, or any card her this-turn window marks --
    /// printed the keyword, fired the family's readers (Coven Errand, Witches'
    /// Circle) and paid nothing. One word cannot mean two sets on one screen,
    /// so under the arm the test is exactly
    /// <c>CompanionHexerei.IsHexerei</c>. Off the arm the Companion gate
    /// stays, because that is the world LAW:145's clause was countersigned
    /// over. The character gate below is untouched either way.
    ///
    /// PLAYED BY KLEE (`EB-434`). The old spelling asked the CARD's pool
    /// against its owner and named no character, so Kokomi playing Gorou banked
    /// a Spark she has no surface to read. Sparks are Klee's resource and the
    /// tip says "gives Klee"; nobody else is paid.
    ///
    /// AND CARRYING THE MARK (`EB-642`) -- under the arm. The Hexerei family is
    /// <c>CompanionHexerei.IsHexerei</c>, the readers' own
    /// question, so the word means one thing on every surface that asks it. OFF
    /// the arm the shipped Personal pool answers instead, and that is R213 B
    /// rather than taste: no shipped sheet row carries <c>hexerei:</c> at all,
    /// so a Hexerei-only rule would silently retire the grant <c>EB-219</c>
    /// moved into the kit at parity. The Balance surface does not move for a
    /// prototype arm.
    /// </summary>
    public static bool PaysKleesSpark(CardModel? card)
    {
        if (card == null) return false;
        var owner = card.Owner;
        if (owner == null) return false;
        if (CompanionPool.CharacterId(owner) != "klee") return false;
#if PROTOTYPE_CARDS
        if (KleeOverhaul.Enabled)
            return CompanionHexerei.IsHexerei(card);
#endif
        return card is ICompanionCard comp && comp.PersonalPool == "klee";
    }

    /// <summary>
    /// Arm the trigger, pre-resolution. Called once per PLAY from
    /// <c>KleeElementalHooks.BeforeCardPlayed</c>, beside
    /// <c>CompanionPlays.Record</c>.
    /// </summary>
    public static void Arm(CardPlay cardPlay)
    {
        _reactionsAtPlayStart = PaysKleesSpark(cardPlay.Card)
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
            // `EB-418`. THE NAME IS THE RULE'S AND NOT ANY CARD'S. The grant
            // moved off Prune's face at `EB-219` and the trigger is keyed on a
            // SET, so every card in it walks this line -- the r11 seat's
            // unnamed Spark was Diona's. A ledger row saying "prune" over a
            // Diona play is the same unreadable number one surface in.
            //
            // THE KEY DOES NOT MOVE AT `EB-642`, deliberately: it is the
            // ledger's stable id for the one kit rule that pays here, aggregated
            // by `MeterLedger` and pinned from the sim side, and the set it
            // names widened rather than became a different rule.
            source: "companion:personal/play");
    }
}
