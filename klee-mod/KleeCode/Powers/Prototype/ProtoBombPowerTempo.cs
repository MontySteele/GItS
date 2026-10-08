using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// THE KLEE TEMPO PAPER's Bomb verb (2026-10-07, ruled,
/// review/active/klee-tempo-paper-2026-10-07.md sec.3): damage READ off her
/// Bombs that leaves them cooking. Cook "has no Common way to deal damage
/// while it waits"; Simmer and Taste Test are that damage, paid for in
/// statuses. Sheet op <c>damage_from_bombs</c>, one awaited call per card.
///
/// IT READS THE PILE AND DOES NOT SPEND IT, Sparks 'n' Splash's read
/// (<see cref="BombEchoPower"/>): nothing goes off, so no Spark (rule 4 pays
/// per explosion), no Mine answers, no "whenever a Bomb goes off" reader, and
/// neither of rule 7's counters moves.
///
/// BUT IT IS THE CARD'S OWN HIT, not a Bomb's: one powered Attack through
/// <see cref="DealCardDamage"/>, so Pyro, the aura and its reaction,
/// Strength, Weak and the target's Vulnerable all land exactly as on any other
/// Attack of hers. A read of zero deals nothing (Taste Test on a bare enemy).
///
/// Sim twin: <c>effects._op_damage_from_bombs</c>.
/// </summary>
public sealed partial class ProtoBombPower
{
    /// <summary>Which Bombs a <c>damage_from_bombs</c> hit is measured off.
    /// </summary>
    public enum BombRead
    {
        /// <summary>Simmer: "plus half your largest Bomb's size" -- the
        /// largest single charge on the living board
        /// (<see cref="LargestSizeFor"/>), halved, rounded down.</summary>
        LargestHalf,

        /// <summary>Taste Test: "damage equal to all your Bombs on the
        /// enemy" -- every one of her charges on the aimed body, Mines
        /// included (<see cref="TotalPlacedBy"/>).</summary>
        TargetTotal,
    }

    /// <summary>The number the hit is dealt for, before the Attack's own
    /// modifiers: the printed flat part plus the read. PURE.</summary>
    public static decimal BombReadDamage(
        Creature? target, Creature applier, decimal baseDamage, BombRead read)
    {
        var bombs = read switch
        {
            BombRead.LargestHalf => LargestSizeFor(applier) / 2,
            BombRead.TargetTotal => TotalPlacedBy(target, applier),
            _ => 0,
        };
        return baseDamage + bombs;
    }

    /// <summary>Simmer and Taste Test: read the Bombs, then hit the aimed
    /// enemy once for <see cref="BombReadDamage"/>. Nothing goes off.</summary>
    public static async Task DealFromBombs(
        PlayerChoiceContext choiceContext, Creature? target, Creature applier,
        decimal baseDamage, BombRead read, CardModel cardSource,
        CardPlay cardPlay)
    {
        if (target == null) return;
        var damage = BombReadDamage(target, applier, baseDamage, read);
        await DealCardDamage(choiceContext, target, damage, cardSource,
                             cardPlay);
    }
}
