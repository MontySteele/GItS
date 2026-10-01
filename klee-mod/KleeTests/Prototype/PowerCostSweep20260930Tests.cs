using System;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// POWER COST SWEEP, 2026-09-30. [USER]: "can we do a sweep over the current
/// card pools and break them up a bit so it's less of a standard? Alter the
/// effects to rebalance at a different energy level, basically (either the
/// higher or the lower)". These are the pins for the rows whose EFFECT moved
/// (the cost-only rows are pinned where their kits' suites already read the
/// cost). Provenance: docs/notes/prototype-surface-provenance.md. Sim twin:
/// <c>tier0/tests/test_power_cost_sweep_2026_09_30.py</c>.
/// </summary>
public class PowerCostSweep20260930Tests
{
    [Fact]
    public void The_long_game_upgraded_installs_the_drawing_twin()
    {
        var play = string.Join(" ",
            Il.CallSequence(Il.Method("ProtoKkTheLongGame", "OnPlay")));
        Assert.Contains("PowerCmd.Apply<TheLongGamePower>", play);
        Assert.Contains("PowerCmd.Apply<TheLongGamePlusPower>", play);
        Assert.Contains("get_IsUpgraded", play);
        Assert.Equal(1, new ProtoKkTheLongGame().EnergyCost.Canonical);
        var signal = string.Join(" ",
            Il.CallSequence(Il.Method("TheLongGamePower", "Signal")));
        Assert.Contains("CardPileCmd.Draw", signal);
    }

    [Fact]
    public void Sworn_brotherhood_base_is_the_current_element_and_the_upgrade_every_element()
    {
        var play = string.Join(" ",
            Il.CallSequence(Il.Method("ProtoVkSwornBrotherhood", "OnPlay")));
        Assert.Contains("PowerCmd.Apply<SwornBrotherhoodCurrentPower>", play);
        Assert.Contains("PowerCmd.Apply<SwornBrotherhoodPower>", play);
        Assert.Equal(1, new ProtoVkSwornBrotherhood().EnergyCost.Canonical);
        var start = string.Join(" ",
            Il.CallSequence(Il.Method("VarkaOath", "TurnStart")));
        Assert.Contains("SwornBrotherhoodCurrentPower", start);
    }

    [Fact]
    public void A_five_century_act_returns_at_the_acts_amount()
    {
        FurinaStageLedger.ResetAll();
        try
        {
            var seat = Seat.Furina();
            var stage = FurinaStageLedger.For(seat.Creature);
            stage.Clear();
            stage.Summon(StagePerformer.Usher);
            Assert.True(stage.ReturnOnce(StagePerformer.Chevalmarin, 3));
            Assert.Equal(3, stage.Seats[stage.Seats.Count - 1].Fanfare);
            Assert.Equal(3, new ProtoFsFiveCenturyAct().EnergyCost.Canonical);
        }
        finally
        {
            FurinaStageLedger.ResetAll();
        }
    }

    [Fact]
    public void One_woman_show_costs_three_and_its_upgrade_two()
    {
        var card = new ProtoFsOneWomanShow();
        Assert.Equal(3, card.EnergyCost.Canonical);
        Assert.Contains("EnergyCost.UpgradeBy",
            string.Join(" ", Il.Calls(Il.Method("ProtoFsOneWomanShow", "OnUpgrade"))));
    }
}
