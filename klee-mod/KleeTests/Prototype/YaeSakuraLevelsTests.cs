using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE SAKURA LEVELS PAPER (ruled 2026-10-17, picks 1 (a) and 2 (a);
/// [USER]: "Agreed on both of these"),
/// <c>review/active/yae-sakura-levels-2026-10-17.md</c>. A Sakura (Thunder)
/// acts for 1 + 2 per Level; Foxfire and Kitsune are unchanged. A plant of
/// another kind into a full shrine withers the Sakura closest to withering
/// and the new one takes its place at the HIGHER of its own plant Level and
/// the withered one's Level. Sim twin: tier0/tests/test_yae_sakura_levels.py.
/// </summary>
public class YaeSakuraLevelsTests
{
    /// <summary>A full shrine of Sakura (Thunder), planted at
    /// <paramref name="levels"/> (Level 1 where none is given), oldest first.
    /// </summary>
    private static YaeShrineLedger FullShrine(params int[] levels)
    {
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        for (var i = 0; i < YaeLaw.SakuraCap; i++)
            ledger.Plant(i < levels.Length ? levels[i] : YaeLaw.PlantLevel, null);
        Assert.Equal(YaeLaw.SakuraCap, ledger.Count);
        return ledger;
    }

    [Theory]
    [InlineData(1, 3)]
    [InlineData(3, 7)]
    [InlineData(5, 11)]
    public void A_thunder_level_is_worth_two(int level, int size)
    {
        Assert.Equal(size, YaeShrineLedger.ActSize(YaeSakuraKind.Thunder, level, YaeAnnotation.None));
        Assert.Equal(size, YaeShrineLedger.StrikeDamage(level, reacts: false, edict: 0));
    }

    [Fact]
    public void Foxfire_and_kitsune_are_unchanged_and_red_ink_still_adds_three()
    {
        Assert.Equal(new[] { 2, 4, 6 }, new[] { 1, 3, 5 }
            .Select(l => YaeShrineLedger.ActSize(YaeSakuraKind.Foxfire, l, YaeAnnotation.None)));
        Assert.Equal(new[] { 3, 5, 7 }, new[] { 1, 3, 5 }
            .Select(l => YaeShrineLedger.ActSize(YaeSakuraKind.Kitsune, l, YaeAnnotation.None)));
        Assert.Equal(7 + YaeLaw.RedInkAmount,
                     YaeShrineLedger.ActSize(YaeSakuraKind.Thunder, 3, YaeAnnotation.RedInk));
    }

    [Fact]
    public void Another_kind_takes_the_replaced_sakuras_level()
    {
        var ledger = FullShrine(4, 1, 1);
        var target = ledger.NextToWither()!;
        Assert.Equal(4, target.Level);
        Assert.True(ledger.WouldReplace(YaeLaw.SakuraCap, YaeSakuraKind.Kitsune));
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, null, kind: YaeSakuraKind.Kitsune));
        Assert.DoesNotContain(target, ledger.Standing);     // it withered
        var planted = ledger.Standing[^1];
        Assert.Equal(YaeSakuraKind.Kitsune, planted.Kind);
        Assert.Equal(4, planted.Level);
        Assert.Equal(4, planted.PlantedLevel);
        Assert.Equal(new[] { 1, 1, 4 }, ledger.Standing.Select(s => s.Level));
    }

    [Fact]
    public void The_level_comes_from_the_one_closest_to_withering()
    {
        var ledger = FullShrine(1, 6, 1);
        ledger.Tick();                       // 2, 2, 2
        ledger.ExtendOldest(2);              // 4, 2, 2: the Level 6 is next
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, null, kind: YaeSakuraKind.Foxfire));
        Assert.Equal(YaeSakuraKind.Foxfire, ledger.Standing[^1].Kind);
        Assert.Equal(6, ledger.Standing[^1].Level);
    }

    [Fact]
    public void A_lower_replaced_level_does_not_lower_a_higher_plant()
    {
        // Guardian of Narukami's "at Level 3" into a shrine of Level 1s.
        var guardian = FullShrine();
        guardian.Plant(YaeLaw.PlantLevel, 3, kind: YaeSakuraKind.Kitsune);
        Assert.Equal(3, guardian.Standing[^1].Level);
        // Fox's Mooncall: planted 1 Level higher, so Level 2 beats a 1 ...
        var mooncall = FullShrine();
        mooncall.Plant(YaeLaw.PlantLevel + 1, null, kind: YaeSakuraKind.Kitsune);
        Assert.Equal(2, mooncall.Standing[^1].Level);
        // ... and loses to a 5.
        var high = FullShrine(5, 1, 1);
        high.Plant(YaeLaw.PlantLevel + 1, null, kind: YaeSakuraKind.Kitsune);
        Assert.Equal(5, high.Standing[^1].Level);
    }

    [Fact]
    public void Same_kind_is_unchanged_refresh_and_one_level()
    {
        var ledger = FullShrine(4, 1, 1);
        ledger.Tick();
        var target = ledger.Standing[0];
        Assert.Same(target, ledger.NextToWither());
        Assert.False(ledger.WouldReplace(YaeLaw.SakuraCap, YaeSakuraKind.Thunder));
        Assert.False(ledger.Plant(YaeLaw.PlantLevel, null));
        Assert.Equal(new[] { 5, 1, 1 }, ledger.Standing.Select(s => s.Level));
        Assert.Same(target, ledger.Standing[0]);
        Assert.Equal(YaeLaw.SakuraTurns, target.TurnsLeft);
    }
}
