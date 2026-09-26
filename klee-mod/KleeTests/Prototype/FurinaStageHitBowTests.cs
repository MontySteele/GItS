using System;
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

        // 2026-09-25 night (the granted-guest seat round): he Bows before the
        // rest of the hit reaches her, so his 3 Block takes 3 of the 7 past
        // his bar: 10 - 3 - 3 = 4 reaches her.
        Assert.Equal(3, result.Absorbed);
        Assert.Equal(3, result.Caught);
        Assert.Equal(4, result.ReachedFurina);
        Assert.True(stage.IsEmpty);
        var owed = stage.TakePendingHitBows();
        var exit = Assert.Single(owed);
        // The Bow, paid at the flush, gains only what is left: nothing.
        Assert.Equal(3, exit.Caught);
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

    // ---- the payout: after the hit, between the hits -----------------------

    [Fact]
    public void The_bow_is_paid_at_the_flush_after_each_hit()
    {
        // `AfterDamageReceived` is what the engine fires once per hit, after
        // that hit's HP loss and before `AttackCommand` deals the next one --
        // so the Bow lands BETWEEN the hits of a multi-hit attack, and Usher's
        // Block meets the next hit.
        var hook = Il.Calls(Il.Method("FurinaResourceHooks",
                                      "AfterDamageReceived"));
        Assert.Contains("FurinaStage.Flush", hook);
        // The damage modifier only queues it: nothing awaited there.
        var absorb = Il.Calls(Il.Method("FurinaStage", "AbsorbHit"));
        Assert.DoesNotContain("FurinaStage.Bow", absorb);

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
