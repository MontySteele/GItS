using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KLEE FINISH-LINE BATCH (2026-10-03). [USER], after the Klee
/// finish-line run: "Agreed all around!" to five changes. Readings in
/// <c>docs/notes/prototype-surface-provenance.md</c>, "Klee finish-line batch,
/// 2026-10-03". Sim twin: <c>tier0/tests/test_klee_finish_batch.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeFinishBatchTests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static List<string> Seq(string type, string method) =>
        Il.CallSequence(Il.Method(type, method)).ToList();

    // 1. "Confiscated should be a Status, not a Skill?"
    [Fact]
    public void Confiscated_is_a_status_that_still_plays_for_one()
    {
        var card = new Confiscated();
        Assert.Equal(CardType.Status, card.Type);
        Assert.Equal(CardRarity.Status, card.Rarity);
        Assert.Equal(1, card.EnergyCost.Canonical);
        // Playable, the base game's Slimed shape: no Unplayable keyword.
        Assert.DoesNotContain(CardKeyword.Unplayable, card.Keywords);
        Assert.True(KleeStatusPackage.IsStatus(card));
        Assert.Equal("Does nothing.", Face(card));
    }

    // 2. "Finders Keepers seems too niche to be useful"
    [Fact]
    public void Finders_keepers_places_a_bomb_on_a_status_drawn()
    {
        Assert.Equal(
            "Whenever you draw a status, place a [gold]Bomb[/gold] "
          + "{PowerAmount:diff()} on a random enemy.",
            Face(new ProtoKoFindersKeepers()));
        Assert.Equal((4m, 6m),
            (new ProtoKoFindersKeepers().DynamicVars["PowerAmount"].BaseValue,
             Upgraded<ProtoKoFindersKeepers>().DynamicVars["PowerAmount"].BaseValue));
        var drawn = Seq("FindersKeepersPower", "AfterCardDrawn");
        Assert.Contains(drawn, c => c.Contains("KleeStatusPackage.IsStatus"));
        Assert.Contains(drawn, c => c.Contains("ProtoBombPower.PlaceOnRandom"));
        Assert.Null(typeof(FindersKeepersPower).GetMethod(
            "AfterCardPlayed", HeadlessGame.All
            | System.Reflection.BindingFlags.DeclaredOnly));
    }

    // 3. Dodoco Tales: "Start each combat with 4 more Sparks."
    [Fact]
    public void Dodoco_tales_opens_with_four_more_sparks()
    {
        Assert.Equal(4, ExplosiveFrags.OpeningSparks);
        Assert.Equal(5, KleeOverhaulLaw.OpeningSpark + ExplosiveFrags.OpeningSparks);
        var face = new ExplosiveFrags().Localization!
            .First(r => r.Item1 == "description").Item2;
        Assert.EndsWith(
            "Start each combat with [blue]4[/blue] more [gold]Sparks[/gold].",
            face);
        var opening = Seq("KleeOverhaulOpening", "GrantSpark");
        var kit = opening.FindIndex(c => c.Contains("SparkPower.Gain"));
        var relic = opening.FindIndex(c => c.Contains("ExplosiveFrags.GrantOpeningSparks"));
        Assert.True(kit >= 0 && relic > kit);
        Assert.Contains("SparkPower.Gain", Seq("ExplosiveFrags", "GrantOpeningSparks"));
    }

    // 4. "how often do you have mines you want to detonate early?"
    [Fact]
    public void Mine_all_mine_hits_then_places_a_mine_and_sets_nothing_off()
    {
        var card = new ProtoKoMineAllMine();
        Assert.Equal(
            "Deal {Damage:diff()} [gold]Pyro[/gold] damage. Place a "
          + "[gold]Mine[/gold] {BombSize:diff()} on that enemy.", Face(card));
        Assert.Equal((8m, 11m), (card.DynamicVars.Damage.BaseValue,
            Upgraded<ProtoKoMineAllMine>().DynamicVars.Damage.BaseValue));
        Assert.Equal((4m, 6m), (card.DynamicVars["BombSize"].BaseValue,
            Upgraded<ProtoKoMineAllMine>().DynamicVars["BombSize"].BaseValue));
        Assert.False(card is ISetOffCard);
        var play = Seq("ProtoKoMineAllMine", "OnPlay");
        var hit = play.FindIndex(c => c.StartsWith("DamageCmd.Attack"));
        var mine = play.IndexOf("ProtoBombPower.Place");
        Assert.True(hit >= 0 && mine > hit);
        Assert.DoesNotContain(play, c => c.Contains("SetOff"));
        Assert.Null(typeof(ProtoBombPower).GetMethod("SetOffMinesAimed", HeadlessGame.All));
        Assert.Null(typeof(ProtoBombPower).GetMethod("SetOffMines", HeadlessGame.All));
    }

    // 5. "probably too good to be a Common now"
    [Fact]
    public void Amber_explosive_puppet_is_uncommon()
    {
        Assert.Equal(CardRarity.Uncommon, new ProtoMcAmberExplosivePuppet().Rarity);
    }
}
