using System.Linq;
using System.Reflection;
using KleeMod.Cards.Generated;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// EB-183 -- MUSTER'S CHARGE SUBSIDY READ AS A FUNNEL PROPERTY, pinned. Sim
/// twin: <c>tier0/tests/test_eb183_muster_subsidy_funnel.py</c>.
///
/// R216 D deferred the subsidy into R213 E1 in these words: *a Mustered
/// Companion costs 1 less, Exhausts, and pays 1 Charge, so blocking with one
/// also advances Kokomi's finisher*. Kokomi slice 2 asked one of that
/// sentence's two readings -- the SIGN, on a card -- and it retired with the
/// rest of slice 2 under R227 / M67 (1). This is the other one: the recruits
/// of an order that PAID for them pay no Charge when they Exhaust, which is a
/// property of the exhaust FUNNEL and of no effect list.
///
/// This whole file is compiled only under <c>-p:PrototypeCards=true</c>
/// (KleeTests.csproj), the same switch that compiles the rule.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL. The stamp registry is a plain
/// static reachable headlessly, so identity, clearing and null-safety are
/// exercised for real. The funnel's own payout is NOT: it needs a live
/// <c>PlayerChoiceContext</c> and a card PLAY, which the headless boundary
/// (KleeTests/README.md) puts out of reach. That half is pinned structurally
/// -- the seam exists, it is inside the flag, and it reads THIS registry --
/// and the behavioural half is the sim's, where it is pinned for real.
/// </summary>
public class MusterSubsidyTests
{
    private const BindingFlags All = HeadlessGame.All;

    private static CardModel Recruit() => new GorouInuzakaCharge();

    // --- the stamp: per INSTANCE, never per model --------------------------

    [Fact]
    public void An_unstamped_recruit_pays_the_shipped_wage()
    {
        MusterSubsidy.ClearForNewCombat();
        Assert.False(MusterSubsidy.IsWaived(Recruit()));
    }

    [Fact]
    public void A_stamped_recruit_is_waived()
    {
        MusterSubsidy.ClearForNewCombat();
        var recruit = Recruit();
        MusterSubsidy.NoteWaived(recruit);
        Assert.True(MusterSubsidy.IsWaived(recruit));
    }

    [Fact]
    public void The_stamp_does_not_spread_to_a_sibling_off_the_same_model()
    {
        // The whole reason the registry keys on the INSTANCE. Two recruits can
        // be the same Companion and come from different orders, and only one
        // of those orders may have been the prototype.
        MusterSubsidy.ClearForNewCombat();
        var stamped = Recruit();
        var sibling = Recruit();
        MusterSubsidy.NoteWaived(stamped);
        Assert.True(MusterSubsidy.IsWaived(stamped));
        Assert.False(MusterSubsidy.IsWaived(sibling));
    }

    [Fact]
    public void The_registry_is_null_safe_both_ways()
    {
        MusterSubsidy.ClearForNewCombat();
        MusterSubsidy.NoteWaived(null);
        Assert.False(MusterSubsidy.IsWaived(null));
    }

    [Fact]
    public void A_waiver_does_not_survive_into_the_next_fight()
    {
        // `EB-196`'s lesson, applied before it can bite: a recruit is a
        // combat-local instance, so a stamp that outlived the fight would be a
        // stale waiver on top of a slow leak of dead CardModels.
        MusterSubsidy.ClearForNewCombat();
        var recruit = Recruit();
        MusterSubsidy.NoteWaived(recruit);
        MusterSubsidy.ClearForNewCombat();
        Assert.False(MusterSubsidy.IsWaived(recruit));
    }

    // --- the gate: the flag cannot escape ----------------------------------

    [Fact]
    public void The_conscript_verb_defaults_to_the_shipped_wage()
    {
        // THE GUARD THAT MATTERS, and the C# half of the sim's
        // `test_no_shipped_card_carries_the_subsidy_key`. Every shipped
        // conscript face emits `KokomiConscript.Run(...)` WITHOUT the argument
        // -- the codegen appends it only for a row that asks -- so what those
        // faces get is this default. If it were ever flipped to true, every
        // shipped Muster in the game would silently stop paying Charge.
        var run = typeof(KokomiConscript).GetMethod("Run", All);
        Assert.NotNull(run);
        var waived = run!.GetParameters()
            .Single(p => p.Name == "subsidyWaived");
        Assert.True(waived.HasDefaultValue);
        Assert.Equal(false, waived.DefaultValue);
    }

    [Fact]
    public void The_funnel_reads_the_registry_inside_the_flag()
    {
        // STRUCTURAL, and labelled as such. The payout itself is unreachable
        // headlessly; what is checkable is that the one reader exists, is
        // public, and answers about a CardModel -- i.e. that the seam the
        // funnel calls is the seam this file pins.
        var reader = typeof(MusterSubsidy).GetMethod("IsWaived", All);
        Assert.NotNull(reader);
        Assert.True(reader!.IsPublic && reader.IsStatic);
        Assert.Equal(typeof(bool), reader.ReturnType);
        Assert.Equal(typeof(CardModel),
                     reader.GetParameters().Single().ParameterType);
    }

    [Fact]
    public void The_prototype_order_prints_the_rule_it_changes()
    {
        // The Muster keyword's tip says the recruit costs 1 less and Exhausts;
        // it does not say what an Exhaust pays, because until this arm every
        // Exhaust of her own card paid the same. A card that takes that back
        // must print it or the blind grader is reading a face that lies.
        var card = new ProtoMusterSubsidyFunnel();
        // The LOC ROW, which is the string the face actually prints. Reading
        // `Description` would go through LocManager, and the headless boundary
        // has no localization singleton.
        var text = (card.Localization ?? new())
            .Where(row => row.Item1 == "description")
            .Select(row => row.Item2)
            .SingleOrDefault() ?? string.Empty;
        Assert.Contains("Muster", text);
        Assert.Contains("no [gold]Charge[/gold]", text);
    }
}
