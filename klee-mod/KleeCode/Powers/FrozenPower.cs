using System.Threading.Tasks;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// Frozen v2 -- soft control, per principles v1.5 section 2.2 errata.
///
/// Deliberately NOT a skip/stun. The frozen enemy's next action deals -50%
/// damage, and while Frozen the first Attack to hit it Shatters: bonus damage,
/// and Frozen is removed. Bosses take Vulnerable instead (round-3 ruling, still
/// standing post-errata) -- "skip a boss turn" is exactly the effect that warps
/// balance math, so it was ruled out.
///
/// Both halves ride the same hook, using the fact that
/// ModifyDamageMultiplicative receives BOTH target and dealer: the -50% checks
/// <c>dealer == Owner</c> (outgoing), Shatter checks <c>target == Owner</c>
/// (incoming). That symmetry is why this needs no second system.
/// </summary>
public sealed class FrozenPower : PowerModel
{
    public override PowerType Type => PowerType.Debuff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageMultiplicative(
        Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        // Outgoing: the frozen creature's own next action is weakened.
        if (dealer == base.Owner && target != base.Owner)
        {
            return ReactionConstants.FrozenDamageMult;
        }

        return 1m;
    }

    /// <summary>
    /// Shatter: the first Attack to land on a Frozen enemy deals bonus damage
    /// and removes Frozen.
    ///
    /// The bonus is additive, so it goes through ModifyDamageAdditive rather
    /// than the multiplicative phase -- SHATTER_DAMAGE is a flat +6 in the sim,
    /// not a multiplier, and putting it in the wrong phase would make it scale
    /// with Vulnerable.
    /// </summary>
    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (target != base.Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;

        return ReactionConstants.ShatterDamage;
    }

    /// <summary>
    /// Removal half of Shatter. Kept out of ModifyDamageAdditive because that
    /// runs in preview/tooltip paths and must stay pure.
    /// </summary>
    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, DamageResult result,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (target != base.Owner) return;
        if (!props.IsPoweredAttack()) return;

        await PowerCmd.Remove(this);
    }

    /// <summary>
    /// The -50% applies to the NEXT action only, so Frozen expires at the end
    /// of the enemy side's turn if it was not Shattered first.
    /// </summary>
    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side, System.Collections.Generic.IEnumerable<Creature> participants)
    {
        if (side == CombatSide.Enemy)
        {
            await PowerCmd.TickDownDuration(this);
        }
    }
}
