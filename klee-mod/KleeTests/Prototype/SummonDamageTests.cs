using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-463` / `EB-565`: a summon's damage takes the Guest Cast fold.
///
/// THE FIND (Furina r8 (c) 1). Guest Cast raised Lynette's and Diona's Block 5
/// to 7 and left Chiori -- Fluttering Hasode's 6 Geo at 6 on the same screen.
/// `EB-565` is the same miss one card over (Furina r14 lane 2 (c) 2): Amber --
/// Explosive Puppet printed 8 and dealt 8 while Chevreuse went 7 to 10 and
/// Gorou 8 to 12.
///
/// WHAT IS REACHABLE HERE. `SpotlightSystem.PrintedDamage` wants a card with an
/// owner, a run and a live Spotlight resource, which is past the headless
/// boundary (KleeTests README) -- so the FOLD's arithmetic is pinned in the sim
/// (`tier0/tests/test_eb463_summon_damage.py`), which owns the same grammar.
/// What is reachable is the CARRIER: the seed, the bank, the number the volley
/// spends, and the hole the badge prints -- which is the half `EB-463` added
/// and the half that could silently do nothing.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class SummonDamageTests
{
    private static string Face(PowerModel power) =>
        ((ILocalizationProvider)power).Localization!
        .Single(entry => entry.Item1 == "description").Item2;

    [Fact]
    public void EB463_the_badge_prints_a_hole_seeded_from_the_constant()
    {
        var tamoto = new TamotoPower();
        var bunny = new BaronBunnyPower();

        // A HOLE AND NOT A LITERAL, which is the whole reason these two left
        // `Every_power_face_prints_the_number_it_pays`: the number the badge
        // shows is the one the play banked, so it cannot be typed here.
        Assert.Contains("[blue]{Damage}[/blue] [gold]Geo[/gold]", Face(tamoto));
        Assert.Contains("[blue]{Damage}[/blue] [gold]Pyro[/gold]", Face(bunny));

        // SEEDED FROM THE CONSTANT, so a power applied by anything but the
        // `summon_damage:` grammar is the number it always was, and a retune
        // of the law moves the seed with it (`EB-89`'s rule).
        Assert.Equal(CompanionOverhaulLaw.TamotoDamage, tamoto.SummonDamage);
        Assert.Equal(CompanionOverhaulLaw.BaronBunnyDamage, bunny.SummonDamage);
        Assert.Equal(CompanionOverhaulLaw.TamotoDamage,
                     (int)tamoto.DynamicVars["Damage"].BaseValue);
        Assert.Equal(CompanionOverhaulLaw.BaronBunnyDamage,
                     (int)bunny.DynamicVars["Damage"].BaseValue);
    }

    [Fact]
    public void EB463_the_bank_moves_the_hit_and_the_badge_together()
    {
        // The defect this row is about is a face and a hit that disagree, so
        // the pin is that ONE write moves both.
        var tamoto = new TamotoPower();
        tamoto.NoteSummonDamage(9);
        Assert.Equal(9, tamoto.SummonDamage);
        Assert.Equal(9, (int)tamoto.DynamicVars["Damage"].BaseValue);

        var bunny = new BaronBunnyPower();
        bunny.NoteSummonDamage(12);
        Assert.Equal(12, bunny.SummonDamage);
        Assert.Equal(12, (int)bunny.DynamicVars["Damage"].BaseValue);
    }

    [Fact]
    public void EB463_the_volley_and_the_trap_spend_the_banked_number()
    {
        // Read off the compiled bodies: both used to hand the law constant
        // straight to `ElementalHit.Deal`, which is exactly why the fold could
        // not reach them.
        var volley = Il.Method("TamotoPower", "FireVolley");
        Assert.Contains(Il.Calls(volley),
                        c => c.Contains("get_SummonDamage"));
        var explode = Il.Method("BaronBunnyPower", "Explode");
        Assert.Contains(Il.Calls(explode),
                        c => c.Contains("get_SummonDamage"));
    }

    [Fact]
    public void EB463_the_fold_is_taken_at_play_and_from_the_card()
    {
        // R72's snapshot rule, and the reason the grammar exists: the power
        // fires turns later, when the card is gone and the mode may have
        // expired, so the number has to be taken while the card is in play.
        var note = Il.Method("SummonDamage", "Note");
        Assert.Contains(Il.Calls(note),
                        c => c.EndsWith("SpotlightSystem.PrintedDamage",
                                        System.StringComparison.Ordinal));
        Assert.Contains(Il.Calls(note), c => c.Contains("NoteSummonDamage"));

        // AND THE GENERATED CARDS CALL IT, immediately after the apply -- the
        // one moment the card, the fold and the power all exist at once.
        foreach (var card in new[] { "ProtoMiChioriHasode",
                                     "ProtoMcAmberExplosivePuppet" })
        {
            var play = Il.Method(card, "OnPlay");
            Assert.Contains(Il.Calls(play), c => c.Contains("SummonDamage.Note"));
        }
    }
}
