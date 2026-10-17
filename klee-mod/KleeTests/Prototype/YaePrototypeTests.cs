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
                               int plantLevel = YaeLaw.PlantLevel)
    {
        for (var i = 0; i < n; i++) ledger.Plant(plantLevel);
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
        Assert.Equal(global::KleeMod.Elements.Element.Electro, new ProtoYmSlyStrike().Element);
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
        Assert.Equal(1, YaeLaw.FoxfireBase);     // review r3
        Assert.Equal(2, YaeLaw.KitsuneBase);     // review r3
        Assert.Equal(1, YaeLaw.PlantLevel);
        Assert.Equal(3, YaeLaw.RedInkAmount);
        Assert.Equal(4, YaeLaw.FoxFireDamage);
        Assert.Equal(1, YaeLaw.RoyaltiesPayout);
    }
    [Fact]
    public void A_plant_is_level_one_with_three_strikes()
    {
        var ledger = Fresh();
        Assert.True(ledger.Plant(YaeLaw.PlantLevel));
        var s = Assert.Single(ledger.Standing);
        Assert.Equal(1, s.Level);
        Assert.Equal(3, s.TurnsLeft);
    }

    [Fact]
    public void Planting_no_longer_levels_the_others_so_three_plants_are_1_1_1()
    {
        // Shrine r2 (ruled 2026-10-14).
        var ledger = Fresh();
        PlantN(ledger, 3);
        Assert.Equal(new[] { 1, 1, 1 }, ledger.Standing.Select(s => s.Level));
    }

    [Fact]
    public void Planting_into_a_full_shrine_refreshes_and_levels_only_the_oldest()
    {
        var ledger = Fresh();
        PlantN(ledger, 3);
        var oldest = ledger.Standing[0];
        ledger.TickAndWither();
        Assert.False(ledger.Plant(YaeLaw.PlantLevel));
        Assert.Equal(3, ledger.Count);
        Assert.Same(oldest, ledger.Standing[0]);
        Assert.Equal(new[] { 2, 1, 1 }, ledger.Standing.Select(s => s.Level));
        Assert.Equal(new[] { 3, 2, 2 }, ledger.Standing.Select(s => s.TurnsLeft));
        PlantN(ledger, 1);                    // no cap (review r1, pick 2)
        Assert.Equal(new[] { 3, 1, 1 }, ledger.Standing.Select(s => s.Level));
    }

    [Fact]
    public void A_two_plant_with_two_standing_plants_one_then_feeds_the_oldest()
    {
        // Twin Sakura with 2 standing: the first plants, the second
        // refreshes and levels the then-oldest.
        var ledger = Fresh();
        PlantN(ledger, 2);
        ledger.TickAndWither();
        PlantN(ledger, 2);
        Assert.Equal(new[] { 2, 1, 1 }, ledger.Standing.Select(s => s.Level));
        Assert.Equal(new[] { 3, 2, 3 }, ledger.Standing.Select(s => s.TurnsLeft));
    }

    [Fact]
    public void A_strike_is_two_plus_level_so_a_mature_shrine_is_fifteen()
    {
        Assert.Equal(3, YaeShrineLedger.StrikeDamage(1, false, 0));
        Assert.Equal(5, YaeShrineLedger.StrikeDamage(3, false, 0));
        Assert.Equal(15, 3 * YaeShrineLedger.StrikeDamage(3, false, 0));
    }

    [Fact]
    public void Edict_adds_only_when_it_applies()
    {
        Assert.Equal(3, YaeShrineLedger.StrikeDamage(1, false, 4));
        Assert.Equal(7, YaeShrineLedger.StrikeDamage(1, true, 4));
        // Edict works solo (design axes sec.4): Weak, or an aura it reacts with.
        Assert.True(YaeShrineLedger.EdictApplies(weak: true, reacts: false));
        Assert.True(YaeShrineLedger.EdictApplies(weak: false, reacts: true));
        Assert.False(YaeShrineLedger.EdictApplies(weak: false, reacts: false));
    }

    // ---- the Tenko kinds (shrine r2, ruled 2026-10-14) -----------------------

    [Fact]
    public void The_shrine_has_no_rite_and_no_typed_tenko()
    {
        Assert.Null(typeof(YaeShrineLedger).GetProperty("Rite"));
        Assert.Null(typeof(YaeCards).GetMethod("Rite"));
        // Review r3: the typed Tenko is gone; Tenko takes no kind.
        Assert.Null(typeof(SakuraBadge).Assembly.GetType("KleeMod.Powers.YaeTenkoKind"));
        Assert.Single(typeof(YaeCards).GetMethods(), m => m.Name == nameof(YaeCards.Tenko));
        Assert.Equal(0, (int)YaeSakuraKind.Thunder);
    }
    [Fact]
    public void Each_sakura_kinds_action_size()
    {
        // Review r3: Sakura 2 + Level, Foxfire 1 + Level, Kitsune 2 + Level.
        Assert.Equal(5, YaeShrineLedger.ActSize(YaeSakuraKind.Thunder, 3, YaeAnnotation.None));
        Assert.Equal(4, YaeShrineLedger.ActSize(YaeSakuraKind.Foxfire, 3, YaeAnnotation.None));
        Assert.Equal(5, YaeShrineLedger.ActSize(YaeSakuraKind.Kitsune, 3, YaeAnnotation.None));
        Assert.True(YaeShrineLedger.DealsDamage(YaeSakuraKind.Foxfire));
        Assert.False(YaeShrineLedger.DealsDamage(YaeSakuraKind.Kitsune));
    }
    [Fact]
    public void Each_kind_does_its_own_job_when_it_acts()
    {
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Act))!).ToList();
        Assert.Contains(calls, c => c.Contains("YaeShrine.Hit"));               // Sakura, Foxfire
        Assert.Contains(calls, c => c.Contains("CreatureCmd.GainBlock"));      // Kitsune
        Assert.Contains(calls, c => c.Contains("HittableEnemies"));            // Foxfire: ALL
        Assert.Contains(calls, c => c.Contains(nameof(YaeShrine.FoxFire)));    // Fox Fire
        Assert.DoesNotContain(calls, c => c.Contains("SakuraChannelingPower"));
        Assert.DoesNotContain(calls, c => c.Contains("PendingDraw"));
    }
    [Fact]
    public void Serialization_pays_per_edit_not_per_annotated_play()
    {
        // Yae review r6, item 1 (was per Annotated card played, shrine r2).
        Assert.DoesNotContain(Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.AfterCardPlayed))!),
                              c => c.Contains("SerializationPower.Pay"));
        Assert.Contains(Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.Edit))!),
                        c => c.Contains("SerializationPower.Pay"));
        Assert.Contains(Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.EditAll))!),
                        c => c.Contains("SerializationPower.Pay"));
        Assert.Contains(Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.EditSakura))!),
                        c => c.Contains("SerializationPower.Pay"));
    }

    [Fact]
    public void Nothing_is_banked_for_her_next_turn_start_any_more()
    {
        // Review r3: Offering left with the typed Tenko and Fallen Petals is
        // an active Skill; the turn start brings Serial Novel's card.
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.TurnStart))!).ToList();
        Assert.DoesNotContain(calls, c => c.Contains("TakePending"));
        Assert.DoesNotContain(calls, c => c.Contains("FallenPetals"));
        Assert.Contains(calls, c => c.Contains("SerialNovelPower"));
        Assert.Contains(calls, c => c.Contains(nameof(YaeEditing.RecallRandomAnnotated)));
        Assert.Null(typeof(SakuraBadge).Assembly.GetType("KleeMod.Powers.FallenPetalsPower"));
    }
    [Fact]
    public void The_rite_badges_are_gone()
    {
        Assert.Null(typeof(SakuraBadge).Assembly.GetType("KleeMod.Powers.WardingRitePower"));
        Assert.Null(typeof(SakuraBadge).Assembly.GetType("KleeMod.Powers.YaeRiteBadgePower"));
        Assert.Null(typeof(SakuraBadge).GetMethod("RiteBadge"));
    }

    [Fact]
    public void The_four_changed_cards_do_their_new_jobs()
    {
        // Review r3's table: the Guard and the Sweep plant their kind,
        // Kitsune Guile Tenkos. Manuscript Pile Edits (Yae review r6, item
        // 2; it extended).
        Assert.Contains(Il.CallSequence(typeof(ProtoYmShrineMaidensGuard).GetMethod(
            "OnPlay", HeadlessGame.All)!), c => c.Contains("YaeCards.Plant"));
        Assert.Contains(Il.CallSequence(typeof(ProtoYmFoxfireSweep).GetMethod(
            "OnPlay", HeadlessGame.All)!), c => c.Contains("YaeCards.Plant"));
        Assert.Contains(Il.CallSequence(typeof(ProtoYmKitsuneGuile).GetMethod(
            "OnPlay", HeadlessGame.All)!), c => c.Contains("YaeCards.Tenko"));
        Assert.Contains(Il.CallSequence(typeof(ProtoYmManuscriptPile).GetMethod(
            "OnPlay", HeadlessGame.All)!), c => c.Contains("YaeCards.Edit"));
        Assert.DoesNotContain(Il.CallSequence(typeof(ProtoYmManuscriptPile).GetMethod(
            "OnPlay", HeadlessGame.All)!), c => c.Contains("YaeCards.Tenko"));
    }
    // ---- Sakura Annotations (ruled 2026-10-14) -------------------------------

    [Fact]
    public void Red_ink_makes_any_kinds_action_three_bigger()
    {
        foreach (var kind in new[] { YaeSakuraKind.Thunder, YaeSakuraKind.Foxfire, YaeSakuraKind.Kitsune })
        {
            Assert.Equal(
                YaeShrineLedger.ActSize(kind, 2, YaeAnnotation.None) + YaeLaw.RedInkAmount,
                YaeShrineLedger.ActSize(kind, 2, YaeAnnotation.RedInk));
        }
        Assert.Equal(YaeShrineLedger.ActSize(YaeSakuraKind.Thunder, 2, YaeAnnotation.None),
                     YaeShrineLedger.ActSize(YaeSakuraKind.Thunder, 2, YaeAnnotation.FoxFire));
    }
    [Fact]
    public void Sakura_edits_reach_newest_oldest_and_every_and_add_up()
    {
        // The pool to 78, pick 2 (a): an Edit joins what a Sakura carries.
        var ledger = Fresh();
        PlantN(ledger, 3);
        Assert.Equal(1, ledger.EditSakura(YaeSakuraEnd.Newest, 1, YaeAnnotation.FoxFire));
        Assert.Equal(new[] { 0, 0, 1 }, ledger.Standing.Select(s => s.Annotations.Count));
        Assert.True(ledger.Standing[2].Has(YaeAnnotation.FoxFire));
        ledger.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.DeadlineExtension);
        Assert.Equal(new[] { YaeAnnotation.DeadlineExtension }, ledger.Standing[0].Annotations);
        Assert.Equal(3, ledger.EditSakura(YaeSakuraEnd.Every, 1, YaeAnnotation.RedInk));
        Assert.All(ledger.Standing, s => Assert.True(s.Has(YaeAnnotation.RedInk)));
        Assert.Equal(new[] { YaeAnnotation.DeadlineExtension, YaeAnnotation.RedInk },
                     ledger.Standing[0].Annotations);
        // Only three Annotations have a Sakura reading.
        Assert.Equal(0, ledger.EditSakura(YaeSakuraEnd.Every, 1, YaeAnnotation.Footnote));
        Assert.All(ledger.Standing, s => Assert.DoesNotContain(YaeAnnotation.Footnote, s.Annotations));
    }

    [Fact]
    public void A_deadline_extension_sakura_never_withers()
    {
        var ledger = Fresh();
        PlantN(ledger, 2);
        ledger.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.DeadlineExtension);
        for (var i = 0; i < 10; i++) ledger.TickAndWither();
        var kept = Assert.Single(ledger.Standing);
        Assert.Equal(new[] { YaeAnnotation.DeadlineExtension }, kept.Annotations);
        Assert.Equal(YaeLaw.SakuraTurns, kept.TurnsLeft);
    }

    [Fact]
    public void An_unannotated_sakura_carries_none()
    {
        var ledger = Fresh();
        PlantN(ledger, 1);
        Assert.Empty(ledger.Standing[0].Annotations);
    }

    // ---- batch two -----------------------------------------------------------

    [Fact]
    public void Grafted_branch_plants_at_its_level_never_below_the_plant_level()
    {
        var ledger = Fresh();
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, 2));
        Assert.Equal(2, ledger.Standing[0].Level);
        Assert.True(ledger.Plant(YaeLaw.PlantLevel + 1, 1));
        Assert.Equal(2, ledger.Standing[1].Level);
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, 9));
        Assert.Equal(9, ledger.Standing[2].Level);   // no cap
    }

    [Fact]
    public void Kitsune_pounce_strikes_only_a_weak_enemy()
    {
        // The pool to 78: the strike itself is StrikeTarget's (Sacred
        // Spark's "A Sakura strikes it"), behind the Weak gate.
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.StrikeIfWeak))!).ToList();
        Assert.Contains(calls, c => c.Contains(nameof(YaeShrine.IsWeak)));
        Assert.Contains(calls, c => c.Contains(nameof(YaeShrine.StrikeTarget)));
        Assert.Contains(Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.StrikeTarget))!),
                        c => c.Contains(nameof(YaeShrineLedger.Highest)));
    }

    // ---- Reprint ([USER], 2026-10-14, on Proofread: "Let's bump it to
    // 'Play it twice.'") ----------------------------------------------------

    [Fact]
    public void Proofread_edits_reprint_at_its_old_cost()
    {
        var proofread = new ProtoYmProofread();
        Assert.Equal(1, proofread.EnergyCost.Canonical);
        Assert.Contains(Il.CallSequence(typeof(ProtoYmProofread).GetMethod(
            "OnPlay", HeadlessGame.All)!), c => c.Contains("YaeCards.Edit"));
        Assert.Equal(YaeAnnotation.Reprint, YaeEditing.ParseDraft("Reprint"));
        // Yae review r6, item 4: each Reprint adds one play.
        Assert.Equal("The first time this card is played each combat, play it "
                     + "once more for each Reprint.",
                     YaeAnnotationText.Rule(YaeAnnotation.Reprint));
        Assert.Contains(YaeAnnotation.Reprint, YaeAnnotationText.All);
        // Reborn as Guuji Yae's faces are unchanged.
        Assert.DoesNotContain(YaeAnnotation.Reprint, YaeModalOptions.Order);
    }

    [Fact]
    public void Reprint_is_a_play_count_hook_on_the_masterpiece()
    {
        var t = typeof(YaeMasterpiece);
        Assert.Equal(t, t.GetMethod("EnchantPlayCount")!.DeclaringType);
        Assert.Equal(t, t.GetMethod("AfterCardPlayed")!.DeclaringType);
        Assert.Contains(Il.CallSequence(t.GetMethod("EnchantPlayCount")!),
                        c => c.Contains(nameof(YaeLayers.Replays)));
    }
    [Fact]
    public void A_spent_reprint_reads_spent()
    {
        // Two blind seats (2026-10-14) expected a second replay off a spent
        // Reprint: the Masterpiece's hover says "Reprint: used this combat."
        Assert.True(YaeLayers.ReprintUsed(1, playedOnce: true, armed: 0));
        Assert.False(YaeLayers.ReprintUsed(1, playedOnce: true, armed: 1));
        Assert.False(YaeLayers.ReprintUsed(1, playedOnce: false, armed: 0));
        Assert.False(YaeLayers.ReprintUsed(0, playedOnce: true, armed: 0));
        Assert.Contains(YaeAnnotationText.ReprintUsed,
                        YaeAnnotationText.Summary(new[] { YaeAnnotation.Reprint },
                                                  YaeAnnotation.None, true));
    }
    [Fact]
    public void Reprint_reaches_any_playable_card()
    {
        Assert.True(YaeAnnotationReach.Affects(YaeAnnotation.Reprint, false, false, false));
        Assert.False(YaeAnnotationReach.Affects(YaeAnnotation.Reprint, true, true, true,
                                                playable: false));
        // Red Ink's filter is unchanged by the new argument.
        Assert.False(YaeAnnotationReach.Affects(YaeAnnotation.RedInk, false, false, false));
    }

    [Fact]
    public void Royalties_gains_energy_after_the_cards_own_effects()
    {
        var t = typeof(YaeMasterpiece);
        Assert.Equal(t, t.GetMethod("OnPlay")!.DeclaringType);
        Assert.Contains(Il.CallSequence(t.GetMethod("OnPlay")!),
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
    public void Tenko_never_shortens_a_timer_extended_past_three()
    {
        // Main session, 2026-10-14 (after a GPT design review): each timer
        // becomes max(its turns, 3).
        var ledger = Fresh();
        PlantN(ledger, 1);
        ledger.Extend(3);                         // 6
        ledger.TickAndWither();                   // 5
        PlantN(ledger, 1);                        // 5, 3
        ledger.TickAndWither();                   // 4, 2
        ledger.Refresh();
        Assert.Equal(new[] { 4, 3 }, ledger.Standing.Select(s => s.TurnsLeft).ToArray());
    }

    [Fact]
    public void A_full_shrine_plant_never_shortens_the_oldests_timer()
    {
        var ledger = Fresh();
        PlantN(ledger, 1);
        ledger.Extend(3);                         // the oldest at 6
        PlantN(ledger, 2);                        // 6, 3, 3: full
        Assert.False(ledger.Plant(YaeLaw.PlantLevel));
        Assert.Equal(6, ledger.Standing.First().TurnsLeft);
        ledger.TickAndWither();
        ledger.TickAndWither();                   // 4, 1, 1
        Assert.False(ledger.Plant(YaeLaw.PlantLevel));
        Assert.Equal(4, ledger.Standing.First().TurnsLeft);
    }

    [Fact]
    public void Tenko_strikes_every_sakura_oldest_first_then_refreshes()
    {
        // The door's order, read off its IL: the strikes, then the refresh.
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Tenko))!).ToList();
        var strike = calls.FindIndex(c => c.Contains(nameof(YaeShrine.ActAll)));
        var refresh = calls.FindIndex(c => c.Contains(nameof(YaeShrineLedger.Refresh)));
        Assert.True(strike >= 0 && refresh > strike, string.Join(", ", calls));
    }

    [Fact]
    public void The_turn_end_strikes_then_ticks_and_blooms()
    {
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.TurnEnd))!).ToList();
        var strike = calls.FindIndex(c => c.Contains(nameof(YaeShrine.ActAll)));
        var tick = calls.FindIndex(c => c.Contains(nameof(YaeShrine.TickAndBloom)));
        Assert.True(strike >= 0 && tick > strike, string.Join(", ", calls));
    }

    [Fact]
    public void A_strike_is_a_pets_hit_through_the_dealer_free_door()
    {
        // "Her Strength and Weak do not apply; the enemy's Vulnerable and
        // Block do; it applies Electro": ElementalHit.DealWithoutDealerMods,
        // in the one hit every damage strike goes through (Thunder and
        // Wildfire, shrine r2).
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
    public void Each_sakura_gains_a_level_has_no_cap()
    {
        var ledger = Fresh();
        PlantN(ledger, 3);
        ledger.LevelUp(1);
        ledger.LevelUp(4);
        Assert.Equal(new[] { 6, 6, 6 }, ledger.Standing.Select(s => s.Level));
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
        // Sakura Channeling (2026-10-14): a badge per Sakura up to nine.
        Assert.Equal(5, SakuraBadge.Wanted(5).Count);
        Assert.Equal(typeof(SakuraFifthPower), SakuraBadge.Wanted(5)[4]);
        Assert.Equal(9, SakuraBadge.Wanted(12).Count);
        Assert.Equal(Enumerable.Range(0, 9),
                     SakuraBadge.Slots.Select(t => ((SakuraBadgePower)Activator.CreateInstance(t)!).Slot));
    }

    // ---- Edit and Annotations (sec.2) ----------------------------------------

    [Fact]
    public void An_edit_reaches_any_card_but_itself_a_status_or_a_curse()
    {
        var editor = new ProtoYmProofread();
        Assert.False(YaeEditing.Editable(editor, editor));
        Assert.True(YaeEditing.Editable(new ProtoYmSlyStrike(), editor));
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
        Assert.Equal(7, (int)YaeAnnotation.Reprint);
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
    public void Red_ink_is_a_powered_hit_rider_and_a_block_rider_per_layer()
    {
        var t = typeof(YaeMasterpiece);
        Assert.Equal(t, t.GetMethod("EnchantDamageAdditive")!.DeclaringType);
        Assert.Equal(t, t.GetMethod("EnchantBlockAdditive")!.DeclaringType);
        Assert.Contains(Il.CallSequence(t.GetMethod("EnchantDamageAdditive")!),
                        c => c.Contains("IsPoweredAttack"));
        Assert.Equal(2, YaeLayers.Count(new[] { YaeAnnotation.RedInk, YaeAnnotation.Reprint },
                                        YaeAnnotation.RedInk, YaeAnnotation.RedInk));
    }
    [Fact]
    public void Riders_resolve_after_the_cards_own_effects()
    {
        // The engine runs an Enchantment's OnPlay after the card's own
        // (CardModel.OnPlayWrapper); the Masterpiece's riders live there.
        var calls = Il.CallSequence(typeof(YaeMasterpiece).GetMethod("OnPlay")!).ToList();
        Assert.Contains(calls, c => c.Contains("YaeShrine.Plant"));
        Assert.Contains(calls, c => c.Contains("YaeShrine.FoxFire"));
        Assert.Contains(calls, c => c.Contains("CardPileCmd.Draw"));
    }
    [Fact]
    public void An_edit_fills_the_temporary_slot_and_records_the_draft_on_the_deck_card()
    {
        var calls = Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.Annotate))!).ToList();
        var apply = calls.FindIndex(c => c.Contains(nameof(YaeEditing.Apply)));
        var draft = calls.FindIndex(c => c.Contains(nameof(YaeEditing.RecordDraft)));
        Assert.True(apply >= 0 && draft > apply, string.Join(", ", calls));
        Assert.Contains(calls, c => c.Contains("get_DeckVersion"));
        Assert.Contains(calls, c => c.Contains(nameof(YaeEditing.Stack)));     // the stack kept
        var swap = Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.Apply))!).ToList();
        var clear = swap.FindIndex(c => c.Contains(nameof(YaeEditing.Clear)));
        var enchant = swap.FindIndex(c => c.Contains("CardCmd.Enchant"));
        Assert.True(clear >= 0 && enchant > clear, string.Join(", ", swap));
    }
    [Fact]
    public void Publish_writes_the_deck_card_which_the_run_save_keeps()
    {
        var calls = Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.PublishFromHand))!).ToList();
        Assert.Contains(calls, c => c.Contains("get_DeckVersion"));
        Assert.Contains(calls, c => c.Contains(nameof(YaeEditing.PublishLayer)));
        Assert.Contains(calls, c => c.Contains(nameof(YaeEditing.PublishToDeck)));
        // The stack is a saved property on the one enchantment.
        var prop = typeof(YaeMasterpiece).GetProperty(nameof(YaeMasterpiece.Published))!;
        Assert.NotNull(prop.GetCustomAttributes(typeof(MegaCrit.Sts2.Core.Saves.Runs.SavedPropertyAttribute), false)
                           .SingleOrDefault());
        Assert.Equal(typeof(int[]), prop.PropertyType);
    }
    // ---- the relic (sec.3) ---------------------------------------------------

    // Publish after elites and bosses (ruled 2026-10-14,
    // review/active/yae-design-axes-2026-10-14.md). Sim twin:
    // tier0/tests/test_yae_shrine.py's after-elite pins.

    /// <summary>A stand-in deck card for the pure offer reads: reference
    /// identity only, so two "Strikes" are two cards.</summary>
    private sealed class DeckSlot
    {
        public DeckSlot(string name) => Name = name;

        public string Name { get; }
    }

    [Fact]
    public void The_rest_site_no_longer_offers_publish()
    {
        Assert.NotEqual(typeof(MeditationsOfAYako),
                        typeof(MeditationsOfAYako).GetMethod("TryModifyRestSiteOptions")!.DeclaringType);
        Assert.NotEqual(typeof(MeditationsOfAYako),
                        typeof(MeditationsOfAYako).GetMethod("ShouldDisableRemainingRestSiteOptions")!.DeclaringType);
        Assert.DoesNotContain(typeof(MeditationsOfAYako).Assembly.GetTypes(),
                              t => typeof(MegaCrit.Sts2.Core.Entities.RestSite.RestSiteOption).IsAssignableFrom(t)
                                   && t.Name.Contains("Publish"));
        Assert.True(typeof(MeditationsOfAYako).IsAssignableFrom(typeof(EnlightenedBlessing)));
        Assert.Equal(1, Uninit<MeditationsOfAYako>().PublishCount);
        Assert.Equal(2, Uninit<EnlightenedBlessing>().PublishCount);
    }

    [Fact]
    public void Publish_is_offered_after_an_elite_or_boss_and_never_after_a_normal_fight()
    {
        Assert.True(YaeEditing.OffersPublish(MegaCrit.Sts2.Core.Rooms.RoomType.Elite, true, false));
        Assert.True(YaeEditing.OffersPublish(MegaCrit.Sts2.Core.Rooms.RoomType.Boss, true, false));
        Assert.False(YaeEditing.OffersPublish(MegaCrit.Sts2.Core.Rooms.RoomType.Monster, true, false));
        Assert.False(YaeEditing.OffersPublish(MegaCrit.Sts2.Core.Rooms.RoomType.Event, true, false));
        // No reward screen follows the final boss or a no-reward encounter.
        Assert.False(YaeEditing.OffersPublish(MegaCrit.Sts2.Core.Rooms.RoomType.Boss, true, true));
        Assert.False(YaeEditing.OffersPublish(MegaCrit.Sts2.Core.Rooms.RoomType.Elite, false, false));
    }

    [Fact]
    public void The_relic_adds_the_reward_only_through_the_gate_and_the_offer()
    {
        var calls = Il.CallSequence(typeof(MeditationsOfAYako).GetMethod("TryModifyRewards")!).ToList();
        var gate = calls.FindIndex(c => c.Contains(nameof(YaeEditing.OffersPublish)));
        var offer = calls.FindIndex(c => c.Contains(nameof(YaeEditing.PublishChoices)));
        var add = calls.FindIndex(c => c.Contains(nameof(YaePublishReward)));
        Assert.True(gate >= 0 && offer > gate && add > offer, string.Join(", ", calls));
        // The fight's evidence is taken at the end of every fight.
        Assert.Contains(Il.CallSequence(typeof(MeditationsOfAYako).GetMethod("AfterCombatEnd")!),
                        c => c.Contains(nameof(YaeEditing.SnapshotDrafts)));
        var snap = Il.CallSequence(typeof(YaeEditing).GetMethod(nameof(YaeEditing.SnapshotDrafts))!).ToList();
        Assert.Contains(snap, c => c.Contains("get_AllCards"));
        Assert.Contains(snap, c => c.Contains("get_DeckVersion"));
        Assert.Contains(snap, c => c.Contains(nameof(YaeEditing.RecordDraft)));
    }

    [Fact]
    public void Nothing_is_offered_when_no_card_is_annotated()
    {
        var a = new DeckSlot("Strike");
        var b = new DeckSlot("Defend");
        Assert.Empty(YaeEditing.PublishChoices(new[]
        {
            (a, YaeAnnotation.None, false),
            (b, YaeAnnotation.None, false),
        }));
        Assert.Empty(YaeEditing.PublishChoices(Array.Empty<(DeckSlot, YaeAnnotation, bool)>()));
    }

    [Fact]
    public void The_offer_is_every_card_with_a_draft_published_ones_included()
    {
        // Review r3, pick 2 (a): stacks grow, so a Published card is offered.
        var strike1 = new DeckSlot("Strike");
        var strike2 = new DeckSlot("Strike");
        var published = new DeckSlot("Bestseller");
        var plain = new DeckSlot("Defend");
        var offer = YaeEditing.PublishChoices(new[]
        {
            (strike1, YaeAnnotation.RedInk, false),
            (plain, YaeAnnotation.None, true),
            (published, YaeAnnotation.SakuraSeal, true),
            (strike2, YaeAnnotation.FoxFire, false),
        });
        Assert.Equal(new[] { strike1, published, strike2 }, offer);
    }
    [Fact]
    public void The_chosen_copy_is_the_one_published_and_a_skip_publishes_nothing()
    {
        var decks = new[] { new DeckSlot("Strike"), new DeckSlot("Strike") };
        var previews = new[] { new DeckSlot("Strike"), new DeckSlot("Strike") };
        Assert.Same(decks[1], Assert.Single(YaeEditing.ResolvePicks(previews, decks, new[] { previews[1] })));
        Assert.Same(decks[0], Assert.Single(YaeEditing.ResolvePicks(previews, decks, new[] { previews[0] })));
        // The grid closed with no pick: nothing.
        Assert.Empty(YaeEditing.ResolvePicks(previews, decks, Array.Empty<DeckSlot>()));
        // A stranger (not a preview) is nothing.
        Assert.Empty(YaeEditing.ResolvePicks(previews, decks, new[] { new DeckSlot("Strike") }));
    }

    [Fact]
    public void The_reward_opens_a_closable_grid_and_publishes_the_draft_on_the_deck_card()
    {
        var prefs = Il.CallSequence(typeof(YaePublishReward).GetMethod(nameof(YaePublishReward.Prefs))!).ToList();
        Assert.Contains(prefs, c => c.Contains("set_Cancelable"));
        var calls = Il.CallSequence(typeof(YaePublishReward).GetMethod("OnSelect",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic)!).ToList();
        var grid = calls.FindIndex(c => c.Contains("FromSimpleGrid"));
        var resolve = calls.FindIndex(c => c.Contains(nameof(YaeEditing.ResolvePicks)));
        var publish = calls.FindIndex(c => c.Contains(nameof(YaeEditing.PublishToDeck)));
        Assert.True(grid >= 0 && resolve > grid && publish > resolve, string.Join(", ", calls));
        // A method group (ldftn), which only the set scan reads.
        Assert.Contains(Il.Calls(typeof(YaePublishReward).GetMethod("OnSelect",
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic)!),
            c => c.Contains(nameof(YaeEditing.PublishPreview)));
        Assert.Contains(calls, c => c.Contains("RemoveCard"));
        Assert.Contains(calls, c => c.Contains(nameof(YaeEditing.ClearDrafts)));
    }

    // ---- the companion and the keywords (picks 5, 6) -------------------------

    [Fact]
    public void Her_universal_companion_is_hidden_from_her_alone()
    {
        var card = new ProtoMiYaeSesshouSakura();
        Assert.True(CompanionPool.IsHiddenFrom(card, "yae"));
        Assert.False(CompanionPool.IsHiddenFrom(card, "klee"));
        Assert.False(CompanionPool.IsHiddenFrom(new ProtoYmSlyStrike(), "yae"));
    }

    [Fact]
    public void Her_sakura_tip_is_her_shrines_and_the_companions_stays_its_own()
    {
        Assert.Equal("At the end of your turn, strikes an enemy for 2 + its "
                     + "Level. Lasts 3 turns, then strikes once more.",
                     ArmKeywordTips.YaeSakuraTip);
        Assert.True(ArmKeywordTips.YaeSakuraTip.Length <= 100);
        Assert.DoesNotContain("Tenko", ArmKeywordTips.YaeSakuraTip);
        // Review r3: Tenko is one plain rule, the paper's words.
        Assert.Equal("Every [gold]Sakura[/gold] acts now. Refresh them to at "
                     + "least 3 turns.",
                     ArmKeywordTips.YaeTenkoTip);
    }
    [Fact]
    public void The_full_shrine_tip_is_the_ledgers_rule()
    {
        // Review r3: same kind levels the oldest; another kind withers it.
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        Assert.True(ledger.Plant(YaeLaw.PlantLevel));
        Assert.True(ledger.Plant(YaeLaw.PlantLevel));
        Assert.True(ledger.Plant(YaeLaw.PlantLevel));
        var before = ledger.Standing.Select(s => s.Level).ToList();
        Assert.False(ledger.Plant(YaeLaw.PlantLevel));
        Assert.Equal(new[] { before[0] + 1, before[1], before[2] },
                     ledger.Standing.Select(s => s.Level));
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, null, kind: YaeSakuraKind.Kitsune));
        Assert.Equal(YaeLaw.SakuraCap, ledger.Count);
        Assert.Equal(YaeSakuraKind.Kitsune, ledger.Standing[^1].Kind);
        Assert.Equal("Planting makes your oldest Sakura act. If the new Sakura "
                     + "is the same kind, the oldest stays and gains a Level. "
                     + "If not, the oldest withers and the new one takes its "
                     + "place.",
                     ArmKeywordTips.YaeFullShrineTip);
    }
    // ---- the Edit tip and each Annotation's own (2026-10-14) ----------------
    // [USER]: "the 'Edit' tooltip seems unnecessarily long; no need to show
    // the text for every possible edit if the card can only apply one."

    [Fact]
    public void The_edit_tip_is_the_general_rule_and_names_no_annotation()
    {
        Assert.Equal("Give a card an Annotation for this combat, replacing "
                     + "its last. Published ones stay and add up.",
                     ArmKeywordTips.YaeEditTip);
        Assert.True(ArmKeywordTips.YaeEditTip.Length <= 100);
        foreach (var name in YaeAnnotationText.All.Select(YaeAnnotationText.Name))
        {
            Assert.DoesNotContain(name, ArmKeywordTips.YaeEditTip);
        }
    }
    [Fact]
    public void An_annotation_tip_is_its_card_reading_or_its_sakura_reading()
    {
        Assert.Equal("This card deals 3 more damage and gives 3 more "
                     + "[gold]Block[/gold]. If it plants, its "
                     + "[gold]Sakura[/gold] get it too.",
                     YaeAnnotationText.TipBody(YaeAnnotation.RedInk, false));
        Assert.Equal("The [gold]Sakura[/gold]'s action is 3 bigger.",
                     YaeAnnotationText.TipBody(YaeAnnotation.RedInk, true));
        Assert.Equal("The [gold]Sakura[/gold] does not wither.",
                     YaeAnnotationText.TipBody(YaeAnnotation.DeadlineExtension, true));
        Assert.Contains("When the [gold]Sakura[/gold] acts",
                        YaeAnnotationText.TipBody(YaeAnnotation.FoxFire, true));
        // One with no Sakura reading falls back to its card reading.
        Assert.Equal(YaeAnnotationText.Rule(YaeAnnotation.Footnote),
                     YaeAnnotationText.TipBody(YaeAnnotation.Footnote, true));
        Assert.Equal("KLEEMOD-ARM_YAE_REDINK", ArmKeywordTips.KeyOf(YaeAnnotation.RedInk));
    }

    [Fact]
    public void A_card_that_applies_one_annotation_carries_that_tip_alone()
    {
        static string Chain(System.Type t) => System.IO.File.ReadAllText(
            System.IO.Path.Combine(Round17Tests.Repo(), "klee-mod", "KleeCode", "Cards",
                                   "Prototype", "Generated", t.Name + ".cs"));
        var proofread = Chain(typeof(ProtoYmProofread));
        Assert.Contains("ForAnnotation(base.ExtraHoverTips, this, YaeAnnotation.Reprint, false)", proofread);
        Assert.DoesNotContain("YaeAnnotation.Footnote, ", proofread);
        var branches = Chain(typeof(ProtoYmInkedBranches));
        Assert.Contains("YaeAnnotation.RedInk, true)", branches);
        // Reborn as Guuji Yae names none: its own chooser shows each face.
        Assert.DoesNotContain("ForAnnotation", Chain(typeof(ProtoYmRebornAsGuujiYae)));
    }

    [Fact]
    public void Each_edit_prompt_names_its_annotation_and_what_it_does()
    {
        Assert.Equal("Choose a card to Edit: Red Ink (it deals 3 more damage "
                     + "and gives 3 more Block).",
                     YaeEditing.EditPromptTextFor(YaeAnnotation.RedInk).Replace(" " + YaeEditing.ReplacesWarning, ""));
        Assert.Equal("Choose a card to Edit: Footnote (when it is played, "
                     + "draw 1 card).",
                     YaeEditing.EditPromptTextFor(YaeAnnotation.Footnote).Replace(" " + YaeEditing.ReplacesWarning, ""));
        Assert.Equal("Choose a card to Edit: Deadline Extension (it has "
                     + "Retain).",
                     YaeEditing.EditPromptTextFor(YaeAnnotation.DeadlineExtension).Replace(" " + YaeEditing.ReplacesWarning, ""));
        Assert.Equal("Choose a card to Edit: Royalties (when it is played, "
                     + "gain 1 Energy).",
                     YaeEditing.EditPromptTextFor(YaeAnnotation.Royalties).Replace(" " + YaeEditing.ReplacesWarning, ""));
        Assert.Equal("Choose a card to Edit: Reprint (the first time it is "
                     + "played each combat, play it once more for each Reprint).",
                     YaeEditing.EditPromptTextFor(YaeAnnotation.Reprint).Replace(" " + YaeEditing.ReplacesWarning, ""));
        Assert.EndsWith(YaeEditing.ReplacesWarning, YaeEditing.EditPromptTextFor(YaeAnnotation.RedInk));
        Assert.Equal(YaeEditing.EditPromptText,
                     YaeEditing.EditPromptTextFor(YaeAnnotation.None));
        Assert.Equal("KLEEMOD-YAE_EDIT_SAKURASEAL.selectionScreenPrompt",
                     YaeEditing.EditPromptKeyFor(YaeAnnotation.SakuraSeal));
        Assert.Equal(YaeAnnotationText.All.Length,
                     YaeAnnotationText.All.Select(YaeEditing.EditPromptKeyFor)
                         .Distinct().Count());
    }
}
