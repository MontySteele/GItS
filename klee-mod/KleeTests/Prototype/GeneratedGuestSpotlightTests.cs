using System;
using KleeMod.Cards.Generated;
using KleeMod.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-413` -- "Companion cards generated in combat by An Invitation take no
/// Spotlight". THEY DO. This file is the row's answer rather than its fix.
///
/// THE FIND (Furina r4 run 2 (c) 1, repeated at r7): "Charlotte -- Framing
/// dealt 6 under Guest Cast where Freminet printed 9 in the same fight;
/// Shinobu gave 6 Block under an active Spotlight."
///
/// THE TWO NUMBERS SUBTRACTED WERE DIFFERENT CARDS. Guest Cast multiplies a
/// card's own PRINTED base and truncates there
/// (<see cref="SpotlightSystem.PrintedDamageDelta"/>, folded into the card's
/// `CalculatedDamageVar`). Charlotte -- Framing prints 4 and Freminet -- Pers,
/// Deploy! prints 6, so under one and the same Spotlight they read 6 and 9 --
/// which is exactly what the seat saw. Shinobu -- Grass Ring prints 4, so its
/// 6 Block is the Spotlighted number too, not the unlit one. There is no
/// generated-versus-drafted split in either figure.
///
/// AND THERE IS NO PROVENANCE TEST TO FIND. `SpotlightSystem.IsSpotlighted`
/// keys on the card's CLASS (`ICompanionCard`) and its owner, and
/// `GuestStarGenerator.Generate` builds the token off the canonical model with
/// `source.Owner` -- same class, owner set -- so a generated copy answers the
/// gate identically to a drafted one. The tier0 twin is
/// `test_eb413_a_generated_guest_takes_the_spotlight.py`, which plays both
/// copies and reads the damage.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class GeneratedGuestSpotlightTests
{
    private static decimal Printed(decimal cardBase) =>
        Math.Truncate(cardBase * SpotlightSystem.GuestCastBaseMultiplier);

    [Fact]
    public void The_seats_two_numbers_are_two_printed_bases_under_one_spotlight()
    {
        var charlotte =
            new CharlotteFreezingPoint().DynamicVars.CalculationBase.BaseValue;
        var freminet =
            new FreminetPersDeploy().DynamicVars.CalculationBase.BaseValue;

        Assert.Equal(4m, charlotte);
        Assert.Equal(6m, freminet);
        // The seat's 6 and 9, both of them lit.
        Assert.Equal(6m, Printed(charlotte));
        Assert.Equal(9m, Printed(freminet));
    }

    [Fact]
    public void Shinobus_six_block_is_the_spotlighted_number_not_the_unlit_one()
    {
        var shinobu =
            new ShinobuGrassRingBond().DynamicVars.CalculationBase.BaseValue;

        Assert.Equal(4m, shinobu);
        Assert.Equal(6m, Printed(shinobu));
    }

    [Fact]
    public void The_generator_builds_its_token_with_an_owner()
    {
        // `IsSpotlighted` returns false on a null owner, so the ONE way the
        // creation path could drop the light is by not passing one. It does.
        var source = Source("Powers/GuestStarGenerator.cs");

        Assert.Contains(
            "source.CombatState!.CreateCard(canonical, source.Owner)", source);
    }

    [Fact]
    public void The_spotlight_gate_asks_the_cards_class_and_nothing_about_provenance()
    {
        var source = Source("Powers/SpotlightSystem.cs");

        Assert.Contains("card is ICompanionCard", source);
        // A generated-only exclusion would have to name the token somewhere in
        // the gate; the absence is the row's finding.
        Assert.DoesNotContain("GeneratedByGuestStar", source);
        Assert.DoesNotContain("IsGenerated", source);
    }

    private static string Source(string relativePath) =>
        Read(System.IO.Path.Combine("klee-mod", "KleeCode",
            relativePath.Replace('/', System.IO.Path.DirectorySeparatorChar)));

    private static string Read(string relative)
    {
        var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = System.IO.Path.Combine(dir.FullName, relative);
            if (System.IO.File.Exists(candidate))
            {
                return System.IO.File.ReadAllText(candidate);
            }

            dir = dir.Parent;
        }

        throw new System.IO.FileNotFoundException(relative);
    }
}
