using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// Klee text-only fixes (2026-10-13, [USER]: "Let's go with (a). Minor text
/// cleanup doesn't need a whole character stage branch,"). The printed Bomb
/// number now folds the two placer-side terms the Set off pays: a waiting
/// Boom Badge doubles each charge, and Durin's Dark adds its bonus to each
/// charge before the amplifier. Klee's own Strength and Weak stay out
/// (`EB-343`, pinned in <c>KleeOverhaulOneNumberTests</c>).
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeTextFixes20261013Tests
{
    [Fact]
    public void A_waiting_boom_badge_doubles_the_printed_number()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(8), new ProtoBombs.Charge(9));

        Assert.Equal(17, pile.DisplayAmount);

        klee.WithPower<BoomBadgePower>(1);

        Assert.Equal(34, pile.PredictedSetOffDamage());
        Assert.Equal(pile.PredictedSetOffDamage(), pile.DisplayAmount);
    }

    [Fact]
    public void Durins_dark_adds_its_bonus_to_each_charge()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(12), new ProtoBombs.Charge(4));

        klee.WithPower<PurityDarkPower>(6);

        // The scaling round's board: printed 12 and 4, and 18 and 10 landed.
        Assert.Equal(18 + 10, pile.PredictedSetOffDamage());
        Assert.Equal(pile.PredictedSetOffDamage(), pile.DisplayAmount);
    }

    [Fact]
    public void The_badge_doubles_before_the_dark_bonus_and_vulnerable_after()
    {
        // `SetOff` multiplies the charge, `ElementalHit.Deal` adds the Dark
        // bonus, then the target's Vulnerable multiplies the sum.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30);
        var pile = ProtoBombs.Place(enemy.Creature, klee.Creature,
            new ProtoBombs.Charge(10));

        klee.WithPower<BoomBadgePower>(1).WithPower<PurityDarkPower>(4);
        enemy.WithPower<VulnerablePower>(1);

        Assert.Equal(36, pile.PredictedSetOffDamage());   // (10 x 2 + 4) x 1.5
    }

    [Fact]
    public void Klees_weak_still_never_reaches_the_printed_number()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(10));

        klee.WithPower<WeakPower>(2);

        Assert.Equal(10, pile.PredictedSetOffDamage());
    }
}
