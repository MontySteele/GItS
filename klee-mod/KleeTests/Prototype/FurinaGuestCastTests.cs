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
        // Eight, and two more with the supporting pool (2026-09-26): Lyney
        // and Escoffier.
        Assert.Equal(10, FurinaStage.Guests.Length);
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
        // Each guest's scene is a LITERAL pack path (the deploy's S12 check
        // reads literals). Read off the IL: calling the method would reach
        // Godot's ResourceLoader, which has no engine under test.
        var scenes = Il.Strings(typeof(StagePerformerMonster)
            .GetMethod("ModVisualsPathFor", HeadlessGame.All)!);
        foreach (var name in FurinaStage.Guests)
        {
            var who = P(name);
            var model = (Type)typeof(FurinaStagePets)
                .GetMethod("ModelFor", HeadlessGame.All)!
                .Invoke(null, new object[] { who })!;
            Assert.Equal(name, model.Name.Replace("Monster", "")
                                   .ToLowerInvariant());
            Assert.Contains($"furina/model/guest_{name}.tscn", scenes);
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

    // ---- the guest seat round (2026-09-25): Wriothesley joins at the front ---

    [Fact]
    public void Wriothesley_played_onto_two_performers_stands_in_front_and_takes_the_next_hit()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 3), ("crabaletta", 4));
        Assert.True(stage.GuestArrives(StagePerformer.Wriothesley, 8,
                                       atFront: true));
        Assert.Equal(new[] { StagePerformer.Wriothesley, StagePerformer.Usher,
                             StagePerformer.Crabaletta },
                     stage.Seats.Select(s => s.Who).ToArray());
        Assert.Equal(new[] { 8, 3, 4 }, Bars(stage));
        var arrive = stage.Beats[^1];
        Assert.Equal(("arrive", 0), (arrive.Event, arrive.Seat));

        // The forecast reads the stage the card left: past Usher's 3 Block
        // the next hit is his, and none of it reaches her.
        var forecast = FurinaStage.Forecast(seat.Creature, new[] { 9 });
        Assert.Equal(StagePerformer.Wriothesley, forecast.Seats[0].Who);
        Assert.Equal(9 - FurinaStageLaw.ActUsherBlock, forecast.FrontTakes);
        Assert.Equal(0, forecast.ReachesFurina);

        // And the hit, dealt: his bar takes it and his reading counts it.
        var hit = stage.Absorb(5);
        Assert.Equal(5, hit.Absorbed);
        Assert.Equal(new[] { 3, 3, 4 }, Bars(stage));
        Assert.Equal(5, stage.Seats[0].LostSinceAct);
    }

    [Fact]
    public void A_second_ushers_arrival_names_his_own_seat_on_the_wire()
    {
        // The guest seat round (2026-09-25): the log said a summoned Usher
        // "stands in the front seat" while the stage showed him at the back.
        // The arrival beat carries the key of the seat he took.
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 3));
        stage.Summon(StagePerformer.Usher);
        var wire = FurinaStageLedger.Snapshot(seat.Player);
        var seats = ((List<object?>)wire["seats"]!)
            .Cast<Dictionary<string, object?>>().ToList();
        var arrive = ((List<object?>)wire["log"]!)
            .Cast<Dictionary<string, object?>>()
            .Single(r => (string?)r["event"] == "arrive");
        Assert.Equal(2, seats.Count);
        Assert.NotEqual(seats[0]["seat_key"], seats[1]["seat_key"]);
        Assert.Equal(seats[1]["seat_key"], arrive["seat_key"]);
        Assert.Equal(1, arrive["seat"]);
    }

    [Fact]
    public void A_front_guest_on_a_full_stage_recasts_the_front()
    {
        // THE RULES PASS (2026-10-01): "Always your front performer", and
        // every summon works as normal around him -- so on a full stage the
        // FRONT performer Bows for him, as for any summon.
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 5), ("chevalmarin", 2),
                               ("crabaletta", 4));
        Assert.Equal(0, stage.LeaverIndex);
        var leaver = stage.BowFromFront()!;
        Assert.Equal(StagePerformer.Usher, leaver.Who);
        Assert.Equal(5, leaver.Fanfare);
        Assert.True(stage.ArriveAtFront(StagePerformer.Wriothesley,
                                        leaver.Fanfare + 8));
        Assert.Equal(new[] { StagePerformer.Wriothesley,
                             StagePerformer.Chevalmarin,
                             StagePerformer.Crabaletta },
                     stage.Seats.Select(s => s.Who).ToArray());
        Assert.Equal(new[] { 13, 2, 4 }, Bars(stage));
        // The card's verb: a front guest on a full stage takes that door.
        var calls = Il.Calls(Il.Method("FurinaStage", "GuestStar"));
        Assert.Contains("FurinaStage.RecastToFront", calls);
        var recast = Il.Calls(Il.Method("FurinaStage", "RecastToFront"));
        Assert.Contains("FurinaStageLedger.BowFromFront", recast);
        Assert.Contains("FurinaStage.Bow", recast);
        Assert.Contains("FurinaStageLedger.ArriveAtFront", recast);
    }

    [Fact]
    public void Wriothesleys_card_puts_him_at_the_front()
    {
        var face = new global::KleeMod.Cards.Prototype.Generated
            .ProtoFsGuestStarWriothesley().Localization!
            .Single(l => l.Item1 == "description").Item2;
        // The second text pass (2026-09-28): "Summon". The rules pass
        // (2026-10-01): one sentence replaces his exceptions.
        Assert.StartsWith("Summon Wriothesley with ", face);
        Assert.EndsWith("Always your [gold]front performer[/gold].", face);
        // The generated play passes the front seat (codegen's `seat: front`).
        var src = RepoFile(Path.Combine("KleeCode", "Cards", "Prototype",
            "Generated", "ProtoFsGuestStarWriothesley.cs"));
        Assert.Contains("\"wriothesley\", DynamicVars[\"GuestFanfare\"]"
                        + ".IntValue, atFront: true);", src);
    }

    private static string RepoFile(string relativePath,
                                   [CallerFilePath] string here = "")
    {
        var dir = Path.GetDirectoryName(here);
        while (dir != null)
        {
            var candidate = Path.Combine(dir, relativePath);
            if (File.Exists(candidate)) return File.ReadAllText(candidate);
            dir = Path.GetDirectoryName(dir);
        }
        throw new FileNotFoundException(relativePath);
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
        // 2026-09-26: an emptied payer's Bow reads the bar it had (Navia).
        Assert.Equal(3, exit.Held);
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

    // ---- Sigewinne the medic (2026-09-29) ------------------------------
    //
    // [USER]: "I think Siegwinne needs to be rethought - she's strictly
    // fanfare-negative while she's summoned." Her act is FREE: the front
    // performer regains half the Fanfare hits took from it since her last
    // act, rounded down, at least 2. The sim's pins are the same boards.

    [Fact]
    public void Sigewinne_heals_the_front_half_what_hits_took_at_least_two()
    {
        using var _ = new Arm();
        var owed = new List<StageExit>();
        var (_, stage) = Stage(("usher", 10), ("sigewinne", 5));
        var her = stage.Seats[1];
        stage.Absorb(7);
        Assert.Equal(7, her.FrontLostSinceAct);
        Assert.True(stage.ActFanfare(StagePerformer.Sigewinne, her, null,
                                     owed));
        Assert.Equal(new[] { 3 + 3, 5 }, Bars(stage));
        Assert.Empty(owed);
        Assert.DoesNotContain(stage.Beats,
                              b => b.Event == FurinaStageLedger.PayEvent);
        // The act resets her reading (GuestAct and the forecast's replay),
        // and an act with nothing to read heals the floor.
        Assert.Contains("StageSeat.set_FrontLostSinceAct",
                        Il.Calls(Il.Method("FurinaStage", "GuestAct")));
        var (_, calm) = Stage(("usher", 6), ("sigewinne", 5));
        calm.ActFanfare(StagePerformer.Sigewinne, calm.Seats[1], null, owed);
        Assert.Equal(new[] { 6 + 2, 5 }, Bars(calm));
        Assert.Equal(2, FurinaStageLaw.SigewinneHeal(0));
        Assert.Equal(2, FurinaStageLaw.SigewinneHeal(5));
        Assert.Equal(3, FurinaStageLaw.SigewinneHeal(7));
    }

    [Fact]
    public void Sigewinne_reads_whoever_stood_in_front_and_only_while_on_stage()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("crabaletta", 3), ("usher", 10),
                               ("sigewinne", 5));
        stage.Absorb(5);                   // Crabaletta eats 3 and leaves
        stage.TakePendingHitBows();
        stage.Absorb(4);                   // Usher eats 4
        Assert.Equal(7, stage.SeatOf(StagePerformer.Sigewinne)!
                            .FrontLostSinceAct);

        var (_, late) = Stage(("usher", 10));
        late.Absorb(6);
        late.GuestArrives(StagePerformer.Sigewinne, 5);
        Assert.Equal(0, late.SeatOf(StagePerformer.Sigewinne)!
                           .FrontLostSinceAct);
    }

    [Fact]
    public void Sigewinne_in_front_heals_herself_and_her_bow_heals_the_new_front()
    {
        using var _ = new Arm();
        var owed = new List<StageExit>();
        var (_, self) = Stage(("sigewinne", 8), ("usher", 2));
        self.Absorb(6);
        self.ActFanfare(StagePerformer.Sigewinne, self.Seats[0], null, owed);
        Assert.Equal(new[] { 2 + 3, 2 }, Bars(self));

        var (_, bow) = Stage(("sigewinne", 6), ("usher", 2));
        var hit = bow.Absorb(6);
        var exit = hit.Exit!.Value;
        Assert.Equal(6, exit.FrontLost);
        // Free: Usher, in front now, regains 6 / 2 = 3.
        bow.ActFanfare(StagePerformer.Sigewinne, null, exit, owed);
        Assert.Equal(new[] { 2 + 3 }, Bars(bow));
    }

    // ---- Wriothesley holds the front (2026-09-29) -----------------------
    //
    // [USER]: "One issue on Wriothesley is that keeping him in the front was
    // actually hard. Can we pin him to the front of the Stage while he's
    // present?" No seat move takes the front from him; he leaves only by
    // Bowing.

    [Fact]
    public void No_seat_move_takes_the_front_from_wriothesley()
    {
        using var _ = new Arm();
        var moves = new System.Action<FurinaStageLedger>[]
        {
            s => s.StepForward(),
            s => s.Reverse(),
            s => s.SceneChange(),
            s => s.SwapToFront(s.Seats[1]),
        };
        foreach (var move in moves)
        {
            var (_, stage) = Stage(("wriothesley", 5), ("usher", 3),
                                   ("crabaletta", 2));
            move(stage);
            Assert.Equal(new[] { StagePerformer.Wriothesley,
                                 StagePerformer.Usher,
                                 StagePerformer.Crabaletta },
                         stage.Company.ToArray());
            var held = Assert.Single(stage.Beats,
                                     b => b.Event == FurinaStageLedger.HeldEvent);
            Assert.Equal(StagePerformer.Wriothesley, held.Who);
        }
        // Without him, the moves move.
        var (_, free) = Stage(("usher", 3), ("crabaletta", 2));
        free.StepForward();
        Assert.Equal(StagePerformer.Crabaletta, free.Lead!.Who);
    }

    [Fact]
    public void A_recast_behind_wriothesley_bows_the_one_behind_him()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("wriothesley", 5), ("usher", 3),
                               ("crabaletta", 2));
        Assert.Equal(1, stage.LeaverIndex);
        var leaver = stage.BowFromFront();
        Assert.Equal(StagePerformer.Usher, leaver!.Who);
        Assert.True(stage.ArriveAtBack(StagePerformer.Navia, 3 + 4));
        Assert.Equal(new[] { StagePerformer.Wriothesley,
                             StagePerformer.Crabaletta,
                             StagePerformer.Navia },
                     stage.Company.ToArray());
        // The ledger's own full-stage summon rotates the one behind him too.
        var (_, full) = Stage(("wriothesley", 5), ("usher", 3),
                              ("crabaletta", 2));
        full.Summon(StagePerformer.Chevalmarin);
        Assert.Equal(StagePerformer.Wriothesley, full.Lead!.Who);
        Assert.DoesNotContain(StagePerformer.Usher, full.Company);
    }

    [Fact]
    public void Wriothesley_returns_to_the_front()
    {
        using var _ = new Arm();
        // A Five-Century return and Let the People Rejoice's return put him
        // back in the seat he holds.
        var (_, stage) = Stage(("usher", 3));
        Assert.True(stage.ReturnToBack(StagePerformer.Wriothesley));
        Assert.Equal(StagePerformer.Wriothesley, stage.Lead!.Who);
        var (_, rejoice) = Stage(("usher", 3));
        rejoice.ReturnCompany(new[] { StagePerformer.Wriothesley });
        Assert.Equal(StagePerformer.Wriothesley, rejoice.Lead!.Who);
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
        // 2026-09-25 night: Lynette's act DEALS Anemo damage now (a Swirl
        // through `Deal`'s own reaction step), so nothing applies only.
        Assert.DoesNotContain("ElementalHit.ApplyOnly", act);
        Assert.DoesNotContain("ElementalHit.DealUnelemented", act);
    }

    // ---- Wriothesley's reading -------------------------------------------------

    [Fact]
    public void Only_hits_count_and_an_act_resets_it()
    {
        // 2026-09-25: Wriothesley counts only what enemy hits took ("he is
        // the tank, not a Spend engine"). Spends, payments, taxes, gifts,
        // cash-outs and the fade take Fanfare and do not count.
        using var _ = new Arm();
        // 2026-09-29: he holds the front now, so he stands alone, the front
        // and the back performer both.
        var (_, stage) = Stage(("wriothesley", 10));
        var wrio = stage.Seats[0];
        stage.Absorb(3);
        Assert.Equal(3, wrio.LostSinceAct);
        stage.Fade();                              // wrio 7 -> 6: not a hit
        stage.Spend(2);                            // wrio 6 -> 4: not a hit
        Assert.Equal(3, wrio.LostSinceAct);
        // The hit that takes him down is in his Bow's reading.
        var hit = stage.Absorb(20);
        Assert.Equal(3 + 4, hit.Exit!.Value.Lost);
        // An act resets it (FurinaStage.Act and the forecast's replay).
        Assert.Contains("StageSeat.set_LostSinceAct",
                        Il.Calls(Il.Method("FurinaStage", "GuestAct")));
    }

    // ---- rule 7, the forecast ------------------------------------------------

    /// <summary>The sim's BOARDS, word for word: (stage, Full House copies,
    /// hits, bars after with 0 for one that leaves, Block after the acts,
    /// what the front takes, what reaches Furina). The fade pass (2026-09-29)
    /// moved every bar of 4 or more: a quarter fades, the front's too.</summary>
    public static IEnumerable<object[]> Boards() => new[]
    {
        B("neuvillette pays", new[] { ("neuvillette", 6), ("usher", 3) }, 0,
          new int[0], new int?[] { 3, 3 }, 3, 0, 0),
        B("tax and gift",
          new[] { ("usher", 3), ("clorinde", 4), ("charlotte", 4) }, 0,
          new int[0], new int?[] { 3, 4, 3 }, 3, 0, 0),
        // 2026-09-29: Sigewinne the medic heals the front 2, free;
        // Neuvillette has left, so she is the front.
        B("the last payment bows",
          new[] { ("neuvillette", 3), ("sigewinne", 8) }, 0, new int[0],
          new int?[] { null, 8 }, 0, 0, 0),
        B("the medic heals the front",
          new[] { ("usher", 2), ("sigewinne", 8) }, 0, new int[0],
          new int?[] { 3, 6 }, 3, 0, 0),
        B("chevreuse spends herself",
          new[] { ("usher", 3), ("chevreuse", 4) }, 0, new int[0],
          new int?[] { 3, 2 }, 3, 0, 0),
        B("chevreuse cannot pay",
          new[] { ("chevreuse", 4), ("usher", 1) }, 0, new int[0],
          new int?[] { 3, 1 }, 3, 0, 0),
        B("full house pays twice",
          new[] { ("neuvillette", 6), ("usher", 3), ("crabaletta", 4) }, 1,
          new int[0], new int?[] { null, 3, 3 }, 6, 0, 0),
        // 2026-09-29 (Furina seat, Vantom, run FS3EL3M3NTS4): the preview
        // was read as "8 Hydro to ALL, twice" with a repeat that "could not
        // pay". The forecast pays each repeat on the clone before it counts
        // it: at 5 Neuvillette pays once, keeps 2, and the repeat is refused.
        B("full house, the repeat cannot pay",
          new[] { ("usher", 3), ("crabaletta", 4), ("neuvillette", 5) }, 1,
          new int[0], new int?[] { 3, 3, 2 }, 6, 0, 0),
        B("the fade is not a hit",
          new[] { ("usher", 3), ("wriothesley", 10) }, 0, new int[0],
          new int?[] { 3, 8 }, 3, 0, 0),
        B("two hits through the front",
          new[] { ("usher", 3), ("crabaletta", 4) }, 0, new[] { 7, 7 },
          new int?[] { 3, 3 }, 3, 6, 2),
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
        // The second text pass (2026-09-28).
        Assert.Contains(
            "You can have one of each on stage. Summoning one already there "
          + "makes it [gold]Bow[/gold], then return with the new "
          + "[gold]Fanfare[/gold] added.",
            Printed("ForGuestStar"));
        // The rules pass (2026-10-01): the Bow covers Grand Finale's stay.
        Assert.Contains("A performer acts one last time, without paying, as "
                        + "it leaves the stage or, if a card says so, stays.",
                        Printed("ForBow"));
        foreach (var guest in new[] { "Neuvillette", "Clorinde", "Navia",
                                      "Chevreuse", "Wriothesley", "Sigewinne",
                                      "Charlotte", "Lynette" })
        {
            Assert.Contains("End of your turn: ", Printed("For" + guest));
        }
    }

    // ---- the Spend warning (pool round 2026-10-01, "What to change" 2) -----

    [Fact]
    public void A_spend_names_the_guests_it_leaves_unable_to_pay()
    {
        using var _ = new Arm();
        // Neuvillette at the back pays the Spend first: 4 - 2 is short of 3.
        var (seat, stage) = Stage(("usher", 3), ("neuvillette", 4));
        Assert.Equal(new[] { StagePerformer.Neuvillette },
                     stage.StrandedBySpend(2));
        Assert.Equal(new[] { StagePerformer.Neuvillette },
                     FurinaStage.StrandedBySpend(seat.Creature, 2));
        Assert.Empty(stage.StrandedBySpend(1));
        // Pure: the board is untouched.
        Assert.Equal(new[] { 3, 4 }, Bars(stage));
        Assert.Empty(stage.Beats);

        // Clorinde left alone: the Spend empties the only other performer.
        var (_, clorinde) = Stage(("clorinde", 5), ("usher", 2));
        Assert.Equal(new[] { StagePerformer.Clorinde },
                     clorinde.StrandedBySpend(2));

        // Chevreuse's act spends the back performer, which the Spend drained.
        var (_, chevreuse) = Stage(("chevreuse", 4), ("usher", 3));
        Assert.Equal(new[] { StagePerformer.Chevreuse },
                     chevreuse.StrandedBySpend(FurinaStageLaw.ActChevreusePrice));

        // Already short before the Spend: the Spend is not the cause.
        var (_, already) = Stage(("usher", 3), ("neuvillette", 2));
        Assert.Empty(already.StrandedBySpend(1));
        // A Spend the stage cannot pay is not offered, so it warns of nothing.
        Assert.Empty(already.StrandedBySpend(9));
    }
}
