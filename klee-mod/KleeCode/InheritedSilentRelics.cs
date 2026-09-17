using System;
using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.RelicPools;

namespace KleeMod;

/// <summary>
/// THE ONE CURATION OF THE BORROWED SILENT RELIC ROSTER.
///
/// All three kits (Klee, Kokomi, Furina) resolve their relic pool to
/// <c>ModelDb.RelicPool&lt;SilentRelicPool&gt;().AllRelics</c> plus their own
/// starter — see the census
/// <c>review/active/inherited-potions-relics-census-2026-09-16.md</c>, which
/// counted that roster off the shipped DLL: 8 relics, identical membership for
/// all three.
///
/// TWO OF THE EIGHT ARE DROPPED, on [USER]'s ruling of QUEUE pick
/// `fanout-picks-2026-09-16 4.3` at its default (2026-09-16):
///
///   * <c>HelicalDart</c> — "after playing a card tagged Shiv, gain Dexterity".
///     No card in <c>docs/klee-cards.yaml</c>, <c>docs/kokomi-cards.yaml</c> or
///     <c>docs/furina-cards.yaml</c> carries <c>Shiv</c>. It can only fire off
///     another item in this same inherited set (CunningPotion, NinjaScroll), so
///     it advertises a card type none of the three sheets has.
///   * <c>SneckoSkull</c> — "Poison you apply is increased by 1". No card in
///     any of the three sheets applies Poison (0 hits in all three), so the
///     only Poison it can amplify is the inherited set's own.
///
/// Every OTHER inherited relic and every inherited potion is left exactly as
/// it was. <c>RingOfTheSnake</c> stays pooled although the census rules it
/// dead: it is dead by RARITY (Starter is never rolled as a reward), not by
/// membership, and removing it would change nothing a seat can see.
///
/// THE DROP IS FROM OUR THREE POOLS ONLY, and it has to be. The two relics
/// remain members of <c>SilentRelicPool</c> itself, which is what
/// <c>RelicModel.Pool</c> — a non-virtual
/// <c>AllRelicPools.First(p =&gt; p.AllRelicIds.Contains(Id))</c> that THROWS
/// for a poolless relic — resolves them through, for Silent's own runs and for
/// ours. Silent precedes all three of our characters in
/// <c>AllCharacters</c>, so <c>First()</c> already took the Silent pool before
/// this change and still does after it. Nothing here can make a relic
/// poolless.
/// </summary>
public static class InheritedSilentRelics
{
    /// <summary>
    /// The two inherited relics the ruling drops, named as TYPES rather than
    /// as id strings so a game patch that renames one breaks the BUILD instead
    /// of silently restoring it to all three pools.
    /// </summary>
    public static readonly IReadOnlyList<Type> Dropped = new[]
    {
        typeof(MegaCrit.Sts2.Core.Models.Relics.HelicalDart),
        typeof(MegaCrit.Sts2.Core.Models.Relics.SneckoSkull),
    };

    /// <summary>
    /// The borrowed Silent roster with <see cref="Dropped"/> removed. Every
    /// one of the three pools goes through here and none reads
    /// <c>ModelDb.RelicPool&lt;SilentRelicPool&gt;()</c> directly — pinned by
    /// <c>InheritedSilentRelicsTests</c>, so a fourth pool cannot quietly
    /// inherit the uncurated eight.
    /// </summary>
    public static IEnumerable<RelicModel> Curated() =>
        ModelDb.RelicPool<SilentRelicPool>().AllRelics.Where(IsKept);

    /// <summary>
    /// Whether a relic survives the curation. <c>IsInstanceOfType</c> rather
    /// than a <c>GetType()</c> equality so a mutable copy or a subclass of a
    /// dropped relic is dropped with it.
    /// </summary>
    public static bool IsKept(RelicModel relic) =>
        !Dropped.Any(dropped => dropped.IsInstanceOfType(relic));
}
