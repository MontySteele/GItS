using System.Collections.Generic;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// EB-183 -- THE MUSTER SUBSIDY READ AS A PROPERTY OF THE EXHAUST FUNNEL.
/// The C# half of the rule the sim carries at
/// <c>tier0/engine/effects.py _op_conscript</c> (the stamp) and
/// <c>tier0/engine/refpowers.py after_card_exhausted</c> (the check).
///
/// THE QUESTION. R216 D deferred Muster's Charge subsidy into R213 E1 rather
/// than settling it, in these words: *a Mustered Companion costs 1 less,
/// Exhausts, and pays 1 Charge, so blocking with one also advances Kokomi's
/// finisher*. That sentence has two readings.
///
/// Kokomi slice 2 asked the FIRST -- it put the subsidy's SIGN on a card, so
/// the order SPENDS Charge instead of paying it. That reading lives in an
/// effect list, and it retired with the rest of slice 2 under R227 / M67 (1).
///
/// This is the SECOND, which nothing in slice 2 could express: the recruits of
/// an order that PAID for them pay no Charge when they Exhaust. It is not an
/// effect list at all. It is a flag on the RECRUIT plus a check at the FUNNEL,
/// which is why it needed its own item and its own pair.
///
/// THE QUARANTINE. This whole directory is <c>Compile Remove</c>d unless
/// <c>-p:PrototypeCards=true</c> (KleeCode.csproj), the same switch that
/// defines <c>PROTOTYPE_CARDS</c>. A release build contains no type from this
/// file, and the one seam that reads it -- the funnel in
/// <c>KokomiResources.cs</c> -- is itself inside <c>#if PROTOTYPE_CARDS</c>.
/// The targeted revert is the flag and nothing else.
///
/// SCOPED TO AN ORDER, NEVER TO THE FUNNEL AT LARGE. R226's signed Charge LAW
/// says the funnel does NOT narrow -- her own cards AND original Companions,
/// Companions INCLUDED -- and explicitly did NOT apply v3 §4(iii)'s
/// Companion-exclusion clause. A blanket carve-out here would contradict that
/// signed text. A prototype ORDER whose own recruits waive their wage asks the
/// open question and leaves the shipped rule exactly where R226 left it.
///
/// A HASHSET OF INSTANCES, matching <c>KurageMemory.MemoryCopies</c>, and for
/// the same reason: <c>CardModel</c> has no per-instance field to hang a
/// prototype stamp on, and adding one would be a shipped-surface change made
/// for a quarantined arm. Combat-scoped, cleared with the rest at
/// <c>BeforeCombatStart</c>.
/// </summary>
public static class MusterSubsidy
{
    /// <summary>
    /// The recruits whose order paid their cost down. Instance identity, not
    /// model identity: two recruits off the same CardModel can differ, because
    /// only one of their orders may have been the prototype.
    /// </summary>
    private static readonly HashSet<CardModel> Waived = new();

    /// <summary>
    /// Per-fight clear. Called from <c>KokomiResourceHooks.BeforeCombatStart</c>
    /// beside <c>KurageMemory.ClearForNewCombat</c> -- the hook the game raises
    /// once per combat, before the first turn opens (`EB-196`). The mod's hook
    /// models are singletons, so the clear is explicit; the sim gets it free
    /// because a recruit is a fresh deepcopy in a fresh CombatState.
    /// </summary>
    public static void ClearForNewCombat() => Waived.Clear();

    /// <summary>
    /// Stamp one recruit. THE ONE WRITER, called from
    /// <c>KokomiConscript.RollRecruit</c> only, and only when the order both
    /// carried <c>subsidy: waived</c> AND actually put the recruit below its
    /// printed cost. Sim twin: <c>recruit.muster_subsidised = True</c>.
    /// </summary>
    public static void NoteWaived(CardModel? recruit)
    {
        if (recruit != null) Waived.Add(recruit);
    }

    /// <summary>
    /// Does this instance's Exhaust pay Charge? THE ONE READER, called from the
    /// exhaust funnel in <c>KokomiResourceHooks.AfterCardExhausted</c>.
    /// Sim twin: <c>getattr(card, "muster_subsidised", False)</c>.
    /// </summary>
    public static bool IsWaived(CardModel? card) =>
        card != null && Waived.Contains(card);
}
