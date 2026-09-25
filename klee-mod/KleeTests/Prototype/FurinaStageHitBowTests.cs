using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- a performer emptied by a hit takes its Bow
/// (2026-09-25). [USER]: "we should also have Stage members bow out when they
/// are destroyed or replaced, not just when you deliberately spend them down
/// to 0." Rule 7 of <c>review/active/furina-stage-brief-2026-09-08.md</c>.
/// Since the evening's seat round a hit on the ENEMY'S turn owes that Bow to
/// the start of her next turn (<c>FurinaStage.PayOwedBows</c>), which
/// replaced paying it between the enemy's hits.
///
/// THE LEDGER HALF IS EXERCISED; THE PAYOUT HALF IS READ OFF IL. The ledger
/// runs headless, so the hit, its overflow and the queued Bow are real
/// numbers. The payout (<c>FurinaStage.Flush</c> -> <c>Bow</c>) awaits
/// <c>CreatureCmd</c>, which needs a live combat, so what is pinned there is
/// the wiring: which hook pays it, that it is the ordinary Bow, and the two
/// guards. The same cases run for real in the sim twin,
/// <c>tier0/tests/test_furina_stage.py</c>.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype arm's arithmetic.
/// </summary>
public class FurinaStageHitBowTests
{
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaStage.Enabled;

        internal Arm()
        {
            FurinaStageLedger.ResetAll();
            FurinaStage.Enabled = true;
        }

        public void Dispose()
        {
            FurinaStage.Enabled = _enabled;
            FurinaStageLedger.ResetAll();
        }
    }

    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        params (StagePerformer Who, int Fanfare)[] seats)
    {
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        foreach (var (who, fanfare) in seats)
        {
            stage.Summon(who);
            stage.Raise(fanfare - FurinaStageLaw.SummonFanfare);
        }
        return (seat, stage);
    }

    private static string RepoFile(string relativePath,
                                   [CallerFilePath] string here = "")
    {
        var dir = Path.GetDirectoryName(here);
        while (dir != null)
        {
            var candidate = Path.Combine(dir, relativePath);
            if (File.Exists(candidate)) return File.ReadAllText(candidate);
            dir = Path.GetDirectoryName(dir);
        }
        throw new FileNotFoundException(relativePath);
    }

    private static string Between(string text, string from, string to)
    {
        var start = text.IndexOf(from, StringComparison.Ordinal);
        Assert.True(start >= 0, from);
        var end = text.IndexOf(to, start, StringComparison.Ordinal);
        Assert.True(end > start, to);
        return text.Substring(start, end - start);
    }

    private static string FlushSource() => Between(
        RepoFile(Path.Combine("klee-mod", "KleeCode", "Powers", "Prototype",
                              "FurinaStage.cs")),
        "public static async Task Flush(", "private static bool CombatOver");

    // ---- the ledger: the hit, its overflow, and the Bow it owes -----------

    [Fact]
    public void A_hit_that_empties_usher_lands_its_overflow_and_owes_his_bow()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 3));

        var result = stage.Absorb(10);

        // The overflow reaches her in full: the Bow is not in this number.
        Assert.Equal(3, result.Absorbed);
        Assert.Equal(7, result.ReachedFurina);
        Assert.True(stage.IsEmpty);
        var owed = stage.TakePendingHitBows();
        var exit = Assert.Single(owed);
        Assert.Equal(StagePerformer.Usher, exit.Who);
        Assert.Equal(StageDeparture.Struck, exit.Cause);
        Assert.True(exit.Bows);
        // Paid once: a second flush finds nothing owed.
        Assert.Empty(stage.TakePendingHitBows());
        // Usher's Bow is his act once more (draft 3, 2026-09-25): 3 Block,
        // through the one act.
        Assert.Contains("FurinaStage.Act",
                        Il.Calls(Il.Method("FurinaStage", "Bow")));
    }

    [Fact]
    public void A_hit_that_empties_crabaletta_owes_her_bow()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Crabaletta, 2));

        stage.Absorb(5);

        var exit = Assert.Single(stage.TakePendingHitBows());
        Assert.Equal(StagePerformer.Crabaletta, exit.Who);
        Assert.True(exit.Bows);
        // Her Bow is her act once more (draft 3, 2026-09-25): a plain hit on
        // a random enemy, through the one act the sweep also uses.
        var bow = Il.Calls(Il.Method("FurinaStage", "Bow"));
        Assert.Contains("FurinaStage.Act", bow);
        var act = Il.Calls(Il.Method("FurinaStage", "Act"));
        Assert.Contains("ElementalHit.DealUnelemented", act);
        Assert.DoesNotContain("ElementalHit.Deal", act);
    }

    [Fact]
    public void A_hit_that_does_not_empty_the_lead_owes_nothing()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 5));

        stage.Absorb(3);

        Assert.Empty(stage.TakePendingHitBows());
    }

    [Fact]
    public void A_rotation_still_earns_no_bow()
    {
        Assert.False(new StageExit(StagePerformer.Usher,
                                   StageDeparture.Rotated).Bows);
        Assert.True(new StageExit(StagePerformer.Usher,
                                  StageDeparture.Spent).Bows);
    }

    [Fact]
    public void A_hit_killed_performer_can_return_with_a_five_century_act()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 3),
                               (StagePerformer.Crabaletta, 5));

        stage.Absorb(3);
        Assert.Single(stage.TakePendingHitBows());
        // AfterBow's return, on the stage the hit left.
        Assert.True(stage.ReturnToBack(StagePerformer.Usher));

        Assert.Equal(
            new[] { StagePerformer.Crabaletta, StagePerformer.Usher },
            stage.Seats.Select(s => s.Who).ToArray());
        Assert.Equal(FurinaStageLaw.SummonFanfare, stage.Back!.Fanfare);
        Assert.True(stage.Back.Resting);
    }

    [Fact]
    public void Clearing_the_stage_forgets_an_unpaid_bow()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 1));

        stage.Absorb(1);
        stage.Clear();

        Assert.Empty(stage.TakePendingHitBows());
    }

    // ---- the enemy's turn: the Bow waits for hers (2026-09-25 evening) -----

    [Fact]
    public void A_hit_on_the_enemys_turn_owes_its_bow_to_her_turn()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 3),
                               (StagePerformer.Crabaletta, 4));
        stage.ClearBeats();

        var result = stage.Absorb(5, waitsForTurn: true);

        // The overflow is unchanged: the Bow is not in this number.
        Assert.Equal(3, result.Absorbed);
        Assert.Equal(2, result.ReachedFurina);
        // Nothing for the flush after the hit; one Bow waiting for her turn.
        Assert.Empty(stage.TakePendingHitBows());
        var owed = Assert.Single(stage.OwedBows);
        Assert.Equal(StagePerformer.Usher, owed.Who);
        Assert.True(owed.Bows);
        // The leave says so, for the page.
        var leave = stage.Beats[^1];
        Assert.Equal("leave", leave.Event);
        Assert.Equal(FurinaStageLedger.HitWaitsReason, leave.Reason);
        // Taken once.
        Assert.Single(stage.TakeOwedBows());
        Assert.Empty(stage.TakeOwedBows());
        Assert.Empty(stage.OwedBows);
    }

    [Fact]
    public void Several_waiting_bows_pay_in_the_order_they_were_earned()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 2),
                               (StagePerformer.Crabaletta, 1),
                               (StagePerformer.Chevalmarin, 5));

        stage.Absorb(2, waitsForTurn: true);   // Usher
        stage.Absorb(2, waitsForTurn: true);   // Crabaletta, 1 through

        Assert.Equal(new[] { StagePerformer.Usher, StagePerformer.Crabaletta },
                     stage.TakeOwedBows().Select(x => x.Who).ToArray());
        Assert.Equal(StagePerformer.Chevalmarin, stage.Lead!.Who);
    }

    [Fact]
    public void Clearing_the_stage_forgets_a_waiting_bow()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 1));

        stage.Absorb(1, waitsForTurn: true);
        stage.Clear();

        Assert.Empty(stage.OwedBows);
    }

    [Fact]
    public void The_damage_modifier_asks_whose_turn_it_is()
    {
        var absorb = Il.Calls(Il.Method("FurinaStage", "AbsorbHit"));
        Assert.Contains("FurinaStage.OnEnemyTurn", absorb);
        // It only queues: nothing is awaited inside a damage modifier.
        Assert.DoesNotContain("FurinaStage.Bow", absorb);
        // With no combat -- every headless pin -- it is not the enemy's turn.
        Assert.False(FurinaStage.OnEnemyTurn(null));
    }

    [Fact]
    public void The_waiting_bows_pay_before_the_draw_after_the_regen()
    {
        // `BeforeHandDraw` runs after the Block clear and the energy reset
        // and before the hand draw (`CombatManager.SetupPlayerTurn`). The
        // lead's regen first, then the Bows: "after her Block clears and
        // after the front's regen, before her draw".
        var seq = Il.CallSequence(
            Il.Method("FurinaStageHooks", "BeforeHandDraw")).ToList();
        var regen = seq.IndexOf("FurinaStage.RegenLead");
        var pay = seq.IndexOf("FurinaStage.PayOwedBows");
        Assert.True(regen >= 0 && pay > regen, string.Join(", ", seq));
        // The regen moved here; the later hook no longer pays it twice.
        Assert.DoesNotContain(
            "FurinaStage.RegenLead",
            Il.Calls(Il.Method("FurinaStageHooks", "AfterPlayerTurnStart")));
    }

    [Fact]
    public void A_waiting_bow_is_the_ordinary_bow_and_dies_with_her()
    {
        var pay = Il.CallSequence(
            Il.Method("FurinaStage", "PayOwedBows")).ToList();
        var take = pay.IndexOf("FurinaStageLedger.TakeOwedBows");
        var bow = pay.IndexOf("FurinaStage.Bow");
        Assert.True(take >= 0 && bow > take, string.Join(", ", pay));
        var src = Between(
            RepoFile(Path.Combine("klee-mod", "KleeCode", "Powers",
                                  "Prototype", "FurinaStage.cs")),
            "public static async Task PayOwedBows(",
            "private static bool CombatOver");
        // The ordinary Bow: readers and A Five-Century Act's return included.
        Assert.Contains("await Bow(choiceContext, owner, exit);", src);
        Assert.DoesNotContain("mayReturn: false", src);
        Assert.Contains("owner.IsDead", src);
        Assert.Contains("CombatOver()", src);
        // Her death drops what is waiting, as it drops what a hit queued.
        var death = Il.Calls(Il.Method("FurinaStageHooks", "AfterDeath"));
        Assert.Contains("FurinaStageLedger.TakeOwedBows", death);
    }

    [Fact]
    public void The_strip_and_the_wire_show_a_waiting_bow()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Usher, 2),
                                  (StagePerformer.Chevalmarin, 4));

        stage.Absorb(2, waitsForTurn: true);

        var lines = Vfx.FurinaStageStrip.Label(seat.Creature).Split('\n');
        Assert.Equal("Usher's Bow waits for your turn.", lines[^1]);
        var owed = (List<object?>)FurinaStageLedger.Snapshot(
            seat.Player)["owed_bows"]!;
        Assert.Equal(new object?[] { "usher" }, owed.ToArray());
    }

    // ---- her own turn: after the hit ----------------------------------------

    [Fact]
    public void A_hit_on_her_own_turn_pays_its_bow_at_the_flush()
    {
        // `AfterDamageReceived` is what the engine fires once per hit, after
        // that hit's HP loss. A hit on HER turn (a Thorns, say) still pays
        // there; a hit on the enemy's turn queued nothing for it.
        var hook = Il.Calls(Il.Method("FurinaResourceHooks",
                                      "AfterDamageReceived"));
        Assert.Contains("FurinaStage.Flush", hook);

        var flush = Il.CallSequence(Il.Method("FurinaStage", "Flush")).ToList();
        var take = flush.IndexOf("FurinaStageLedger.TakePendingHitBows");
        var bow = flush.IndexOf("FurinaStage.Bow");
        var sync = flush.IndexOf("FurinaStagePets.Sync");
        Assert.True(take >= 0 && bow > take && sync > bow,
                    string.Join(", ", flush));
    }

    [Fact]
    public void A_hits_bow_is_the_ordinary_bow_readers_and_return_included()
    {
        // Same `Bow` a Spend takes, with `mayReturn` left at true: Thunderous
        // Applause draws and Raises (on an empty stage the Raise summons), and
        // A Five-Century Act returns the performer.
        var flush = FlushSource();
        Assert.Contains("await Bow(choiceContext, owner, exit);", flush);
        Assert.DoesNotContain("mayReturn: false", flush);
        var after = Il.Calls(Il.Method("FurinaStage", "AfterBow"));
        Assert.Contains("CardPileCmd.Draw", after);
        Assert.Contains("FurinaStage.Raise", after);
        Assert.Contains("FurinaStageLedger.ReturnToBack", after);
    }

    [Fact]
    public void No_bow_for_a_dead_furina_or_a_finished_combat()
    {
        var flush = FlushSource();
        Assert.Contains("owner.IsDead", flush);
        Assert.Contains("CombatOver()", flush);
        // The engine skips AfterDamageReceived for a target the hit killed;
        // her death drops what that hit owed, so a revive cannot pay it later.
        var death = Il.Calls(Il.Method("FurinaStageHooks", "AfterDeath"));
        Assert.Contains("FurinaStageLedger.TakePendingHitBows", death);
    }

    [Fact]
    public void A_guest_of_honor_hit_bows_through_the_same_flush()
    {
        var received = Il.Calls(Il.Method("GuestOfHonorPower",
                                          "AfterDamageReceived"));
        Assert.Contains("FurinaStage.Flush", received);
        // An ally the hit killed gets no AfterDamageReceived; its death pays.
        var death = Il.Calls(Il.Method("GuestOfHonorPower", "AfterDeath"));
        Assert.Contains("FurinaStage.Flush", death);
    }
}
