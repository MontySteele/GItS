#nullable enable

using System;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE POOL SWEEP (2026-10-18, <c>review/active/pool-sweep-2026-10-18.md</c>
/// sec.1; [USER]: "Let's have a couple agents do a general sweep over the
/// card pools looking for any bad picks or undertuned options after the
/// recent revisions."). Forbidden Art: Daisesshou now pays 3 [4] to ALL per
/// Level the withered Sakura had, read before they wither ("I feel like
/// that's probably too punishing since it resets all progress you're made
/// towards leveling them up."); Fallen Petals draws 1 [2]. Pure ledger reads
/// and call-graph pins, as every Yae pin is. Sim twin:
/// <c>tier0/tests/test_yae_pool_to_78.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaePoolSweep20261018Tests : IDisposable
{
    public YaePoolSweep20261018Tests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose() => YaeShrineLedger.ResetAll();

    private static YaeShrineLedger Fresh() => YaeShrineLedger.For(Seat.Yae().Creature);

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static int Var(CardModel card, string name) => (int)card.DynamicVars[name].BaseValue;

    [Fact]
    public void Daisesshou_pays_per_level_summed_before_the_withers()
    {
        var ledger = Fresh();
        Assert.True(ledger.Plant(1));
        Assert.True(ledger.Plant(2));
        Assert.True(ledger.Plant(3));
        var levels = ledger.Standing.Sum(s => s.Level);
        Assert.Equal(6, levels);

        Assert.Equal(3, Var(new ProtoYmForbiddenArtDaisesshou(), "YmPer"));
        Assert.Equal(4, Var(Upgraded<ProtoYmForbiddenArtDaisesshou>(), "YmPer"));
        Assert.Equal(18, YaeCards.DaisesshouDamage(3, levels));
        Assert.Equal(24, YaeCards.DaisesshouDamage(4, levels));

        // Each Sakura's Level is read before it acts and withers.
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.WitherAll))!).ToList();
        var read = calls.FindIndex(c => c == "YaeShrine.EffectiveLevel");
        var wither = calls.FindIndex(c => c == "YaeShrineLedger.Wither");
        Assert.True(read >= 0 && wither > read, string.Join(", ", calls));

        // The card hits with the Levels WitherAll returned.
        var play = Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.Daisesshou))!).ToList();
        var all = play.FindIndex(c => c.Contains(nameof(YaeShrine.WitherAll)));
        var dmg = play.FindIndex(c => c.Contains(nameof(YaeCards.DaisesshouDamage)));
        Assert.True(all >= 0 && dmg > all, string.Join(", ", play));
    }

    [Fact]
    public void Daisesshou_on_an_empty_shrine_does_not_hit()
    {
        var ledger = Fresh();
        Assert.Empty(ledger.Standing);
        Assert.Equal(0, YaeCards.DaisesshouDamage(3, ledger.Standing.Sum(s => s.Level)));
        Assert.Equal(0, YaeCards.DaisesshouDamage(4, 0));
    }

    [Fact]
    public void Fallen_petals_draws_one_and_two_upgraded()
    {
        Assert.Equal(1, YaeCards.FallenPetalsDraw(false));
        Assert.Equal(2, YaeCards.FallenPetalsDraw(true));
        var calls = Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.FallenPetals))!).ToList();
        Assert.Contains(calls, c => c.Contains(nameof(YaeCards.FallenPetalsDraw)));
    }

    // ---- Eternity: "Their Levels count twice." ([USER]: "I do think that
    // Yae's Eternity may need a rethink to be better as a Rare level payoff")

    [Fact]
    public void Eternity_doubles_a_level_2_strike_and_not_the_stored_level()
    {
        var plain = Seat.Yae().Creature;
        var ledger = YaeShrineLedger.For(plain);
        Assert.True(ledger.Plant(2));
        var s = ledger.Standing[0];
        Assert.Equal(1 + 2 * 2, YaeShrine.Size(plain, s));

        var yae = Seat.Yae().WithPower<EternityPower>(1).Creature;
        var eternal = YaeShrineLedger.For(yae);
        Assert.True(eternal.Plant(2));
        var e = eternal.Standing[0];
        Assert.Equal(4, YaeShrine.EffectiveLevel(yae, e));
        Assert.Equal(1 + 2 * 4, YaeShrine.Size(yae, e));       // 9, not 5
        Assert.Equal(2, e.Level);                              // stored Level
        Assert.Equal(1 + 2 * 4,
                     YaeShrineFace.Total(eternal.Standing, YaeSakuraKind.Thunder, eternal: true));
    }

    [Fact]
    public void Eternity_doubles_daisesshous_sum_and_counts_for_sesshou_fang()
    {
        var yae = Seat.Yae().WithPower<EternityPower>(1).Creature;
        var ledger = YaeShrineLedger.For(yae);
        Assert.True(ledger.Plant(1));
        Assert.True(ledger.Plant(2));
        var levels = ledger.Standing.Sum(s => YaeShrine.EffectiveLevel(yae, s));
        Assert.Equal(6, levels);
        Assert.Equal(18, YaeCards.DaisesshouDamage(3, levels));
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.WitherAll))!).ToList();
        Assert.Contains(calls, c => c == "YaeShrine.EffectiveLevel");

        // Sesshou Fang: a Level-2 Sakura reads as 4, so "Level 3 or higher".
        var fang = YaeShrineLedger.For(Seat.Yae().Creature);
        Assert.True(fang.Plant(2));
        Assert.False(fang.AnyAtLevel(YaeLaw.FangLevel));
        Assert.True(fang.AnyAtLevel(YaeLaw.FangLevel, eternal: true));
        Assert.Contains(Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.LevelStrike))!),
                        c => c == "YaeShrine.Eternal");
    }
}
