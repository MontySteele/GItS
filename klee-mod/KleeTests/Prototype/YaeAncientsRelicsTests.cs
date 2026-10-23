#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Cards.Yae;
using KleeMod.Potions;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Relics;
using SilentRelics = MegaCrit.Sts2.Core.Models.Relics;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// YAE: THE RATE PASS, HER TWO ANCIENTS, HER RELICS AND POTIONS (the Yae
/// pass, 2026-10-16, <c>review/active/yae-ancients-relics-2026-10-16.md</c>;
/// [USER]: "Let's do a design pass over the current Yae pool. ... And let's
/// design the two Yae Ancient cards ... Plus potions and regular relics").
/// Pure ledger reads, headless seats and call-graph pins, as every Yae pin
/// is. Sim twin of the rate pass: <c>tier0/tests/test_yae_pass.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeAncientsRelicsTests : IDisposable
{
    public YaeAncientsRelicsTests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose() => YaeShrineLedger.ResetAll();

    private const BindingFlags Instance = BindingFlags.Instance | BindingFlags.NonPublic;

    private static string Face(object model) =>
        ((ILocalizationProvider)model).Localization!.First(r => r.Item1 == "description").Item2;

    private static string Plain(string face) =>
        System.Text.RegularExpressions.Regex.Replace(face, @"\[/?\w+\]", "");

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static int UpCost<T>() where T : CardModel, new() =>
        (int)Upgraded<T>().EnergyCost.GetWithModifiers(MegaCrit.Sts2.Core.Entities.Cards.CostModifiers.None);

    private static int Var(CardModel card, string name) => (int)card.DynamicVars[name].BaseValue;

    private static List<string> OnPlay<T>() =>
        Il.CallSequence(typeof(T).GetMethod("OnPlay", Instance)!).ToList();

    private static T Canon<T>(Type type) where T : class =>
        (T)RuntimeHelpers.GetUninitializedObject(type);

    private static void SetField(object target, string field, object value)
    {
        for (var t = target.GetType(); t != null; t = t.BaseType)
        {
            var f = t.GetField(field, HeadlessGame.All);
            if (f == null) continue;
            f.SetValue(target, value);
            return;
        }
        throw new InvalidOperationException(field);
    }

    private static YaeMasterpiece Fresh()
    {
        var m = new YaeMasterpiece();
        Seat.Set(m, "IsMutable", true);
        return m;
    }

    // ==== sec.1, the rate pass ==============================================

    [Fact]
    public void The_pool_stays_78_at_20_39_19_with_the_two_rarities_swapped()
    {
        var pool = Il.CallSequence(Il.Method("YaeRoster", "Pool"))
            .Where(c => c.StartsWith("ModelDb.Card<", StringComparison.Ordinal)).ToList();
        Assert.Equal(78, pool.Count);
        var types = typeof(ProtoYmThunderRite).Assembly.GetTypes()
            .Where(t => t.Namespace == typeof(ProtoYmThunderRite).Namespace && !t.IsNested)
            .ToDictionary(t => t.Name);
        var rarities = pool.Select(c => c["ModelDb.Card<".Length..^1])
            .Select(n => ((CardModel)Activator.CreateInstance(types[n])!).Rarity).ToList();
        Assert.Equal(20, rarities.Count(r => r == CardRarity.Common));
        // Upgrade census (2026-10-23): Sakura Channeling went Uncommon.
        Assert.Equal(39, rarities.Count(r => r == CardRarity.Uncommon));
        Assert.Equal(19, rarities.Count(r => r == CardRarity.Rare));
        Assert.Equal(CardRarity.Rare, new ProtoYmEditorialPriority().Rarity);
        Assert.Equal(CardRarity.Uncommon, new ProtoYmMischievousTeasing().Rarity);
    }

    [Fact]
    public void Evergreen_charm_makes_the_most_turns_left_last_2_more_turns()
    {
        // The user's ruling, 2026-10-20 (turns-left targeting): was the oldest.
        var card = new ProtoYmEvergreenCharm();
        Assert.Equal("Gain {Block:diff()} [gold]Block[/gold]. Your [gold]Sakura[/gold] with the "
                   + "most turns left lasts {YmAmount:diff()} more turns.", Face(card));
        Assert.Equal(2, Var(card, "YmAmount"));
        Assert.Contains(OnPlay<ProtoYmEvergreenCharm>(), c => c.Contains("YaeCards.ExtendMostTurnsLeft"));
        Assert.DoesNotContain(OnPlay<ProtoYmEvergreenCharm>(), c => c.Contains("EditSakura"));

        var ledger = new YaeShrineLedger();
        Assert.False(ledger.ExtendMostTurnsLeft(2));
        ledger.Plant(1);
        ledger.Plant(1);
        // A tie goes to the newest; then it has the most and keeps growing.
        Assert.True(ledger.ExtendMostTurnsLeft(2));
        Assert.Equal(YaeLaw.SakuraTurns, ledger.Standing[0].TurnsLeft);
        Assert.Equal(YaeLaw.SakuraTurns + 2, ledger.Standing[1].TurnsLeft);
        Assert.True(ledger.ExtendMostTurnsLeft(2));
        Assert.Equal(YaeLaw.SakuraTurns + 4, ledger.Standing[1].TurnsLeft);
        Assert.False(ledger.Standing[1].Has(YaeAnnotation.DeadlineExtension));
    }

    [Fact]
    public void The_upgrades_the_pass_moved()
    {
        // Fox Fire Draft+: the 2 with the most turns left (was every Sakura;
        // the 2 newest until the user's ruling of 2026-10-20).
        Assert.Equal(2, Var(Upgraded<ProtoYmFoxFireDraft>(), "YmAmount"));
        Assert.Contains("your 2 [gold]Sakura[/gold] with the most turns left",
                        Face(new ProtoYmFoxFireDraft()));
        // Thunderbolt Tithe+: 4, plus 5 each.
        Assert.Equal(4, Var(Upgraded<ProtoYmThunderboltTithe>(), "YmBase"));
        Assert.Equal(5, Var(Upgraded<ProtoYmThunderboltTithe>(), "YmPer"));
        // Edict of Cleansing+: +4.
        Assert.Equal(3, Var(new ProtoYmEdictOfCleansing(), "PowerAmount"));
        Assert.Equal(4, Var(Upgraded<ProtoYmEdictOfCleansing>(), "PowerAmount"));
        // Fox Trick: draws 2; its upgrade is 3 Weak.
        Assert.Equal(2, Var(new ProtoYmFoxTrick(), "Cards"));
        Assert.Equal(3, Var(Upgraded<ProtoYmFoxTrick>(), "PowerAmount"));
        Assert.Contains("Draw 2 cards.", Face(new ProtoYmFoxTrick()));
    }

    [Fact]
    public void Rewrite_draws_2_discards_1_then_edits_red_ink()
    {
        Assert.Equal("Draw {Cards:diff()} cards. Discard 1 card. [gold]Edit[/gold] a card in "
                   + "your [gold]Hand[/gold]: [gold]Red Ink[/gold].", Face(new ProtoYmRewrite()));
        Assert.Equal(2, Var(new ProtoYmRewrite(), "Cards"));
        var calls = OnPlay<ProtoYmRewrite>();
        var draw = calls.FindIndex(c => c.Contains("CardPileCmd.Draw"));
        var discard = calls.FindIndex(c => c.Contains("FromHandForDiscard"));
        var edit = calls.FindIndex(c => c.Contains("YaeCards.Edit"));
        Assert.True(draw >= 0 && discard > draw && edit > discard, string.Join(", ", calls));
    }

    // ==== sec.2, the Archaic Tooth's card ===================================

    [Fact]
    public void Sesshou_sakura_is_an_ancient_skill_1_cost_0_upgraded()
    {
        var card = new YakanEvocationSesshouSakura();
        Assert.Equal(CardRarity.Ancient, card.Rarity);
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(0, UpCost<YakanEvocationSesshouSakura>());
        Assert.Equal(3, Var(card, "YmAmount"));
        Assert.Equal("Yakan Evocation: Sesshou Sakura",
                     card.Localization!.First(r => r.Item1 == "title").Item2);
        Assert.Equal("Plant a Foxfire Sakura at Level {YmAmount:diff()}. Edit it: Deadline Extension.",
                     Plain(Face(card)));
        Assert.IsAssignableFrom<ISakuraPlanterCard>(card);
        Assert.Contains(OnPlay<YakanEvocationSesshouSakura>(), c => c.Contains("YaeCards.SesshouSakura"));
        var verb = Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.SesshouSakura))!).ToList();
        var plant = verb.FindIndex(c => c.Contains("YaeShrine.Plant"));
        var edit = verb.FindIndex(c => c.Contains("EditOne"));
        var after = verb.FindIndex(c => c.Contains("AfterEdits"));
        Assert.True(plant >= 0 && edit > plant && after > edit, string.Join(", ", verb));
    }

    [Fact]
    public void Its_foxfire_sakura_never_withers_and_a_second_play_levels_it_or_stands_beside()
    {
        var ledger = new YaeShrineLedger();
        ledger.Plant(YaeLaw.PlantLevel, 3, kind: YaeSakuraKind.Foxfire);
        var it = ledger.LastPlanted;
        Assert.NotNull(it);
        Assert.Equal(3, it!.Level);
        Assert.Equal(4, YaeShrineLedger.ActSize(it.Kind, it.Level, it.Annotations));  // 4 to ALL
        Assert.True(ledger.EditOne(it, YaeAnnotation.DeadlineExtension));
        Assert.Equal(1, ledger.Edits);
        // Deadline Extension twice is the same as once, and no Edit.
        Assert.False(ledger.EditOne(it, YaeAnnotation.DeadlineExtension));
        Assert.Equal(1, ledger.Edits);
        for (var i = 0; i < 6; i++) Assert.Empty(ledger.Tick());
        Assert.Equal(YaeLaw.SakuraTurns, it.TurnsLeft);

        // A second play with room: the new one stands beside it.
        ledger.Plant(YaeLaw.PlantLevel, 3, kind: YaeSakuraKind.Foxfire);
        Assert.Equal(2, ledger.Count);
        Assert.NotSame(it, ledger.LastPlanted);

        // Into a full shrine: it never withers, so (2026-10-17) the plant
        // Levels the Foxfire Sakura closest to withering, not it.
        var second = ledger.LastPlanted!;
        ledger.Plant(YaeLaw.PlantLevel, 3, kind: YaeSakuraKind.Foxfire);
        ledger.Plant(YaeLaw.PlantLevel, 3, kind: YaeSakuraKind.Foxfire);
        Assert.Equal(3, ledger.Count);
        Assert.Same(second, ledger.LastPlanted);
        Assert.Equal(4, second.Level);
        Assert.Equal(3, it.Level);
    }

    [Fact]
    public void The_archaic_tooth_turns_yakan_evocation_into_sesshou_sakura()
    {
        Assert.IsAssignableFrom<ITranscendenceCard>(new ProtoYmYakanEvocation());
        var made = Il.CallSequence(Il.Method("ProtoYmYakanEvocation", "GetTranscendenceTransformedCard"));
        Assert.Contains(made, c => c.Contains("YakanEvocationSesshouSakura"));
        var ledger = Il.CallSequence(typeof(RosterAncientCards).GetProperty("Yae")!.GetGetMethod()!)
            .Where(c => c.StartsWith("ModelDb.Card<", StringComparison.Ordinal)).ToList();
        Assert.Equal(new[] { "ModelDb.Card<YakanEvocationSesshouSakura>",
                             "ModelDb.Card<YaePublishingHouse>" }, ledger);
        Assert.Contains(Il.CallSequence(Il.Method("YaeRoster", "OfferablePool")),
                        c => c.Contains("get_Yae"));
        Assert.Contains(Il.CallSequence(Il.Method("YaeCardPool", "GenerateAllCards")),
                        c => c.Contains("get_Yae"));
        // The Darv guard went with her Ancients.
        Assert.DoesNotContain(typeof(RosterAncientCards).Assembly.GetTypes(),
                              t => t.Name.Contains("YaeDustyTomeGuard"));
    }

    // [USER], 2026-10-16: "let's make it so that any existing annotations on
    // the starter card carry over to the Ancient version. I can already see
    // that being a complaint." The vanilla Tooth (0.111.0, read by decompile
    // 2026-10-16) already does it: GetTranscendenceTransformedCard makes the
    // Ancient, upgrades it if the starter was upgraded, and enchants it with a
    // MutableClone of the starter's enchantment. BaseLib only adds the pair to
    // the map. These two pins hold both halves.

    [Fact]
    public void The_vanilla_tooth_upgrades_and_carries_the_starters_enchantment()
    {
        var transform = typeof(ArchaicTooth).GetMethod("GetTranscendenceTransformedCard",
            BindingFlags.Instance | BindingFlags.NonPublic)!;
        var calls = Il.CallSequence(transform).ToList();
        Assert.Contains(calls, c => c.Contains("get_IsUpgraded"));
        Assert.Contains(calls, c => c.Contains("CardCmd.Upgrade"));
        Assert.Contains(calls, c => c.Contains("get_Enchantment"));
        Assert.Contains(calls, c => c.Contains("MutableClone"));
        Assert.Contains(calls, c => c.Contains("CardCmd.Enchant"));
    }

    [Fact]
    public void A_published_red_ink_and_reprint_ride_the_clone_onto_sesshou_sakura()
    {
        var starter = Fresh();
        starter.Published = new[] { (int)YaeAnnotation.RedInk, (int)YaeAnnotation.Reprint };

        // The vanilla Tooth's step: a MutableClone of the starter's enchantment.
        var carried = (YaeMasterpiece)starter.MutableClone();

        Assert.Equal(new[] { YaeAnnotation.RedInk, YaeAnnotation.Reprint }, carried.Stack);
        Assert.Equal(starter.Published, carried.Published);
        Assert.Equal(1, carried.Count(YaeAnnotation.RedInk));
        Assert.Equal(1, carried.Count(YaeAnnotation.Reprint));
        Assert.Equal(YaeAnnotation.None, carried.Temporary);
        // The Masterpiece rides any card type, so it may enchant the Ancient.
        Assert.True(carried.CanEnchantCardType(new YakanEvocationSesshouSakura().Type));
        Assert.Equal("Published: Red Ink, Reprint.", carried.SummaryText);
    }

    // ==== sec.2, the Dusty Tome's card ======================================

    [Fact]
    public void Yae_publishing_house_is_an_ancient_power_2_cost_1_upgraded()
    {
        var card = new YaePublishingHouse();
        Assert.Equal(CardRarity.Ancient, card.Rarity);
        Assert.Equal(CardType.Power, card.Type);
        Assert.Equal(2, card.EnergyCost.Canonical);
        Assert.Equal(1, UpCost<YaePublishingHouse>());
        Assert.Equal("Your Edits write their Annotation twice.", Plain(Face(card)));
        Assert.Contains(OnPlay<YaePublishingHouse>(),
                        c => c.Contains("PowerCmd.Apply") && c.Contains("YaePublishingHousePower"));
        Assert.Equal("Your Edits write their Annotation twice.",
                     Plain(Face(new YaePublishingHousePower())));
    }

    [Fact]
    public void Its_holder_writes_each_edit_twice_and_the_layers_add_up()
    {
        Assert.Equal(1, YaeEditing.WriteTimes(Seat.Yae().Creature));
        Assert.Equal(2, YaeEditing.WriteTimes(Seat.Yae().WithPower<YaePublishingHousePower>(1).Creature));
        Assert.Equal(1, YaeEditing.WriteTimes(null));

        var m = Fresh();
        typeof(YaeMasterpiece).GetMethod("Set", HeadlessGame.All)!.Invoke(m, new object[]
            { new[] { YaeAnnotation.RedInk }, YaeAnnotation.RedInk, false, 0, 2 });
        Assert.Equal(3, m.Count(YaeAnnotation.RedInk));          // Red Ink 9: 3 layers
        Assert.Equal(2, m.TemporaryCount);
        Assert.Equal("Published: Red Ink. This combat: Red Ink x2.", m.SummaryText);
        Assert.Equal(new[] { YaeAnnotation.Footnote, YaeAnnotation.Footnote },
                     YaeLayers.All(Array.Empty<YaeAnnotation>(), YaeAnnotation.Footnote, 2));
        // Reprint written twice arms two replays: the card plays three times,
        // still once a combat (the armed replays are spent on its play).
        Assert.Equal(2, YaeLayers.Replays(0, false, 2));
        Assert.Equal(0, YaeLayers.Replays(0, true, 0));
        // A Publish moves one layer; a doubled Reprint keeps one armed.
        Assert.Equal(1, YaeLayers.ArmedAfterPublish(YaeAnnotation.Reprint, false, 2));
        Assert.Equal(0, YaeLayers.ArmedAfterPublish(YaeAnnotation.Reprint, false, 1));
        // The default is one layer, as every Edit before.
        Assert.Equal(1, YaeLayers.Count(Array.Empty<YaeAnnotation>(), YaeAnnotation.Royalties,
                                        YaeAnnotation.Royalties));
    }

    [Fact]
    public void Every_card_edit_asks_how_many_times_to_write()
    {
        foreach (var name in new[] { "EditAll" })
        {
            Assert.Contains(Il.CallSequence(typeof(YaeEditing).GetMethod(name)!),
                            c => c.Contains(nameof(YaeEditing.WriteTimes)));
        }
        Assert.Contains(Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.Edit))!),
                        c => c.Contains(nameof(YaeEditing.WriteTimes)));
        Assert.Contains(Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.EditOneFor))!),
                        c => c.Contains(nameof(YaeEditing.WriteTimes)));
        Assert.Contains(Il.CallSequence(Il.Method("SaiguusInkstone", "Edit")),
                        c => c.Contains(nameof(YaeEditing.WriteTimes)));
    }

    // ==== sec.3, her relics =================================================

    [Fact]
    public void Seven_relics_in_the_base_games_shape_and_three_potions()
    {
        Assert.Equal(new[]
        {
            RelicRarity.Common, RelicRarity.Uncommon, RelicRarity.Uncommon,
            RelicRarity.Rare, RelicRarity.Rare, RelicRarity.Rare, RelicRarity.Shop,
        }, YaeArmRelics.Types.Select(t => Canon<RelicModel>(t).Rarity).ToArray());

        var potions = YaePotions.Types.Select(t => Canon<PotionModel>(t)).ToList();
        Assert.Equal(new[] { PotionRarity.Common, PotionRarity.Uncommon, PotionRarity.Rare },
                     potions.Select(p => p.Rarity).ToArray());
        Assert.All(potions, p => Assert.Equal(PotionUsage.CombatOnly, p.Usage));
        Assert.All(potions, p => Assert.Equal(TargetType.AnyPlayer, p.TargetType));
    }

    [Fact]
    public void Every_face_is_the_papers_word_for_word()
    {
        var faces = YaeArmRelics.Types.Concat(YaePotions.Types)
            .Select(t => ((ILocalizationProvider)Canon<AbstractModel>(t)).Localization!)
            .Select(loc => (loc[0].Item2, Plain(loc[1].Item2)))
            .ToArray();
        Assert.Equal(new[]
        {
            ("Kitsune Mask", "At the start of each combat, apply 1 Weak to ALL enemies."),
            ("Sacred Sakura Branch", "At the start of each combat, plant a Sakura."),
            // House text rules (docs/current/text-conventions.md): the
            // first-time order, "additional damage", a golded Hand.
            ("Proofreader's Glasses", "The first time each turn you Edit a card, draw 1 card."),
            ("Electroculus", "Your Sakura's strikes deal 1 additional damage."),
            ("Saiguu's Inkstone",
             "At the start of your turn, Edit a random card in your Hand: Red Ink."),
            ("Kagura Bell", "Whenever you Tenko, each Sakura gains a Level."),
            ("Fox Ofuda", "You can have 1 more Sakura."),
            ("Bottled Sakura", "Plant 2 Sakura."),
            ("Fox's Inkwell", "Edit a card in your Hand with an Annotation of your choice."),
            ("Narukami Sake", "Each Sakura gains 2 Levels. Tenko."),
        }, faces);
    }

    [Fact]
    public void Her_offer_is_meditations_her_seven_and_enlightened_blessing()
    {
        Assert.Equal(
            new[] { typeof(MeditationsOfAYako) }.Concat(YaeArmRelics.Types)
                .Append(typeof(EnlightenedBlessing)),
            ArmRelicPools.YaeArmPool);
        var members = Il.CallSequence(Il.Method("YaeRelicPool", "GenerateAllRelics"));
        foreach (var t in ArmRelicPools.YaeArmPool)
        {
            Assert.Contains($"ModelDb.Relic<{t.Name}>", members);
        }
        Assert.Contains(members, c => c.Contains("InheritedSilentRelics.Curated"));

        var pool = (YaeRelicPool)RuntimeHelpers.GetUninitializedObject(typeof(YaeRelicPool));
        var silent = new[]
        {
            typeof(SilentRelics.NinjaScroll), typeof(SilentRelics.PaperKrane),
            typeof(SilentRelics.RingOfTheSnake), typeof(SilentRelics.TwistedFunnel),
        };
        SetField(pool, "_relics", silent.Concat(ArmRelicPools.YaeArmPool)
            .Select(t => (RelicModel)RuntimeHelpers.GetUninitializedObject(t)).ToList());
        var offer = pool.GetUnlockedRelics(null!).Select(r => r.GetType()).ToList();
        Assert.Equal(ArmRelicPools.YaeArmPool.OrderBy(t => t.Name), offer.OrderBy(t => t.Name));
    }

    [Fact]
    public void Electroculus_adds_1_to_a_striking_sakura_and_not_to_kitsune_block()
    {
        var yae = Seat.Yae().WithRelic<Electroculus>();
        Assert.Equal(1, Electroculus.Bonus(yae.Creature));
        Assert.Equal(0, Electroculus.Bonus(Seat.Yae().Creature));
        Assert.Equal(0, Electroculus.Bonus(Seat.Kokomi().WithRelic<Electroculus>().Creature));

        var ledger = YaeShrineLedger.For(yae.Creature);
        ledger.Plant(1);
        ledger.Plant(1, null, kind: YaeSakuraKind.Foxfire);
        ledger.Plant(1, null, kind: YaeSakuraKind.Kitsune);
        Assert.Equal(YaeLaw.SakuraBase + YaeLaw.SakuraPerLevel * 1 + 1, YaeShrine.Size(yae.Creature, ledger.Standing[0]));
        Assert.Equal(YaeLaw.FoxfireBase + 1 + 1, YaeShrine.Size(yae.Creature, ledger.Standing[1]));
        Assert.Equal(YaeLaw.KitsuneBase + 1, YaeShrine.Size(yae.Creature, ledger.Standing[2]));
        // Before Edict: the act's hit adds Edict on top of Size.
        Assert.Contains(Il.CallSequence(Il.Method("YaeShrine", "Act")), c => c.Contains("Size"));
    }

    [Fact]
    public void Fox_ofuda_raises_the_cap_by_1_and_stacks_with_channeling()
    {
        Assert.Equal(YaeLaw.SakuraCap + 1,
                     YaeShrine.MaxSakura(Seat.Yae().WithRelic<FoxOfuda>().Creature));
        Assert.Equal(YaeLaw.SakuraCap + 3,
                     YaeShrine.MaxSakura(Seat.Yae().WithRelic<FoxOfuda>()
                         .WithPower<SakuraChannelingPower>(2).Creature));
        Assert.Equal(YaeLaw.SakuraCap, YaeShrine.MaxSakura(Seat.Yae().Creature));
    }

    [Fact]
    public void Kagura_bell_levels_every_sakura_after_the_tenkos_strikes()
    {
        Assert.Equal(1, KaguraBell.LevelsFor(Seat.Yae().WithRelic<KaguraBell>().Creature));
        Assert.Equal(0, KaguraBell.LevelsFor(Seat.Yae().Creature));
        var ring = Il.CallSequence(Il.Method("KaguraBell", "Ring")).ToList();
        Assert.Contains(ring, c => c.Contains("LevelUp"));
        Assert.Contains(ring, c => c.Contains("get_Count"));            // no Sakura: nothing

        var tenko = Il.CallSequence(Il.Method("YaeShrine", "Tenko")).ToList();
        var act = tenko.FindIndex(c => c.Contains("ActAll"));
        var rings = tenko.FindIndex(c => c.Contains("KaguraBell.Ring"));
        Assert.True(act >= 0 && rings > act, string.Join(", ", tenko));
    }

    [Fact]
    public void Proofreaders_glasses_draw_on_the_turns_first_edit()
    {
        Assert.Equal(1, ProofreadersGlasses.DrawFor(Seat.Yae().WithRelic<ProofreadersGlasses>().Creature));
        Assert.Equal(0, ProofreadersGlasses.DrawFor(Seat.Yae().Creature));
        var after = Il.CallSequence(Il.Method("YaeShrine", "AfterEdits")).ToList();
        Assert.Contains(after, c => c.Contains("SerializationPower.Pay"));
        Assert.Contains(after, c => c.Contains("get_EditsThisTurn"));
        Assert.Contains(after, c => c.Contains("ProofreadersGlasses.FirstEdit"));
        // Every Edit door goes through it.
        Assert.Contains(Il.CallSequence(Il.Method("YaeCards", "EditSakura")), c => c.Contains("AfterEdits"));
        Assert.Contains(Il.CallSequence(Il.Method("YaeEditing", "EditAll")), c => c.Contains("AfterEdits"));
    }

    [Fact]
    public void Saiguus_inkstone_edits_a_random_card_red_ink_would_change_at_turn_start()
    {
        var hand = new CardModel[] { new ProtoYmThunderPetal(), new ProtoYmKitsuneRite() };
        var cands = SaiguusInkstone.Candidates(hand);
        Assert.Contains(cands, c => c is ProtoYmThunderPetal);
        Assert.DoesNotContain(cands, c => c is ProtoYmKitsuneRite);

        var edit = Il.CallSequence(Il.Method("SaiguusInkstone", "Edit")).ToList();
        Assert.Contains(edit, c => c.Contains("CombatCardSelection"));
        Assert.Contains(edit, c => c.Contains(nameof(YaeEditing.Annotate)));
        Assert.Contains(edit, c => c.Contains("NoteEdit"));
        Assert.Contains(edit, c => c.Contains("AfterEdits"));
        // After the turn's Edit count is cleared, so it is the turn's first.
        var start = Il.CallSequence(Il.Method("YaeShrine", "TurnStart")).ToList();
        var clear = start.FindIndex(c => c.Contains("set_EditsThisTurn"));
        var ink = start.FindIndex(c => c.Contains("SaiguusInkstone.Edit"));
        Assert.True(clear >= 0 && ink > clear, string.Join(", ", start));
    }

    [Fact]
    public void Kitsune_mask_and_the_branch_act_on_her_first_turn()
    {
        var mask = Il.CallSequence(typeof(KitsuneMask).GetMethod("AfterPlayerTurnStart")!).ToList();
        Assert.Contains(mask, c => c.Contains("FirstTurnOf"));
        Assert.Contains(mask, c => c.Contains("PowerCmd.Apply") && c.Contains("WeakPower"));
        var branch = Il.CallSequence(typeof(SacredSakuraBranch).GetMethod("AfterPlayerTurnStart")!).ToList();
        Assert.Contains(branch, c => c.Contains("FirstTurnOf"));
        Assert.Contains(branch, c => c.Contains("YaeShrine.Plant"));
        Assert.Equal(0, ProofreadersGlasses.DrawFor(Seat.Kokomi().WithRelic<ProofreadersGlasses>().Creature));
    }

    // ==== sec.4, her potions ================================================

    [Fact]
    public void Her_potion_pool_is_her_three_and_the_defect_borrow_left()
    {
        var calls = Il.CallSequence(typeof(global::KleeMod.Yae).GetProperty("PotionPool")!.GetGetMethod()!);
        Assert.Equal(new[] { "ModelDb.PotionPool<YaePotionPool>" },
                     calls.Where(c => c.StartsWith("ModelDb.")).ToArray());
        var pool = Il.CallSequence(Il.Method("YaePotionPool", "GenerateAllPotions"));
        foreach (var t in YaePotions.Types)
        {
            Assert.Contains($"ModelDb.Potion<{t.Name}>", pool);
        }
    }

    [Fact]
    public void Each_potion_uses_her_own_doors()
    {
        Assert.Contains(Il.CallSequence(Il.Method("BottledSakura", "OnUse")),
                        c => c.Contains("YaeShrine.Plant"));
        var ink = Il.CallSequence(Il.Method("FoxsInkwell", "OnUse")).ToList();
        var choose = ink.FindIndex(c => c.Contains("YaeModalOptions.Choose"));
        var edit = ink.FindIndex(c => c.Contains("YaeEditing.Edit"));
        Assert.True(choose >= 0 && edit > choose, string.Join(", ", ink));
        var sake = Il.CallSequence(Il.Method("NarukamiSake", "OnUse")).ToList();
        var level = sake.FindIndex(c => c.Contains("LevelUp"));
        var tenko = sake.FindIndex(c => c.Contains("YaeShrine.Tenko"));
        Assert.True(level >= 0 && tenko > level, string.Join(", ", sake));
    }
}
