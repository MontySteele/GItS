#nullable enable

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- THE GUEST CAST (2026-09-25), the mod's pins.
///
/// The design is <c>review/active/furina-guest-batch-2026-09-25.md</c>, with
/// two rulings after it: no guest cap, and one of each guest. The sim's pins
/// are <c>tier0/tests/test_furina_guest_cast.py</c>, and the SCRIPTED BOARDS
/// here are that file's word for word: the forecast below is pinned to the
/// numbers the sim's ACTUAL end of turn produces on the same boards (the
/// acts themselves need a live combat this harness does not have; the
/// Fanfare they move is the ledger's, which runs here).
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class FurinaGuestCastTests
{
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaStage.Enabled;

        internal Arm()
        {
            FurinaStageLedger.ResetAll();
            FurinaStage.Enabled = true;
        }

        public void Dispose()
        {
            FurinaStage.Enabled = _enabled;
            FurinaStageLedger.ResetAll();
        }
    }

    private static StagePerformer P(string member) => FurinaStage.Parse(member);

    /// <summary>A stage of these seats, front first, with an empty log.
    /// Guests arrive holding their bar; the trio are summoned and raised.
    /// </summary>
    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        Seat seat, params (string Member, int Fanfare)[] seats)
    {
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        foreach (var (member, fanfare) in seats)
        {
            var who = P(member);
            if (FurinaStage.IsGuest(who))
            {
                stage.GuestArrives(who, fanfare);
            }
            else
            {
                stage.Summon(who);
                stage.Raise(fanfare - FurinaStageLaw.SummonFanfare);
            }
        }
        stage.ClearBeats();
        return (seat, stage);
    }

    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        params (string Member, int Fanfare)[] seats) =>
        Stage(Seat.Furina().WithCombatState(), seats);

    private static int[] Bars(FurinaStageLedger stage) =>
        stage.Seats.Select(s => s.Fanfare).ToArray();

    // ---- the cast ------------------------------------------------------------

    [Fact]
    public void The_eight_guests_parse_and_are_guests_and_the_trio_are_not()
    {
        Assert.Equal(8, FurinaStage.Guests.Length);
        foreach (var name in FurinaStage.Guests)
        {
            var who = P(name);
            Assert.True(FurinaStage.IsGuest(who), name);
            Assert.Equal(name, FurinaStage.Name(who));
            // A guest is named by its own name, the card's title's.
            Assert.Equal(char.ToUpperInvariant(name[0]) + name[1..],
                         FurinaStageLedger.DisplayName(who));
        }
        foreach (var name in FurinaStage.Performers)
        {
            Assert.False(FurinaStage.IsGuest(P(name)), name);
        }
    }

    [Fact]
    public void Every_guest_has_a_body_a_badge_and_a_short_name()
    {
        foreach (var name in FurinaStage.Guests)
        {
            var who = P(name);
            var model = (Type)typeof(FurinaStagePets)
                .GetMethod("ModelFor", HeadlessGame.All)!
                .Invoke(null, new object[] { who })!;
            Assert.Equal(name, model.Name.Replace("Monster", "")
                                   .ToLowerInvariant());
            // No scene yet: the Osty fallback, and no pack literal the
            // deploy's S12 check would refuse.
            Assert.Null(typeof(StagePerformerMonster)
                .GetMethod("ModVisualsPathFor", HeadlessGame.All)!
                .Invoke(null, new object[] { who }));
            Assert.Equal(FurinaStageLedger.DisplayName(who),
                         Vfx.FurinaStageStrip.NameOf(who));
        }
        var pin = Il.Calls(Il.Method("StagePerformerBadge", "Pin"));
        Assert.Contains(pin, c => c.Contains("Apply"));
    }

    // ---- arrival -------------------------------------------------------------

    [Fact]
    public void A_guest_arrives_at_the_back_most_empty_seat_holding_its_n()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 3));
        Assert.True(stage.GuestArrives(StagePerformer.Clorinde, 4));
        Assert.Equal(new[] { StagePerformer.Usher, StagePerformer.Clorinde },
                     stage.Seats.Select(s => s.Who).ToArray());
        Assert.Equal(new[] { 3, 4 }, Bars(stage));
        Assert.Equal("arrive", stage.Beats[^1].Event);
    }

    [Fact]
    public void Guests_may_fill_all_three_seats_and_a_fourth_does_not_fit()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("neuvillette", 6), ("clorinde", 4),
                               ("navia", 4));
        Assert.True(stage.IsFull);
        Assert.False(stage.GuestArrives(StagePerformer.Lynette, 8));
    }

    [Fact]
    public void A_guest_star_on_a_full_stage_recasts_the_front()
    {
        // The card's verb: an already-seated guest repeats, a full stage
        // recasts (the front Bows, the guest takes its Fanfare), else the
        // guest arrives.
        var calls = Il.Calls(Il.Method("FurinaStage", "GuestStar"));
        Assert.Contains("FurinaStageLedger.SeatOf", calls);
        Assert.Contains("FurinaStageLedger.GuestSteps", calls);
        Assert.Contains("FurinaStage.Bow", calls);
        Assert.Contains("FurinaStageLedger.GuestReturns", calls);
        Assert.Contains("FurinaStage.RecastFromFront", calls);
        Assert.Contains("FurinaStageLedger.GuestArrives", calls);
    }

    [Fact]
    public void A_second_copy_bows_the_guest_and_returns_it_with_the_n_added()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 3), ("navia", 5), ("charlotte", 4));
        var navia = stage.SeatOf(StagePerformer.Navia)!;
        var exit = stage.GuestSteps(navia)!.Value;
        // It bows HOLDING its bar (Navia reads it) from the seat it stood in.
        Assert.Equal(5, exit.Held);
        Assert.Equal(1, exit.FormerSeat);
        Assert.True(exit.Bows);
        Assert.Equal(2, stage.Seats.Count);
        Assert.True(stage.GuestReturns(navia, 1, 4));
        Assert.Same(navia, stage.Seats[1]);
        Assert.Equal(new[] { 3, 9, 4 }, Bars(stage));
    }

    // ---- every act pays --------------------------------------------------------

    [Fact]
    public void Neuvillette_pays_three_of_his_own_or_cannot_pay()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("neuvillette", 6));
        var owed = new List<StageExit>();
        Assert.True(stage.ActFanfare(StagePerformer.Neuvillette,
                                     stage.Seats[0], null, owed));
        Assert.Equal(new[] { 3 }, Bars(stage));
        var pay = stage.Beats.Single(b => b.Event == FurinaStageLedger.PayEvent);
        Assert.Equal(3, pay.Moved);
        Assert.Equal("Neuvillette", pay.By);
        Assert.Empty(owed);

        var (_, short2) = Stage(("neuvillette", 2));
        Assert.False(short2.ActFanfare(StagePerformer.Neuvillette,
                                       short2.Seats[0], null, owed));
        Assert.Equal(new[] { 2 }, Bars(short2));
        Assert.Contains(short2.Beats,
                        b => b.Event == FurinaStageLedger.UnpaidEvent);
    }

    [Fact]
    public void A_payment_that_empties_the_payer_owes_its_bow_after_the_act()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("neuvillette", 3), ("usher", 2));
        var owed = new List<StageExit>();
        stage.ActFanfare(StagePerformer.Neuvillette, stage.Seats[0], null,
                         owed);
        var exit = Assert.Single(owed);
        Assert.Equal(StagePerformer.Neuvillette, exit.Who);
        Assert.Equal(0, exit.Held);
        Assert.Equal(new[] { StagePerformer.Usher },
                     stage.Seats.Select(s => s.Who).ToArray());
        // The act's order: pay, the effect, then the Bows owed.
        var seq = Il.CallSequence(Il.Method("FurinaStage", "Act")).ToList();
        var fanfare = seq.IndexOf("FurinaStageLedger.ActFanfare");
        var act = seq.IndexOf("FurinaStage.GuestAct");
        var bows = seq.IndexOf("FurinaStage.BowTheOwed");
        Assert.True(fanfare >= 0 && act > fanfare && bows > act,
                    string.Join(", ", seq));
    }

    [Fact]
    public void Clorinde_taxes_each_other_performer_and_alone_cannot_pay()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("clorinde", 4), ("usher", 1),
                               ("crabaletta", 3));
        var owed = new List<StageExit>();
        Assert.True(stage.ActFanfare(StagePerformer.Clorinde, stage.Seats[0],
                                     null, owed));
        Assert.Equal(new[] { 4, 2 }, Bars(stage));
        Assert.Equal(StagePerformer.Usher, Assert.Single(owed).Who);
        Assert.Equal(2, stage.Beats.Count(
            b => b.Event == FurinaStageLedger.PayEvent && b.By == "Clorinde"));

        var (_, alone) = Stage(("clorinde", 4));
        Assert.False(alone.ActFanfare(StagePerformer.Clorinde, alone.Seats[0],
                                      null, owed));
    }

    [Fact]
    public void Chevreuse_spends_two_from_the_back_which_may_be_herself()
    {
        using var _ = new Arm();
        var owed = new List<StageExit>();
        var (_, front) = Stage(("chevreuse", 4), ("usher", 5));
        Assert.True(front.ActFanfare(StagePerformer.Chevreuse, front.Seats[0],
                                     null, owed));
        Assert.Equal(new[] { 4, 3 }, Bars(front));
        var (_, back) = Stage(("usher", 3), ("chevreuse", 4));
        back.ActFanfare(StagePerformer.Chevreuse, back.Seats[1], null, owed);
        Assert.Equal(new[] { 3, 2 }, Bars(back));
        var (_, poor) = Stage(("chevreuse", 4), ("usher", 1));
        Assert.False(poor.ActFanfare(StagePerformer.Chevreuse, poor.Seats[0],
                                     null, owed));
        // The Energy is the base game's own next-turn power.
        Assert.Contains("PowerCmd.Apply",
                        Il.Calls(Il.Method("FurinaStage", "GuestAct")));
    }

    [Fact]
    public void Sigewinne_gives_behind_her_wraps_to_the_front_and_bows_free()
    {
        using var _ = new Arm();
        var owed = new List<StageExit>();
        var (_, mid) = Stage(("usher", 2), ("sigewinne", 8), ("navia", 1));
        mid.ActFanfare(StagePerformer.Sigewinne, mid.Seats[1], null, owed);
        Assert.Equal(new[] { 2, 5, 4 }, Bars(mid));

        var (_, back) = Stage(("usher", 2), ("sigewinne", 8));
        back.ActFanfare(StagePerformer.Sigewinne, back.Seats[1], null, owed);
        Assert.Equal(new[] { 5, 5 }, Bars(back));

        var (_, poor) = Stage(("usher", 2), ("sigewinne", 2));
        poor.ActFanfare(StagePerformer.Sigewinne, poor.Seats[1], null, owed);
        var exit = Assert.Single(owed);
        Assert.Equal(new[] { 4 }, Bars(poor));
        // Her Bow is free: the performer behind where she stood gains 3.
        poor.ActFanfare(StagePerformer.Sigewinne, null, exit, owed);
        Assert.Equal(new[] { 7 }, Bars(poor));
    }

    [Fact]
    public void Charlotte_gives_each_other_performer_one()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 2), ("charlotte", 4), ("navia", 1));
        stage.ActFanfare(StagePerformer.Charlotte, stage.Seats[1], null,
                         new List<StageExit>());
        Assert.Equal(new[] { 3, 4, 2 }, Bars(stage));
    }

    [Fact]
    public void A_bow_is_free_and_the_trio_never_pay()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 2), ("crabaletta", 2));
        var owed = new List<StageExit>();
        foreach (var who in new[] { StagePerformer.Neuvillette,
                                    StagePerformer.Clorinde,
                                    StagePerformer.Chevreuse })
        {
            Assert.True(stage.ActFanfare(
                who, null, new StageExit(who, StageDeparture.Spent), owed));
        }
        Assert.True(stage.ActFanfare(StagePerformer.Usher, stage.Seats[0],
                                     null, owed));
        Assert.Equal(new[] { 2, 2 }, Bars(stage));
        Assert.Empty(owed);
        Assert.DoesNotContain(stage.Beats,
                              b => b.Event == FurinaStageLedger.PayEvent);
    }

    [Fact]
    public void The_guests_elements_go_through_the_reacting_door()
    {
        var act = Il.Calls(Il.Method("FurinaStage", "GuestAct"));
        Assert.Contains("ElementalHit.Deal", act);
        Assert.Contains("ElementalHit.ApplyOnly", act);
        Assert.DoesNotContain("ElementalHit.DealUnelemented", act);
    }

    // ---- Wriothesley's reading -------------------------------------------------

    [Fact]
    public void Every_loss_counts_and_an_act_resets_it()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("wriothesley", 10), ("usher", 3));
        var wrio = stage.Seats[0];
        stage.Absorb(3);
        Assert.Equal(3, wrio.LostSinceAct);
        stage.StepForward();                       // Usher to the front
        stage.Fade();                              // wrio 7 -> 6, loses 1
        Assert.Equal(4, wrio.LostSinceAct);
        // The hit that takes him down is in his Bow's reading.
        stage.StepForward();
        var hit = stage.Absorb(20);
        Assert.Equal(4 + 6, hit.Exit!.Value.Lost);
        // An act resets it (FurinaStage.Act and the forecast's replay).
        Assert.Contains("StageSeat.set_LostSinceAct",
                        Il.Calls(Il.Method("FurinaStage", "GuestAct")));
    }

    // ---- rule 7, the forecast ------------------------------------------------

    /// <summary>The sim's BOARDS, word for word: (stage, Full House copies,
    /// hits, bars after with 0 for one that leaves, Block after the acts,
    /// what the front takes, what reaches Furina).</summary>
    public static IEnumerable<object[]> Boards() => new[]
    {
        B("neuvillette pays", new[] { ("neuvillette", 6), ("usher", 3) }, 0,
          new int[0], new int?[] { 3, 3 }, 3, 0, 0),
        B("tax and gift",
          new[] { ("usher", 3), ("clorinde", 4), ("charlotte", 4) }, 0,
          new int[0], new int?[] { 3, 5, 3 }, 3, 0, 0),
        B("the last payment bows",
          new[] { ("neuvillette", 3), ("sigewinne", 8) }, 0, new int[0],
          new int?[] { null, 8 }, 0, 0, 0),
        B("a gift wraps to the front",
          new[] { ("usher", 2), ("sigewinne", 8) }, 0, new int[0],
          new int?[] { 5, 5 }, 3, 0, 0),
        B("chevreuse spends herself",
          new[] { ("usher", 3), ("chevreuse", 4) }, 0, new int[0],
          new int?[] { 3, 2 }, 3, 0, 0),
        B("chevreuse cannot pay",
          new[] { ("chevreuse", 4), ("usher", 1) }, 0, new int[0],
          new int?[] { 4, 1 }, 3, 0, 0),
        B("full house pays twice",
          new[] { ("neuvillette", 6), ("usher", 3), ("crabaletta", 4) }, 1,
          new int[0], new int?[] { null, 3, 4 }, 6, 0, 0),
        B("the fade counts as lost",
          new[] { ("usher", 3), ("wriothesley", 10) }, 0, new int[0],
          new int?[] { 3, 8 }, 3, 0, 0),
        B("two hits through the front",
          new[] { ("usher", 3), ("crabaletta", 4) }, 0, new[] { 7, 7 },
          new int?[] { 3, 4 }, 3, 7, 1),
    };

    private static object[] B(string name, (string, int)[] stage, int fullHouse,
                              int[] hits, int?[] after, int block, int front,
                              int furina) =>
        new object[] { name, stage, fullHouse, hits, after, block, front,
                       furina };

    [Theory]
    [MemberData(nameof(Boards))]
    public void The_forecast_is_the_sims_actual_end_of_turn(
        string name, (string, int)[] seats, int fullHouse, int[] hits,
        int?[] after, int block, int front, int furina)
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        if (fullHouse > 0) seat.WithPower<FullHousePower>(fullHouse);
        var (_, stage) = Stage(seat, seats);
        var before = Bars(stage);
        var beats = stage.Beats.Count;

        var forecast = FurinaStage.Forecast(seat.Creature, hits);

        // PURE: the stage, its log and her Block have not moved.
        Assert.Equal(before, Bars(stage));
        Assert.Equal(beats, stage.Beats.Count);
        Assert.Equal(0, (int)seat.Creature.Block);

        Assert.Equal(after.Select(a => a ?? 0).ToArray(),
                     forecast.Seats.Select(r => r.After).ToArray());
        Assert.Equal(after.Select(a => a == null).ToArray(),
                     forecast.Seats.Select(r => r.Leaves).ToArray());
        Assert.Equal(before, forecast.Seats.Select(r => r.Now).ToArray());
        Assert.Equal(block, forecast.BlockAfterActs);
        Assert.Equal(front, forecast.FrontTakes);
        Assert.Equal(furina, forecast.ReachesFurina);
        Assert.True(forecast.IntentKnown, name);
    }

    [Fact]
    public void The_forecast_rides_the_wire_and_the_strip()
    {
        using var _ = new Arm();
        var (seat, _) = Stage(("neuvillette", 6), ("usher", 3));
        var wire = (Dictionary<string, object?>)FurinaStageLedger.Snapshot(
            seat.Player)["forecast"]!;
        var rows = (List<object?>)wire["seats"]!;
        var first = (Dictionary<string, object?>)rows[0]!;
        Assert.Equal("neuvillette", first["member"]);
        Assert.Equal(6, first["now"]);
        Assert.Equal(3, first["after"]);
        Assert.Equal(3, wire["block_after_acts"]);

        var lines = Vfx.FurinaStageStrip.Label(seat.Creature).Split('\n');
        Assert.Contains("End: Neuvillette 6 → 3  Usher 3 → 3", lines);
    }

    [Fact]
    public void A_pay_beat_carries_who_paid_on_the_wire()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("clorinde", 4), ("usher", 3));
        stage.ActFanfare(StagePerformer.Clorinde, stage.Seats[0], null,
                         new List<StageExit>());
        var log = (List<object?>)FurinaStageLedger.Snapshot(
            seat.Player)["log"]!;
        var pay = (Dictionary<string, object?>)log[0]!;
        Assert.Equal("pay", pay["event"]);
        Assert.Equal("usher", pay["member"]);
        Assert.Equal("Clorinde", pay["by"]);
        Assert.Equal("clorinde", pay["by_member"]);
        // #674's leak test: every event name is one plain word.
        Assert.Matches("^[a-z]+$", FurinaStageLedger.PayEvent);
        Assert.Matches("^[a-z]+$", FurinaStageLedger.UnpaidEvent);
    }

    // ---- the tips ------------------------------------------------------------

    [Fact]
    public void The_guest_star_and_bow_tips_are_the_ruled_sentences()
    {
        string Printed(string method) => string.Concat(Il.Strings(
            typeof(ArmKeywordTips).GetMethod(method, HeadlessGame.All)!));
        Assert.Contains(
            "A performer who joins the stage, one of each. A second copy "
          + "makes it Bow, then return with the new Fanfare added.",
            Printed("ForGuestStar"));
        Assert.Contains("on its way out, without paying.", Printed("ForBow"));
        foreach (var guest in new[] { "Neuvillette", "Clorinde", "Navia",
                                      "Chevreuse", "Wriothesley", "Sigewinne",
                                      "Charlotte", "Lynette" })
        {
            Assert.Contains("End of your turn: ", Printed("For" + guest));
        }
    }
}
