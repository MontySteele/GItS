using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// The verbs that belong to no rule -- Rally's discount, Cleansing Wave's
/// cleanse -- and the ONE definition of "she applied a debuff to an enemy",
/// which two different things read.
///
/// Kept out of <see cref="KokomiRules"/> because that file is the RULES and
/// these are cards, with one exception: <see cref="IsHerDebuffOnEnemy"/> is a
/// shared EVENT rather than a card, and it lives here so the relic and The
/// Clouds Like Waves ask one question instead of two that drift.
/// </summary>
public static class KokomiOverhaulKit
{
    /// <summary>
    /// Rally: "The next Companion card you play this turn costs 1 less."
    ///
    /// ONE STACK, ALWAYS. The grant is a switch, not a counter -- two Rallies
    /// in one turn do not make the next Companion cost two less, because the
    /// card says "costs 1 less" and not "costs 1 less per Rally" -- so this
    /// applies at 1 whether or not the power is already there, and
    /// <see cref="NextCompanionDiscountPower"/> removes itself on the play that
    /// spends it.
    /// </summary>
    public static async Task NextCompanionDiscount(
        PlayerChoiceContext choiceContext, Creature? kokomi, CardModel? cardSource)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (kokomi!.Powers.OfType<NextCompanionDiscountPower>().Any()) return;
        await PowerCmd.Apply<NextCompanionDiscountPower>(
            choiceContext, kokomi, 1, applier: kokomi, cardSource: cardSource);
    }

    /// <summary>
    /// Cleansing Wave: "Remove a debuff from yourself."
    ///
    /// A READING, recorded because the card says "a debuff" and not "the worst
    /// one": the FIRST debuff on her power list goes, which is the oldest one
    /// still standing, and the card gives the player no choice. A selection
    /// screen would be a different card, and picking "the largest" would be a
    /// rule nothing printed. The alternative is one line away if play says so.
    ///
    /// AN AURA IS NOT A DEBUFF and cannot be cleansed by this: the mod's
    /// <c>AuraPower</c> is <c>PowerType.Buff</c> (decompile-checked; the base
    /// game's own aura reads as a debuff only through its per-amount helper),
    /// and it lives on enemies anyway.
    /// </summary>
    public static async Task RemoveOneDebuff(
        PlayerChoiceContext choiceContext, Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var debuff = kokomi!.Powers
            .FirstOrDefault(p => p.Type == PowerType.Debuff);
        if (debuff == null) return;
        await PowerCmd.Remove(debuff);
    }

    /// <summary>
    /// Undertow's "if the enemy has a debuff". The definition is the ENGINE'S
    /// OWN -- <c>PowerType.Debuff</c> -- rather than a list of names this file
    /// would have to keep current as the arm, the companions and the base game
    /// each add one.
    /// </summary>
    public static bool HasDebuff(Creature? creature) =>
        creature != null && creature.Powers.Any(p => p.Type == PowerType.Debuff);

    /// <summary>
    /// Re-entrancy latch for <see cref="IsHerDebuffOnEnemy"/>'s consumers.
    ///
    /// IT IS NOT PARANOIA. The Casket's answer to a debuff is a HYDRO hit, and
    /// a Hydro hit can meet a Cryo aura and Freeze -- and Frozen is a debuff,
    /// applied by her, to an enemy. Without this the relic would answer its own
    /// answer until the stack ran out. The latch is a plain static because the
    /// whole event is synchronous within one hook broadcast and the mod is
    /// single-threaded; it is cleared in a `finally` so a throw inside a strike
    /// cannot leave the relic permanently deaf.
    /// </summary>
    private static bool _answering;

    /// <summary>Is the arm's debuff answer allowed to fire right now?</summary>
    public static bool Answering => _answering;

    /// <summary>Run <paramref name="answer"/> with the latch held.</summary>
    public static async Task Answer(System.Func<Task> answer)
    {
        if (_answering) return;
        _answering = true;
        try
        {
            await answer();
        }
        finally
        {
            _answering = false;
        }
    }

    /// <summary>
    /// "SHE APPLIED A DEBUFF TO AN ENEMY", once, for everything that reads it.
    ///
    /// The hook is <c>AfterPowerAmountChanged</c>, which the game fans to every
    /// model in the combat and raises on both <c>PowerCmd</c> paths, so nothing
    /// that puts a debuff on an enemy can slip past -- a card, a Plan, a
    /// companion or a reaction.
    ///
    /// FOUR CLAUSES AND EVERY ONE OF THEM EARNS ITS PLACE:
    ///   * <c>amount &gt; 0</c> -- a debuff being REMOVED or ticking down is
    ///     not one being applied;
    ///   * <c>power.Type == Debuff</c> -- the engine's own classification, so a
    ///     Buff on an enemy (an aura, which this mod files as a Buff) does not
    ///     count and the list never needs maintaining;
    ///   * the carrier is an ENEMY -- her own Weak is not a debuff she applied
    ///     to an enemy;
    ///   * the applier is HER -- in co-op the other seat's Weak is not hers,
    ///     and an enemy debuffing another enemy is nobody's.
    /// </summary>
    public static bool IsHerDebuffOnEnemy(
        PowerModel power, decimal amount, Creature? applier, Creature? kokomi)
    {
        if (kokomi == null || amount <= 0m) return false;
        if (applier != kokomi) return false;
        if (power.Type != PowerType.Debuff) return false;
        var carrier = power.Owner;
        return carrier != null && carrier.IsEnemy && !carrier.IsDead;
    }
}
