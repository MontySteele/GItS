using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// TURNS-LEFT TARGETING (the user's ruling, 2026-10-20, from a friend's
/// report: "A couple of times I had a Sakura with 7+ turns left on it and the
/// kill oldest card replaced it with one only had 3 turns."). The user: "For
/// cards designed to benefit you, they should target the one with the most
/// turns left. For cards designed to cost something, they should target the
/// one with the fewest turns left. This might not be the same as the planting
/// order." A cost reaches <see cref="YaeShrineLedger.NextToWither"/>, a
/// benefit its mirror <see cref="YaeShrineLedger.LastToWither"/>. Sim twin:
/// tier0/tests/test_yae_turns_left_targeting.py.
/// </summary>
public class YaeTurnsLeftTargetingTests
{
    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    /// <summary>The friend's shrine: Evergreen Charm twice on the only
    /// Sakura (A, 7 turns left), then two more planted (3 each).</summary>
    private static (Creature yae, YaeShrineLedger ledger, YaeSakura a) FriendsShrine()
    {
        var yae = Seat.Yae().Creature;
        var ledger = YaeShrineLedger.For(yae);
        ledger.Plant(YaeLaw.PlantLevel);
        var a = ledger.Standing[0];
        Assert.True(ledger.ExtendMostTurnsLeft(2));
        Assert.True(ledger.ExtendMostTurnsLeft(2));
        Assert.Equal(7, a.TurnsLeft);
        ledger.Plant(YaeLaw.PlantLevel);
        ledger.Plant(YaeLaw.PlantLevel);
        return (yae, ledger, a);
    }

    [Fact]
    public void Replanting_withers_the_3_turn_sakura_not_the_7_turn_one()
    {
        var (yae, ledger, a) = FriendsShrine();
        var b = ledger.Standing[1];
        Assert.Same(b, ledger.NextToWither());             // 3 and 3: the older
        YaeShrine.Replant(null!, yae, 1).GetAwaiter().GetResult();
        Assert.Contains(a, ledger.Standing);
        Assert.Equal(7, a.TurnsLeft);
        Assert.DoesNotContain(b, ledger.Standing);
        Assert.Equal(3, ledger.Count);
        Assert.Equal(b.Level + 1, ledger.Standing[^1].Level);
    }

    [Fact]
    public void Fallen_petals_and_hide_behind_the_shrine_wither_the_fewest_turns_left()
    {
        var (yae, ledger, a) = FriendsShrine();
        var b = ledger.Standing[1];
        var c = ledger.Standing[2];
        Assert.True(YaeShrine.WitherFewestTurnsLeft(null!, yae).GetAwaiter().GetResult());
        Assert.DoesNotContain(b, ledger.Standing);
        Assert.True(YaeShrine.WitherFewestTurnsLeft(null!, yae).GetAwaiter().GetResult());
        Assert.DoesNotContain(c, ledger.Standing);
        Assert.Same(a, Assert.Single(ledger.Standing));
    }

    [Fact]
    public void The_benefit_cards_reach_the_most_turns_left()
    {
        var (yae, ledger, a) = FriendsShrine();
        Assert.Same(a, ledger.LastToWither());
        // Dawn Prayer: its Levels and its strike land on A.
        Assert.True(ledger.LevelMostTurnsLeft(2));
        Assert.Equal(new[] { 3, 1, 1 }, ledger.Standing.Select(s => s.Level));
        Assert.True(YaeShrine.StrikeMostTurnsLeft(null!, yae).GetAwaiter().GetResult());
        // Falling Blossom: A strikes, none of its turns.
        Assert.True(YaeShrine.StrikeMostTurnsLeftAt(null!, yae, null).GetAwaiter().GetResult());
        Assert.Equal(7, a.TurnsLeft);
        // Fox Fire Draft+ (2): A, then the newer of the two 3s.
        Assert.Equal(2, ledger.EditSakura(YaeSakuraEnd.MostTurnsLeft, 2, YaeAnnotation.FoxFire));
        Assert.Equal(new[] { true, false, true },
                     ledger.Standing.Select(s => s.Has(YaeAnnotation.FoxFire)));
    }

    [Fact]
    public void A_tie_goes_to_the_newest_for_a_benefit_and_the_oldest_for_a_cost()
    {
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        Assert.Null(ledger.LastToWither());
        Assert.Null(ledger.NextToWither());
        for (var i = 0; i < 3; i++) ledger.Plant(YaeLaw.PlantLevel);
        Assert.Same(ledger.Standing[2], ledger.LastToWither());
        Assert.Same(ledger.Standing[0], ledger.NextToWither());
        Assert.Equal(ledger.WitherOrder().Reverse(),
                     ledger.Standing.Reverse());
    }

    [Fact]
    public void Deadline_extension_comes_first_for_a_benefit_and_last_for_a_cost()
    {
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        for (var i = 0; i < 3; i++) ledger.Plant(YaeLaw.PlantLevel);
        var dl = ledger.Standing[0];
        ledger.EditOne(dl, YaeAnnotation.DeadlineExtension);
        ledger.Plant(YaeLaw.PlantLevel, null, cap: 4, extraTurns: 3);  // 6 turns
        Assert.Same(dl, ledger.LastToWither());           // 3 turns, but it never ticks
        Assert.Same(ledger.Standing[1], ledger.NextToWither());
        Assert.Equal(new[] { ledger.Standing[1], ledger.Standing[2], ledger.Standing[3], dl },
                     ledger.WitherOrder());
    }

    [Fact]
    public void Evergreen_charm_skips_a_deadline_extension_sakura()
    {
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        ledger.Plant(YaeLaw.PlantLevel);
        ledger.Plant(YaeLaw.PlantLevel);
        var dl = ledger.Standing[1];
        ledger.EditOne(dl, YaeAnnotation.DeadlineExtension);
        Assert.True(ledger.ExtendMostTurnsLeft(2));
        Assert.Equal(YaeLaw.SakuraTurns + 2, ledger.Standing[0].TurnsLeft);
        Assert.Equal(YaeLaw.SakuraTurns, dl.TurnsLeft);

        // Every one carries it: none is extended.
        var all = YaeShrineLedger.For(Seat.Yae().Creature);
        all.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.DeadlineExtension);
        Assert.False(all.ExtendMostTurnsLeft(2));
        Assert.Equal(YaeLaw.SakuraTurns, all.Standing[0].TurnsLeft);
    }

    [Fact]
    public void A_level_tie_goes_to_the_most_turns_left()
    {
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        ledger.Plant(YaeLaw.PlantLevel, null, extraTurns: 2);   // 5 turns
        ledger.Plant(YaeLaw.PlantLevel);                        // 3 turns
        Assert.Same(ledger.Standing[0], ledger.Highest());
        Assert.Same(ledger.Standing[0], ledger.Highest(damageOnly: true));
    }

    [Fact]
    public void The_faces_name_turns_left_not_planting_order()
    {
        Assert.Contains("Your [gold]Sakura[/gold] with the fewest turns left withers. If one did",
                        Face(new ProtoYmHideBehindTheShrine()));
        Assert.StartsWith("Your [gold]Sakura[/gold] with the fewest turns left withers. Plant one",
                          Face(new ProtoYmReplanting()));
        Assert.EndsWith("Ties go to the one with the most turns left.",
                        Face(new ProtoYmKitsunesBlessing()));
    }
}
