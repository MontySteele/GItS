using System;
using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Relics;

/// <summary>
/// THE ARMS' RELIC OFFER, one rule for both pools
/// (<c>review/active/relics-potions-klee-furina-2026-09-27.md</c>, pick 1(a)):
/// a character's pool is the starter, its own seven and the Ancient; the
/// Silent borrow is gone. Kokomi's pool has no override and keeps the borrow.
///
/// Pure, over the pool's own members, so the tests run it on the real
/// relic types without a booted <c>ModelDb</c>.
/// </summary>
public static class ArmRelicPools
{
    /// <summary>Klee's arm pool: Pounding Surprise, her seven, Dodoco Tales.
    /// </summary>
    public static readonly IReadOnlyList<Type> KleeArmPool =
        new[] { typeof(PoundingSurprise) }
            .Concat(KleeArmRelics.Types)
            .Append(typeof(ExplosiveFrags))
            .ToArray();

    /// <summary>Furina's Stage pool: Salon Solitaire, her seven, The Curtain
    /// Never Falls. The Ethereal Spotlight is not in it.</summary>
    public static readonly IReadOnlyList<Type> FurinaArmPool =
        new[] { typeof(SalonSolitaire) }
            .Concat(FurinaStageRelics.Types)
            .Append(typeof(CurtainNeverFalls))
            .ToArray();

    /// <summary>Varka's pool: Boreas's Fang, his seven, Wolf's Gravestone
    /// (<c>review/active/varka-expansion-2026-10-01.md</c> sec.4).</summary>
    public static readonly IReadOnlyList<Type> VarkaArmPool =
        new[] { typeof(BoreasFang) }
            .Concat(VarkaArmRelics.Types)
            .Append(typeof(WolfsGravestone))
            .ToArray();

    /// <summary>What the pool offers: the members in the arm pool.</summary>
    public static IEnumerable<RelicModel> Offer(
        IEnumerable<RelicModel> members, IReadOnlyList<Type> armPool) =>
        members.Where(relic => armPool.Contains(relic.GetType()));
}
