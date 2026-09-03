using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// THE FURINA REFRAME'S DRAIN, C# side (R220 A; the packet's sec.4.6, staged as
/// slice two). Twin of the sim's <c>effects._op_drain_fanfare</c> and of the
/// per-play count it writes, <c>CombatState.fanfare_drained_this_card</c>.
///
/// THE OP IS TWO LINES AND THIS CLASS IS THE SECOND ONE. Draining is trivial --
/// the held meter goes to nothing -- and every difficulty is in what comes
/// AFTER it on the same card, because by then the meter reads 0. The Rare's
/// hit and the Skill's Block are both priced off what the drain TOOK, so the
/// number has to survive the act of taking it. That is the whole of
/// <see cref="Amount"/>, and it is why the drain is not simply
/// <c>FurinaResources</c> with a minus sign.
///
/// ONE VALUE PATH, WHICH IS THE POINT (the Legibility sprint's rule, 2026-07-24:
/// the face, the hover preview and the resolved number must be one value). Both
/// rows render through the base game's own <c>CalculatedDamageVar</c> /
/// <c>CalculatedBlockVar</c> rail, whose multiplier is a lambda the game calls
/// BOTH while the card sits in hand and again as it resolves. So this answers
/// two questions with one method:
///
///   * <b>in hand</b>, no play in flight -- "what WOULD this drain?", which is
///     the live readable meter, so the card previews the hit it is about to
///     make;
///   * <b>resolving</b>, after the drain -- "what DID this play drain?", which
///     is the recorded amount, so the hit that lands is the hit that was shown.
///
/// A meter read alone would pay nothing every time (the drain has already run);
/// a recorded amount alone would preview nothing at all (no play has run yet).
///
/// THE RECORD IS OPENED PER CARD PLAY AND NOT CLOSED PER DRAIN.
/// <see cref="BeginPlay"/> is called from <c>FurinaResourceHooks
/// .BeforeCardPlayed</c>, inside <c>#if PROTOTYPE_CARDS</c>, which is the same
/// seam the shipped Encore spend already uses and runs before <c>OnPlay</c>.
/// Clearing at the START rather than at the end is what keeps a stale number
/// off a later preview: the next card play wipes the record before anything can
/// read it, so a drain row redrawn after being played previews the live meter
/// again rather than the number it took last time.
///
/// ONE EDGE IS DECLARED RATHER THAN DEFENDED, and the sim declares the same one
/// from the other side: a card played INSIDE another card's resolution (a free
/// play) opens its own record and the outer card's remaining reads fall back to
/// the meter. The sim saves and restores <c>fanfare_drained_this_card</c> across
/// a free play (<c>combat._FREE_PLAY_CONTEXT</c>) because that engine has one
/// list to save; here there is no card on either sheet that drains and then
/// plays another card, so the honest state is a note rather than a mechanism
/// nothing exercises.
///
/// PER CREATURE, keyed the way <see cref="FurinaReframeLedger"/> is keyed and
/// for the same reason (R205): in co-op the other seat's meter is not hers.
///
/// QUARANTINED. <c>Powers/Prototype/</c> is <c>Compile Remove</c>d from a
/// release build, so a shipped mod contains no drain at all -- and unlike the
/// four legs of <see cref="FurinaReframe"/> there is no flag to read, because
/// there is no shipped rule for this one to replace. The gate is the ROWS: only
/// a prototype card carries <c>drain_fanfare</c>, and a prototype card exists
/// only under <c>-p:PrototypeCards=true</c>.
/// </summary>
public static class FurinaDrain
{
    /// <summary>What the card currently resolving took, per seat. Absent means
    /// "no drain has happened in this play", which is what makes the fallback
    /// in <see cref="Amount"/> a preview rather than a guess.</summary>
    private static readonly Dictionary<Creature, int> _drained = new();

    /// <summary>A fresh, EMPTY record for one card play. Called from
    /// <c>FurinaResourceHooks.BeforeCardPlayed</c>; a null owner (an autoplay
    /// or token path hands one in) is a no-op rather than a throw, exactly as
    /// the three shipped lines beside it are.</summary>
    public static void BeginPlay(Creature? owner)
    {
        if (owner != null) _drained.Remove(owner);
    }

    /// <summary>
    /// TAKE THE WHOLE HELD METER, and record what was taken. Returns the amount
    /// drained, which is what the ledger and the pins read.
    ///
    /// WHAT IT DOES NOT TOUCH, each for the sim's stated reason: the FLOOR
    /// (<c>crash_fanfare</c> is the op that moves it, and moving it is that
    /// card's whole price), the CAP (a falling ceiling would make the card
    /// quietly worse the second time it is played in one combat), the FOCUS
    /// term (the reframe's scaling invariant is that Focus multiplies
    /// performance numerics and nothing else) and DECAY.
    ///
    /// A DEBT CANNOT BE DRAINED. <see cref="FurinaResources.ReadableFanfare"/>
    /// is the clamp every reader in this mod goes through, so a meter left
    /// negative by <c>crash_fanfare</c> drains 0 and stays where it is rather
    /// than paying the card for a hole.
    /// </summary>
    public static int Drain(Creature? owner)
    {
        if (owner == null || !FurinaResources.IsFurina(owner)) return 0;
        // Through the ONE mutation funnel, so the A7 delta-Block trigger
        // fires for a drain exactly as it does for a gain or a decay --
        // "whenever Fanfare changes amount" is one rule with one home.
        var drained = FurinaResources.DrainFanfare(owner);
        _drained[owner] = drained;
        FurinaReframeLedger.For(owner).NoteDrain(drained);
        return drained;
    }

    /// <summary>
    /// The count the two rows' <c>CalculatedVar</c> multipliers read: what this
    /// play drained, or -- with no play in flight -- what a play would drain.
    /// See the class note; this ONE method is what makes the previewed number
    /// and the resolved number the same number.
    /// </summary>
    public static int Amount(CardModel? card)
    {
        if (card?.Owner?.Creature is not { } owner) return 0;
        return _drained.TryGetValue(owner, out var taken)
            ? taken
            : FurinaResources.ReadableFanfare(owner);
    }

    /// <summary>Every seat's record, dropped. Test-facing, and the same
    /// courtesy <c>FurinaReframeLedger.ResetAll</c> extends: a static table
    /// keyed on live objects outlives a headless fixture otherwise.</summary>
    public static void ResetAll() => _drained.Clear();
}
