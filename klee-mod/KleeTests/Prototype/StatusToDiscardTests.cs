using System.Linq;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// STATUS CARDS GO TO THE DISCARD PILE, AS IN THE BASE GAME (2026-10-03).
/// [USER]: "I agree that we should adopt the same convention". Every base card
/// that creates a status (Turbo, Overclock, Gunk Up, Boost Away, Fight
/// Through) adds it with <c>CardPileCmd.AddGeneratedCardToCombat(card,
/// PileType.Discard, owner)</c>, and none uses the draw pile. The nine cards
/// of ours that shuffled a Dazed or a Confiscated into the draw pile at a
/// random depth now add it into the discard pile, and their faces read the
/// base's "Add a [gold]Burn[/gold] into your [gold]Discard Pile[/gold]."
/// (<c>OVERCLOCK</c>). Pinned off the printed source, as the other emitted-
/// call pins are. Sim twins: <c>tier0/tests/test_klee_status_package.py</c>,
/// <c>test_kokomi_status_batch.py</c>, <c>test_klee_overhaul_rules.py</c>.
/// </summary>
public class StatusToDiscardTests
{
    public static TheoryData<string, string> Cards => new()
    {
        { "ProtoKoFishBlasting", "Add a [gold]Confiscated[/gold] into your [gold]Discard Pile[/gold]." },
        { "ProtoKoForbiddenFun", "Add a [gold]Dazed[/gold] into your [gold]Discard Pile[/gold]." },
        // It Wasn't Me! cut by the Klee tempo paper (2026-10-07).
        { "ProtoKoSimmer", "Add a [gold]Dazed[/gold] into your [gold]Discard Pile[/gold]." },
        { "ProtoKoTinkering", "Add a [gold]Confiscated[/gold] into your [gold]Discard Pile[/gold]." },
        { "ProtoKoDodocoTag", "Add a [gold]Dazed[/gold] into your [gold]Discard Pile[/gold]." },
        { "ProtoKoLisasTreats", "Add 2 [gold]Confiscated[/gold] into your [gold]Discard Pile[/gold]." },
        { "ProtoKoRedKnight", "Add 2 [gold]Confiscated[/gold] into your [gold]Discard Pile[/gold]." },
        { "ProtoKoUpInSmoke", "Add a [gold]Dazed[/gold] into your [gold]Discard Pile[/gold]." },
        { "ProtoKoBehindJeansDesk", "Add a [gold]Confiscated[/gold] into your [gold]Discard Pile[/gold]." },
        { "ProtoKkFlotsamSurge", "Add 2 [gold]Dazed[/gold] into your [gold]Discard Pile[/gold]." },
        { "ProtoKkRiptideRuin", "Add 3 [gold]Dazed[/gold] into your [gold]Discard Pile[/gold]." },
    };

    [Theory]
    [MemberData(nameof(Cards))]
    public void The_status_is_added_into_the_discard_pile(string type, string face)
    {
        var source = Printed(type);
        var adds = source.Split('\n')
            .Where(l => l.Contains("CardPileCmd.AddGeneratedCardToCombat"))
            .ToList();
        Assert.NotEmpty(adds);
        Assert.All(adds, l => Assert.Contains("PileType.Discard, Owner);", l));
        Assert.DoesNotContain("PileType.Draw", source);
        Assert.DoesNotContain("CardPilePosition.Random", source);
        Assert.Contains(face, source);
        Assert.DoesNotContain("draw pile", source);
    }

    private static string Printed(string type)
    {
        var relative = System.IO.Path.Combine("klee-mod", "KleeCode", "Cards",
            "Prototype", "Generated", type + ".cs");
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = System.IO.Path.Combine(dir.FullName, relative);
            if (System.IO.File.Exists(candidate))
            {
                return System.IO.File.ReadAllText(candidate);
            }
            dir = dir.Parent;
        }
        throw new System.IO.FileNotFoundException(relative);
    }
}
