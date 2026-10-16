using System;
using System.Linq;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Vfx;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA'S GUEST EFFECTS (2026-10-16, "guest-star pizazz";
/// review/active/furina-guest-fx-2026-10-16.md). The table of which effect
/// plays for which guest on which trigger, and where, is pure
/// (<see cref="FurinaGuestFx.PlaceFor"/>); the beats it hangs on are the
/// board's lunge, an act's hit and a line's cue, which the recording board
/// shows the rules make once per act, again on every repeat, and never on a
/// beat that did not happen. The game half needs a scene tree; headless it
/// must do nothing and never throw.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaGuestFxTests
{
    private static readonly StagePerformer[] AtTarget =
    {
        StagePerformer.Wriothesley, StagePerformer.Lynette, StagePerformer.Clorinde,
        StagePerformer.Lyney, StagePerformer.Escoffier,
    };

    private static readonly StagePerformer[] OnFurina =
    {
        StagePerformer.Charlotte, StagePerformer.Sigewinne, StagePerformer.Freminet,
    };

    [Fact]
    public void Every_guest_has_exactly_one_effect_on_the_trigger_and_place_the_table_names()
    {
        foreach (var who in Enum.GetValues<StagePerformer>())
        {
            var places = Enum.GetValues<GuestFxTrigger>()
                .Select(t => (t, p: FurinaGuestFx.PlaceFor(who, t)))
                .Where(x => x.p != GuestFxPlace.None)
                .ToList();
            Assert.Single(places);
            var (trigger, place) = places[0];
            if (AtTarget.Contains(who))
            {
                Assert.Equal((GuestFxTrigger.Act, GuestFxPlace.Target), (trigger, place));
            }
            else if (OnFurina.Contains(who))
            {
                Assert.Equal((GuestFxTrigger.Act, GuestFxPlace.Furina), (trigger, place));
            }
            else if (who is StagePerformer.Navia or StagePerformer.Chevreuse)
            {
                Assert.Equal((GuestFxTrigger.Line, GuestFxPlace.Self), (trigger, place));
            }
            else
            {
                Assert.Equal(StagePerformer.Neuvillette, who);
                Assert.Equal((GuestFxTrigger.HydroBonus, GuestFxPlace.Target), (trigger, place));
            }
        }
    }

    [Fact]
    public void Each_guest_has_its_own_scene_named_for_it()
    {
        var paths = Enum.GetValues<StagePerformer>().Select(FurinaGuestFx.ScenePath).ToList();
        Assert.Equal(paths.Count, paths.Distinct().Count());
        Assert.Equal("furina/model/guest_fx_wriothesley.tscn",
                     FurinaGuestFx.ScenePath(StagePerformer.Wriothesley));
        Assert.Equal("neuvillette", FurinaGuestFx.NameOf(StagePerformer.Neuvillette));
        Assert.True(FurinaGuestFx.OnFeet("feet"));
        Assert.False(FurinaGuestFx.OnFeet("center"));
        Assert.False(FurinaGuestFx.OnFeet(null));
    }

    [Fact]
    public void Neuvillettes_ring_shows_only_when_his_bonus_is_in_a_hydro_hit()
    {
        Assert.True(FurinaGuestFx.BonusShows(2, Element.Hydro));
        Assert.False(FurinaGuestFx.BonusShows(0, Element.Hydro));
        Assert.False(FurinaGuestFx.BonusShows(2, Element.Cryo));
    }

    [Fact]
    public void Headless_every_entry_point_does_nothing_and_never_throws()
    {
        var kit = StageKit.Of(StagePerformer.Charlotte, StagePerformer.Navia);
        foreach (var seat in kit.Stage.Seats)
        {
            FurinaGuestFx.OnAct(null, seat);
            FurinaGuestFx.OnLine(seat);
        }
        FurinaGuestFx.OnAct(null, null);
        FurinaGuestFx.OnLine(null);
        FurinaGuestFx.OnHit(StagePerformer.Lyney, null);
        FurinaGuestFx.OnHydroBonus(2, Element.Hydro, null);
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void Each_act_lunges_once_and_a_repeat_lunges_again()
    {
        var kit = StageKit.With(new StageMods { Showstopper = 1 }, 5,
                                StagePerformer.Charlotte, StagePerformer.Wriothesley);
        StageKit.Run(kit.Director.Drain(4));
        StageKit.Run(kit.Director.EndOfTurn(0));
        // the sweep, then Showstopper's second sweep
        Assert.Equal(new StagePerformer?[]
        {
            StagePerformer.Charlotte, StagePerformer.Wriothesley,
            StagePerformer.Charlotte, StagePerformer.Wriothesley,
        }, kit.Board.Lunges);
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void An_act_to_all_is_one_hit_per_enemy_by_its_guest()
    {
        var kit = StageKit.With(0, StagePerformer.Escoffier);
        StageKit.Run(kit.Director.ActOldest());
        Assert.Equal(new StagePerformer?[] { StagePerformer.Escoffier }, kit.Board.Lunges);
        Assert.Contains(kit.Board.Hits, h => h.StartsWith("damage Escoffier All"));
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void Bottled_encore_plays_each_guests_act_twice()
    {
        var kit = StageKit.Of(StagePerformer.Sigewinne, StagePerformer.Freminet);
        StageKit.Run(kit.Director.ActEachTwice());
        Assert.Equal(new StagePerformer?[]
        {
            StagePerformer.Sigewinne, StagePerformer.Sigewinne,
            StagePerformer.Freminet, StagePerformer.Freminet,
        }, kit.Board.Lunges);
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void Navias_discount_and_chevreuses_line_cue_their_bodies_on_a_spend()
    {
        var navia = StageKit.With(10, StagePerformer.Navia);
        Assert.True(StageKit.Run(navia.Director.Spend(3)) > 0);
        Assert.Contains("cue Navia", navia.Board.Log);
        // the discount is the turn's first Spend only: a second Spend shows nothing
        navia.Board.Log.Clear();
        Assert.True(StageKit.Run(navia.Director.Spend(1)) > 0);
        Assert.DoesNotContain("cue Navia", navia.Board.Log);

        var chev = StageKit.With(10, StagePerformer.Chevreuse);
        Assert.True(StageKit.Run(chev.Director.Spend(2)) > 0);
        Assert.True(StageKit.Run(chev.Director.Spend(2)) > 0);
        Assert.Equal(2, chev.Board.Log.Count(l => l == "cue Chevreuse"));
        Assert.Empty(chev.Board.Lunges);
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void A_spend_not_made_cues_no_line()
    {
        var kit = StageKit.With(1, StagePerformer.Chevreuse);
        Assert.Equal(0, StageKit.Run(kit.Director.Spend(5)));
        Assert.DoesNotContain("cue Chevreuse", kit.Board.Log);
        FurinaStageLedger.ResetAll();
    }
}
