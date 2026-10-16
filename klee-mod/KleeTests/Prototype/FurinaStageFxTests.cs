using KleeMod.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA'S STAGE EFFECTS (2026-10-13, her model art, phase B): the director
/// asks the board for the Spend, Drain and Repay effects at exactly the beats
/// the rules make, and never for a beat that did not happen. The board's
/// game half (<c>KleeMod.Vfx.FurinaStageFx</c>) needs a scene tree; here the
/// recording board keeps the asks apart from its rule log, so no rule pin
/// moves.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaStageFxTests
{
    [Fact]
    public void A_spend_of_any_shape_asks_for_the_gold_burst_once()
    {
        var kit = StageKit.With(10);
        Assert.Equal(3, StageKit.Run(kit.Director.Spend(3)));
        Assert.Equal(new[] { StageEffect.Spend }, kit.Board.Effects);

        kit.Board.Effects.Clear();
        Assert.Equal(4, StageKit.Run(kit.Director.SpendUpTo(4)));
        Assert.Equal(new[] { StageEffect.Spend }, kit.Board.Effects);

        kit.Board.Effects.Clear();
        Assert.Equal(3, StageKit.Run(kit.Director.SpendAll()));
        Assert.Equal(new[] { StageEffect.Spend }, kit.Board.Effects);
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void A_spend_that_is_not_made_asks_for_nothing()
    {
        var kit = StageKit.With(2);
        Assert.Equal(0, StageKit.Run(kit.Director.Spend(5)));
        var empty = StageKit.Of();
        Assert.Equal(0, StageKit.Run(empty.Director.SpendAll()));
        Assert.Equal(0, StageKit.Run(empty.Director.SpendUpTo(3)));
        Assert.Empty(kit.Board.Effects);
        Assert.Empty(empty.Board.Effects);
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void A_drain_and_its_repay_ask_for_the_droplets_out_and_back()
    {
        var kit = StageKit.Of();
        Assert.True(StageKit.Run(kit.Director.Drain(4)));
        Assert.Equal(4, StageKit.Run(kit.Director.Repay(4)));
        Assert.Equal(new[] { StageEffect.Drain, StageEffect.Repay }, kit.Board.Effects);
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void A_repay_with_nothing_owed_and_a_refused_drain_ask_for_nothing()
    {
        var kit = StageKit.Of();
        Assert.Equal(0, StageKit.Run(kit.Director.Repay(3)));
        // A Drain to 0 HP is refused (rule 1): nothing happens, nothing shows.
        var low = StageKit.At(3, 78);
        Assert.False(StageKit.Run(low.Director.Drain(3)));
        Assert.Empty(kit.Board.Effects);
        Assert.Empty(low.Board.Effects);
        FurinaStageLedger.ResetAll();
    }

    [Fact]
    public void The_curtain_call_returns_hp_with_no_repay_droplets()
    {
        var kit = StageKit.Of();
        Assert.True(StageKit.Run(kit.Director.Drain(5)));
        kit.Board.Effects.Clear();
        Assert.True(StageKit.Run(kit.Director.CurtainCall()) > 0);
        Assert.Empty(kit.Board.Effects);
        FurinaStageLedger.ResetAll();
    }
}
