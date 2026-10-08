using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Saves.Runs;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KLEE SCALING PASS (staging branch `klee-next`, 2026-10-05,
/// `review/active/klee-scaling-pass-2026-10-05.md` sec.4): A Klee's Secret
/// Base (v3: a Bomb 4 [6] every turn), B the grant-only Witch's Homework II, C Boom Badge, D the tempo
/// relic. Pure reads where the rule is pure; structural (IL) pins where the
/// rule runs through <c>PowerCmd.Apply</c>, outside the headless boundary
/// (README).
/// </summary>

public sealed class KleeScalingPassTests
{
    // ==== A. Klee's Secret Base, v3 ==========================================

    [Fact]
    public void Secret_base_v3_places_a_bomb_six_eight_upgraded_at_turn_start()
    {
        var card = new ProtoKoSecretBase();
        Assert.Equal("At the start of your turn, place a [gold]Bomb[/gold] "
                   + "{PowerAmount:diff()} on a random enemy.", Face(card));
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Power, card.Type);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        // 6 [8] since the Klee design review (2026-10-08): every placer +2.
        Assert.Equal(6m, card.DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal(8m, Upgraded<ProtoKoSecretBase>().DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal("At the start of your turn, place a [gold]Bomb[/gold] "
                   + "[blue]{Amount}[/blue] on a random enemy.",
                     ((ILocalizationProvider)RuntimeHelpers
                         .GetUninitializedObject(typeof(SecretBasePower)))
                         .Localization!.Single(r => r.Item1 == "description").Item2);
    }

    [Fact]
    public void Secret_base_copies_stack_like_noxious_fumes_into_one_bomb()
    {
        // REAL: the size the sequencer places, read off the stack.
        Assert.Equal(0, SecretBasePower.BombSizeFor(null));
        var klee = Seat.Klee();
        Assert.Equal(0, SecretBasePower.BombSizeFor(klee.Creature));
        klee.WithPower<SecretBasePower>(4);
        Assert.Equal(4, SecretBasePower.BombSizeFor(klee.Creature));
        // A Counter: a second copy adds (two copies, one Bomb 8).
        klee.WithPower<SecretBasePower>(4);
        Assert.Equal(8, SecretBasePower.BombSizeFor(klee.Creature));
        var upgraded = Seat.Klee().WithPower<SecretBasePower>(6).WithPower<SecretBasePower>(6);
        Assert.Equal(12, SecretBasePower.BombSizeFor(upgraded.Creature));
        Assert.Equal(PowerStackType.Counter,
            ((PowerModel)RuntimeHelpers.GetUninitializedObject(typeof(SecretBasePower)))
                .StackType);

        // STRUCTURAL: ONE placement of that sum, not one per copy.
        var run = Il.CallSequence(Il.Method("KleeExpansion", "RunTurnStartPlacements"))
            .ToList();
        Assert.Equal(1, run.Count(c => c == "SecretBasePower.BombSizeFor"));
    }

    [Fact]
    public void Secret_base_places_after_the_growth_so_it_shows_four_when_she_acts()
    {
        // STRUCTURAL. Rule 1's growth is ProtoBombPower.BeforeSideTurnStart;
        // the Secret Base Bomb is AfterPlayerTurnStart, which the game runs
        // after it -- so the new Bomb does not grow on the turn it arrives.
        Assert.Contains("ProtoBombPower.GrowBy",
                        Il.Calls(Il.Method("ProtoBombPower", "BeforeSideTurnStart")));
        Assert.Equal(typeof(SecretBasePower),
                     typeof(SecretBasePower).GetMethod("AfterPlayerTurnStart")!.DeclaringType);
        Assert.NotEqual(typeof(SecretBasePower),
                        typeof(SecretBasePower).GetMethod("BeforeSideTurnStart")!.DeclaringType);
        Assert.Contains("KleeExpansion.RunTurnStartPlacements",
                        Il.Calls(Il.Method("SecretBasePower", "AfterPlayerTurnStart")));

        // The one sequencer: latch, echo, Secret Base's Bomb, then Dodoco's
        // Mine. It grows nothing itself.
        var run = Il.CallSequence(Il.Method("KleeExpansion", "RunTurnStartPlacements"))
            .ToList();
        Assert.DoesNotContain("ProtoBombPower.GrowBy", run);
        Assert.DoesNotContain("ProtoBombPower.AnyPlacedBy", run);
        var latch = run.IndexOf("KleeOverhaulLedger.TakeTurnStartPlacements");
        var echo = run.IndexOf("BombEchoPower.Fire");
        var size = run.IndexOf("SecretBasePower.BombSizeFor");
        var firstPlace = run.IndexOf("ProtoBombPower.PlaceOnRandom");
        Assert.True(latch >= 0 && latch < echo && echo < size && size < firstPlace,
                    string.Join(" ", run));
        Assert.True(firstPlace < run.LastIndexOf("ProtoBombPower.PlaceOnRandom"),
                    "Dodoco's Mine is a second PlaceOnRandom, after Secret Base's");
    }

    [Fact]
    public void Secret_base_uses_pops_door_and_a_random_living_enemy_or_nothing()
    {
        // STRUCTURAL: PlaceOnRandom is Place on a random living enemy, and
        // with none it places nothing; Place is the door Pop! goes through,
        // so merge, Sparks and the relics apply as they do to Pop!.
        var random = Il.Calls(Il.Method("ProtoBombPower", "PlaceOnRandom"));
        Assert.Contains("Creature.get_IsDead", random);
        Assert.Contains("ProtoBombPower.Place", random);
        Assert.Contains("ProtoBombPower.Place", Il.Calls(Il.Method("ProtoKoPop", "OnPlay")));

        // REAL: no combat, no enemy -- the sequencer runs and places nothing.
        KleeOverhaulLedger.ResetAll();
        var klee = Seat.Klee().WithPower<SecretBasePower>(4);
        KleeExpansion.RunTurnStartPlacements(null!, klee.Player)
            .GetAwaiter().GetResult();
        Assert.Empty(klee.Creature.Powers.OfType<ProtoBombPower>());
        KleeOverhaulLedger.ResetAll();
    }

    [Fact]
    public void No_placement_bonus_is_left_and_faces_print_their_own_numbers()
    {
        // The first draft's bonus is gone from the one door and from the faces.
        Assert.DoesNotContain(Il.Calls(Il.Method("ProtoBombPower", "Place")),
                              c => c.StartsWith("SecretBasePower."));
        Assert.Null(typeof(ProtoBombPower).GetMethod("PlacementBonus", HeadlessGame.All));
        Assert.Null(typeof(SecretBasePower).GetMethod("BonusFor", HeadlessGame.All));
        Assert.Null(typeof(SecretBasePower).Assembly.GetTypes()
                        .FirstOrDefault(t => t.Name == "BombSizeVar"));

        // Pop! and friends print their sheet numbers through a plain var.
        foreach (var (card, name, size) in new (CardModel, string, decimal)[]
                 {
                     (new ProtoKoPop(), "BombSize", 5m),
                     (new ProtoKoJumpyDumpty(), "BombSize", 8m),
                     (new ProtoKoJumpyDumpty(), "PayloadMine", 3m),
                     (new ProtoKoMineToss(), "BombSize", 9m),
                     (new ProtoKoWitchsHomeworkNext(), "BombSize", 6m),
                 })
        {
            var var = card.DynamicVars[name];
            Assert.Equal(typeof(DynamicVar), var.GetType());
            Assert.Equal(size, var.BaseValue);
        }
    }

    // ==== C. Boom Badge =======================================================

    [Fact]
    public void Boom_badge_retains_and_does_not_stack()
    {
        var card = new ProtoKoBoomBadge();
        Assert.Contains(CardKeyword.Retain, card.CanonicalKeywords);
        Assert.EndsWith("deal double damage. Does not stack.", Face(card));
        Assert.Equal(2, card.PrintedSparkPrice);
        Assert.Equal(1, Upgraded<ProtoKoBoomBadge>().PrintedSparkPrice);
        Assert.Equal(1, BoomBadgePower.FactorFor(0));
        Assert.Equal(2, BoomBadgePower.FactorFor(1));
        Assert.Equal(2, BoomBadgePower.FactorFor(2));
        Assert.Equal(2, BoomBadgePower.FactorFor(9));
    }

    // ==== B. Witch's Homework II ==============================================

    [Fact]
    public void Homework_prints_its_face_and_is_offered_nowhere()
    {
        var card = new ProtoKoWitchsHomeworkNext();
        Assert.Equal(
            "Place a [gold]Bomb[/gold] {BombSize:diff()}. When it goes off, this "
          + "card's [gold]Bomb[/gold] is {IfUpgraded:show:3|2} larger for the rest "
          + "of the run.", Face(card));
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(CardRarity.Uncommon, card.Rarity);
        Assert.Contains(CardKeyword.Exhaust, card.CanonicalKeywords);
        Assert.Equal(6m, card.DynamicVars["BombSize"].BaseValue);
        Assert.Equal(2, ((IHomeworkCard)card).HomeworkStep);
        Assert.Equal(3, ((IHomeworkCard)Upgraded<ProtoKoWitchsHomeworkNext>()).HomeworkStep);
        Assert.Contains("KleeScalingPass.PlaceHomework",
                        Il.Calls(Il.Method("ProtoKoWitchsHomeworkNext", "OnPlay")));
        // Grant-only: not in her offer roster (the pool's Witch's Homework is).
        var slice = Il.CallSequence(Il.Method("KleeOverhaulRoster", "Slice"));
        Assert.DoesNotContain(slice, c => c.Contains("ProtoKoWitchsHomeworkNext"));
        Assert.Contains(slice, c => c.Contains("ProtoKoOneMoreCharge"));
    }

    [Fact]
    public void Homework_growth_is_a_saved_property_that_writes_the_face()
    {
        var prop = typeof(ProtoKoWitchsHomeworkNext).GetProperty("HomeworkGrowth")!;
        Assert.NotNull(prop.GetCustomAttribute<SavedPropertyAttribute>());

        // A save load writes the property; the face follows.
        var loaded = Mutable(new ProtoKoWitchsHomeworkNext());
        ((IHomeworkCard)loaded).HomeworkGrowth = 4;
        Assert.Equal(10m, loaded.DynamicVars["BombSize"].BaseValue);
        Assert.Equal(10, loaded.DynamicVars["BombSize"].IntValue);
    }

    [Fact]
    public void Homework_grows_the_combat_copy_and_its_deck_card_like_genetic_algorithm()
    {
        var deck = Mutable(new ProtoKoWitchsHomeworkNext());
        var combat = Mutable(new ProtoKoWitchsHomeworkNext());
        combat.DeckVersion = deck;

        KleeScalingPass.Grow(combat, 2);
        Assert.Equal(2, ((IHomeworkCard)deck).HomeworkGrowth);
        Assert.Equal(2, ((IHomeworkCard)combat).HomeworkGrowth);
        Assert.Equal(8m, deck.DynamicVars["BombSize"].BaseValue);
        Assert.Equal(8m, combat.DynamicVars["BombSize"].BaseValue);

        // A card with no deck version (made in combat) grows only itself.
        var made = Mutable(new ProtoKoWitchsHomeworkNext());
        KleeScalingPass.Grow(made, 3);
        Assert.Equal(9m, made.DynamicVars["BombSize"].BaseValue);
    }

    [Fact]
    public void Homework_grows_at_most_once_a_combat_whatever_replays_it()
    {
        KleeOverhaulLedger.ResetAll();
        var klee = Seat.Klee();
        var deck = Mutable(new ProtoKoWitchsHomeworkNext());
        var first = Mutable(new ProtoKoWitchsHomeworkNext());
        first.DeckVersion = deck;
        // A replay is the same combat card; a second copy of the same deck
        // card shares the key.
        var second = Mutable(new ProtoKoWitchsHomeworkNext());
        second.DeckVersion = deck;

        KleeScalingPass.AfterHomeworkWentOff(klee.Creature, Marked(first));
        KleeScalingPass.AfterHomeworkWentOff(klee.Creature, Marked(first));
        KleeScalingPass.AfterHomeworkWentOff(klee.Creature, Marked(second));
        Assert.Equal(2, ((IHomeworkCard)deck).HomeworkGrowth);

        // An unmarked charge (a copy from All of My Treasures!) grows nothing.
        var other = Mutable(new ProtoKoWitchsHomeworkNext());
        KleeScalingPass.AfterHomeworkWentOff(klee.Creature,
            new ProtoBombPower.ProtoCharge(20, false, 0));
        Assert.Equal(0, ((IHomeworkCard)other).HomeworkGrowth);

        // The next combat (a fresh ledger) grows it again.
        KleeOverhaulLedger.ResetAll();
        KleeScalingPass.AfterHomeworkWentOff(klee.Creature, Marked(first));
        Assert.Equal(4, ((IHomeworkCard)deck).HomeworkGrowth);
        KleeOverhaulLedger.ResetAll();
    }

    [Fact]
    public void The_mark_survives_a_jump_and_a_merge_and_a_copy_never_has_it()
    {
        // Explode is where it is read.
        Assert.Contains("KleeScalingPass.AfterHomeworkWentOff",
                        Il.Calls(Il.Method("ProtoBombPower", "Explode")));
        // A jump hands the charge's mark to its landing.
        Assert.Contains("ProtoCharge.get_Homework",
                        Il.Calls(Il.Method("ProtoBombPower", "JumpCharges")));
        // A merge carries every mark it swallowed.
        Assert.Contains("KleeScalingPass.MergeMarks",
                        Il.Calls(Il.Method("ProtoBombPower", "MergeAllTo")));
        // A copy reads the size and nothing else.
        foreach (var copy in new[] { "PlaceCopyOfLargest", "PlaceCopyOfLargestOnAll" })
        {
            Assert.DoesNotContain("ProtoCharge.get_Homework",
                                  Il.Calls(Il.Method("ProtoBombPower", copy)));
        }

        var a = Mutable(new ProtoKoWitchsHomeworkNext());
        var b = Mutable(new ProtoKoWitchsHomeworkNext());
        Assert.Null(KleeScalingPass.MergeMarks(null, null));
        Assert.Equal(new CardModel[] { a }, KleeScalingPass.MergeMarks(null, new CardModel[] { a }));
        Assert.Equal(new CardModel[] { a, b },
                     KleeScalingPass.MergeMarks(new CardModel[] { a }, new CardModel[] { b, a }));
    }

    [Fact]
    public void Two_merged_homework_bombs_grow_both_cards()
    {
        KleeOverhaulLedger.ResetAll();
        var klee = Seat.Klee();
        var a = Mutable(new ProtoKoWitchsHomeworkNext());
        var b = Mutable(Upgraded<ProtoKoWitchsHomeworkNext>());
        KleeScalingPass.AfterHomeworkWentOff(klee.Creature,
            new ProtoBombPower.ProtoCharge(20, false, 0, new CardModel[] { a, b }));
        Assert.Equal(2, ((IHomeworkCard)a).HomeworkGrowth);
        Assert.Equal(3, ((IHomeworkCard)b).HomeworkGrowth);
        KleeOverhaulLedger.ResetAll();
    }

    [Fact]
    public void Fight_telemetry_writes_each_homeworks_run_long_bomb_size()
    {
        var grown = Mutable(new ProtoKoWitchsHomeworkNext());
        ((IHomeworkCard)grown).HomeworkGrowth = 4;
        var fresh = Mutable(Upgraded<ProtoKoWitchsHomeworkNext>());
        Assert.Equal(10, KleeScalingPass.RunBombSize((IHomeworkCard)grown));
        Assert.Equal(6, ((IHomeworkCard)fresh).HomeworkBaseSize);

        var telemetry = typeof(global::KleeMod.Diagnostics.PlayTelemetryHooks).Assembly.GetTypes()
            .First(t => t.Name == "PlayTelemetry");
        var sizes = telemetry.GetMethod("HomeworkBombSizes", HeadlessGame.All)!;
        // Deck order, one per Witch's Homework II; other cards are skipped.
        Assert.Equal(new List<int> { 10, 6 },
            (List<int>)sizes.Invoke(null, new object?[]
                { new CardModel[] { grown, new ProtoKoPop(), fresh } })!);
        Assert.Empty((List<int>)sizes.Invoke(null, new object?[] { null })!);
        Assert.Empty((List<int>)sizes.Invoke(null, new object?[]
            { new CardModel[] { new ProtoKoPop() } })!);

        // The key is always written, `[]` with none, and the flush fills it.
        Environment.SetEnvironmentVariable("GITS_TELEMETRY_INTENT", "");
        telemetry.GetMethod("ResetForTest", HeadlessGame.All)!.Invoke(null, null);
        var seat = Seat.Klee();
        telemetry.GetMethod("OpenSeatForTest", HeadlessGame.All)!
            .Invoke(null, new object[] { seat.Player, 1, 0 });
        var json = (string)telemetry.GetMethod("JsonForTest", HeadlessGame.All)!
            .Invoke(null, new object[] { seat.Player })!;
        Assert.Contains("\"homework_bomb_size\":[]", json);
        telemetry.GetMethod("ResetForTest", HeadlessGame.All)!.Invoke(null, null);
        Assert.Contains("PlayTelemetry.HomeworkBombSizes",
                        Il.Calls(Il.Method("PlayTelemetry", "FlushAll")));
    }

    // ==== D. The tempo relic ==================================================

    [Fact]
    public void The_tempo_relic_is_pounding_surprise_plus_a_bomb_six_at_combat_start()
    {
        var relic = (PoundingSurpriseNext)RuntimeHelpers
            .GetUninitializedObject(typeof(PoundingSurpriseNext));
        Assert.Equal(RelicRarity.Starter, relic.Rarity);
        Assert.EndsWith(
            "At the start of each combat, place a [gold]Bomb[/gold] [blue]6[/blue] "
          + "on a random enemy.", RelicFace(relic));
        Assert.StartsWith("Whenever a [gold]Bomb[/gold] goes off, gain [blue]1[/blue] "
                        + "[gold]Spark[/gold].", RelicFace(relic));
        Assert.Equal(6, PoundingSurpriseNext.OpeningBomb);
        Assert.IsAssignableFrom<IProtoExplosionListener>(relic);

        // Placed at BeforeCombatStart, which runs before the first StartTurn;
        // turn 1's BeforeSideTurnStart grows it by rule 1 before she acts.
        Assert.Contains("ProtoBombPower.PlaceOnRandom",
                        Il.Calls(Il.Method("PoundingSurpriseNext", "BeforeCombatStart")));
        Assert.Contains("ProtoBombPower.GrowBy",
                        Il.Calls(Il.Method("ProtoBombPower", "BeforeSideTurnStart")));
        Assert.Equal(8, PoundingSurpriseNext.OpeningBomb + KleeOverhaulLaw.BombGrowth);

        // It replaces the original when granted, and Orobas upgrades it the same way.
        Assert.Contains("RelicCmd.Remove",
                        Il.Calls(Il.Method("PoundingSurpriseNext", "AfterObtained")));
        Assert.Contains("ModelDb.Relic",
                        string.Join(" ", Il.Calls(Il.Method("PoundingSurpriseNext",
                                                            "GetUpgradeReplacement"))));
    }

    [Fact]
    public void The_tempo_relic_is_a_pool_member_and_offered_nowhere()
    {
        Assert.DoesNotContain(typeof(PoundingSurpriseNext), ArmRelicPools.KleeArmPool);
        Assert.Contains("ModelDb.Relic<PoundingSurpriseNext>",
                        Il.CallSequence(Il.Method("KleeRelicPool", "GenerateAllRelics")));
    }

    // ==== helpers =============================================================

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    private static string RelicFace(RelicModel relic) =>
        ((ILocalizationProvider)relic).Localization!.Single(r => r.Item1 == "description").Item2;

    private static T Mutable<T>(T card) where T : CardModel
    {
        Seat.Set(card, "IsMutable", true);
        return card;
    }

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, new object?[] { });
        return card;
    }

    private static ProtoBombPower.ProtoCharge Marked(CardModel card) =>
        new(10, false, 0, new[] { card });
}
