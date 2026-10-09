using System;
using System.Linq;
using System.Reflection;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE POOL TO 75 (<c>review/active/furina-pool-growth-2026-10-09.md</c>,
/// ruled 2026-10-09): sec.3's guest rule and sec.5's new verbs, pinned
/// headlessly over the director and the recording board
/// (<see cref="StageKit"/>). The sim twin is <c>tier0/tests/test_furina_pool75.py</c>.
///
/// THE RULE: a Guest Star exhausts when played and has no effect on summon;
/// when its guest leaves (a fourth summon, or Final Bow) its card goes to the
/// discard pile; a duplicate moves its guest to the newest seat with no act;
/// at the end of her turn the guests act oldest first, then Showstopper
/// Spends 5 and they act again, then Salon Solitaire Repays; a guest's line
/// gets a cue and a log line of its own.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaGuestRuleTests
{
    private const BindingFlags All = BindingFlags.Public | BindingFlags.NonPublic
        | BindingFlags.Instance | BindingFlags.Static;

    private static readonly Type[] GuestCards =
    {
        typeof(ProtoFsGuestStarCharlotte), typeof(ProtoFsGuestStarWriothesley),
        typeof(ProtoFsGuestStarLynette), typeof(ProtoFsGuestStarClorinde),
        typeof(ProtoFsGuestStarLyney), typeof(ProtoFsGuestStarSigewinne),
        typeof(ProtoFsGuestStarChevreuse), typeof(ProtoFsGuestStarFreminet),
        typeof(ProtoFsGuestStarNavia), typeof(ProtoFsGuestStarNeuvillette),
        typeof(ProtoFsGuestStarEscoffier),
    };

    private static T Run<T>(System.Threading.Tasks.Task<T> task) =>
        StageKit.Run(task);

    private static void Run(System.Threading.Tasks.Task task) =>
        StageKit.Run(task);

    private static CardModel Upgraded(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, null);
        return card;
    }

    // ---- a Guest Star exhausts, hands itself over, and never upgrades cost --

    [Fact]
    public void Every_guest_star_exhausts_and_its_upgrade_is_not_a_cost_cut()
    {
        foreach (var type in GuestCards)
        {
            var card = (CardModel)Activator.CreateInstance(type)!;
            Assert.Contains(CardKeyword.Exhaust, card.CanonicalKeywords);
            var upgrade = Il.Calls(type.GetMethod("OnUpgrade", All)!);
            Assert.DoesNotContain(upgrade, c => c.Contains("UpgradeBy"));
            // The card hands itself to the summon (its seat holds it).
            Assert.Contains("FurinaStage.GuestStar",
                            Il.Calls(type.GetMethod("OnPlay", All)!));
            Assert.Equal(1, FurinaCards.IsGuestStar(card) ? 1 : 0);
        }
        Assert.Equal(11, FurinaStage.Guests.Length);
    }

    [Fact]
    public void A_summon_has_no_effect_and_the_seat_holds_the_card()
    {
        var kit = StageKit.Of();
        var card = new ProtoFsGuestStarClorinde();
        Assert.Equal(StageSummonResult.Seated,
            Run(kit.Director.SummonGuest(StagePerformer.Clorinde, false, card)));
        Assert.Empty(kit.Board.Hits);
        Assert.Same(card, kit.Stage.Seats.Single().Cards.Single());
    }

    // ---- the card returns when its guest leaves ------------------------------

    [Fact]
    public void An_evicted_guest_sends_its_card_to_the_discard_pile()
    {
        var kit = StageKit.Of();
        var first = new ProtoFsGuestStarWriothesley();
        Run(kit.Director.SummonGuest(StagePerformer.Wriothesley, false, first));
        Run(kit.Director.SummonGuest(StagePerformer.Lynette));
        Run(kit.Director.SummonGuest(StagePerformer.Clorinde));
        Run(kit.Director.SummonGuest(StagePerformer.Charlotte));
        Assert.Equal(new[] { StagePerformer.Lynette, StagePerformer.Clorinde,
                             StagePerformer.Charlotte }, kit.Company);
        Assert.Same(first, kit.Board.Returned.Single());
        Assert.Empty(kit.Board.Hits);
    }

    [Fact]
    public void Final_bow_acts_twice_then_leaves_and_returns_the_card()
    {
        var kit = StageKit.Of(StagePerformer.Charlotte);
        var card = new ProtoFsGuestStarClorinde();
        Run(kit.Director.SummonGuest(StagePerformer.Clorinde, false, card));
        Assert.True(Run(kit.Director.FinalBow(1, 2)));
        Assert.Equal(2, kit.Board.Hits.Count(h => h == "damage Clorinde Random 6 Electro"));
        Assert.Equal(new[] { StagePerformer.Charlotte }, kit.Company);
        Assert.Same(card, kit.Board.Returned.Single());
        // Upgraded: three times.
        var up = StageKit.Of(StagePerformer.Wriothesley);
        Run(up.Director.FinalBow(0, 3));
        Assert.Equal(3, up.Board.Hits.Count());
        Assert.Empty(up.Company);
    }

    // ---- a duplicate moves its guest, with no act ----------------------------

    [Fact]
    public void A_duplicate_moves_its_guest_to_the_newest_seat_and_keeps_both_cards()
    {
        var kit = StageKit.Of();
        var a = new ProtoFsGuestStarLynette();
        var b = new ProtoFsGuestStarLynette();
        Run(kit.Director.SummonGuest(StagePerformer.Lynette, false, a));
        Run(kit.Director.SummonGuest(StagePerformer.Chevreuse));
        var seat = kit.Stage.Seats[0];
        Assert.Equal(StageSummonResult.Repeat,
            Run(kit.Director.SummonGuest(StagePerformer.Lynette, true, b)));
        Assert.Equal(new[] { StagePerformer.Chevreuse, StagePerformer.Lynette },
                     kit.Company);
        Assert.Same(seat, kit.Stage.Seats[1]);
        Assert.True(seat.Upgraded);
        Assert.Equal(new CardModel[] { a, b }, seat.Cards);
        Assert.Empty(kit.Board.Hits);
        Assert.Equal(1, kit.Beats(FurinaStageLedger.MoveEvent, StagePerformer.Lynette));
        Assert.Equal(0, kit.Beats(FurinaStageLedger.ActEvent));
    }

    // ---- the end of her turn --------------------------------------------------

    [Fact]
    public void At_the_end_of_turn_guests_act_oldest_first_then_showstopper_then_the_singer()
    {
        var kit = StageKit.With(new StageMods { Showstopper = 1 }, 5,
                                StagePerformer.Wriothesley, StagePerformer.Clorinde);
        Run(kit.Director.Drain(4));
        kit.Board.Log.Clear();
        Run(kit.Director.EndOfTurn(FurinaStageLaw.SingerRepay));
        var expected = new[]
        {
            "damage Wriothesley Random 4 Cryo",
            "damage Clorinde Random 6 Electro",
            // Showstopper: Spend 5 (the bank held 5 + 4 drained), act again.
            "damage Wriothesley Random 4 Cryo",
            "damage Clorinde Random 6 Electro",
            // Salon Solitaire, then Clorinde's line answers its Repay.
            "heal 1",
        };
        Assert.Equal(expected, kit.Board.Log.Take(5).ToArray());
        Assert.Equal(1, kit.Stage.SpendsThisTurn);
        Assert.Contains("cue Clorinde", kit.Board.Log.Skip(5));
    }

    [Fact]
    public void Showstopper_does_not_spend_on_an_empty_stage_or_a_short_bank()
    {
        var empty = StageKit.With(new StageMods { Showstopper = 1 }, 9);
        Run(empty.Director.EndOfTurn(0));
        Assert.Equal(9, empty.Stage.Fanfare);
        var poor = StageKit.With(new StageMods { Showstopper = 1 }, 4,
                                 StagePerformer.Chevreuse);
        Run(poor.Director.EndOfTurn(0));
        Assert.Equal(4, poor.Stage.Fanfare);
        Assert.Single(poor.Board.Hits);
    }

    // ---- a line has a cue and a log line of its own --------------------------

    [Fact]
    public void A_line_is_logged_and_cued_apart_from_an_act()
    {
        var kit = StageKit.Of(StagePerformer.Wriothesley);
        Run(kit.Director.Drain(3));
        Assert.Equal(1, kit.Beats(FurinaStageLedger.LineEvent, StagePerformer.Wriothesley));
        Assert.Equal(0, kit.Beats(FurinaStageLedger.ActEvent));
        Assert.Contains("cue Wriothesley", kit.Board.Log);
    }

    // ---- the four new guests --------------------------------------------------

    [Fact]
    public void Freminet_blocks_each_drain_and_acts_for_five_cryo()
    {
        var kit = StageKit.Of(StagePerformer.Freminet);
        Run(kit.Director.Drain(4));
        Assert.Contains("block 4", kit.Board.Log);
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.Contains("damage Freminet Random 5 Cryo", kit.Board.Log);
        Assert.Equal(8, StageDirector.ActAmount(StagePerformer.Freminet, true));
    }

    [Fact]
    public void Navias_first_spend_each_turn_costs_two_less_and_a_spend_all_keeps_two()
    {
        var kit = StageKit.With(6, StagePerformer.Navia);
        Assert.True(kit.Stage.CanSpend(8));
        Assert.False(kit.Stage.CanSpend(9));
        Assert.Equal(6, Run(kit.Director.Spend(6)));
        Assert.Equal(2, kit.Stage.Fanfare);                 // paid 4
        Assert.Equal(1, kit.Beats(FurinaStageLedger.LineEvent, StagePerformer.Navia));
        Assert.Equal(2, Run(kit.Director.Spend(2)));       // second: full price
        Assert.Equal(0, kit.Stage.Fanfare);
        var all = StageKit.With(9, StagePerformer.Navia);
        Assert.Equal(9, Run(all.Director.SpendAll()));
        Assert.Equal(2, all.Stage.Fanfare);
        // Her act deals the Fanfare spent this turn, as Geo.
        Run(all.Director.Act(all.Stage.Seats[0]));
        Assert.Contains("damage Navia Random 7 Geo", all.Board.Log);
    }

    [Fact]
    public void Neuvillettes_act_deals_the_hp_lost_since_her_last_turn_to_all()
    {
        var kit = StageKit.Of(StagePerformer.Neuvillette);
        Run(kit.Director.Drain(3));
        Run(kit.Director.Drain(2));
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.Contains("damage Neuvillette All 5 Hydro", kit.Board.Log);
        Assert.Equal(3, FurinaStageLaw.NeuvilletteHydroBonusUpgraded);
    }

    [Fact]
    public void Escoffiers_line_repays_one_whenever_a_guest_acts_his_own_included()
    {
        var kit = StageKit.Of(StagePerformer.Charlotte, StagePerformer.Escoffier);
        Run(kit.Director.Drain(10));
        kit.Board.Log.Clear();
        Run(kit.Director.ActAll());
        Assert.Equal(2, kit.Beats(FurinaStageLedger.LineEvent, StagePerformer.Escoffier));
        Assert.Contains("damage Escoffier All 4 Cryo", kit.Board.Log);
        // Charlotte Repays 2, Escoffier 1 after each act.
        Assert.Equal(new[] { "heal 2", "heal 1", "heal 1" },
                     kit.Board.Log.Where(l => l.StartsWith("heal ")).ToArray());
    }

    [Fact]
    public void An_upgraded_guest_raises_its_act_or_its_line()
    {
        var kit = StageKit.Of();
        Run(kit.Director.SummonGuest(StagePerformer.Clorinde, true));
        Run(kit.Director.Act(kit.Stage.Seats[0]));
        Assert.Contains("damage Clorinde Random 9 Electro", kit.Board.Log);
        var chev = StageKit.With(5);
        Run(chev.Director.SummonGuest(StagePerformer.Chevreuse, true));
        Run(chev.Director.Spend(1));
        Assert.Contains("weak Random 1", chev.Board.Log);
        Assert.Contains("Repay[/gold] 4",
            StagePerformerBadge.ActText(StagePerformer.Charlotte, true));
        Assert.Contains("Weak", StagePerformerBadge.ActText(StagePerformer.Chevreuse, true));
    }

    [Fact]
    public void Ensemble_cast_seats_four_guests()
    {
        var kit = StageKit.With(new StageMods { Capacity = FurinaStageLaw.EnsembleSeats }, 0,
                                StagePerformer.Charlotte, StagePerformer.Lynette,
                                StagePerformer.Clorinde);
        Assert.Equal(StageSummonResult.Seated,
            Run(kit.Director.SummonGuest(StagePerformer.Sigewinne)));
        Assert.Equal(4, kit.Company.Length);
        Assert.Equal(StageSummonResult.Evict,
            Run(kit.Director.SummonGuest(StagePerformer.Lyney)));
    }

    // ---- the new verbs ---------------------------------------------------------

    [Fact]
    public void Encore_acts_the_oldest_and_tutti_acts_each_guest()
    {
        var kit = StageKit.Of(StagePerformer.Wriothesley, StagePerformer.Clorinde);
        Assert.True(Run(kit.Director.ActOldest()));
        Assert.Equal("damage Wriothesley Random 4 Cryo", kit.Board.Hits.Single());
        Assert.Equal(2, Run(kit.Director.ActAll()));
        Assert.False(Run(StageKit.Of().Director.ActOldest()));
        Assert.Contains("FurinaCards.ActOldest",
            Il.Calls(typeof(ProtoFsEncore).GetMethod("OnPlay", All)!));
        Assert.Contains("FurinaCards.ActAll",
            Il.Calls(typeof(ProtoFsTutti).GetMethod("OnPlay", All)!));
        Assert.Contains("FurinaCards.ActAll",
            Il.Calls(typeof(ProtoFsBringTheHouseDown).GetMethod("OnPlay", All)!));
        Assert.Contains("FurinaCards.FinalBow",
            Il.Calls(typeof(ProtoFsFinalBow).GetMethod("OnPlay", All)!));
        Assert.Contains("FurinaCards.TutorGuest",
            Il.Calls(typeof(ProtoFsCastingCall).GetMethod("OnPlay", All)!));
        Assert.Contains("FurinaCards.RepayNextTurn",
            Il.Calls(typeof(ProtoFsGentleCurrent).GetMethod("OnPlay", All)!));
    }

    [Fact]
    public void Crescendo_draws_on_the_first_spend_each_turn_only()
    {
        var kit = StageKit.With(new StageMods { Crescendo = 1 }, 9);
        Run(kit.Director.Spend(2));
        Run(kit.Director.Spend(2));
        Assert.Equal(1, kit.Board.Drawn);
        kit.Stage.OpenTurn();
        Run(kit.Director.SpendAll());
        Assert.Equal(2, kit.Board.Drawn);
    }

    [Fact]
    public void Standing_room_only_gives_strength_on_a_spend_all_of_at_least_one()
    {
        var kit = StageKit.With(new StageMods { StandingRoomOnly = 1 }, 3);
        Run(kit.Director.SpendAll());
        Run(kit.Director.SpendAll());                   // nothing held
        Assert.Equal(1, kit.Board.Gained);
    }

    [Fact]
    public void Hymn_of_renewal_counts_hp_actually_repaid()
    {
        var kit = StageKit.With(new StageMods { HymnOfRenewal = 1 }, 0);
        Run(kit.Director.Drain(3));
        Run(kit.Director.Repay(6));                     // returns 3: no Strength
        Assert.Equal(0, kit.Board.Gained);
        Run(kit.Director.Drain(5));
        Run(kit.Director.Repay(4));                     // returns 4: Strength
        Assert.Equal(1, kit.Board.Gained);
    }

    [Fact]
    public void Regina_drains_three_for_a_strength_and_pneuma_tides_repays()
    {
        var kit = StageKit.Of();
        Assert.Equal(2, Run(kit.Director.Regina(2)));
        Assert.Equal(72, kit.Board.Hp);
        Assert.Equal(2, kit.Board.Gained);
        Assert.Equal(2, Run(kit.Director.PneumaTides(2)));
        var low = StageKit.At(3, 78);                   // 3 - 3 = 0 HP: no room
        Assert.Equal(0, Run(low.Director.Regina(1)));
        Assert.Equal(0, low.Board.Gained);
        foreach (var hook in new[] { "FurinaStage.ReginaDrains",
                                     "FurinaStage.PneumaTidesRepays",
                                     "FurinaStage.RepayNextTurnRepays",
                                     "FurinaStage.PrimaDonnaEnergy" })
        {
            Assert.Contains(hook, Il.Calls(Il.Method("FurinaStage", "TurnStart")));
        }
    }

    [Fact]
    public void The_counts_the_new_attacks_read()
    {
        var kit = StageKit.Of();
        Run(kit.Director.Drain(4));
        Run(kit.Director.Drain(4));
        Assert.Equal(2, kit.Stage.DrainsThisCombat);
        kit.Stage.BeginPlay();
        Run(kit.Director.Repay(3));
        Run(kit.Director.Repay(2));
        Assert.Equal(2, kit.Stage.RepaysThisTurn);
        Assert.Equal(5, kit.Stage.RepaidThisPlay);
        kit.Stage.EndPlay();
        Assert.Equal(0, kit.Stage.RepaidThisPlay);
        kit.Stage.OpenTurn();
        Assert.Equal(0, kit.Stage.RepaysThisTurn);
        Assert.Equal(2, kit.Stage.DrainsThisCombat);
    }

    [Fact]
    public void Overdraft_and_sold_out_give_their_energy_next_turn()
    {
        // The 2026-10-09 build's loop ruling, Interval Bell's fix: the
        // loop probe found 16 thin-deck cycles while the Energy came now.
        foreach (var type in new[] { typeof(ProtoFsOverdraft),
                                     typeof(ProtoFsSoldOut) })
        {
            var calls = Il.Calls(type.GetMethod("OnPlay", All)!);
            Assert.Contains("FurinaStage.EnergyNextTurn", calls);
            Assert.DoesNotContain("PlayerCmd.GainEnergy", calls);
        }
    }

    [Fact]
    public void Within_five_hp_of_the_line_is_near_it()
    {
        Assert.True(FurinaStageLaw.NearTheLine(44, 39));
        Assert.True(FurinaStageLaw.NearTheLine(39, 39));
        Assert.False(FurinaStageLaw.NearTheLine(45, 39));
    }

    [Fact]
    public void Grand_entrance_repays_after_a_guest_star_and_star_turn_reads_fanfare()
    {
        Assert.Contains("StageDirector.RepayFloor",
            Il.Calls(Il.Method("FurinaStage", "GuestStar")));
        Assert.Contains("FurinaStage.FanfareOf",
            Il.Calls(typeof(ProtoFsStarTurn).GetMethod("TryModifyEnergyCostInCombat", All)!));
    }
}
