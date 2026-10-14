using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>The one collection every pin that resets the static
/// <see cref="YaeShrineLedger"/> runs in.</summary>
[CollectionDefinition(Name, DisableParallelization = true)]
public sealed class YaeArm
{
    public const string Name = "YaeArm";
}

/// <summary>
/// YAE MIKO (<c>review/active/yae-card-paper-2026-10-13.md</c>, ruled
/// 2026-10-13). One pin per reading in the paper's sec.2, Varka's way: a hit
/// landing needs a live combat, outside the headless boundary, so each rule
/// is a pure decision read value by value -- the shrine ledger is pure for
/// exactly this -- and the call graph is pinned to prove the live sites take
/// that decision rather than their own. The sim twin is
/// <c>tier0/tests/test_yae_shrine.py</c>; <c>tier0/tests/test_yae_parity.py</c>
/// holds the two engines' numbers and row grammar together.
/// </summary>
[Collection(YaeArm.Name)]
public class YaePrototypeTests : IDisposable
{
    public YaePrototypeTests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose()
    {
        YaeShrineLedger.ResetAll();
    }

    private static YaeShrineLedger Fresh() => YaeShrineLedger.For(Seat.Yae().Creature);

    private static void PlantN(YaeShrineLedger ledger, int n,
                               int plantLevel = YaeLaw.PlantLevel,
                               int cap = YaeLaw.LevelCap)
    {
        for (var i = 0; i < n; i++) ledger.Plant(plantLevel, cap);
    }

    /// <summary>A model allocated uninitialised: a CustomRelicModel's or
    /// CustomEnchantmentModel's constructor registers with BaseLib's tables
    /// (<see cref="Seat.WithRelic{T}"/>'s note).</summary>
    private static T Uninit<T>() =>
        (T)System.Runtime.CompilerServices.RuntimeHelpers.GetUninitializedObject(typeof(T));

    private static List<string> Cards(string type, string method) =>
        Il.CallSequence(Il.Method(type, method))
            .Where(c => c.StartsWith("ModelDb.Card<", StringComparison.Ordinal))
            .ToList();

    // ---- who she is ----------------------------------------------------------

    [Fact]
    public void She_is_72_hp_and_her_identity_gates_the_rules()
    {
        var yae = Seat.Yae();
        Assert.Equal(72, new global::KleeMod.Yae().StartingHp);
        Assert.True(YaePrototype.IsYae(yae.Creature));
        Assert.True(YaeShrine.Live(yae.Creature));
        Assert.False(YaeShrine.Live(Seat.Varka().Creature));
        Assert.Equal(0, YaeShrine.Count(Seat.Klee().Creature));
        Assert.Equal("yae", YaePrototype.CharacterId);
    }

    [Fact]
    public void Her_starter_is_the_base_eight_yakan_evocation_and_proofread()
    {
        var deck = Cards("YaeRoster", "StartingDeck");
        Assert.Equal(10, deck.Count);
        Assert.Equal(4, deck.Count(c => c.Contains("StrikeDefect")));
        Assert.Equal(4, deck.Count(c => c.Contains("DefendDefect")));
        Assert.Contains(deck, c => c.Contains(nameof(ProtoYmYakanEvocation)));
        Assert.Contains(deck, c => c.Contains(nameof(ProtoYmProofread)));
        var relics = Il.CallSequence(Il.Method("YaeRoster", "StartingRelics")).ToList();
        Assert.Contains(relics, c => c.Contains(nameof(MeditationsOfAYako)));
    }

    [Fact]
    public void Her_attacks_deal_electro_and_proofread_has_no_block()
    {
        Assert.Equal(global::KleeMod.Elements.Element.Electro, new ProtoYmKitsuneFlash().Element);
        Assert.Equal(global::KleeMod.Elements.Element.Electro, new ProtoYmTenkoKenshin().Element);
        var proofread = new ProtoYmProofread();
        Assert.Equal(CardType.Skill, proofread.Type);
        Assert.Equal(1, proofread.EnergyCost.Canonical);
        Assert.False(proofread.DynamicVars.ContainsKey("Block"));
    }

    // ---- Sakura (sec.2) ------------------------------------------------------

    [Fact]
    public void The_law_numbers_are_the_papers()
    {
        Assert.Equal(3, YaeLaw.SakuraCap);
        Assert.Equal(3, YaeLaw.SakuraTurns);
        Assert.Equal(2, YaeLaw.SakuraBase);
        Assert.Equal(1, YaeLaw.PlantLevel);
        Assert.Equal(3, YaeLaw.LevelCap);
        Assert.Equal(2, YaeLaw.MooncallPlantLevel);
        Assert.Equal(4, YaeLaw.MooncallLevelCap);
        Assert.Equal(3, YaeLaw.RedInkAmount);
        Assert.Equal(4, YaeLaw.FoxFireDamage);
    }

    [Fact]
    public void A_plant_is_level_one_with_three_strikes()
    {
        var ledger = Fresh();
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, YaeLaw.LevelCap));
        var s = Assert.Single(ledger.Standing);
        Assert.Equal(1, s.Level);
        Assert.Equal(3, s.TurnsLeft);
    }

    [Fact]
    public void Planting_levels_every_standing_sakura_and_three_plants_are_3_2_1()
    {
        var ledger = Fresh();
        PlantN(ledger, 3);
        Assert.Equal(new[] { 3, 2, 1 }, ledger.Standing.Select(s => s.Level));
    }

    [Fact]
    public void Planting_into_a_full_shrine_levels_the_three_and_adds_none()
    {
        var ledger = Fresh();
        PlantN(ledger, 3);
        Assert.False(ledger.Plant(YaeLaw.PlantLevel, YaeLaw.LevelCap));
        Assert.Equal(3, ledger.Count);
        Assert.Equal(new[] { 3, 3, 2 }, ledger.Standing.Select(s => s.Level));
        PlantN(ledger, 1);
        Assert.Equal(new[] { 3, 3, 3 }, ledger.Standing.Select(s => s.Level));
    }

    [Fact]
    public void A_strike_is_two_plus_level_so_a_mature_shrine_is_fifteen()
    {
        Assert.Equal(3, YaeShrineLedger.StrikeDamage(1, 0, false, 0));
        Assert.Equal(5, YaeShrineLedger.StrikeDamage(3, 0, false, 0));
        Assert.Equal(15, 3 * YaeShrineLedger.StrikeDamage(3, 0, false, 0));
    }

    [Fact]
    public void Sakura_grove_adds_to_every_strike_and_edict_only_when_it_reacts()
    {
        Assert.Equal(4, YaeShrineLedger.StrikeDamage(1, 1, false, 4));
        Assert.Equal(8, YaeShrineLedger.StrikeDamage(1, 1, true, 4));
    }

    [Fact]
    public void A_sakura_planted_on_turn_n_strikes_n_n1_n2_and_is_gone_on_n3()
    {
        var ledger = Fresh();
        PlantN(ledger, 1);
        var strikes = 0;
        for (var turn = 0; turn < 4; turn++)
        {
            strikes += ledger.Count;          // the end-of-turn strikes
            ledger.TickAndWither();           // then the timers tick
        }
        Assert.Equal(3, strikes);
        Assert.Equal(0, ledger.Count);
    }

    [Fact]
    public void The_oldest_withers_first()
    {
        var ledger = Fresh();
        PlantN(ledger, 1);
        ledger.TickAndWither();
        PlantN(ledger, 1);
        ledger.TickAndWither();
        Assert.Equal(1, ledger.TickAndWither());
        var survivor = Assert.Single(ledger.Standing);
        Assert.Equal(2, survivor.Seq);
    }

    [Fact]
    public void Tenko_resets_every_timer_to_three_and_keeps_the_board()
    {
        var ledger = Fresh();
        PlantN(ledger, 2);
        ledger.TickAndWither();
        ledger.TickAndWither();
        Assert.All(ledger.Standing, s => Assert.Equal(1, s.TurnsLeft));
        ledger.Refresh();
        Assert.Equal(2, ledger.Count);
        Assert.All(ledger.Standing, s => Assert.Equal(3, s.TurnsLeft));
    }

    [Fact]
    public void Tenko_strikes_every_sakura_oldest_first_then_refreshes()
    {
        // The door's order, read off its IL: the strikes, then the refresh.
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Tenko))!).ToList();
        var strike = calls.FindIndex(c => c.Contains(nameof(YaeShrine.StrikeAll)));
        var refresh = calls.FindIndex(c => c.Contains(nameof(YaeShrineLedger.Refresh)));
        Assert.True(strike >= 0 && refresh > strike, string.Join(", ", calls));
    }

    [Fact]
    public void The_turn_end_strikes_then_ticks()
    {
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.TurnEnd))!).ToList();
        var strike = calls.FindIndex(c => c.Contains(nameof(YaeShrine.StrikeAll)));
        var tick = calls.FindIndex(c => c.Contains(nameof(YaeShrineLedger.TickAndWither)));
        Assert.True(strike >= 0 && tick > strike, string.Join(", ", calls));
    }

    [Fact]
    public void A_strike_is_a_pets_hit_through_the_dealer_free_door()
    {
        // "Her Strength and Weak do not apply; the enemy's Vulnerable and
        // Block do; it applies Electro": ElementalHit.DealWithoutDealerMods.
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Strike))!).ToList();
        Assert.Contains(calls, c => c.Contains("DealWithoutDealerMods"));
        Assert.DoesNotContain(calls, c => c.Contains("DamageCmd.Attack"));
    }

    [Fact]
    public void Each_sakura_lasts_one_more_turn_adds_a_strike_to_every_timer()
    {
        var ledger = Fresh();
        PlantN(ledger, 2);
        ledger.Extend(1);
        Assert.All(ledger.Standing, s => Assert.Equal(4, s.TurnsLeft));
    }

    [Fact]
    public void Each_sakura_gains_a_level_is_capped()
    {
        var ledger = Fresh();
        PlantN(ledger, 3);
        ledger.LevelUp(1, YaeLaw.LevelCap);
        Assert.Equal(new[] { 3, 3, 2 }, ledger.Standing.Select(s => s.Level));
    }

    [Fact]
    public void Foxs_mooncall_plants_at_two_and_reaches_four()
    {
        var ledger = Fresh();
        PlantN(ledger, 3, YaeLaw.MooncallPlantLevel, YaeLaw.MooncallLevelCap);
        Assert.Equal(new[] { 4, 3, 2 }, ledger.Standing.Select(s => s.Level));
        PlantN(ledger, 2, YaeLaw.MooncallPlantLevel, YaeLaw.MooncallLevelCap);
        Assert.Equal(new[] { 4, 4, 4 }, ledger.Standing.Select(s => s.Level));
        Assert.Equal(18, 3 * YaeShrineLedger.StrikeDamage(4, 0, false, 0));
    }

    [Fact]
    public void Editor_in_chief_strikes_with_the_highest_level_oldest_on_a_tie()
    {
        var ledger = Fresh();
        PlantN(ledger, 3);
        PlantN(ledger, 1);                    // 3 / 3 / 2
        Assert.Equal(1, ledger.Highest()!.Seq);
        Assert.Null(YaeShrineLedger.For(Seat.Klee().Creature).Highest());
    }

    [Fact]
    public void The_lure_aims_the_strikes_while_its_enemy_lives()
    {
        // Aim reads the Lure first and falls back to a random living enemy.
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(
            "Aim", HeadlessGame.All)!).ToList();
        Assert.Contains(calls, c => c.Contains("get_Lure"));
        Assert.Contains(calls, c => c.Contains("CombatTargets"));
    }

    [Fact]
    public void The_badges_follow_the_count_oldest_first()
    {
        Assert.Empty(SakuraBadge.Wanted(0));
        Assert.Equal(new[] { typeof(SakuraFirstPower), typeof(SakuraSecondPower) },
                     SakuraBadge.Wanted(2));
        Assert.Equal(3, SakuraBadge.Wanted(5).Count);
    }

    // ---- Edit and Annotations (sec.2) ----------------------------------------

    [Fact]
    public void An_edit_reaches_any_card_but_itself_a_status_or_a_curse()
    {
        var editor = new ProtoYmProofread();
        Assert.False(YaeEditing.Editable(editor, editor));
        Assert.True(YaeEditing.Editable(new ProtoYmKitsuneFlash(), editor));
        Assert.False(YaeEditing.Editable(new Dazed(), editor));
        Assert.False(YaeEditing.Editable(new Regret(), editor));
    }

    [Fact]
    public void The_five_annotations_and_their_rules()
    {
        Assert.Equal(new[] { "Red Ink", "Footnote", "Deadline Extension",
                             "Fox Fire", "Sakura Seal" },
                     YaeModalOptions.Order.Select(YaeAnnotationText.Name));
        Assert.Contains("3 more damage", YaeAnnotationText.Rule(YaeAnnotation.RedInk));
        Assert.Contains("draw 1 card", YaeAnnotationText.Rule(YaeAnnotation.Footnote));
        Assert.Contains("Retain", YaeAnnotationText.Rule(YaeAnnotation.DeadlineExtension));
        Assert.Contains("4 [gold]Electro[/gold]", YaeAnnotationText.Rule(YaeAnnotation.FoxFire));
        Assert.Contains("plant a [gold]Sakura[/gold]", YaeAnnotationText.Rule(YaeAnnotation.SakuraSeal));
    }

    [Fact]
    public void The_annotation_members_follow_the_sheets_order()
    {
        Assert.Equal(1, (int)YaeAnnotation.RedInk);
        Assert.Equal(2, (int)YaeAnnotation.Footnote);
        Assert.Equal(3, (int)YaeAnnotation.DeadlineExtension);
        Assert.Equal(4, (int)YaeAnnotation.FoxFire);
        Assert.Equal(5, (int)YaeAnnotation.SakuraSeal);
    }

    [Fact]
    public void A_saved_draft_reads_back_and_junk_reads_as_none()
    {
        Assert.Equal(YaeAnnotation.SakuraSeal, YaeEditing.ParseDraft("SakuraSeal"));
        Assert.Equal(YaeAnnotation.RedInk, YaeEditing.ParseDraft("RedInk"));
        Assert.Equal(YaeAnnotation.None, YaeEditing.ParseDraft(null));
        Assert.Equal(YaeAnnotation.None, YaeEditing.ParseDraft("Purple"));
    }

    [Fact]
    public void Red_ink_is_a_powered_hit_rider_and_a_block_rider()
    {
        var red = Uninit<RedInkAnnotation>();
        Assert.Equal(3m, red.EnchantDamageAdditive(6m,
            MegaCrit.Sts2.Core.ValueProps.ValueProp.Move));
        Assert.Equal(0m, red.EnchantDamageAdditive(6m,
            MegaCrit.Sts2.Core.ValueProps.ValueProp.Unpowered));
        Assert.Equal(3m, red.EnchantBlockAdditive(5m));
    }

    [Fact]
    public void Riders_resolve_after_the_cards_own_effects()
    {
        // The engine runs an Enchantment's OnPlay after the card's own
        // (CardModel.OnPlayWrapper); the three riders live there.
        foreach (var t in new[] { typeof(FootnoteAnnotation), typeof(FoxFireAnnotation),
                                  typeof(SakuraSealAnnotation) })
        {
            Assert.Equal(t, t.GetMethod("OnPlay")!.DeclaringType);
        }
        var seal = Il.CallSequence(typeof(SakuraSealAnnotation).GetMethod("OnPlay")!).ToList();
        Assert.Contains(seal, c => c.Contains("YaeShrine.Plant"));
    }

    [Fact]
    public void An_edit_overwrites_and_records_the_draft_on_the_deck_card()
    {
        var calls = Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.Annotate))!).ToList();
        var clear = calls.FindIndex(c => c.Contains(nameof(YaeEditing.Clear)));
        var enchant = calls.FindIndex(c => c.Contains("CardCmd.Enchant"));
        var draft = calls.FindIndex(c => c.Contains(nameof(YaeEditing.RecordDraft)));
        Assert.True(clear >= 0 && enchant > clear && draft > enchant,
                    string.Join(", ", calls));
        Assert.Contains(calls, c => c.Contains("get_DeckVersion"));
    }

    [Fact]
    public void Publish_writes_the_deck_card_which_the_run_save_keeps()
    {
        var calls = Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.PublishFromHand))!).ToList();
        Assert.Contains(calls, c => c.Contains("get_DeckVersion"));
        Assert.Contains(calls, c => c.Contains(nameof(YaeEditing.PublishToDeck)));
    }

    // ---- the relic (sec.3) ---------------------------------------------------

    [Fact]
    public void Meditations_adds_publish_to_the_rest_site_and_upgrades_to_enlightened_blessing()
    {
        Assert.Equal(typeof(MeditationsOfAYako),
                     typeof(MeditationsOfAYako).GetMethod("TryModifyRestSiteOptions")!.DeclaringType);
        Assert.False(Uninit<MeditationsOfAYako>().PublishKeepsTheSite);
        Assert.True(Uninit<EnlightenedBlessing>().PublishKeepsTheSite);
        Assert.True(typeof(MeditationsOfAYako).IsAssignableFrom(typeof(EnlightenedBlessing)));
    }

    [Fact]
    public void The_rest_site_publish_reads_the_draft()
    {
        var calls = Il.CallSequence(typeof(PublishRestSiteOption).GetMethod("OnSelect")!).ToList();
        Assert.Contains(calls, c => c.Contains("FromDeckGeneric"));
        Assert.Contains(calls, c => c.Contains(nameof(YaeEditing.Draft))
                                    || c.Contains(nameof(YaeEditing.Publishable)));
    }

    // ---- the companion and the keywords (picks 5, 6) -------------------------

    [Fact]
    public void Her_universal_companion_is_hidden_from_her_alone()
    {
        var card = new ProtoMiYaeSesshouSakura();
        Assert.True(CompanionPool.IsHiddenFrom(card, "yae"));
        Assert.False(CompanionPool.IsHiddenFrom(card, "klee"));
        Assert.False(CompanionPool.IsHiddenFrom(new ProtoYmKitsuneFlash(), "yae"));
    }

    [Fact]
    public void Her_sakura_tip_is_her_shrines_and_the_companions_stays_its_own()
    {
        Assert.Contains("Tenko", ArmKeywordTips.YaeSakuraTip);
        Assert.Contains("Level", ArmKeywordTips.YaeSakuraTip);
        foreach (var name in YaeModalOptions.Order.Select(YaeAnnotationText.Name))
        {
            Assert.Contains(name, ArmKeywordTips.YaeEditTip);
        }
    }
}
