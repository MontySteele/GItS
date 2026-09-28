#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The wave-3 seat round's fixes (2026-09-26): A Five-Century Act's face, the
/// Ancient's retired keyword under the Klee arm, why an act could not pay,
/// and three stage-log labels (Pneuma's regain, a hit a card in hand dealt,
/// Let the People Rejoice's emptying). The page halves are
/// <c>tier0/tests/test_wave3_fixes_2026_09_26.py</c>.
/// </summary>
public class Wave3Fixes20260926Tests
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

    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        params (string Member, int Fanfare)[] seats)
    {
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        foreach (var (member, fanfare) in seats)
        {
            var who = FurinaStage.Parse(member);
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

    private static string Description(List<(string, string)>? loc) =>
        loc!.Single(row => row.Item1 == "description").Item2;

    // ---- 1. A Five-Century Act's face ---------------------------------------

    [Fact]
    public void A_five_century_act_says_it_returns_only_to_a_free_seat()
    {
        // 2026-09-27: once a turn.
        const string face =
            "The first time each turn a performer [gold]Bow[/gold]s and "
          + "leaves, it returns at the back with 1 [gold]Fanfare[/gold] if a "
          + "seat is free.";
        Assert.Equal(face, Description(new ProtoFsFiveCenturyAct().Localization));
        Assert.Equal(face, Description(new FiveCenturyActPower().Localization));
    }

    // ---- 3. The Ancient's Elemental Skill keyword under the Klee arm -------

    [Fact]
    public void Jumpy_dumpty_mk_omega_drops_the_burst_keyword_under_the_arm()
    {
        var was = KleeOverhaul.Enabled;
        try
        {
            // BaseLib assigns the custom keywords' values at registration, so
            // headless they are all one value: the pin is the count.
            KleeOverhaul.Enabled = true;
            var arm = new JumpyDumptyMkOmega().CanonicalKeywords.ToList();
            Assert.Equal(new[] { KleeKeywords.AppliesPyro }, arm);

            KleeOverhaul.Enabled = false;
            var shipped = new JumpyDumptyMkOmega().CanonicalKeywords.ToList();
            Assert.Equal(new[] { KleeKeywords.ElementalSkill,
                                 KleeKeywords.AppliesPyro }, shipped);
        }
        finally
        {
            KleeOverhaul.Enabled = was;
        }
    }

    // ---- 4. Why an act could not pay ----------------------------------------

    [Fact]
    public void Chevreuse_files_that_the_back_performer_is_short()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("chevreuse", 4), ("usher", 1));
        Assert.False(stage.ActFanfare(StagePerformer.Chevreuse,
                                      stage.Seats[0], null,
                                      new List<StageExit>()));
        var unpaid = stage.Beats.Single(
            b => b.Event == FurinaStageLedger.UnpaidEvent);
        Assert.Equal(FurinaStageLedger.UnpaidBack, unpaid.Reason);
        Assert.Equal(FurinaStageLaw.ActChevreusePrice, unpaid.Moved);
    }

    [Fact]
    public void Neuvillette_files_his_own_bar_and_clorinde_that_she_is_alone()
    {
        using var _ = new Arm();
        var (_, own) = Stage(("neuvillette", 2));
        own.ActFanfare(StagePerformer.Neuvillette, own.Seats[0], null,
                       new List<StageExit>());
        var unpaid = own.Beats.Single(
            b => b.Event == FurinaStageLedger.UnpaidEvent);
        Assert.Equal(FurinaStageLedger.UnpaidOwn, unpaid.Reason);
        Assert.Equal(FurinaStageLaw.ActNeuvillettePrice, unpaid.Moved);

        var (_, alone) = Stage(("clorinde", 4));
        alone.ActFanfare(StagePerformer.Clorinde, alone.Seats[0], null,
                         new List<StageExit>());
        Assert.Equal(FurinaStageLedger.UnpaidAlone,
                     alone.Beats.Single(
                         b => b.Event == FurinaStageLedger.UnpaidEvent).Reason);
    }

    [Fact]
    public void The_unpaid_reasons_cross_the_wire_as_plain_words()
    {
        foreach (var word in new[]
                 {
                     FurinaStageLedger.UnpaidOwn, FurinaStageLedger.UnpaidBack,
                     FurinaStageLedger.UnpaidAlone,
                     FurinaStageLedger.RejoiceReason,
                 })
        {
            Assert.Matches("^[a-z]+$", word);
        }
    }

    // ---- 13. Stage-log labels -----------------------------------------------

    [Fact]
    public void Pneumas_regain_names_pneuma_and_the_turn_start_regain_does_not()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage(("usher", 3), ("crabaletta", 1));
        ArkheAlignmentPower.Choose(seat.Creature, pneuma: true);
        var regain = stage.Beats.Single(b => b.Event == "regain");
        Assert.Equal(ArkheAlignmentPower.PneumaTitle, regain.Source);
        Assert.Equal(ArkheAlignmentPower.PneumaLeadRegain, regain.Moved);

        stage.ClearBeats();
        ArkheAlignmentPower.ChooseForTurn(seat.Creature, pneuma: true);
        Assert.Equal(ArkheAlignmentPower.PneumaTitle,
                     stage.Beats.Single(b => b.Event == "regain").Source);
        // And the scope closed: nothing after it is stamped Pneuma.
        Assert.Equal("", stage.Cause);
    }

    [Fact]
    public void A_hit_no_enemy_dealt_carries_the_card_that_dealt_it()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 5));
        stage.Absorb(2, source: "Burn");
        var hit = stage.Beats.Single(b => b.Event == "hit");
        Assert.Equal("Burn", hit.Source);
        Assert.Equal("", hit.Target);
    }

    [Fact]
    public void Let_the_people_rejoice_empties_the_stage_without_a_spend()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(("usher", 3), ("crabaletta", 2));
        stage.CollectAll();
        var leaves = stage.Beats.Where(b => b.Event == "leave").ToList();
        Assert.Equal(2, leaves.Count);
        Assert.All(leaves, b => Assert.Equal(FurinaStageLedger.RejoiceReason,
                                             b.Reason));
    }

    // ---- 12 and 14. The Pneuma and Thunderous Applause faces ---------------

    [Fact]
    public void The_pneuma_tip_says_it_summons_nobody()
    {
        var printed = string.Concat(Il.Strings(
            typeof(ArmKeywordTips).GetMethod(nameof(ArmKeywordTips.ForPneuma),
                                             HeadlessGame.All)!));
        // The second text pass (2026-09-28): "regains", as the front
        // performer's tip says, in place of "It summons nobody."
        Assert.Contains("and your front performer regains ", printed);
        Assert.DoesNotContain("It summons nobody.", printed);
    }

    [Fact]
    public void Thunderous_applause_names_its_amount()
    {
        Assert.Contains(
            "your back performer gains [blue]{Amount}[/blue]",
            Description(new ThunderousApplausePower().Localization));
    }
}
