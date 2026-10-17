using System;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// YAE FLAT-VALUE PASS, 2026-10-17 (<c>review/active/yae-flat-value-2026-10-17.md</c>
/// sec.3, ruled 2026-10-17: [USER], "This all looks good" and "let's run just
/// the Commons for now and then see where we're at"). The eight attacks' new
/// numbers, and Thunder Petal's "It strikes this enemy." / Foxfire Sweep's "It
/// strikes now." (<see cref="YaeCards.StrikePlanted"/>): the planted Sakura acts
/// once at its Level, on the card's target (a Foxfire on ALL), using none of its
/// turns, not a Tenko; into a full shrine the refreshed Sakura strikes. Pure
/// ledger reads, the no-combat path and call-graph pins, as every Yae pin is.
/// Sim twin: <c>tier0/tests/test_yae_flat_value.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeFlatValueTests : IDisposable
{
    public YaeFlatValueTests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose() => YaeShrineLedger.ResetAll();

    private const BindingFlags Instance = BindingFlags.Instance | BindingFlags.NonPublic;

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    private static void Upgrade(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
    }

    private static int Var(CardModel card, string name) => (int)card.DynamicVars[name].BaseValue;

    private static (int, int) Damage<T>() where T : CardModel, new()
    {
        var card = new T();
        var base_ = Var(card, "Damage");
        Upgrade(card);
        return (base_, Var(card, "Damage"));
    }

    private static System.Collections.Generic.List<string> OnPlay<T>() =>
        Il.CallSequence(typeof(T).GetMethod("OnPlay", Instance)!).ToList();

    // ---- the numbers ---------------------------------------------------------------

    [Fact]
    public void The_attacks_pay_at_the_base_rate()
    {
        Assert.Equal((8, 10), Damage<ProtoYmSlyStrike>());
        Assert.Equal((7, 10), Damage<ProtoYmMarginNote>());
        Assert.Equal((13, 17), Damage<ProtoYmThunderRite>());
        Assert.Equal((14, 18), Damage<ProtoYmPublishersDeadline>());
        Assert.Equal((14, 18), Damage<ProtoYmGalleyProof>());
        // Unchanged: Thunder Petal 5 [8], Foxfire Sweep 4 [6].
        Assert.Equal((5, 8), Damage<ProtoYmThunderPetal>());
        Assert.Equal((4, 6), Damage<ProtoYmFoxfireSweep>());
    }

    [Fact]
    public void Sly_strike_upgrades_to_2_weak()
    {
        var card = new ProtoYmSlyStrike();
        Assert.Equal(1, Var(card, "PowerAmount"));
        Upgrade(card);
        Assert.Equal(2, Var(card, "PowerAmount"));
    }

    [Fact]
    public void Sesshou_fang_hits_8_and_its_bonus_stays_6()
    {
        var card = new ProtoYmSesshouFang();
        Assert.Equal((8, 6), (Var(card, "YmBase"), Var(card, "YmAmount")));
        Upgrade(card);
        Assert.Equal((10, 8), (Var(card, "YmBase"), Var(card, "YmAmount")));
        Assert.StartsWith("Deal {YmBase:diff()}", Face(card));
    }

    // ---- "It strikes this enemy." / "It strikes now." --------------------------------

    [Fact]
    public void The_two_planters_print_the_new_line()
    {
        Assert.EndsWith("Plant a [gold]Sakura[/gold]. It strikes this enemy.",
                        Face(new ProtoYmThunderPetal()));
        Assert.EndsWith("Plant a [gold]Foxfire Sakura[/gold]. It strikes now.",
                        Face(new ProtoYmFoxfireSweep()));
    }

    [Fact]
    public void The_strike_follows_the_plant_on_both_cards()
    {
        foreach (var calls in new[] { OnPlay<ProtoYmThunderPetal>(), OnPlay<ProtoYmFoxfireSweep>() })
        {
            var plant = calls.FindIndex(c => c.Contains("YaeCards.Plant"));
            var strike = calls.FindIndex(c => c.Contains(nameof(YaeCards.StrikePlanted)));
            Assert.True(plant >= 0 && strike > plant, string.Join(", ", calls));
        }
    }

    [Fact]
    public void A_sakura_strikes_the_cards_target_a_foxfire_hits_all()
    {
        // The card's target is the aim (Thunder Petal: "this enemy").
        var at = Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.StrikePlanted))!).ToList();
        Assert.Contains(at, c => c.Contains("get_Target"));
        Assert.Contains(at, c => c.Contains("YaeShrine.StrikePlanted"));
        // The shrine's door: the last-planted Sakura acts, aimed only when it
        // is a plain Sakura (a Foxfire's unaimed act hits ALL).
        var door = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.StrikePlanted))!).ToList();
        Assert.Contains(door, c => c.Contains("get_LastPlanted"));
        Assert.Contains(door, c => c.Contains("get_Kind"));
        Assert.Contains(door, c => c.Contains("YaeShrine.Act"));
        Assert.Equal("aim", typeof(YaeShrine).GetMethod(nameof(YaeShrine.StrikePlanted))!
            .GetParameters().Last().Name);
        // Foxfire Sweep still targets ALL (no aim to pick).
        Assert.Equal(TargetType.AllEnemies, new ProtoYmFoxfireSweep().TargetType);
        Assert.Equal(TargetType.AnyEnemy, new ProtoYmThunderPetal().TargetType);
    }

    [Fact]
    public void The_strike_uses_no_turns_and_is_not_a_tenko()
    {
        var door = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.StrikePlanted))!).ToList();
        Assert.DoesNotContain(door, c => c.Contains("Tenko"));
        Assert.DoesNotContain(door, c => c.Contains("KaguraBell"));
        Assert.DoesNotContain(door, c => c.Contains("Refresh"));
        Assert.DoesNotContain(door, c => c.Contains("TurnsLeft"));
        Assert.DoesNotContain(door, c => c.Contains("Tick"));

        // The no-combat path, with Kagura Bell held: one Sakura, the strike
        // returns true, and its turns and Level are as planted.
        var yae = Seat.Yae().WithRelic<KaguraBell>().Creature;
        var ledger = YaeShrineLedger.For(yae);
        Assert.False(YaeShrine.StrikePlanted(null!, yae, null).GetAwaiter().GetResult());
        ledger.Plant(YaeLaw.PlantLevel);
        var planted = Assert.Single(ledger.Standing);
        Assert.True(YaeShrine.StrikePlanted(null!, yae, null).GetAwaiter().GetResult());
        Assert.Equal((YaeLaw.PlantLevel, YaeLaw.SakuraTurns), (planted.Level, planted.TurnsLeft));
    }

    [Fact]
    public void Into_a_full_shrine_the_refreshed_sakura_is_the_one_that_strikes()
    {
        var yae = Seat.Yae().Creature;
        var ledger = YaeShrineLedger.For(yae);
        for (var i = 0; i < YaeLaw.SakuraCap; i++) ledger.Plant(YaeLaw.PlantLevel);
        var oldest = ledger.Standing[0];
        ledger.Plant(YaeLaw.PlantLevel);                 // the same kind: refreshed
        Assert.Equal(YaeLaw.SakuraCap, ledger.Count);
        Assert.Same(oldest, ledger.LastPlanted);
        // Another kind: the oldest withers and the new one is "it".
        ledger.Plant(YaeLaw.PlantLevel, null, kind: YaeSakuraKind.Foxfire);
        Assert.Equal(YaeSakuraKind.Foxfire, ledger.LastPlanted!.Kind);
        Assert.Same(ledger.Standing[ledger.Count - 1], ledger.LastPlanted);
        Assert.True(YaeShrine.StrikePlanted(null!, yae, null).GetAwaiter().GetResult());
    }

    [Fact]
    public void Proofread_is_unchanged()
    {
        // Yakan Evocation's "It strikes now." is the draft pass's (2026-10-17,
        // round 9 pick 1 (a)): YaeDraftPassTests.
        Assert.DoesNotContain(OnPlay<ProtoYmProofread>(), c => c.Contains(nameof(YaeCards.StrikePlanted)));
    }
}
