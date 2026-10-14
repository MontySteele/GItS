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
        Assert.Equal(1, YaeLaw.OfferingPerStrike);
        Assert.Equal(1, YaeLaw.RoyaltiesPayout);
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
    public void Sakura_grove_adds_to_every_strike_and_edict_only_when_it_applies()
    {
        Assert.Equal(4, YaeShrineLedger.StrikeDamage(1, 1, false, 4));
        Assert.Equal(8, YaeShrineLedger.StrikeDamage(1, 1, true, 4));
        // Edict works solo (design axes sec.4): Weak, or an aura it reacts with.
        Assert.True(YaeShrineLedger.EdictApplies(weak: true, reacts: false));
        Assert.True(YaeShrineLedger.EdictApplies(weak: false, reacts: true));
        Assert.False(YaeShrineLedger.EdictApplies(weak: false, reacts: false));
    }

    // ---- the Rites (design axes, ruled 2026-10-14) ---------------------------

    [Fact]
    public void Every_combat_opens_in_thunder()
    {
        Assert.Equal(YaeRite.Thunder, Fresh().Rite);
        Assert.Equal(0, (int)YaeRite.Thunder);
    }

    [Fact]
    public void Each_rites_strike_size()
    {
        // Thunder and Warding 2 + Level; Wildfire Level; Offering 1 card.
        Assert.Equal(5, YaeShrineLedger.StrikeSize(YaeRite.Thunder, 3, 0, 0, YaeAnnotation.None));
        Assert.Equal(5, YaeShrineLedger.StrikeSize(YaeRite.Warding, 3, 0, 0, YaeAnnotation.None));
        Assert.Equal(3, YaeShrineLedger.StrikeSize(YaeRite.Wildfire, 3, 0, 0, YaeAnnotation.None));
        Assert.Equal(1, YaeShrineLedger.StrikeSize(YaeRite.Offering, 3, 0, 0, YaeAnnotation.None));
    }

    [Fact]
    public void Grove_and_mikage_size_three_rites_and_not_offering()
    {
        Assert.Equal(3 + 2 + 1, YaeShrineLedger.StrikeSize(YaeRite.Thunder, 1, 2, 1, YaeAnnotation.None));
        Assert.Equal(3 + 2 + 1, YaeShrineLedger.StrikeSize(YaeRite.Warding, 1, 2, 1, YaeAnnotation.None));
        Assert.Equal(1 + 2 + 1, YaeShrineLedger.StrikeSize(YaeRite.Wildfire, 1, 2, 1, YaeAnnotation.None));
        Assert.Equal(1, YaeShrineLedger.StrikeSize(YaeRite.Offering, 1, 2, 1, YaeAnnotation.None));
    }

    [Fact]
    public void Each_rite_does_its_own_job_in_the_strike()
    {
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Strike))!).ToList();
        Assert.Contains(calls, c => c.Contains("CreatureCmd.GainBlock"));      // Warding
        Assert.Contains(calls, c => c.Contains("set_PendingDraw"));            // Offering
        Assert.Contains(calls, c => c.Contains("HittableEnemies"));            // Wildfire
        Assert.Contains(calls, c => c.Contains("SakuraChannelingPower"));      // the bend
        Assert.Contains(calls, c => c.Contains(nameof(YaeShrine.FoxFire)));    // Fox Fire
    }

    [Fact]
    public void Offering_and_fallen_petals_pay_at_her_next_turn_start()
    {
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.TurnStart))!).ToList();
        Assert.Contains(calls, c => c.Contains("TakePending"));
        Assert.Contains(calls, c => c.Contains("FallenPetalsPower"));
        Assert.Contains(calls, c => c.Contains("FallenPetalsPlusPower"));
        Assert.Contains(calls, c => c.Contains("PlayerCmd.GainEnergy"));
        Assert.Contains(calls, c => c.Contains("CardPileCmd.Draw"));
    }

    [Fact]
    public void A_wither_is_banked_for_fallen_petals()
    {
        var ledger = Fresh();
        PlantN(ledger, 1);
        for (var i = 0; i < 3; i++) ledger.TickAndWither();
        Assert.Equal(0, ledger.Count);
        Assert.Equal(1, ledger.PendingWithers);
    }

    [Fact]
    public void The_rite_badge_follows_the_rite()
    {
        Assert.Equal(typeof(ThunderRitePower), SakuraBadge.RiteBadge(YaeRite.Thunder));
        Assert.Equal(typeof(WardingRitePower), SakuraBadge.RiteBadge(YaeRite.Warding));
        Assert.Equal(typeof(WildfireRitePower), SakuraBadge.RiteBadge(YaeRite.Wildfire));
        Assert.Equal(typeof(OfferingRitePower), SakuraBadge.RiteBadge(YaeRite.Offering));
        Assert.Contains("Block", YaeRiteText.Rule(YaeRite.Warding));
        Assert.Contains("ALL", YaeRiteText.Rule(YaeRite.Wildfire));
    }

    [Fact]
    public void Rite_cards_set_the_rite()
    {
        Assert.Contains(Il.CallSequence(typeof(ProtoYmShrineMaidensGuard).GetMethod(
            "OnPlay", HeadlessGame.All)!), c => c.Contains("YaeCards.Rite"));
        Assert.Contains(Il.CallSequence(typeof(ProtoYmFoxfireSweep).GetMethod(
            "OnPlay", HeadlessGame.All)!), c => c.Contains("YaeCards.Rite"));
    }

    // ---- Sakura Annotations (ruled 2026-10-14) -------------------------------

    [Fact]
    public void Red_ink_makes_a_sakuras_strike_three_bigger_but_not_in_offering()
    {
        // Claude, 2026-10-14: Red Ink skips Offering, like Sakura Grove.
        Assert.Equal(YaeShrineLedger.StrikeSize(YaeRite.Offering, 2, 0, 0, YaeAnnotation.None),
                     YaeShrineLedger.StrikeSize(YaeRite.Offering, 2, 0, 0, YaeAnnotation.RedInk));
        foreach (var rite in new[] { YaeRite.Thunder, YaeRite.Warding, YaeRite.Wildfire })
        {
            Assert.Equal(
                YaeShrineLedger.StrikeSize(rite, 2, 0, 0, YaeAnnotation.None) + YaeLaw.RedInkAmount,
                YaeShrineLedger.StrikeSize(rite, 2, 0, 0, YaeAnnotation.RedInk));
        }
        Assert.Equal(YaeShrineLedger.StrikeSize(YaeRite.Thunder, 2, 0, 0, YaeAnnotation.None),
                     YaeShrineLedger.StrikeSize(YaeRite.Thunder, 2, 0, 0, YaeAnnotation.FoxFire));
    }

    [Fact]
    public void Sakura_edits_reach_newest_oldest_and_every_and_replace()
    {
        var ledger = Fresh();
        PlantN(ledger, 3);
        Assert.Equal(1, ledger.EditSakura(YaeSakuraEnd.Newest, 1, YaeAnnotation.FoxFire));
        Assert.Equal(new[] { YaeAnnotation.None, YaeAnnotation.None, YaeAnnotation.FoxFire },
                     ledger.Standing.Select(s => s.Annotation));
        ledger.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.DeadlineExtension);
        Assert.Equal(YaeAnnotation.DeadlineExtension, ledger.Standing[0].Annotation);
        Assert.Equal(3, ledger.EditSakura(YaeSakuraEnd.Every, 1, YaeAnnotation.RedInk));
        Assert.All(ledger.Standing, s => Assert.Equal(YaeAnnotation.RedInk, s.Annotation));
        // Only three Annotations have a Sakura reading.
        Assert.Equal(0, ledger.EditSakura(YaeSakuraEnd.Every, 1, YaeAnnotation.Footnote));
        Assert.All(ledger.Standing, s => Assert.Equal(YaeAnnotation.RedInk, s.Annotation));
    }

    [Fact]
    public void A_deadline_extension_sakura_never_withers()
    {
        var ledger = Fresh();
        PlantN(ledger, 2);
        ledger.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.DeadlineExtension);
        for (var i = 0; i < 10; i++) ledger.TickAndWither();
        var kept = Assert.Single(ledger.Standing);
        Assert.Equal(YaeAnnotation.DeadlineExtension, kept.Annotation);
        Assert.Equal(YaeLaw.SakuraTurns, kept.TurnsLeft);
    }

    [Fact]
    public void An_unannotated_sakura_carries_none()
    {
        var ledger = Fresh();
        PlantN(ledger, 1);
        Assert.Equal(YaeAnnotation.None, ledger.Standing[0].Annotation);
    }

    // ---- batch two -----------------------------------------------------------

    [Fact]
    public void Grafted_branch_plants_at_its_level_never_below_the_plant_level()
    {
        var ledger = Fresh();
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, YaeLaw.LevelCap, 2));
        Assert.Equal(2, ledger.Standing[0].Level);
        Assert.True(ledger.Plant(YaeLaw.MooncallPlantLevel, YaeLaw.LevelCap, 1));
        Assert.Equal(2, ledger.Standing[1].Level);
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, YaeLaw.LevelCap, 9));
        Assert.Equal(YaeLaw.LevelCap, ledger.Standing[2].Level);
    }

    [Fact]
    public void Kitsune_pounce_strikes_only_a_weak_enemy()
    {
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.StrikeIfWeak))!).ToList();
        Assert.Contains(calls, c => c.Contains(nameof(YaeShrine.IsWeak)));
        Assert.Contains(calls, c => c.Contains(nameof(YaeShrineLedger.Highest)));
    }

    [Fact]
    public void Mikage_thunder_tenkos_then_applies_its_power()
    {
        var calls = Il.CallSequence(typeof(ProtoYmMikageThunder).GetMethod(
            "OnPlay", HeadlessGame.All)!).ToList();
        var tenko = calls.FindIndex(c => c.Contains("YaeCards.Tenko"));
        var power = calls.FindIndex(c => c.Contains("MikageThunderPower"));
        Assert.True(tenko >= 0 && power > tenko, string.Join(", ", calls));
    }

    [Fact]
    public void Royalties_gains_energy_after_the_cards_own_effects()
    {
        Assert.Equal(typeof(RoyaltiesAnnotation),
                     typeof(RoyaltiesAnnotation).GetMethod("OnPlay")!.DeclaringType);
        Assert.Contains(Il.CallSequence(typeof(RoyaltiesAnnotation).GetMethod("OnPlay")!),
                        c => c.Contains("PlayerCmd.GainEnergy"));
        Assert.Equal(6, (int)YaeAnnotation.Royalties);
        Assert.Equal(YaeAnnotation.Royalties, YaeEditing.ParseDraft("Royalties"));
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
        // Block do; it applies Electro": ElementalHit.DealWithoutDealerMods,
        // in the one hit every damage strike goes through (the Rites,
        // 2026-10-14).
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(
            "Hit", HeadlessGame.All)!).ToList();
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
        Assert.Equal(6, (int)YaeAnnotation.Royalties);
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
