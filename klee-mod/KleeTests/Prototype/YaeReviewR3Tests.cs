using System;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// YAE REVIEW R3 (ruled 2026-10-14, both picks (a) as amended,
/// <c>review/active/yae-review-r3-2026-10-14.md</c>). The pure decisions
/// read value by value, and the live doors' call graphs pinned. The sim
/// half is <c>tier0/tests/test_yae_review_r3.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeReviewR3Tests : IDisposable
{
    public YaeReviewR3Tests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose()
    {
        YaeShrineLedger.ResetAll();
    }

    private static YaeShrineLedger Fresh() => YaeShrineLedger.For(Seat.Yae().Creature);

    private static string Face(CardModel card) =>
        ((BaseLib.Abstracts.CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    private static T Mutable<T>(T card) where T : CardModel
    {
        Seat.Set(card, "IsMutable", true);
        return card;
    }

    // ==== 1. Sakura kinds ===================================================

    [Fact]
    public void Each_kind_acts_for_its_base_plus_level_and_red_ink_adds_three()
    {
        // The Sakura Levels paper (2026-10-17): Sakura 1 + 2 per Level.
        Assert.Equal(1 + 2 * 4, YaeShrineLedger.ActSize(YaeSakuraKind.Thunder, 4, YaeAnnotation.None));
        Assert.Equal(1 + 4, YaeShrineLedger.ActSize(YaeSakuraKind.Foxfire, 4, YaeAnnotation.None));
        Assert.Equal(2 + 4, YaeShrineLedger.ActSize(YaeSakuraKind.Kitsune, 4, YaeAnnotation.None));
        Assert.Equal(1 + 4 + 3, YaeShrineLedger.ActSize(YaeSakuraKind.Foxfire, 4, YaeAnnotation.RedInk));
        Assert.Equal(2 + 4 + 3, YaeShrineLedger.ActSize(YaeSakuraKind.Kitsune, 4, YaeAnnotation.RedInk));
    }

    [Fact]
    public void A_plant_carries_its_kind_and_its_planted_level()
    {
        var ledger = Fresh();
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, 2, kind: YaeSakuraKind.Foxfire));
        var s = Assert.Single(ledger.Standing);
        Assert.Equal(YaeSakuraKind.Foxfire, s.Kind);
        Assert.Equal(2, s.PlantedLevel);
        ledger.LevelUp(3);
        Assert.Equal((2, 5), (s.PlantedLevel, s.Level));
    }

    [Fact]
    public void A_full_shrine_plant_of_the_same_kind_levels_the_oldest()
    {
        var ledger = Fresh();
        for (var i = 0; i < 3; i++) ledger.Plant(YaeLaw.PlantLevel, null, kind: YaeSakuraKind.Kitsune);
        var oldest = ledger.Standing[0];
        ledger.Tick();
        ledger.Tick();                                 // 1 turn left each
        Assert.False(ledger.Plant(YaeLaw.PlantLevel, null, kind: YaeSakuraKind.Kitsune));
        Assert.Same(oldest, ledger.Standing[0]);
        Assert.Equal(2, oldest.Level);
        Assert.Equal(YaeLaw.SakuraTurns, oldest.TurnsLeft);
        Assert.Equal(3, ledger.Count);
    }

    [Fact]
    public void A_full_shrine_plant_of_another_kind_withers_the_oldest_and_takes_its_place()
    {
        var ledger = Fresh();
        for (var i = 0; i < 3; i++) ledger.Plant(YaeLaw.PlantLevel);
        ledger.LevelUp(4);
        var oldest = ledger.Standing[0];
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.RedInk,
                                 kind: YaeSakuraKind.Foxfire));
        Assert.DoesNotContain(oldest, ledger.Standing);
        Assert.Equal(3, ledger.Count);
        var newest = ledger.Standing[^1];
        Assert.Equal(YaeSakuraKind.Foxfire, newest.Kind);
        // The Sakura Levels paper (2026-10-17, pick 1 (a)): the withered
        // Sakura's Level 5 carries over to the one taking its place.
        Assert.Equal(5, newest.Level);
        Assert.Equal(new[] { YaeAnnotation.RedInk }, newest.Annotations);
        Assert.Equal(new[] { 5, 5, 5 }, ledger.Standing.Select(s => s.Level));
    }

    [Fact]
    public void The_door_makes_the_oldest_act_before_the_ledger_decides()
    {
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Plant))!).ToList();
        var act = calls.FindIndex(c => c == "YaeShrine.Act");
        var plant = calls.FindIndex(c => c == "YaeShrineLedger.Plant");
        Assert.True(act >= 0 && plant > act, string.Join(", ", calls));
    }

    [Fact]
    public void A_sakura_acts_at_turn_end_last_bloom_and_tenko()
    {
        Assert.Contains(Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.TurnEnd))!),
                        c => c.Contains(nameof(YaeShrine.ActAll)));
        Assert.Contains(Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.TickAndBloom))!),
                        c => c.Contains("YaeShrine.Act"));
        var tenko = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Tenko))!).ToList();
        var all = tenko.FindIndex(c => c.Contains(nameof(YaeShrine.ActAll)));
        var refresh = tenko.FindIndex(c => c.Contains(nameof(YaeShrineLedger.Refresh)));
        Assert.True(all >= 0 && refresh > all, string.Join(", ", tenko));
    }

    [Fact]
    public void Edict_rides_the_damage_kinds_only()
    {
        // Hit carries Edict; the Kitsune branch gives Block and never hits.
        Assert.Contains(Il.CallSequence(typeof(YaeShrine).GetMethod("Hit", HeadlessGame.All)!),
                        c => c.Contains("EdictOfCleansingPower"));
        Assert.False(YaeShrineLedger.DealsDamage(YaeSakuraKind.Kitsune));
        var ledger = Fresh();
        ledger.Plant(YaeLaw.PlantLevel, null, kind: YaeSakuraKind.Kitsune);
        ledger.LevelUp(5);
        ledger.Plant(YaeLaw.PlantLevel, null, kind: YaeSakuraKind.Foxfire);
        Assert.Equal(YaeSakuraKind.Kitsune, ledger.Highest()!.Kind);           // Editor-in-Chief
        Assert.Equal(YaeSakuraKind.Foxfire, ledger.Highest(damageOnly: true)!.Kind);  // Pounce
    }

    [Fact]
    public void The_four_cards_and_every_planter_are_as_ruled()
    {
        Assert.Equal("Gain {Block:diff()} [gold]Block[/gold]. Plant a [gold]Kitsune Sakura[/gold].",
                     Face(new ProtoYmShrineMaidensGuard()));
        Assert.Equal("Deal {Damage:diff()} [gold]Electro[/gold] damage to ALL enemies. Plant a "
                     + "[gold]Foxfire Sakura[/gold]. It strikes now.",   // flat-value pass, 2026-10-17
                     Face(new ProtoYmFoxfireSweep()));
        Assert.Contains("Weak[/gold] to ALL enemies. [gold]Tenko[/gold]", Face(new ProtoYmKitsuneGuile()));
        // Yae review r6, item 2.
        Assert.Equal("Draw {Cards:diff()} cards. [gold]Edit[/gold] a card in your hand: "
                     + "[gold]Red Ink[/gold].",
                     Face(new ProtoYmManuscriptPile()));
        Assert.Contains(Il.CallSequence(Il.Method("ProtoYmShrineMaidensGuard", "OnPlay")),
                        c => c.Contains("YaeCards.Plant"));
        // Every planting card carries the full-shrine tip.
        foreach (var card in new CardModel[]
                 {
                     new ProtoYmYakanEvocation(), new ProtoYmTwinSakura(), new ProtoYmReplanting(),
                     new ProtoYmShrineMaidensGuard(), new ProtoYmFoxfireSweep(),
                 })
        {
            Assert.True(card is ISakuraPlanterCard, card.GetType().Name);
            Assert.Contains(Il.Calls(card.GetType().GetProperty("ExtraHoverTips", HeadlessGame.All)!
                                .GetGetMethod(true)!),
                            c => c.Contains(nameof(ArmKeywordTips.ForFullShrine)));
        }
    }

    [Fact]
    public void The_badge_names_the_kind_the_planted_level_and_the_action()
    {
        var loc = new SakuraFirstPower().Localization!
            .Single(r => r.Item1 == "smartDescription").Item2;
        Assert.Contains("{Kind:cond:==1?Foxfire Sakura|==2?Kitsune Sakura|Sakura}", loc);
        Assert.Contains(", planted at {Planted}.", loc);
        Assert.Contains("Hits ALL enemies for", loc);
        Assert.Contains("You gain", loc);
        Assert.Contains("Turns left: {Turns}", loc);
    }

    // ==== 2. the Masterpiece ================================================

    [Fact]
    public void Stacked_layers_add_up_and_the_temporary_slot_counts_too()
    {
        var stack = new[] { YaeAnnotation.RedInk, YaeAnnotation.RedInk, YaeAnnotation.SakuraSeal };
        Assert.Equal(3, YaeLayers.Count(stack, YaeAnnotation.RedInk, YaeAnnotation.RedInk));
        Assert.Equal(1, YaeLayers.Count(stack, YaeAnnotation.Footnote, YaeAnnotation.SakuraSeal));
        Assert.Equal(4, YaeLayers.All(stack, YaeAnnotation.Footnote).Count);
        Assert.Equal(YaeAnnotation.Footnote, YaeLayers.All(stack, YaeAnnotation.Footnote)[^1]);
    }

    [Fact]
    public void Reprint_exactly()
    {
        // First play each combat: once per stacked Reprint, plus an armed
        // temporary one; then the stack is inert.
        Assert.Equal(2, YaeLayers.Replays(2, playedOnce: false, armed: 0));
        Assert.Equal(3, YaeLayers.Replays(2, playedOnce: false, armed: 1));
        Assert.Equal(0, YaeLayers.Replays(2, playedOnce: true, armed: 0));
        // A new temporary Reprint arms one fresh replay.
        Assert.Equal(1, YaeLayers.Replays(2, playedOnce: true, armed: 1));
        // Publishing an armed temporary Reprint before the first play: the
        // stack counts it now, so it is never counted twice.
        Assert.Equal(0, YaeLayers.ArmedAfterPublish(YaeAnnotation.Reprint, false, 1));
        Assert.Equal(1, YaeLayers.ArmedAfterPublish(YaeAnnotation.Reprint, true, 1));
        Assert.Equal(1, YaeLayers.ArmedAfterPublish(YaeAnnotation.Footnote, false, 1));
    }

    [Fact]
    public void A_copys_reprints_are_armed()
    {
        var calls = Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.AuthorsCopy))!).ToList();
        var clone = calls.FindIndex(c => c.Contains("CreateClone"));
        var arm = calls.FindIndex(c => c.Contains("ArmAsCopy"));
        var add = calls.FindIndex(c => c.Contains("AddGeneratedCardToCombat"));
        Assert.True(clone >= 0 && arm > clone && add > arm, string.Join(", ", calls));
    }

    [Fact]
    public void The_tip_lists_both_layers_and_the_face_its_play_riders()
    {
        Assert.Equal("Published: Red Ink x2, Reprint. This combat: Footnote.",
                     YaeAnnotationText.Summary(
                         new[] { YaeAnnotation.RedInk, YaeAnnotation.Reprint, YaeAnnotation.RedInk },
                         YaeAnnotation.Footnote, false));
        Assert.Equal("This combat: Reprint. Reprint: used this combat.",
                     YaeAnnotationText.Summary(Array.Empty<YaeAnnotation>(), YaeAnnotation.Reprint, true));
        Assert.Equal("[gold]Sakura Seal[/gold] x2. [gold]Footnote[/gold].",
                     YaeAnnotationText.FaceLine(new[]
                     {
                         YaeAnnotation.SakuraSeal, YaeAnnotation.RedInk,
                         YaeAnnotation.SakuraSeal, YaeAnnotation.Footnote,
                     }));
        Assert.Equal("", YaeAnnotationText.FaceLine(new[] { YaeAnnotation.RedInk }));
        var loc = new YaeMasterpiece().Localization!;
        Assert.Equal("Annotated", loc.Single(r => r.Item1 == "title").Item2);
        Assert.Equal("{Layers}", loc.Single(r => r.Item1 == "description").Item2);
    }

    [Fact]
    public void One_enchantment_holds_both_layers_and_the_old_seven_are_gone()
    {
        var asm = typeof(YaeMasterpiece).Assembly;
        foreach (var gone in new[] { "RedInkAnnotation", "FootnoteAnnotation", "ReprintAnnotation",
                                     "RoyaltiesAnnotation", "SakuraSealAnnotation",
                                     "FoxFireAnnotation", "DeadlineExtensionAnnotation",
                                     "YaeAnnotationModel" })
        {
            Assert.Null(asm.GetType("KleeMod.Powers." + gone));
        }
        Assert.Equal(typeof(YaeMasterpiece),
                     typeof(YaeEditing).GetMethod(nameof(YaeEditing.Masterpiece))!.ReturnType
                         .GetGenericArguments().FirstOrDefault() ?? typeof(YaeMasterpiece));
    }

    [Fact]
    public void An_edit_reaches_a_published_card_and_publish_stacks()
    {
        // Pick 2 (a): the dead-edit filter only; #1308's skip is gone.
        Assert.DoesNotContain($"{nameof(YaeEditing)}.{nameof(YaeEditing.Published)}",
            Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.EditReaches))!));
        var toDeck = Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.PublishToDeck))!);
        Assert.Contains(toDeck, c => c.Contains(nameof(YaeEditing.Stack)));
        var layer = Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.PublishLayer))!);
        Assert.Contains(layer, c => c.Contains(nameof(YaeLayers.ArmedAfterPublish)));
        // The after-elite offer and the drafts read the temporary layer.
        Assert.Contains(Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.SnapshotDrafts))!),
                        c => c.Contains(nameof(YaeEditing.Temporary)));
    }

    [Fact]
    public void Every_reader_of_an_annotation_reads_the_layers()
    {
        // Serialization and Editor-in-Chief read IsAnnotated, which is "any
        // layer". (Bestseller and Print Run count Edits since Yae review r5,
        // pick 1 (a): YaeReviewR5Tests.)
        Assert.Contains(Il.Calls(typeof(YaeEditing).GetMethod(nameof(YaeEditing.IsAnnotated))!),
                        c => c.Contains(nameof(YaeEditing.Layers)));
        Assert.Contains(Il.Calls(typeof(YaeShrine).GetMethod(nameof(YaeShrine.AfterCardPlayed))!),
                        c => c.Contains(nameof(YaeEditing.IsAnnotated)));
        // Red Ink inheritance counts layers.
        Assert.Contains(Il.Calls(typeof(YaeAnnotationReach).GetMethod(nameof(YaeAnnotationReach.Inherited))!),
                        c => c.Contains(nameof(YaeEditing.Count)));
    }

    // ==== 3. the signature cards ============================================

    [Fact]
    public void The_signature_cards_are_the_papers()
    {
        var sp = new ProtoYmSecondPrinting();
        Assert.Equal((0, CardType.Skill, CardRarity.Uncommon), (sp.EnergyCost.Canonical, sp.Type, sp.Rarity));
        Assert.Contains(CardKeyword.Exhaust, sp.CanonicalKeywords);
        Assert.Equal("Put an [gold]Annotated[/gold] card from your [gold]Discard Pile[/gold] into your [gold]Hand[/gold]."
                     + "{IfUpgraded:show: It costs 0 this turn.|}", Face(sp));
        var ac = new ProtoYmAuthorsCopy();
        Assert.Equal((1, CardType.Skill, CardRarity.Uncommon), (ac.EnergyCost.Canonical, ac.Type, ac.Rarity));
        Assert.Contains(CardKeyword.Exhaust, ac.CanonicalKeywords);
        Assert.Contains(Il.Calls(Il.Method("ProtoYmAuthorsCopy", "OnUpgrade")), c => c.Contains("EnergyCost"));
        var sn = new ProtoYmSerialNovel();
        Assert.Equal((2, CardType.Power, CardRarity.Rare), (sn.EnergyCost.Canonical, sn.Type, sn.Rarity));
        Assert.Contains(Il.Calls(Il.Method("ProtoYmSerialNovel", "OnUpgrade")), c => c.Contains("EnergyCost"));
    }

    [Fact]
    public void Second_printing_picks_an_annotated_card_from_the_discard()
    {
        var calls = Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.SecondPrinting))!).ToList();
        Assert.Contains(calls, c => c.Contains("FromCombatPile"));
        Assert.Contains(calls, c => c.Contains("CardPileCmd.Add"));
        Assert.Contains(calls, c => c.Contains("SetThisTurn"));
        Assert.Contains(Il.Calls(typeof(YaeCards).GetMethod(nameof(YaeCards.SecondPrinting))!),
                        c => c.Contains("get_IsUpgraded"));
    }

    [Fact]
    public void Authors_copy_can_never_copy_an_authors_copy_so_no_energy_loop()
    {
        // GPT's loop: an Author's Copy+ with Royalties, copied by another,
        // copies the original again for +1 Energy each time. The target is
        // refused by TYPE, before anything else is read, so no layer can
        // make it reachable.
        var editor = Mutable(new ProtoYmAuthorsCopy());
        var other = Mutable(new ProtoYmAuthorsCopy());
        Assert.True(YaeEditing.IsAuthorsCopy(other));
        Assert.False(YaeEditing.CopyReaches(other, editor));
        Assert.False(YaeEditing.CopyReaches(editor, editor));
        // A plain card with no layer is not a target either.
        Assert.False(YaeEditing.CopyReaches(Mutable(new StrikeIronclad()), editor));
        var calls = Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.CopyReaches))!).ToList();
        var ban = calls.FindIndex(c => c.Contains(nameof(YaeEditing.IsAuthorsCopy)));
        var annotated = calls.FindIndex(c => c.Contains(nameof(YaeEditing.IsAnnotated)));
        Assert.True(ban >= 0 && annotated > ban, string.Join(", ", calls));
    }

    [Fact]
    public void Serial_novel_returns_annotated_cards_at_her_turn_start()
    {
        var calls = Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.RecallRandomAnnotated))!).ToList();
        Assert.Contains(calls, c => c.Contains("CombatCardSelection"));
        Assert.Contains(calls, c => c.Contains("CardPileCmd.Add"));
        Assert.Contains(Il.CallSequence(Il.Method("ProtoYmSerialNovel", "OnPlay")),
                        c => c.Contains("SerialNovelPower"));
    }

    // ==== 4. Fallen Petals ==================================================

    [Fact]
    public void Fallen_petals_withers_the_oldest_then_pays_energy_and_its_upgrade_draws()
    {
        var petals = new ProtoYmFallenPetals();
        Assert.Equal((0, CardType.Skill), (petals.EnergyCost.Canonical, petals.Type));
        Assert.Equal("Your oldest [gold]Sakura[/gold] withers (it acts once, its Last Bloom). "
                     + "If one did, gain {energyPrefix:energyIcons(1)}{IfUpgraded:show:, and draw 1 card|}.",
                     Face(petals));
        var calls = Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.FallenPetals))!).ToList();
        var wither = calls.FindIndex(c => c.Contains(nameof(YaeShrine.WitherOldest)));
        var energy = calls.FindIndex(c => c.Contains("PlayerCmd.GainEnergy"));
        var draw = calls.FindIndex(c => c.Contains("CardPileCmd.Draw"));
        Assert.True(wither >= 0 && energy > wither && draw > energy, string.Join(", ", calls));
        Assert.Contains(calls, c => c.Contains("get_IsUpgraded"));
        var oldest = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.WitherOldest))!).ToList();
        var act = oldest.FindIndex(c => c.Contains("YaeShrine.Act"));
        var gone = oldest.FindIndex(c => c == "YaeShrineLedger.Wither");
        Assert.True(act >= 0 && gone > act, string.Join(", ", oldest));
    }
}
