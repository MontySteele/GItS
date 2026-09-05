using System.Linq;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Powers;

/// <summary>
/// `EB-463`. A SUMMON'S PRINTED DAMAGE, SNAPSHOTTED AT PLAY.
///
/// THE FIND (Furina r8 (c) 1). Guest Cast -- "Spotlight every Companion card.
/// Their printed damage and Block are 50% stronger" -- raised Lynette's and
/// Diona's Block 5 to 7 and left Chiori -- Fluttering Hasode's 6 Geo at 6 on
/// the same screen. `EB-565` is the same miss one card over: Amber --
/// Explosive Puppet printed 8 and dealt 8 while Chevreuse went 7 to 10 and
/// Gorou 8 to 12.
///
/// WHY THOSE TWO AND NOT THE OTHERS. A Companion whose damage is a `damage`
/// op runs it through the card's own printed-damage path, which
/// <see cref="SpotlightSystem.PrintedDamage"/> already folds. A row whose whole
/// body is `apply_power` prints a number the POWER will deal LATER -- at the
/// end of a turn, or the next time an enemy attacks -- and that number never
/// passes the card's path at all. There was nothing between the card and the
/// power to carry it.
///
/// THE SNAPSHOT IS THE ANSWER AND IT IS R72's RULE. The number is the CARD's,
/// so it takes the card's fold; the power fires turns later, when the card is
/// gone and the mode may have expired. So the fold is taken ONCE, at play, and
/// banked on the power -- which is also what lets the badge print the number
/// the board will actually deal.
///
/// THE SHEET GRAMMAR IS `apply_power`'s `summon_damage:`, read by both
/// engines: `tier0.engine.effects._op_apply_power` banks it in
/// `Fighter.summon_damage`, and this banks it on the power instance. A power
/// applied by anything else keeps its own constant, which is why
/// <see cref="ISummonDamagePower.SummonDamage"/> is seeded to it.
/// </summary>
internal static class SummonDamage
{
    /// <summary>
    /// Bank the folded number on the power <paramref name="card"/> just
    /// applied. Called by the generated `OnPlay` immediately after the
    /// `PowerCmd.Apply`, which is the one moment the card, the fold and the
    /// power all exist at once.
    ///
    /// THE NEWEST INSTANCE, and on a refresh that is the same object: these
    /// powers are Counters, so a second play raises the stack rather than
    /// adding a second power, and the newest fold wins -- which is what a
    /// player who re-cast the card under Guest Cast would expect.
    /// </summary>
    internal static void Note<T>(Creature? owner, CardModel card, int printed)
        where T : PowerModel, ISummonDamagePower
    {
        if (owner == null) return;
        var power = owner.Powers.OfType<T>().LastOrDefault();
        if (power == null) return;
        power.NoteSummonDamage(
            (int)SpotlightSystem.PrintedDamage(card, printed));
    }
}

/// <summary>A power whose damage is a number its CARD printed, and therefore
/// takes the card's play-time folds. See <see cref="SummonDamage"/>.</summary>
internal interface ISummonDamagePower
{
    /// <summary>The number this power will deal: the card's printed damage
    /// with the card's fold on it, or the power's own constant where nothing
    /// banked one.</summary>
    int SummonDamage { get; }

    /// <summary>Bank the folded number, at play.</summary>
    void NoteSummonDamage(int amount);
}
