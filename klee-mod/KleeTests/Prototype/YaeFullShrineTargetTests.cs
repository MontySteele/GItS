using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// A FULL-SHRINE PLANT FEEDS THE SAKURA CLOSEST TO WITHERING (2026-10-17).
/// [USER]'s co-op run: a run of Sakura Seals refreshed the first Sakura
/// planted again and again while the other two ran out. Agreed: "I think
/// that's closest to the expectation". The target is the fewest turns left,
/// the oldest on a tie; a Deadline Extension Sakura (it never withers) last.
/// Sim twin: tier0/tests/test_yae_shrine.py.
/// </summary>
public class YaeFullShrineTargetTests
{
    private static YaeShrineLedger FullShrine()
    {
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        for (var i = 0; i < YaeLaw.SakuraCap; i++) ledger.Plant(YaeLaw.PlantLevel, null);
        return ledger;
    }

    [Fact]
    public void Same_kind_refreshes_and_levels_the_one_closest_to_withering()
    {
        var ledger = FullShrine();
        ledger.Tick();                       // 2, 2, 2
        ledger.ExtendOldest(2);              // 4, 2, 2
        var second = ledger.Standing[1];
        Assert.Same(second, ledger.NextToWither());
        Assert.False(ledger.Plant(YaeLaw.PlantLevel, null));
        Assert.Equal(new[] { 1, 2, 1 }, ledger.Standing.Select(s => s.Level));
        Assert.Equal(YaeLaw.SakuraTurns, second.TurnsLeft);
        // The third (2 left) is next; the order stays planting order.
        Assert.Same(ledger.Standing[2], ledger.NextToWither());
    }

    [Fact]
    public void Another_kind_replaces_the_one_closest_to_withering()
    {
        var ledger = FullShrine();
        ledger.Tick();
        ledger.ExtendOldest(2);
        var first = ledger.Standing[0];
        var third = ledger.Standing[2];
        Assert.True(ledger.WouldReplace(YaeLaw.SakuraCap, YaeSakuraKind.Foxfire));
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, null, kind: YaeSakuraKind.Foxfire));
        Assert.Equal(3, ledger.Count);
        Assert.Same(first, ledger.Standing[0]);
        Assert.Same(third, ledger.Standing[1]);
        Assert.Equal(YaeSakuraKind.Foxfire, ledger.Standing[2].Kind);
    }

    [Fact]
    public void A_deadline_extension_sakura_is_fed_last()
    {
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.DeadlineExtension);
        ledger.Plant(YaeLaw.PlantLevel, null);
        ledger.Plant(YaeLaw.PlantLevel, null);
        ledger.Tick();
        ledger.Tick();                       // 3 (never ticks), 1, 1
        Assert.Same(ledger.Standing[1], ledger.NextToWither());

        var eternal = YaeShrineLedger.For(Seat.Yae().Creature);
        for (var i = 0; i < YaeLaw.SakuraCap; i++)
            eternal.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.DeadlineExtension);
        // Every one carries it: the fewest turns, then the oldest.
        Assert.Same(eternal.Standing[0], eternal.NextToWither());
    }
}
