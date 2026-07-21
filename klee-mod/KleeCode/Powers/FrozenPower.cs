using System.Threading.Tasks;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
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
    /// PHASE CORRECTION (bug hunt 2026-07-21). This was a ModifyDamageAdditive
    /// override, whose doc claimed the additive phase kept SHATTER_DAMAGE from
    /// scaling with Vulnerable. That is inverted: the pipeline is
    /// (base + additive) * vuln * amp, so riding the additive phase made the
    /// bonus scale with Vulnerable AND made enemy Block absorb it. The sim does
    /// neither -- effects.py deals it as raw `enemy.hp -= shatter` AFTER the
    /// main hit's block subtraction, commented "Direct HP, like splash".
    /// Frozen + Vulnerable 2 on a 10-damage attack: sim 21, game 24. Into 12
    /// Block: sim 6 through, game 4.
    ///
    /// So it is dealt here instead, with the Overload-splash idiom
    /// (ReactionEffects: Unblockable | Unpowered, no dealer, no card source) --
    /// Unpowered also keeps the Shatter from re-entering this hook or
    /// early-detonating bombs, which the sim's `source == "attack"` gate
    /// likewise prevents.
    ///
    /// The sim's `enemy.alive` gate is mirrored: a hit that kills does not
    /// Shatter.
    /// </summary>
    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, DamageResult result,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (target != base.Owner) return;
        if (!props.IsPoweredAttack()) return;
        // tier0 gates Shatter on source == "attack" -- the same attack-card
        // predicate BombPower's early detonation uses.
        if (cardSource is not { Type: CardType.Attack }) return;

        await PowerCmd.Remove(this);

        if (target.IsDead) return;

        // shatter_bonus (Freminet, Shattering Pressure): a flat rider the sim
        // adds inside the same raw `enemy.hp -=`, so it is unblockable and
        // unamplified exactly like the base Shatter. Read off the DEALER --
        // the sim reads state.player.powers, and the dealer is who broke the
        // ice.
        var shatter = ReactionConstants.ShatterDamage
            + ShatterBonusPower.BonusFor(dealer);

        await CreatureCmd.Damage(
            choiceContext, target, shatter,
            ValueProp.Unblockable | ValueProp.Unpowered,
            dealer: null, cardSource: null);
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
