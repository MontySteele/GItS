using System;
using System.Linq;
using System.Globalization;
using System.Reflection;
using System.Text.RegularExpressions;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE POOL TO 75 (<c>review/ruled/furina-pool-growth-2026-10-09.md</c>,
/// ruled 2026-10-09): sec.3's guest rule and sec.5's new verbs, pinned
/// headlessly over the director and the recording board
/// (<see cref="StageKit"/>). The sim twin is <c>tier0/tests/test_furina_pool75.py</c>.
///
/// THE RULE: a Guest Star exhausts when played and has no effect on summon;
/// when its guest leaves (a fourth summon, or Final Bow) its card goes to the
/// discard pile; a duplicate moves its guest to the newest seat and acts once
/// (2026-10-11; it moved with no act before);
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
        // ...after it acts once on the way out (2026-10-11).
        Assert.Equal(new[] { "damage Wriothesley Random 5 Cryo" },
                     kit.Board.Hits.ToArray());
    }

    // ---- a guest pushed off a full stage acts once as it leaves ---------------
    //
    // Ruled 2026-10-11: "I lean towards b) as well. That way there's some
    // reward for taking multiples, but if you want consistency in the end of
    // turn act, there's also a deck issue with spamming them out, which seems
    // fine." The option: "(b) a guest who's pushed out takes a bow: they act
    // once as they leave."

    [Fact]
    public void A_fourth_guest_makes_the_oldest_act_once_then_leave_then_sits()
    {
        var kit = StageKit.Of(StagePerformer.Clorinde, StagePerformer.Lynette,
                              StagePerformer.Charlotte);
        var oldest = kit.Stage.Seats[0];
        oldest.Cards.Add(new ProtoFsGuestStarClorinde());
        Assert.Equal(StageSummonResult.Evict,
            Run(kit.Director.SummonGuest(StagePerformer.Wriothesley)));
        Assert.Equal(new[] { StagePerformer.Lynette, StagePerformer.Charlotte,
                             StagePerformer.Wriothesley }, kit.Company);
        Assert.Equal(1, kit.Beats(FurinaStageLedger.ActEvent, StagePerformer.Clorinde));
        Assert.Equal(1, kit.Beats(FurinaStageLedger.ActEvent));
        // It acts, then leaves (its card back), then the new guest is seated.
        var acted = kit.Board.Log.IndexOf("damage Clorinde Random 6 Electro");
        var left = kit.Board.Log.IndexOf("return Clorinde 1");
        Assert.True(acted >= 0 && left > acted);
        var beats = kit.Stage.Beats.ToList();
        var actBeat = beats.FindIndex(b => b.Event == FurinaStageLedger.ActEvent);
        var leaveBeat = beats.FindIndex(b => b.Event == FurinaStageLedger.LeaveEvent);
        Assert.True(actBeat >= 0 && leaveBeat > actBeat);
        Assert.Equal("evicted", beats[leaveBeat].Reason);
    }

    [Fact]
    public void An_evicted_lyney_pays_his_drain()
    {
        var kit = StageKit.Of(StagePerformer.Lyney, StagePerformer.Lynette,
                              StagePerformer.Charlotte);
        var before = kit.Stage.Drained;
        Run(kit.Director.SummonGuest(StagePerformer.Clorinde));
        Assert.Equal(before + FurinaStageLaw.LyneyActDrain, kit.Stage.Drained);
        Assert.Equal(76, kit.Board.Hp);
        Assert.Contains("damage Lyney All 5 Pyro", kit.Board.Log);
        Assert.Equal(1, kit.Beats(FurinaStageLedger.ActEvent, StagePerformer.Lyney));
        Assert.DoesNotContain(StagePerformer.Lyney, kit.Company);
    }

    [Fact]
    public void An_evicted_neuvillette_reads_the_window_as_usual()
    {
        var kit = StageKit.Of(StagePerformer.Neuvillette, StagePerformer.Lynette,
                              StagePerformer.Charlotte);
        Run(kit.Director.Drain(4));
        Run(kit.Director.SummonGuest(StagePerformer.Clorinde));
        Assert.Contains("damage Neuvillette All 4 Hydro", kit.Board.Log);
        Assert.Equal(1, kit.Beats(FurinaStageLedger.ActEvent, StagePerformer.Neuvillette));
        Assert.DoesNotContain(StagePerformer.Neuvillette, kit.Company);
    }

    [Fact]
    public void Final_bows_leave_adds_no_extra_act()
    {
        var kit = StageKit.Of(StagePerformer.Clorinde, StagePerformer.Lynette,
                              StagePerformer.Charlotte);
        Assert.True(Run(kit.Director.FinalBow(0, 2)));
        Assert.Equal(2, kit.Beats(FurinaStageLedger.ActEvent, StagePerformer.Clorinde));
        Assert.Equal(2, kit.Board.Hits.Count());
        Assert.Equal(new[] { StagePerformer.Lynette, StagePerformer.Charlotte },
                     kit.Company);
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

    // ---- a duplicate moves its guest, and it acts -----------------------------
    //
    // The 2026-10-11 playtest: "I'm thinking to let the guest star Act when
    // replayed to make getting a second copy do something at all."

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
        // ...and then it acts once, from its new seat, upgraded by the merge.
        Assert.Single(kit.Board.Hits);
        Assert.StartsWith("damage Lynette Aura ", kit.Board.Hits.Single());
        Assert.Equal(1, kit.Beats(FurinaStageLedger.MoveEvent, StagePerformer.Lynette));
        Assert.Equal(1, kit.Beats(FurinaStageLedger.ActEvent));
    }

    [Fact]
    public void Played_twice_the_first_copy_seats_the_guest_and_the_second_acts()
    {
        var kit = StageKit.Of();
        Assert.Equal(StageSummonResult.Seated,
            Run(kit.Director.SummonGuest(StagePerformer.Clorinde, false,
                                         new ProtoFsGuestStarClorinde())));
        Assert.Empty(kit.Board.Hits);
        Assert.Equal(0, kit.Beats(FurinaStageLedger.ActEvent));
        Assert.Equal(StageSummonResult.Repeat,
            Run(kit.Director.SummonGuest(StagePerformer.Clorinde, false,
                                         new ProtoFsGuestStarClorinde())));
        Assert.Equal(new[] { "damage Clorinde Random 6 Electro" },
                     kit.Board.Hits.ToArray());
        Assert.Equal(1, kit.Beats(FurinaStageLedger.ActEvent, StagePerformer.Clorinde));
        Assert.Equal(new[] { StagePerformer.Clorinde }, kit.Company);
    }

    [Fact]
    public void A_repeat_act_pays_the_drain_its_act_costs()
    {
        // Lyney's act Drains 2 (never past the line) before his hit; a
        // repeat's act is the same act.
        var kit = StageKit.Of(StagePerformer.Lyney);
        var before = kit.Stage.Drained;
        Run(kit.Director.SummonGuest(StagePerformer.Lyney));
        Assert.Equal(before + FurinaStageLaw.LyneyActDrain, kit.Stage.Drained);
        Assert.Equal(76, kit.Board.Hp);
        Assert.Contains("damage Lyney All 5 Pyro", kit.Board.Log);
        Assert.Single(kit.Board.Hits);
        Assert.Equal(1, kit.Beats(FurinaStageLedger.ActEvent, StagePerformer.Lyney));
    }

    // ---- the upgrade shows on the face ----------------------------------------
    //
    // The 2026-10-11 playtest: "Guest star upgrades don't show what the +
    // version will do." Each face prints the number its upgrade raises as a
    // var (or, for Chevreuse, a clause behind IfUpgraded), so the upgrade
    // preview shows the + version.

    private static readonly Regex UpgradeSwap =
        new(@"\{IfUpgraded:show:([^{}|]*)\|([^{}|]*)\}");

    private static readonly Regex VarToken = new(@"\{(\w+)(?::diff\(\))?\}");

    private static string Render(CardModel card)
    {
        var raw = ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;
        var text = UpgradeSwap.Replace(raw,
            m => card.IsUpgraded ? m.Groups[1].Value : m.Groups[2].Value);
        return VarToken.Replace(text, m =>
            card.DynamicVars.TryGetValue(m.Groups[1].Value, out var v)
                ? ((int)v.BaseValue).ToString(CultureInfo.InvariantCulture)
                : m.Value);
    }

    [Fact]
    public void Every_guest_stars_upgraded_face_differs_from_its_base_face()
    {
        foreach (var type in GuestCards)
        {
            var card = (CardModel)Activator.CreateInstance(type)!;
            var plain = Render(card);
            Seat.Set(card, "IsMutable", true);
            typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
                .Invoke(card, Array.Empty<object>());
            var upgraded = Render(card);
            Assert.NotEqual(plain, upgraded);
            // Past the name's "+": the face itself says what changed.
            Assert.NotEqual(plain.Replace("+", ""), upgraded.Replace("+", ""));
        }
    }

    [Fact]
    public void A_guest_stars_face_number_is_the_number_the_guest_uses()
    {
        var lynette = new ProtoFsGuestStarLynette();
        Assert.Equal(FurinaStageLaw.LynetteActDamage,
                     (int)lynette.DynamicVars["GuestAct"].BaseValue);
        Seat.Set(lynette, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(lynette, Array.Empty<object>());
        Assert.Equal(FurinaStageLaw.LynetteActDamageUpgraded,
                     (int)lynette.DynamicVars["GuestAct"].BaseValue);
        Assert.Equal(StageDirector.ActAmount(StagePerformer.Lynette, true),
                     (int)lynette.DynamicVars["GuestAct"].BaseValue);
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
            "damage Wriothesley Random 5 Cryo",
            "damage Clorinde Random 6 Electro",
            // Showstopper: Spend 5 (the bank held 5 + 4 drained), act again.
            "damage Wriothesley Random 5 Cryo",
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
    public void Freminet_blocks_each_drain_and_acts_for_block()
    {
        // His act since the Spend paper (ruled 2026-10-10; 4 [7] since the
        // guest package, 2026-10-13): "Gain 4 Block. Spend a quarter of your
        // Fanfare (rounded down): gain that much more Block."
        var kit = StageKit.Of(StagePerformer.Freminet);
        Run(kit.Director.Drain(4));
        Assert.Contains("block 4", kit.Board.Log);
        Run(kit.Director.Act(kit.Stage.Seats[0]));     // 4 Fanfare: +1
        Assert.Contains("block 4", kit.Board.Log);
        Assert.Contains("block 1", kit.Board.Log);
        Assert.DoesNotContain(kit.Board.Log, l => l.StartsWith("damage Freminet"));
        Assert.Equal(7, StageDirector.ActAmount(StagePerformer.Freminet, true));
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
        // Her act Spends a third of the bank and deals twice that as Geo (the
        // guest package, 2026-10-13): a third of 7 is 2, for 4.
        var act = StageKit.With(7, StagePerformer.Navia);
        Run(act.Director.Act(act.Stage.Seats[0]));
        Assert.Contains("damage Navia Random 4 Geo", act.Board.Log);
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
    public void Escoffiers_line_adds_two_to_every_damaging_act_his_own_included()
    {
        var kit = StageKit.Of(StagePerformer.Charlotte, StagePerformer.Escoffier,
                              StagePerformer.Lyney);
        Run(kit.Director.Drain(10));
        kit.Board.Log.Clear();
        Run(kit.Director.ActAll());
        // His own 4 lands as 6; Lyney's 5 as 7; Charlotte's Repay 2 is not
        // damage and is not touched.
        Assert.Contains("damage Escoffier All 6 Cryo", kit.Board.Log);
        Assert.Contains("damage Lyney All 7 Pyro", kit.Board.Log);
        Assert.Contains("heal 3", kit.Board.Log);
        Assert.Equal(0, kit.Beats(FurinaStageLedger.LineEvent, StagePerformer.Escoffier));
        Assert.Equal(2, FurinaStageLaw.EscoffierLineBonus);
        Assert.Equal(3, FurinaStageLaw.EscoffierLineBonusUpgraded);
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
        Assert.Contains("Repay[/gold] 5",
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
        Assert.Equal("damage Wriothesley Random 5 Cryo", kit.Board.Hits.Single());
        Assert.Equal(2, Run(kit.Director.ActAll()));
        Assert.False(Run(StageKit.Of().Director.ActOldest()));
        Assert.Contains("FurinaCards.ActOldest",
            Il.Calls(typeof(ProtoFsEncore).GetMethod("OnPlay", All)!));
        Assert.Contains("FurinaCards.ActAll",
            Il.Calls(typeof(ProtoFsTutti).GetMethod("OnPlay", All)!));
        // Bring the House Down (the upgrade census, 2026-10-23): its own
        // conditional Spend, then each guest acts twice.
        Assert.Contains("FurinaCards.HouseDown",
            Il.Calls(typeof(ProtoFsBringTheHouseDown).GetMethod("OnPlay", All)!));
        Assert.Contains("FurinaCards.FinalBow",
            Il.Calls(typeof(ProtoFsFinalBow).GetMethod("OnPlay", All)!));
        Assert.Contains("FurinaCards.TutorGuest",
            Il.Calls(typeof(ProtoFsCastingCall).GetMethod("OnPlay", All)!));
    }

    // Crescendo and Standing Room Only (furina-next, 2026-10-16): pinned in
    // FurinaEnginesTests.

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
        foreach (var hook in new[] { "FurinaStage.CrescendoGains",
                                     "FurinaStage.ReginaDrains",
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
    public void Grand_entrance_repays_after_a_guest_star_and_star_turn_reads_fanfare()
    {
        Assert.Contains("StageDirector.RepayFloor",
            Il.Calls(Il.Method("FurinaStage", "GuestStar")));
        Assert.Contains("FurinaStage.FanfareOf",
            Il.Calls(typeof(ProtoFsStarTurn).GetMethod("TryModifyEnergyCostInCombat", All)!));
    }
}
