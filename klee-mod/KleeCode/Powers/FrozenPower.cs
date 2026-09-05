using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
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
/// WHILE FROZEN IS ONE ACTION LONG, which is <see cref="AfterSideTurnEnd"/>'s
/// tick and is the fact <c>EB-517</c> put on the face: the Shatter window opens
/// when the freeze lands and closes when the body takes the action the first
/// clause halves, so the two clauses are one rider and not two.
///
/// Both halves ride the same hook, using the fact that
/// ModifyDamageMultiplicative receives BOTH target and dealer: the -50% checks
/// <c>dealer == Owner</c> (outgoing), Shatter checks <c>target == Owner</c>
/// (incoming). That symmetry is why this needs no second system.
/// </summary>
public sealed class FrozenPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Frozen"),
        ("description",
            // `EB-345` / R249. The badge names the Shatter number instead of
            // calling it "unblockable damage" and leaving the player to
            // guess it, the same discipline the tips keep -- and it is the
            // one the tip beside it already prints
            // (`KLEEMOD-FROZEN_PREVIEW`). "and removes Frozen" is a RULE, so
            // it stays: the packet's shorter form dropped it and the
            // sentence fits with it kept.
            //
            // `EB-517`: AND THE WINDOW, WHICH IS THE HALF THAT WAS MISSING.
            // The two clauses read as independent riders -- a halved action,
            // and a standing promise about the next Attack -- and they are
            // not: `AfterSideTurnEnd` ticks the counter down at the end of
            // the enemy side's turn, so the Shatter window closes when the
            // body takes the action the first clause halves. A Kokomi r18
            // seat played a 2-damage Attack into a 7-HP body expecting 2 + 6,
            // dealt 2, and read the freeze gone with nothing having Shattered
            // it: "the one place in the round where I acted on the printed
            // text and the printed text was wrong." "Until it acts" is LAW's
            // one-action Frozen said on the face.
            //
            // "the first Attack" GOES, and nothing is lost: a Shatter removes
            // Frozen, so there is never a second Attack inside the window for
            // "first" to distinguish it from. That is the eleven characters
            // the window clause needed to stay under the badge ceiling
            // (`docs/current/text-conventions.md`, 125).
            "Its next action deals 50% less damage. Until it acts, an Attack "
          + $"Shatters it for [blue]{ReactionConstants.ShatterDamage}[/blue] "
          + "unblockable damage and removes Frozen."),
    };

    public override PowerType Type => PowerType.Debuff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageMultiplicative(
        Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource, CardPlay? cardPlay)
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
            dealer: null, cardSource: null, cardPlay: null);

        // `EB-423`. "and removes Frozen" has to survive the rest of THIS
        // broadcast. `AuraPower.AfterDamageReceived` may still be ahead of us
        // in the same one, and a Hydro aura meeting this Cryo hit resolves a
        // Frozen reaction that puts the freeze straight back -- which is what
        // the round-5 seat read off the board: "the shatter demonstrably
        // happened (the 6 is in the HP total) and the board still read Frozen
        // 1". The sim cannot reach that state; it reacts first and zeroes
        // `enemy.frozen` after. The full argument, and why the mark is set
        // HERE rather than before the damage above, is at
        // `ReactionEffects.MarkShattered`.
        ReactionEffects.MarkShattered(target);
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
