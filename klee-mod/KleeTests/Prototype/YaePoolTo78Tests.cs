using System;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// YAE, THE POOL TO 78 (<c>review/active/yae-pool-to-78-2026-10-15.md</c>,
/// ruled 2026-10-15, all picks (a)): the Annotation rule (pick 2 (a), as made
/// exact in the revision), the Foxfire targeting rule, the batch's new verbs
/// and powers, and sec.3's changes. Pure ledger reads and call-graph pins, as
/// every Yae pin is. Sim twin: <c>tier0/tests/test_yae_pool_to_78.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaePoolTo78Tests : IDisposable
{
    public YaePoolTo78Tests()
    {
        HeadlessGame.Arm();
        YaeShrineLedger.ResetAll();
    }

    public void Dispose() => YaeShrineLedger.ResetAll();

    private static YaeShrineLedger Fresh() => YaeShrineLedger.For(Seat.Yae().Creature);

    // ---- pick 2 (a): Annotations coexist on a Sakura ----------------------

    [Fact]
    public void Distinct_annotations_coexist_and_a_duplicate_does_nothing()
    {
        var ledger = Fresh();
        ledger.Plant(YaeLaw.PlantLevel);
        var s = ledger.Standing[0];
        Assert.Equal(1, ledger.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.RedInk));
        Assert.Equal(1, ledger.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.FoxFire));
        Assert.Equal(1, ledger.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.DeadlineExtension));
        Assert.Equal(new[] { YaeAnnotation.RedInk, YaeAnnotation.FoxFire,
                             YaeAnnotation.DeadlineExtension }, s.Annotations);
        var size = YaeShrineLedger.ActSize(s.Kind, s.Level, s.Annotations);
        Assert.Equal(YaeLaw.SakuraBase + s.Level + YaeLaw.RedInkAmount, size);
        // A second Red Ink changes nothing: no second +3.
        Assert.Equal(0, ledger.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.RedInk));
        Assert.Equal(size, YaeShrineLedger.ActSize(s.Kind, s.Level, s.Annotations));
    }

    [Fact]
    public void The_seat_page_read_names_each_sakuras_annotations_in_the_order_applied()
    {
        var ledger = Fresh();
        for (var i = 0; i < 2; i++) ledger.Plant(YaeLaw.PlantLevel);
        ledger.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.FoxFire);
        ledger.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.DeadlineExtension);
        ledger.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.RedInk);
        var rows = ledger.SakuraRows()
            .Cast<System.Collections.Generic.Dictionary<string, object?>>().ToList();
        Assert.Equal(2, rows.Count);
        Assert.Equal(1, rows[0]["slot"]);
        Assert.Equal(new object?[] { "Fox Fire", "Deadline Extension", "Red Ink" },
                     ((System.Collections.Generic.List<object?>)rows[0]["annotations"]!).ToArray());
        Assert.Equal(2, rows[1]["slot"]);
        Assert.Empty((System.Collections.Generic.List<object?>)rows[1]["annotations"]!);
    }

    [Fact]
    public void An_edit_that_changes_nothing_is_not_an_edit()
    {
        var ledger = Fresh();
        for (var i = 0; i < 2; i++) ledger.Plant(YaeLaw.PlantLevel);
        ledger.EditSakura(YaeSakuraEnd.Newest, 1, YaeAnnotation.FoxFire);
        var edits = ledger.Edits;
        // Every Sakura: the newest already has it, so one Edit, not two.
        Assert.Equal(1, ledger.EditSakura(YaeSakuraEnd.Every, 1, YaeAnnotation.FoxFire));
        Assert.Equal(edits + 1, ledger.Edits);
        Assert.Equal(0, ledger.EditSakura(YaeSakuraEnd.Every, 1, YaeAnnotation.FoxFire));
        Assert.Equal(edits + 1, ledger.Edits);
    }

    [Fact]
    public void Annotations_survive_refreshes_and_go_with_the_sakura()
    {
        var ledger = Fresh();
        for (var i = 0; i < 3; i++) ledger.Plant(YaeLaw.PlantLevel);
        var oldest = ledger.Standing[0];
        ledger.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.FoxFire);
        ledger.Refresh();                                    // Tenko's refresh
        Assert.True(oldest.Has(YaeAnnotation.FoxFire));
        Assert.False(ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.RedInk));
        Assert.Equal(new[] { YaeAnnotation.FoxFire, YaeAnnotation.RedInk },
                     oldest.Annotations);                    // same-kind refresh
        Assert.True(ledger.WouldReplace(YaeLaw.SakuraCap, YaeSakuraKind.Kitsune));
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, null, YaeAnnotation.None,
                                 kind: YaeSakuraKind.Kitsune));
        Assert.DoesNotContain(oldest, ledger.Standing);      // replaced: gone
        Assert.Empty(ledger.Standing[^1].Annotations);
    }

    [Fact]
    public void Evergreen_charm_lost_its_red_ink_sentence()
    {
        var face = new ProtoYmEvergreenCharm().Localization!
            .First(l => l.Item1 == "description").Item2;
        Assert.DoesNotContain("Red Ink", face);
    }

    // ---- the Foxfire targeting rule ----------------------------------------

    [Fact]
    public void An_aimed_strike_is_one_hit_and_only_its_own_act_hits_all()
    {
        // The aimed branch comes before the ALL loop in the Foxfire arm.
        var calls = Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.Act))!).ToList();
        Assert.Contains(calls, c => c.Contains("get_IsAlive"));
        foreach (var name in new[] { nameof(YaeShrine.StrikeTarget), nameof(YaeShrine.StrikeAllAt),
                                     nameof(YaeShrine.Verdict) })
        {
            Assert.Contains(Il.CallSequence(typeof(YaeShrine).GetMethod(name)!),
                            c => c.Contains(nameof(YaeShrine.Act)));
        }
        Assert.Contains(Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.StrikeIfWeak))!),
                        c => c.Contains(nameof(YaeShrine.StrikeTarget)));
    }

    // ---- the batch's verbs ---------------------------------------------------

    [Fact]
    public void Genre_shift_reads_the_missing_kinds_in_kind_order()
    {
        var ledger = Fresh();
        Assert.Equal(new[] { YaeSakuraKind.Thunder, YaeSakuraKind.Foxfire, YaeSakuraKind.Kitsune },
                     ledger.MissingKinds());
        ledger.Plant(YaeLaw.PlantLevel, null, kind: YaeSakuraKind.Foxfire);
        Assert.Equal(new[] { YaeSakuraKind.Thunder, YaeSakuraKind.Kitsune }, ledger.MissingKinds());
    }

    [Fact]
    public void Kitsune_veil_levels_its_kind_only()
    {
        var ledger = Fresh();
        ledger.Plant(YaeLaw.PlantLevel, null, kind: YaeSakuraKind.Kitsune);
        ledger.Plant(YaeLaw.PlantLevel);
        ledger.LevelUp(2, YaeSakuraKind.Kitsune);
        Assert.Equal(new[] { 3, 1 }, ledger.Standing.Select(s => s.Level));
    }

    [Fact]
    public void Grafted_branch_is_level_3_and_lasts_one_more_turn()
    {
        var ledger = Fresh();
        Assert.True(ledger.Plant(YaeLaw.PlantLevel, 3, extraTurns: 1));
        Assert.Equal((3, YaeLaw.SakuraTurns + 1),
                     (ledger.Standing[0].Level, ledger.Standing[0].TurnsLeft));
        var card = new ProtoYmGraftedBranch();
        Assert.Equal(3, (int)card.DynamicVars["YmAmount"].BaseValue);
        Assert.Contains(Il.CallSequence(typeof(ProtoYmGraftedBranch).GetMethod("OnPlay",
                            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic)!),
                        c => c.Contains(nameof(YaeCards.PlantLevel)));
    }

    [Fact]
    public void The_withers_pay_enlightened_blessing()
    {
        foreach (var name in new[] { nameof(YaeShrine.TickAndBloom), nameof(YaeShrine.WitherOldest),
                                     nameof(YaeShrine.WitherAll), nameof(YaeShrine.Plant) })
        {
            Assert.Contains(Il.CallSequence(typeof(YaeShrine).GetMethod(name)!),
                            c => c.Contains(nameof(YaeShrine.Withered)));
        }
    }

    // ---- the powers ------------------------------------------------------------

    [Fact]
    public void Eternity_stops_every_timer()
    {
        var ledger = Fresh();
        ledger.Plant(YaeLaw.PlantLevel);
        for (var i = 0; i < 10; i++) Assert.Empty(ledger.Tick(eternal: true));
        Assert.Equal(YaeLaw.SakuraTurns, Assert.Single(ledger.Standing).TurnsLeft);
    }

    [Fact]
    public void Editorial_priority_frees_only_the_first_annotated_card_in_hand()
    {
        Assert.True(EditorialPriorityPower.Frees(true, true, false));
        Assert.False(EditorialPriorityPower.Frees(false, true, false));
        Assert.False(EditorialPriorityPower.Frees(true, false, false));
        Assert.False(EditorialPriorityPower.Frees(true, true, true));
        Assert.Contains(Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.TurnStart))!),
                        c => c.Contains("set_PriorityUsed"));
    }

    [Fact]
    public void Saiguus_lesson_pays_only_weak_she_applies()
    {
        Assert.False(SaiguusLessonPower.Pays(null, 1m, null, null));
        Assert.Contains(Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.OnWeakApplied))!),
                        c => c.Contains(nameof(YaeShrine.StrikeTarget)));
    }

    [Fact]
    public void Stellar_conduct_reads_the_reaction_count_across_a_hit()
    {
        var hit = typeof(YaeShrine).GetMethod("Hit",
            System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic)!;
        var calls = Il.CallSequence(hit).ToList();
        Assert.Contains(calls, c => c.Contains("get_TotalResolved"));
        Assert.Contains(calls, c => c.Contains(nameof(StellarConductPower)));
    }

    [Fact]
    public void Sacred_shade_pays_at_turn_end()
    {
        Assert.Contains(Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.TurnEnd))!),
                        c => c.Contains(nameof(SacredShadePower)));
    }

    // ---- sec.3 and the revision -------------------------------------------------

    [Fact]
    public void Grove_and_mooncall_swapped_rarities_and_mooncall_costs_1()
    {
        Assert.Equal(CardRarity.Rare, new ProtoYmSakuraGrove().Rarity);
        var moon = new ProtoYmFoxsMooncall();
        Assert.Equal((CardRarity.Uncommon, 1), (moon.Rarity, moon.EnergyCost.Canonical));
        Assert.Equal(2, new ProtoYmGenreShift().EnergyCost.Canonical);
    }
}
