using System.Collections.Generic;
using System;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards.Furina;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND 17, the Furina reframe's half: two readings a seat could not
/// reconcile from the screen, and in both cases the ENGINE was right and the
/// line the page printed was not.
/// </summary>
public class Round17Tests
{
    private const BindingFlags All =
        BindingFlags.Public | BindingFlags.NonPublic
        | BindingFlags.Instance | BindingFlags.Static;

    // ==================================================================
    // `EB-511` -- the amplifier that "went missing" the moment a second
    //             multiplier was on the board
    // ==================================================================
    //
    // WHAT THE SEAT SAW (Furina r11, natural lane, (c) 1). Fight 3 turn 2:
    // Chevreuse -- Interdiction Fire printed 7 under a Weak stack with a
    // `Reaction preview: Vaporize 1.5x` under it, and the fight's HP said it
    // had dealt 8. "7 x 1.5 = 10 or 11, not 8. 8 is exactly what you get if
    // the Vaporize multiplier never applied." Fight 4 turn 6 read the same
    // way one member over: Crabaletta's line said "hit Seapunk for 4 Hydro,
    // and left no aura on it" -- the glossary's own signature for a reaction
    // consuming the aura -- at a number with no 1.5 in it.
    //
    // NOTHING WAS DROPPED. The card's base is 7, Guest Cast rewrites the
    // PRINTED number to 10 (`SpotlightSystem.PrintedDamageDelta`, folded into
    // the card's own `CalculatedDamageVar` rather than into a damage hook),
    // and the engine then folds Weak and the amplifier multiplicatively over
    // that: 10 x 0.75 x 1.5 = 11.25, and 11 landed. The seat's arithmetic
    // reached 8 because the two numbers it SUBTRACTED were wrong.
    //
    // THE LIAR WAS THE SALON BLOCK. `PerformMember` filed the performance at
    // `TickValue` -- what the tick was worth BEFORE the pipeline -- so under
    // Weak a Crabaletta reported at 6 had landed for 4, and the Vaporizing one
    // reported at 4 had landed for 6. `ElementalHit.Deal` has RETURNED the
    // truncated landed amount since `EB-270` for exactly this reason, and now
    // that is what the row carries.

    [Fact]
    public void Weak_and_vaporize_compose_over_the_spotlit_base()
    {
        // `SimDamagePipeline.Resolve` IS `ElementalHit.Deal`'s three steps in
        // Deal's own order, and `KleeOverhaulRoundOneFixTests` pins the two
        // spellings against each other -- so this is the elemental path's
        // answer and the Bomb's alike.
        var weak = Seat.Furina().WithPower<WeakPower>(1);
        var target = Seat.Klee(400);

        var landed = SimDamagePipeline.Resolve(
            weak.Creature, target.Creature, 10m,
            ReactionConstants.VaporizeMult);

        Assert.Equal(11, landed);
        // ...and it is not 8, which is the number the seat's arithmetic
        // produced and the reason the row was filed.
        Assert.NotEqual(8, landed);
    }

    [Fact]
    public void Deal_still_hands_back_what_it_dealt()
    {
        // The return the fix above depends on, stated as a fact about the
        // signature rather than trusted: `EB-270` built it and nothing may
        // quietly make it void again.
        var deal = Il.Method("ElementalHit", "Deal");

        Assert.Equal(typeof(System.Threading.Tasks.Task<int>),
                     ((MethodInfo)deal).ReturnType);
    }

    // ==================================================================
    // `EB-500` / `EB-501` / `EB-503` -- one number, three readers
    // ==================================================================
    //
    // Three r17 findings that turn out to be the same quantity read three
    // ways. Tide Wall, Well Laid and Tide Chart all print "carried out this
    // morning" and all read `KokomiOverhaulLedger.PlansThisMorning`, which
    // counted the Plans WRITTEN -- so under Nereid's Ascension a one-Plan
    // morning was carried out twice and paid once. The number is now
    // `due.Count * CarryOutTimes`, still taken once at the drain so a reader's
    // answer does not depend on where in the queue it sits.
    //
    // `EB-500` is the sentence over the same rule: "carries out every Plan
    // twice" admits no exception and the built rule has one -- the doubling is
    // the MORNING's, and The Moon's now-copy is single. The rule stands (D
    // default) and the face and the tip name the morning.
    //
    // `EB-503` is the line that was never said: Tide Chart's draw happens
    // inside the morning and nothing reported it. It is paid through
    // `Announce`, the block's own door, so it is a beat over the pet and a row
    // in the list every carry-out already lands in -- rather than a second
    // narration idiom the page would have to learn.

    [Fact]
    public void The_mornings_depth_is_carry_outs_and_is_read_once()
    {
        // `EB-643` MOVED THE CARRY-OUT LOOP INTO `Drain`, which both drains
        // now share, so the thing the note must precede is the DRAIN CALL --
        // the same assertion one name over, and the same rule: the depth is
        // written before anything is carried out.
        var sequence = Il.CallSequence(Il.Method("KokomiPlan", "ResolveAll"));
        var times = IndexOf(sequence, c => c.Contains("CarryOutTimes"));
        var note = IndexOf(sequence, c => c.Contains("NoteMorning"));
        var resolve = IndexOf(sequence, c => c.Contains("KokomiPlan.Drain"));

        Assert.True(times >= 0 && note > times, string.Join(", ", sequence));
        Assert.True(note < resolve, string.Join(", ", sequence));
    }

    [Fact]
    public void The_three_readers_still_ask_the_one_ledger()
    {
        // What makes the fix a fix rather than three: the per-Plan clause and
        // Tide Chart's promise read the same property. (R276 pick 1 re-aimed
        // Well Laid and Tide Wall off the morning; the property and its two
        // readers stand.)
        Assert.Contains(
            Il.Calls(Il.Method("KokomiPlan", "PromisedDraw")),
            c => c.Contains("PlansThisMorning"));
    }

    [Fact]
    public void The_ascensions_face_and_its_power_both_name_the_morning()
    {
        var face = Face(new ProtoKkNereidsAscension());
        var badge = new NereidsAscensionPower().Localization!
            .Single(row => row.Item1 == "description").Item2;

        Assert.StartsWith("At the start of your turn, ", face);
        Assert.StartsWith("At the start of your turn, ", badge);
        Assert.Contains("carries out your first [gold]Plan[/gold] twice.", badge);
    }

    [Fact]
    public void The_now_copy_never_asks_how_many_times()
    {
        // `EB-500`'s pin: the doubling is read in `ResolveAll` and nowhere
        // else, so the two mid-turn doors -- The Moon's now-copy and Change of
        // Plans' front-copy -- are single by construction.
        Assert.DoesNotContain(
            Il.Calls(Il.Method("KokomiPlan", "ResolveNow")),
            c => c.Contains("CarryOutTimes"));
        Assert.DoesNotContain(
            Il.Calls(Il.Method("KokomiPlan", "ResolveFront")),
            c => c.Contains("CarryOutTimes"));
        Assert.Contains(
            Il.Calls(Il.Method("KokomiPlan", "ResolveAll")),
            c => c.Contains("CarryOutTimes"));
    }

    [Fact]
    public void The_tide_charts_draw_says_so_in_the_block()
    {
        var sequence = Il.CallSequence(
            Il.Method("KokomiPlan", "PayPromisedDraws"));
        var draw = IndexOf(sequence, c => c.Contains("CardPileCmd.Draw"));
        var said = IndexOf(sequence, c => c.Contains("Record"));

        Assert.True(draw >= 0, string.Join(", ", sequence));
        // AFTER the draw: the number the seat is owed is what arrived.
        Assert.True(said > draw, string.Join(", ", sequence));
    }

    [Fact]
    public void The_draw_line_names_the_card_and_the_kind()
    {
        var source = System.IO.File.ReadAllText(
            System.IO.Path.Combine(Repo(), "klee-mod", "KleeCode", "Powers",
                                   "Prototype", "KokomiPlan.cs"));

        Assert.Contains("private const string TideChartTitle = \"Tide Chart\";",
                        source);
        Assert.Contains("Vfx.KurageBeat.Line(TideChartTitle, cards)", source);
        Assert.Contains("NumberKind(Kind.Draw)", source);
        // The word the page prints off `Kind.Draw`, so the row's number is
        // read as cards and not as damage.
        Assert.Equal("cards drawn", (string)typeof(KokomiPlan)
            .GetMethod("NumberKind", All)!
            .Invoke(null, new object[] { KokomiPlan.Kind.Draw })!);
    }

    // ==================================================================
    // `EB-449` -- the printed half of a retired meter, by rule
    // ==================================================================
    //
    // WHAT THE SEAT SAW (Furina r11, lane 1). Under the arm the Burst meter is
    // retired, and r8 took the explanatory TIP off her faces. It did not touch
    // the two things a seat actually reads: the printed "Burst +5." at the end
    // of the body and the gold "Elemental Skill" keyword under it. The seat
    // met both on Gentilhomme Usher at two rewards and skipped the card for
    // it -- a Common enabler passed over because its face promised a resource
    // that does not exist.
    //
    // BY RULE AND NOT BY NAME, which is the reopen: the set is every Furina
    // face carrying `tags: [skill_tag]`, derived at codegen off the same field
    // that emits `ISkillTagCard`, so a fourteenth row inherits the blank.
    //
    // SHEET-WIDE, over the classes themselves rather than a list retyped here.


    /// <summary>A card's printed body, joined the way the generator writes
    /// it.</summary>
    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(row => row.Item1 == "description").Item2;

    private static int IndexOf(
        System.Collections.Generic.IReadOnlyList<string> calls,
        Func<string, bool> match)
    {
        for (var i = 0; i < calls.Count; i++)
        {
            if (match(calls[i])) return i;
        }
        return -1;
    }

    /// <summary>The repo root, from the test assembly's own location.</summary>
    internal static string Repo()
    {
        var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(
                   System.IO.Path.Combine(dir.FullName, "klee-mod")))
        {
            dir = dir.Parent;
        }
        return dir?.FullName
            ?? throw new InvalidOperationException("no repo root above " +
                                                   AppContext.BaseDirectory);
    }
}
