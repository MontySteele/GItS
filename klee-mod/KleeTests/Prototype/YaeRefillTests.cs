using System;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// YAE, THE DEDUPE AND THE REFILL (<c>review/active/yae-dedupe-2026-10-16.md</c>
/// and <c>review/active/yae-refill-2026-10-16.md</c>, ruled 2026-10-16:
/// [USER], "Agreed on the Yae paper picks!"). Eleven near-copies cut, eleven
/// cards added; each new mechanic pinned once. Pure ledger reads, the door's
/// no-combat paths and call-graph pins, as every Yae pin is. Sim twin:
/// <c>tier0/tests/test_yae_refill.py</c>.
/// </summary>
[Collection(YaeArm.Name)]
public class YaeRefillTests : IDisposable
{
    public YaeRefillTests()
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

    private static T Owned<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    private static int Var(CardModel card, string name) => (int)card.DynamicVars[name].BaseValue;

    private static System.Collections.Generic.List<string> OnPlay<T>() =>
        Il.CallSequence(typeof(T).GetMethod("OnPlay", Instance)!).ToList();

    private static void NoteEdit(YaeShrineLedger ledger) =>
        typeof(YaeShrineLedger).GetMethod("NoteEdit", HeadlessGame.All)!.Invoke(ledger, null);

    // ---- the pool ---------------------------------------------------------------

    [Fact]
    public void The_eleven_cut_are_gone_and_the_eleven_new_are_in_the_pool()
    {
        var names = typeof(ProtoYmThunderRite).Assembly.GetTypes().Select(t => t.Name).ToHashSet();
        foreach (var cut in new[] { "ProtoYmKitsuneFlick", "ProtoYmShrineLantern", "ProtoYmGraftedBranch",
                                    "ProtoYmShrineBell", "ProtoYmShrineOffering", "ProtoYmDeadline",
                                    "ProtoYmSacredSpark", "ProtoYmKitsuneFlash", "ProtoYmPrintRun",
                                    "ProtoYmRootedShrine", "ProtoYmOmikuji" })
        {
            Assert.DoesNotContain(cut, names);
        }
        var pool = Il.CallSequence(Il.Method("YaeRoster", "Pool")).ToList();
        foreach (var added in new[] { nameof(ProtoYmKitsuneBarrage), nameof(ProtoYmSesshouFang),
                                      nameof(ProtoYmFallingBlossom), nameof(ProtoYmPublishersDeadline),
                                      nameof(ProtoYmFoxsShade), nameof(ProtoYmHideBehindTheShrine),
                                      nameof(ProtoYmRewrite), nameof(ProtoYmDawnPrayer),
                                      nameof(ProtoYmHuntingGaze), nameof(ProtoYmInscribedThunder),
                                      nameof(ProtoYmKitsunesBlessing) })
        {
            Assert.Single(pool, c => c.Contains("<" + added + ">"));
        }
    }

    // ---- Falling Blossom ------------------------------------------------------------

    [Fact]
    public void Falling_blossom_hits_then_its_oldest_strikes_the_target()
    {
        // Yae draft pass, 2026-10-17: no wither (was "withers; its Last Bloom
        // strikes this enemy"). YaeDraftPassTests has the rest.
        var card = new ProtoYmFallingBlossom();
        Assert.Equal((1, 7), (card.EnergyCost.Canonical, Var(card, "Damage")));
        Upgrade(card);
        Assert.Equal(10, Var(card, "Damage"));
        var calls = OnPlay<ProtoYmFallingBlossom>();
        var hit = calls.FindIndex(c => c.Contains("DamageCmd.Attack"));
        var strike = calls.FindIndex(c => c.Contains(nameof(YaeCards.StrikeOldestAt)));
        Assert.True(hit >= 0 && strike > hit, string.Join(", ", calls));
        var at = Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.StrikeOldestAt))!).ToList();
        Assert.Contains(at, c => c.Contains("get_Target"));
        Assert.Contains(at, c => c.Contains(nameof(YaeShrine.StrikeOldestAt)));
    }

    // ---- Hunting Gaze -------------------------------------------------------------------

    [Fact]
    public void Hunting_gaze_remembers_only_her_attack_cards_hits()
    {
        var yae = Seat.Yae();
        var other = Seat.Klee().Creature;
        var ledger = YaeShrineLedger.For(yae.Creature);
        Assert.Null(ledger.LastAttacked);
        YaeShrine.NoteAttacked(yae.Creature, other, ValueProp.Move, Owned<ProtoYmFoxTrick>(yae));
        Assert.Null(ledger.LastAttacked);                    // a Skill's hit
        YaeShrine.NoteAttacked(yae.Creature, other, ValueProp.Unpowered, null);
        Assert.Null(ledger.LastAttacked);                    // a Sakura's hit
        YaeShrine.NoteAttacked(yae.Creature, other, ValueProp.Move, Owned<ProtoYmSlyStrike>(yae));
        Assert.Same(other, ledger.LastAttacked);             // her Attack card
        // The listener feeds it every hit.
        Assert.Contains(Il.Calls(typeof(KleeElementalHooks).GetMethod("AfterDamageGiven")!),
                        c => c.Contains(nameof(YaeShrine.NoteAttacked)));
    }

    [Fact]
    public void Hunting_gaze_aims_after_the_lure_while_its_target_lives_and_copies_do_not_stack()
    {
        var aim = Il.CallSequence(typeof(YaeShrine).GetMethod("Aim",
            BindingFlags.Static | BindingFlags.NonPublic)!).ToList();
        var lure = aim.FindIndex(c => c.Contains("get_Lure"));
        var gaze = aim.FindIndex(c => c.Contains(nameof(HuntingGazePower)));
        var last = aim.FindIndex(c => c.Contains("get_LastAttacked"));
        var random = aim.FindIndex(c => c.Contains("NextItem"));
        Assert.True(lure >= 0 && gaze > lure && last > gaze && random > last, string.Join(", ", aim));
        Assert.Equal(PowerStackType.Single, new HuntingGazePower().StackType);
        var card = new ProtoYmHuntingGaze();
        Assert.Equal("Your [gold]Sakura[/gold] strike the last enemy you attacked, while it lives.",
                     Face(card));
        Assert.Contains(OnPlay<ProtoYmHuntingGaze>(), c => c.Contains(nameof(HuntingGazePower)));
    }

    // ---- Inscribed Thunder ------------------------------------------------------------------

    [Fact]
    public void Inscribed_thunder_counts_distinct_annotations_published_included()
    {
        var layers = YaeLayers.All(new[] { YaeAnnotation.Footnote, YaeAnnotation.Footnote },
                                   YaeAnnotation.Reprint);
        Assert.Equal(2, YaeEditing.DistinctCount(layers));
        Assert.Equal(0, YaeEditing.DistinctCount(Array.Empty<YaeAnnotation>()));
        var card = new ProtoYmInscribedThunder();
        Assert.Equal((7, 5), (Var(card, "CalculationBase"), Var(card, "ExtraDamage")));
        Assert.Equal(0, YaeEditing.DistinctLayers(card));    // a plain card
        Upgrade(card);
        Assert.Equal((10, 5), (Var(card, "CalculationBase"), Var(card, "ExtraDamage")));
        Assert.Contains("for each [gold]Annotation[/gold] on this card", Face(card));
    }

    // ---- Publisher's Deadline ---------------------------------------------------------------

    [Fact]
    public void Publishers_deadline_costs_1_less_after_an_edit_this_turn()
    {
        var seat = Seat.Yae();
        var card = Owned<ProtoYmPublishersDeadline>(seat);
        Assert.Equal(2, card.EnergyCost.Canonical);
        Assert.False(card.TryModifyEnergyCostInCombat(card, 2m, out var unchanged));
        Assert.Equal(2m, unchanged);
        var ledger = YaeShrineLedger.For(seat.Creature);
        NoteEdit(ledger);
        Assert.Equal(1, ledger.EditsThisTurn);
        Assert.True(card.TryModifyEnergyCostInCombat(card, 2m, out var cost));
        Assert.Equal(1m, cost);
        Assert.Equal(1, ledger.Edits);
        // Her turn start clears it (the combat count stays).
        Assert.Contains(Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.TurnStart))!),
                        c => c.Contains("set_EditsThisTurn"));
        // A Sakura Edit counts too.
        ledger.Plant(YaeLaw.PlantLevel);
        ledger.EditSakura(YaeSakuraEnd.Oldest, 1, YaeAnnotation.RedInk);
        Assert.Equal(2, ledger.EditsThisTurn);
    }

    // ---- Sesshou Fang and Kitsune Barrage -----------------------------------------------------

    [Fact]
    public void Sesshou_fang_reads_any_sakura_at_level_3()
    {
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        ledger.Plant(YaeLaw.PlantLevel, 2);
        Assert.False(ledger.AnyAtLevel(YaeLaw.FangLevel));
        ledger.Plant(YaeLaw.PlantLevel, 3, kind: YaeSakuraKind.Kitsune);
        Assert.True(ledger.AnyAtLevel(YaeLaw.FangLevel));
        var card = new ProtoYmSesshouFang();
        // Yae flat-value pass, 2026-10-17: base 8 [10], the bonus stays 6 [8].
        Assert.Equal((8, 6), (Var(card, "YmBase"), Var(card, "YmAmount")));
        Upgrade(card);
        Assert.Equal((10, 8), (Var(card, "YmBase"), Var(card, "YmAmount")));
        Assert.Contains(OnPlay<ProtoYmSesshouFang>(), c => c.Contains(nameof(YaeCards.LevelStrike)));
        Assert.Contains(Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.LevelStrike))!),
                        c => c.Contains(nameof(YaeShrineLedger.AnyAtLevel)));
    }

    [Fact]
    public void Kitsune_barrage_hits_twice_and_three_times_with_3_sakura()
    {
        Assert.Equal(new[] { 2, 2, 2, 3, 3 },
                     Enumerable.Range(0, 5).Select(YaeLaw.BarrageHitCount));
        var card = new ProtoYmKitsuneBarrage();
        Assert.Equal(4, Var(card, "YmAmount"));
        Upgrade(card);
        Assert.Equal(5, Var(card, "YmAmount"));
        var barrage = Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.Barrage))!).ToList();
        Assert.Contains(barrage, c => c.Contains(nameof(YaeLaw.BarrageHitCount)));
        Assert.Contains(barrage, c => c.Contains("YaeShrine.Count"));
        var hit = typeof(YaeCards).GetMethod("CardHit", BindingFlags.Static | BindingFlags.NonPublic)!;
        Assert.Contains(Il.CallSequence(hit), c => c.Contains("WithHitCount"));
    }

    // ---- Hide Behind the Shrine ---------------------------------------------------------------

    [Fact]
    public void Hide_behind_the_shrine_withers_the_newest_and_pays_only_if_one_did()
    {
        var yae = Seat.Yae().Creature;
        var ledger = YaeShrineLedger.For(yae);
        // No Sakura: nothing withers (and the 5 more is not paid).
        Assert.False(YaeShrine.WitherNewest(null!, yae).GetAwaiter().GetResult());
        ledger.Plant(YaeLaw.PlantLevel);
        ledger.Plant(YaeLaw.PlantLevel, null, kind: YaeSakuraKind.Kitsune);
        var oldest = ledger.Standing[0];
        Assert.True(YaeShrine.WitherNewest(null!, yae).GetAwaiter().GetResult());
        Assert.Same(oldest, Assert.Single(ledger.Standing));
        var calls = Il.CallSequence(typeof(YaeCards).GetMethod(nameof(YaeCards.WitherNewestBlock))!).ToList();
        var wither = calls.FindIndex(c => c.Contains(nameof(YaeShrine.WitherNewest)));
        var block = calls.FindIndex(c => c.Contains("CardBlock"));
        Assert.True(wither >= 0 && block > wither, string.Join(", ", calls));
        Assert.Contains(Il.CallSequence(typeof(YaeShrine).GetMethod(nameof(YaeShrine.WitherNewest))!),
                        c => c.Contains("YaeShrine.Act"));
        var card = new ProtoYmHideBehindTheShrine();
        Assert.True(card is IYaeBlockCard);
        Assert.Equal((7, 5), (Var(card, "Block"), Var(card, "YmAmount")));
        Upgrade(card);
        Assert.Equal((9, 5), (Var(card, "Block"), Var(card, "YmAmount")));
    }

    // ---- Rewrite --------------------------------------------------------------------------------

    [Fact]
    public void Rewrite_draws_2_discards_1_then_edits_red_ink()
    {
        // The Yae pass (2026-10-16, review/active/yae-ancients-relics-2026-10-16.md
        // sec.1): "Draw 2 cards. Discard 1 card. Edit a card in your hand: Red
        // Ink." (was discard up to 2, draw that many). The `rewrite` verb has
        // no row now; YaeAncientsRelicsTests pins the card's order.
        var card = new ProtoYmRewrite();
        Assert.Equal(2, Var(card, "Cards"));
        Assert.DoesNotContain(OnPlay<ProtoYmRewrite>(), c => c.Contains(nameof(YaeCards.Rewrite)));
        Assert.Contains(OnPlay<ProtoYmRewrite>(), c => c.Contains("FromHandForDiscard"));
    }

    // ---- Dawn Prayer and Kitsune's Blessing ------------------------------------------------------

    [Fact]
    public void Dawn_prayer_levels_the_newest()
    {
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        Assert.False(ledger.LevelNewest(2));
        ledger.Plant(YaeLaw.PlantLevel);
        ledger.Plant(YaeLaw.PlantLevel);
        Assert.True(ledger.LevelNewest(2));
        Assert.Equal(new[] { 1, 3 }, ledger.Standing.Select(s => s.Level));
        var card = new ProtoYmDawnPrayer();
        Assert.Equal((0, 2), (card.EnergyCost.Canonical, Var(card, "YmAmount")));
        Upgrade(card);
        Assert.Equal(3, Var(card, "YmAmount"));
    }

    [Fact]
    public void Kitsunes_blessing_picks_the_highest_level_the_oldest_on_a_tie()
    {
        var ledger = YaeShrineLedger.For(Seat.Yae().Creature);
        Assert.Null(ledger.Bless(3, 2));
        ledger.Plant(YaeLaw.PlantLevel, 2);
        ledger.Plant(YaeLaw.PlantLevel, 2, kind: YaeSakuraKind.Kitsune);
        ledger.Plant(YaeLaw.PlantLevel);
        var blessed = ledger.Bless(3, 2);
        Assert.Same(ledger.Standing[0], blessed);            // the oldest of the two 2s
        Assert.Equal((5, YaeLaw.SakuraTurns + 2), (blessed!.Level, blessed.TurnsLeft));
        Assert.Equal((2, YaeLaw.SakuraTurns), (ledger.Standing[1].Level, ledger.Standing[1].TurnsLeft));
        var card = new ProtoYmKitsunesBlessing();
        Assert.Equal(3, Var(card, "YmAmount"));
        Upgrade(card);
        Assert.Equal(4, Var(card, "YmAmount"));
        Assert.Contains(OnPlay<ProtoYmKitsunesBlessing>(), c => c.Contains(nameof(YaeCards.BlessHighest)));
    }

    // ---- Fox's Shade --------------------------------------------------------------------------------

    [Fact]
    public void Foxs_shade_is_8_and_4_more_if_any_enemy_is_weak()
    {
        var card = new ProtoYmFoxsShade();
        Assert.Equal((8, 4), (Var(card, "Block"), Var(card, "BranchBlock")));
        Upgrade(card);
        Assert.Equal((11, 4), (Var(card, "Block"), Var(card, "BranchBlock")));
        Assert.Contains(OnPlay<ProtoYmFoxsShade>(), c => c.Contains(nameof(YaeShrine.WeakEnemies)));
        Assert.Equal("Gain {Block:diff()} [gold]Block[/gold]. If any enemy is [gold]Weak[/gold], "
                     + "gain {BranchBlock:diff()} more.", Face(card));
    }
}
