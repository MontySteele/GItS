using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND 16, and it is round 15's list one debuff and one keyword further on:
/// a rule stated in words narrower than the rule, found by a seat that ran the
/// experiment and read the wrong sentence off the screen afterwards.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class Round16Tests
{
    private const BindingFlags All =
        BindingFlags.Public | BindingFlags.NonPublic
        | BindingFlags.Instance | BindingFlags.Static;

    /// <summary>
    /// The literal text one tip attach prints, read off the compiled method --
    /// `Round15Tests`' own reader, and its note applies here unchanged:
    /// enumerating a tip is not reachable headless because every yielded
    /// `HoverTip` formats its title through `LocManager.Instance`, null until
    /// the game boots.
    /// </summary>
    private static string Printed(Type owner, string method) =>
        string.Concat(Il.Strings(owner.GetMethod(method, All)!)
            .Where(s => !s.StartsWith("KLEEMOD-", StringComparison.Ordinal)));

    // ==================================================================
    // `EB-481` -- "Receive 50% more damage from Attacks", and a Skill that
    //             took the 1.5x
    // ==================================================================
    //
    // THE FIND (Kokomi r16 (c) 2), and it is `EB-469`'s twin one debuff over:
    // the status line says "from Attacks", the glossary said "every hit", and
    // `Kurage's Oath` -- printed `cost 1, skill` -- took the 1.5x. So the
    // glossary was right and the pair still disagreed, which is a player
    // sequencing badly off whichever of the two it read.
    //
    // THE ENGINE IS NOT WHAT IS WRONG, the same finding as the twin's.
    // `VulnerablePower` is the TARGET's own power and its
    // `ModifyDamageMultiplicative` asks `props.IsPoweredAttack()` -- a
    // property of the HIT -- while the generator emits `ValueProp.Move` for
    // every `op: damage` clause whatever `type:` the row declares.

    [Fact]
    public void A_skills_damage_clause_is_read_by_vulnerable_as_an_attack_hit()
    {
        // THE CARD IS A SKILL, and it is the exact card the seat watched take
        // the 1.5x -- the same one `EB-469` watched lose 25%.
        var oath = new ProtoKkKuragesOath();
        Assert.Equal(CardType.Skill, oath.Type);

        var vars = ((IEnumerable<DynamicVar>)typeof(ProtoKkKuragesOath)
            .GetProperty("CanonicalVars", All)!.GetValue(oath)!).ToList();
        var damage = vars.OfType<DamageVar>().Single();
        Assert.Equal(ValueProp.Move, damage.Props);
        Assert.True(damage.Props.IsPoweredAttack());

        // AND THE GAME'S OWN POWER AGREES, run for real rather than reasoned
        // about. `VulnerablePower` sits on the creature TAKING the hit and
        // guards on `target == Owner`, which is the shape `AuraPower` was
        // written against; the card is never handed to it at all.
        var wearer = Seat.Kokomi(30).WithPower<VulnerablePower>(1);
        var attacker = Seat.Kokomi();
        var vulnerable =
            wearer.Creature.Powers.OfType<VulnerablePower>().Single();

        Assert.Equal(1.5m, vulnerable.ModifyDamageMultiplicative(
            wearer.Creature, 0m, damage.Props, attacker.Creature, null, null));

        // 3 x 1.5 = 4.5, and the seat read the whole 1.5x off the body.
        Assert.Equal(3m, damage.BaseValue);
    }

    [Fact]
    public void The_vulnerable_tip_names_the_case_the_status_line_leaves_open()
    {
        var body = Printed(typeof(BaseKeywordTips), "ForVulnerable");

        Assert.Equal(
            "The wearer takes 50% more damage from every hit it takes, a "
          + "Skill's damage too. One stack falls off at the end of each of "
          + "its turns.", body);
        // The tip a player hovers is inside the in-game box either way, and
        // it is exactly its twin's length.
        Assert.True(body.Length <= 135, body.Length.ToString());
        Assert.Equal(Printed(typeof(BaseKeywordTips), "ForWeak").Length,
                     body.Length);
    }
}
