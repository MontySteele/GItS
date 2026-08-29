using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// THE STARTER SWAP, and it is ONE seam
/// (review/active/klee-sparks-2026-08-29.md sec.10.10 item 4).
///
/// Klee's printed template is 4x Ka-boom!, 4x Duck and Cover, 1x Jumpy Dumpty,
/// 1x Pop. Under the alternative cost two of those ten slots carry the PRICED
/// twins instead, and nothing else about the kit moves.
///
///   * <b>Pop -> Powder Pop.</b> Pop's whole body is one 5-damage Bomb; Powder
///     Pop's is the same Bomb plus <c>gain_spark 1</c>. That is the income the
///     sink is priced against, and it is the PICK 1 answer the seat FOLLOWed:
///     the control has to be reachable in the starter kit, not only through a
///     rare.
///   * <b>ONE Ka-boom! of four -> Ka-pow!.</b> Same 7 damage, 0 energy, Spend 1
///     Spark. Regent's own ten cards ship exactly one sink; four would make four
///     of her ten opening cards unplayable on an empty bank. How many copies
///     convert is sec.10.11 item 2 and it goes back to [USER] as a pick.
///
/// THE PRINTED SHEET DOES NOT MOVE. <c>docs/klee-cards.yaml</c> still says
/// Ka-boom! and Pop and their generated rows are untouched; only
/// <c>Klee.StartingDeck</c> moves, and only under the flag. The sim twin is
/// <c>tier0/content/loader._starter_ids</c>, which exists for the same reason:
/// both readers of a printed starter go through one seam, so the tier 0 battery
/// and the tier 0.5 run cannot disagree about what she opens with.
///
/// COMPOSES WITH THE COMPANION ROLL by construction, not by luck.
/// <c>KleeStartingCompanionsPatch.ReplaceFirst</c> matches on
/// <c>card.GetType() == typeof(Kaboom)</c>, and <c>ProtoKaboomSink</c> is not
/// that type -- so the roll can never consume the sink slot whichever position
/// it sits in.
/// </summary>
internal static class SparkStarter
{
    /// <summary>Slot 1 of the four Ka-boom!s: the priced twin, `proto_kaboom_sink`.</summary>
    internal static CardModel PricedKaboom() => ModelDb.Card<ProtoKaboomSink>();

    /// <summary>Slot 10: Pop's twin that also makes the Spark, `proto_pop_spark`.</summary>
    internal static CardModel SparkingPop() => ModelDb.Card<ProtoPopSpark>();
}
