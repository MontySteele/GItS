using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-506`. WHO IS AT THE FRONT, ON THE WIRE.
///
/// WHAT THE SEAT SAW (Furina r11 lane 1, (c) 4): "I could never tell who the
/// front member was. The stage buff always names one -- *A Companion card you
/// play performs the Usher* -- but the Companion glossary says a play
/// *performs the front member, then sends it to the back*, and after doing
/// exactly that in fight 3 the line still named the Usher. With two members up
/// I was guessing which one my next Companion card would fire."
///
/// THE BUFF'S FACE CANNOT BE THE ANSWER. It is a smart description keyed on
/// the front member (<c>SalonMemberPower.ManualKey</c>), so it is one of four
/// registered rows redrawn when the game decides to redraw it -- and after a
/// rotation it had not been. The COMPANY is a live list in slot order:
/// <c>PerformLeftmost</c> takes <c>company[0]</c> and <c>RotateLeftmost</c>
/// moves it to the back, so the head of the list is the seat's question
/// answered by construction rather than by a second copy of the rule.
///
/// So the snapshot carries the stage, front first, and
/// <c>understudy/blindplay_board.furina_salon</c> reads it under `company`.
/// </summary>
public class FurinaStageOrderTests
{
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;

        internal Arm()
        {
            FurinaReframe.Enabled = true;
            FurinaReframe.ManualEnabled = true;
        }

        public void Dispose()
        {
            FurinaReframe.Enabled = _enabled;
            FurinaReframe.ManualEnabled = _manual;
        }
    }

    /// <summary>A seat with a company on stage, without running Deploy (which
    /// needs a live combat). Lifted from <c>FurinaReframeRuleTests.Stage</c>,
    /// where every reflective step is reasoned out.</summary>
    private static Seat Stage(params SalonMember[] members)
    {
        FurinaReframeLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();

        var power = (SalonMemberPower)RuntimeHelpers
            .GetUninitializedObject(typeof(SalonMemberPower));
        Seat.Force(power, "Amount", members.Length);
        ((System.Collections.IList)seat.Creature.Powers).Add(power);
        Seat.Force(power, "IsMutable", true);
        Seat.Force(power, "Owner", seat.Creature);

        Company()[seat.Creature] = members.ToList();
        return seat;
    }

    private static IDictionary<Creature, List<SalonMember>> Company() =>
        (IDictionary<Creature, List<SalonMember>>)typeof(SalonMemberPower)
            .GetField("Company", HeadlessGame.All)!
            .GetValue(null)!;

    private static List<object?> CompanyOnTheWire(Seat seat) =>
        Assert.IsType<List<object?>>(
            FurinaReframeLedger.Snapshot(seat.Player)["company"]);

    [Fact]
    public void The_snapshot_carries_the_stage_front_first()
    {
        // The names are the STAGE names every Salon face and the buff itself
        // print (`ManualFrontName`), not the card titles, so the page and the
        // screen call one member one thing.
        using var _ = new Arm();
        var seat = Stage(SalonMember.Usher, SalonMember.Crabaletta);

        Assert.Equal(new object?[] { "the Usher", "Crabaletta" },
                     CompanyOnTheWire(seat));
    }

    [Fact]
    public void A_rotation_moves_the_front_and_the_wire_says_so()
    {
        // The seat's exact complaint: a Companion play performs the front
        // member and sends it to the back, and the line went on naming the
        // one that had just left. `RotateLeftmost` is that move.
        using var _ = new Arm();
        var seat = Stage(SalonMember.Usher, SalonMember.Crabaletta);

        SalonMemberPower.RotateLeftmost(seat.Creature, 1);

        Assert.Equal(new object?[] { "Crabaletta", "the Usher" },
                     CompanyOnTheWire(seat));
        // ...and it is the same list the perform verb reads, which is the
        // whole reason this is the answer rather than a second copy of it.
        Assert.Equal(SalonMember.Crabaletta,
                     SalonMemberPower.LeftmostMember(seat.Creature));
    }

    [Fact]
    public void An_empty_stage_carries_an_empty_list_and_not_a_missing_key()
    {
        // ABSENT IS NOT EMPTY, this snapshot's standing split: a build with no
        // reframe sends no `furina_salon` block at all, and a Furina with
        // nobody on stage sends the block with an empty stage in it. The page
        // prints no stage line either way, and the two facts stay tellable
        // apart.
        using var _ = new Arm();
        var seat = Stage();

        Assert.Empty(CompanyOnTheWire(seat));
    }

    [Fact]
    public void A_klee_gets_the_empty_map_it_always_got()
    {
        // The manual leg off is "the rule is here and this seat is not playing
        // it", and that answer must not grow a stage key.
        using var _ = new Arm();
        FurinaReframe.ManualEnabled = false;
        FurinaReframeLedger.ResetAll();
        var seat = Seat.Furina().WithCombatState();

        Assert.Empty(FurinaReframeLedger.Snapshot(seat.Player));
    }
}
