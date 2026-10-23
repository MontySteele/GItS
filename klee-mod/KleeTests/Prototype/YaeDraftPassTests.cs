using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// YAE DRAFT PASS, 2026-10-17 (<c>review/active/yae-draft-pass-2026-10-17.md</c>
/// sec.1 and sec.3). [USER] on round 9's pick: "I agree with the starter
/// change, but let's also scan the draft rates and see what cards the seats
/// refuse to take and wherever they are bad value or just undervalued by the
/// seats." Yakan Evocation's "It strikes now." (no target, so a null aim);
/// Falling Blossom's "Your oldest Sakura strikes this enemy." (no wither);
/// Dawn Prayer's Levels, then its strike; Kitsune Pounce's "deal 5 more" with
/// Weak read before the hit; Mikage Thunder's 7 first; The Seven Glamours at 1.
/// Pure ledger reads, the no-combat path and call-graph pins, as every Yae pin
/// is. Sim twin: <c>tier0/tests/test_yae_draft_pass.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeDraftPassTests : IDisposable
{
    public YaeDraftPassTests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose() => YaeShrineLedger.ResetAll();

    private const BindingFlags Instance = BindingFlags.Instance | BindingFlags.NonPublic;

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static int Cost(CardModel card) =>
        (int)card.EnergyCost.GetWithModifiers(CostModifiers.None);

    private static int Var(CardModel card, string name) => (int)card.DynamicVars[name].BaseValue;

    private static List<string> OnPlay<T>() =>
        Il.CallSequence(typeof(T).GetMethod("OnPlay", Instance)!).ToList();

    private static List<string> Door(string name) =>
        Il.CallSequence(typeof(YaeShrine).GetMethod(name)!).ToList();

    private static void NotATenko(List<string> door)
    {
        Assert.DoesNotContain(door, c => c.Contains("Tenko"));
        Assert.DoesNotContain(door, c => c.Contains("KaguraBell"));
        Assert.DoesNotContain(door, c => c.Contains("Refresh"));
        // No timer is written; the doors' own names say "MostTurnsLeft"
        // since the user's ruling of 2026-10-20.
        Assert.DoesNotContain(door, c => c.Contains("set_TurnsLeft"));
        Assert.DoesNotContain(door, c => c.Contains("Tick"));
        // Reading which Sakura is LAST to wither (the user's ruling,
        // 2026-10-20, turns-left targeting) is not a wither.
        Assert.DoesNotContain(door, c => c.Contains("Wither") && !c.Contains("LastToWither"));
    }

    // ---- sec.1: Yakan Evocation ---------------------------------------------------------

    [Fact]
    public void Yakan_evocation_plants_and_it_strikes_now()
    {
        var card = new ProtoYmYakanEvocation();
        Assert.Equal("Plant a [gold]Sakura[/gold]. It strikes now.", Face(card));
        var calls = OnPlay<ProtoYmYakanEvocation>();
        var plant = calls.FindIndex(c => c.Contains("YaeCards.Plant"));
        var strike = calls.FindIndex(c => c.Contains(nameof(YaeCards.StrikePlanted)));
        Assert.True(plant >= 0 && strike > plant, string.Join(", ", calls));
        // No target: cardPlay.Target is null, so the Sakura's Aim picks the
        // Lure's, Hunting Gaze's or a random enemy.
        Assert.Equal(TargetType.Self, card.TargetType);
        Assert.Contains(Il.CallSequence(typeof(YaeShrine).GetMethod("Aim", HeadlessGame.All)!),
                        c => c.Contains("HuntingGazePower"));
        // Upgrade stays cost -1.
        Assert.Equal((1, 0), (Cost(card), Cost(Upgraded<ProtoYmYakanEvocation>())));
    }

    [Fact]
    public void Yakan_evocations_strike_uses_none_of_its_turns()
    {
        var yae = Seat.Yae().Creature;
        var ledger = YaeShrineLedger.For(yae);
        ledger.Plant(YaeLaw.PlantLevel);
        var planted = Assert.Single(ledger.Standing);
        Assert.True(YaeShrine.StrikePlanted(null!, yae, null).GetAwaiter().GetResult());
        Assert.Equal((YaeLaw.PlantLevel, YaeLaw.SakuraTurns), (planted.Level, planted.TurnsLeft));
    }

    // ---- sec.3: Falling Blossom ----------------------------------------------------------

    [Fact]
    public void Falling_blossoms_most_turns_left_strikes_this_enemy_and_does_not_wither()
    {
        // The user's ruling, 2026-10-20 (turns-left targeting): was the oldest.
        Assert.Equal("Deal {Damage:diff()} [gold]Electro[/gold] damage. "
                     + "Your [gold]Sakura[/gold] with the most turns left strikes this enemy.",
                     Face(new ProtoYmFallingBlossom()));
        Assert.Equal((7, 10), (Var(new ProtoYmFallingBlossom(), "Damage"),
                               Var(Upgraded<ProtoYmFallingBlossom>(), "Damage")));
        var door = Door(nameof(YaeShrine.StrikeMostTurnsLeftAt));
        Assert.Contains(door, c => c.Contains("YaeShrine.Act"));
        Assert.DoesNotContain(door, c => c.Contains("Withered"));
        NotATenko(door);
        Assert.Equal("aim", typeof(YaeShrine).GetMethod(nameof(YaeShrine.StrikeMostTurnsLeftAt))!
            .GetParameters().Last().Name);

        var yae = Seat.Yae().Creature;
        var ledger = YaeShrineLedger.For(yae);
        Assert.False(YaeShrine.StrikeMostTurnsLeftAt(null!, yae, null).GetAwaiter().GetResult());
        ledger.Plant(YaeLaw.PlantLevel);
        ledger.Plant(YaeLaw.PlantLevel);
        var target = ledger.LastToWither()!;
        Assert.Same(ledger.Standing[1], target);             // a tie: the newest
        Assert.True(YaeShrine.StrikeMostTurnsLeftAt(null!, yae, null).GetAwaiter().GetResult());
        Assert.Equal(2, ledger.Count);
        Assert.Same(target, ledger.Standing[1]);
        Assert.Equal(YaeLaw.SakuraTurns, target.TurnsLeft);
    }

    // ---- sec.3: Dawn Prayer ---------------------------------------------------------------

    [Fact]
    public void Dawn_prayer_levels_the_most_turns_left_then_it_strikes_now()
    {
        // The user's ruling, 2026-10-20 (turns-left targeting): was the newest.
        Assert.Equal("Your [gold]Sakura[/gold] with the most turns left gains {YmAmount:diff()} Levels. It strikes now.",
                     Face(new ProtoYmDawnPrayer()));
        Assert.Equal((2, 3), (Var(new ProtoYmDawnPrayer(), "YmAmount"),
                              Var(Upgraded<ProtoYmDawnPrayer>(), "YmAmount")));
        var calls = OnPlay<ProtoYmDawnPrayer>();
        var level = calls.FindIndex(c => c.Contains(nameof(YaeCards.LevelMostTurnsLeft)));
        var strike = calls.FindIndex(c => c.Contains(nameof(YaeCards.StrikeMostTurnsLeft)));
        Assert.True(level >= 0 && strike > level, string.Join(", ", calls));
        Assert.Equal(TargetType.Self, new ProtoYmDawnPrayer().TargetType);
        var door = Door(nameof(YaeShrine.StrikeMostTurnsLeft));
        Assert.Contains(door, c => c.Contains("YaeShrine.Act"));
        NotATenko(door);

        var yae = Seat.Yae().Creature;
        var ledger = YaeShrineLedger.For(yae);
        Assert.False(YaeShrine.StrikeMostTurnsLeft(null!, yae).GetAwaiter().GetResult());
        ledger.Plant(YaeLaw.PlantLevel);
        ledger.Plant(YaeLaw.PlantLevel);
        Assert.True(ledger.LevelMostTurnsLeft(2));
        Assert.True(YaeShrine.StrikeMostTurnsLeft(null!, yae).GetAwaiter().GetResult());
        Assert.Equal(new[] { 1, 3 }, ledger.Standing.Select(s => s.Level));
        Assert.All(ledger.Standing, s => Assert.Equal(YaeLaw.SakuraTurns, s.TurnsLeft));
    }

    // ---- sec.3: Kitsune Pounce -------------------------------------------------------------

    [Fact]
    public void Kitsune_pounce_deals_5_more_to_a_weak_enemy_read_before_the_hit()
    {
        var card = new ProtoYmKitsunePounce();
        Assert.Equal("Deal {Damage:diff()} [gold]Electro[/gold] damage. "
                     + "If the enemy is [gold]Weak[/gold], deal {BranchDamage:diff()} additional damage.",
                     Face(card));
        var up = Upgraded<ProtoYmKitsunePounce>();
        Assert.Equal((8, 5), (Var(card, "Damage"), Var(card, "BranchDamage")));
        Assert.Equal((11, 5), (Var(up, "Damage"), Var(up, "BranchDamage")));
        var calls = OnPlay<ProtoYmKitsunePounce>();
        // Fox's Bargain's order: the Weak read, then the hits.
        var weak = calls.FindIndex(c => c.Contains("OfType") && c.Contains("WeakPower"));
        var hit = calls.FindIndex(c => c.Contains("DamageCmd.Attack"));
        Assert.True(weak >= 0 && hit > weak, string.Join(", ", calls));
        Assert.Equal(2, calls.Count(c => c.Contains("DamageCmd.Attack")));
        Assert.DoesNotContain(calls, c => c.Contains("YaeCards."));
    }

    // ---- sec.3: Mikage Thunder --------------------------------------------------------------

    [Fact]
    public void Mikage_thunder_deals_7_first_on_its_target()
    {
        var card = new ProtoYmMikageThunder();
        Assert.StartsWith("Deal {Damage:diff()} [gold]Electro[/gold] damage. ", Face(card));
        Assert.Equal(TargetType.AnyEnemy, card.TargetType);
        var up = Upgraded<ProtoYmMikageThunder>();
        Assert.Equal((7, 7), (Var(card, "Damage"), Var(up, "Damage")));
        Assert.Equal((1, 2), (Var(card, "YmAmount"), Var(up, "YmAmount")));
        Assert.Equal((2, 2), (Cost(card), Cost(up)));
        var calls = OnPlay<ProtoYmMikageThunder>();
        var hit = calls.FindIndex(c => c.Contains("DamageCmd.Attack"));
        var level = calls.FindIndex(c => c.Contains("YaeCards.LevelUp"));
        var tenko = calls.FindIndex(c => c.Contains("YaeCards.Tenko"));
        Assert.True(hit >= 0 && level > hit && tenko > level, string.Join(", ", calls));
    }

    // ---- sec.3: The Seven Glamours ------------------------------------------------------------

    [Fact]
    public void The_seven_glamours_costs_1()
    {
        var card = new ProtoYmTheSevenGlamours();
        var up = Upgraded<ProtoYmTheSevenGlamours>();
        Assert.Equal((1, 1), (Cost(card), Cost(up)));
        Assert.Equal((12, 16), (Var(card, "Damage"), Var(up, "Damage")));
        Assert.Contains(CardKeyword.Exhaust, card.CanonicalKeywords);
    }

    // ---- BACKLOG check, Yae round 9 lane 4: Narukami Ray through Reprint ------------------

    /// <summary>Not a bug. The base game's play loop (<c>CardModel</c>'s
    /// <c>for (i &lt; playCount)</c>, the count taken once before the first
    /// play) runs the whole <c>OnPlay</c> per play, so each replay is the 5
    /// to ALL and the Level. A Published Reprint replays only the card's
    /// FIRST play each combat (<see cref="YaeLayers.Replays"/>), so a later
    /// Narukami Ray that combat levels once.</summary>
    [Fact]
    public void Narukami_ray_replays_the_whole_card_and_a_published_reprint_only_its_first_play()
    {
        var calls = OnPlay<ProtoYmNarukamiRay>();
        var hit = calls.FindIndex(c => c.Contains("DamageCmd.Attack"));
        var level = calls.FindIndex(c => c.Contains("YaeCards.LevelUp"));
        Assert.True(hit >= 0 && level > hit, string.Join(", ", calls));
        Assert.Equal(1, YaeLayers.Replays(1, playedOnce: false, armed: 0));
        Assert.Equal(0, YaeLayers.Replays(1, playedOnce: true, armed: 0));
        Assert.Equal(1, YaeLayers.Replays(1, playedOnce: true, armed: 1));   // a fresh Edit
        Assert.True(YaeLayers.ReprintUsed(1, playedOnce: true, armed: 0));
    }
}
