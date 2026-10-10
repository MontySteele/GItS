using System.IO;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// Regina of All Waters stops at the Drain line, like a guest's act
/// (2026-10-10, "I'm good with stopping Regina's Drain at the line"): "At
/// the start of your turn, Drain 3, never past your line. If you do, gain 1
/// Strength." Sim twin: <c>tier0/tests/test_furina_regina_navia.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class FurinaReginaLineTests
{
    private static T Run<T>(System.Threading.Tasks.Task<T> task) =>
        StageKit.Run(task);

    [Fact]
    public void Regina_drains_only_the_room_above_the_line()
    {
        // Entered at 78: line 59. At 61 there are 2 HP of room: the first
        // copy drains 2 and gains its Strength, the second finds no room.
        var kit = StageKit.At(61, 78);
        Assert.Equal(1, Run(kit.Director.Regina(2)));
        Assert.Equal(59, kit.Board.Hp);
        Assert.Equal(1, kit.Board.Gained);
    }

    [Fact]
    public void Regina_at_or_below_the_line_drains_nothing()
    {
        var kit = StageKit.At(59, 78);
        Assert.Equal(0, Run(kit.Director.Regina(1)));
        Assert.Equal(59, kit.Board.Hp);
        Assert.Equal(0, kit.Board.Gained);
    }

    [Fact]
    public void Regina_and_navia_read_as_ruled()
    {
        var dir = Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode",
                               "Cards", "Prototype", "Generated");
        Assert.Contains("Drain[/gold] 3, never past your line. If you do",
            File.ReadAllText(Path.Combine(dir, "ProtoFsReginaOfAllWaters.cs")));
        Assert.Contains("CardRarity.Uncommon",
            File.ReadAllText(Path.Combine(dir, "ProtoFsGuestStarNavia.cs")));
    }
}
