using System;
using System.IO;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE LIVE LOOK OF 2026-09-16, the mod half.
///
/// The record is not on main; it is on PR #570's branch, retrieved as
/// <c>git show 02039d2b:review/records/live-looks-8b-2026-09-16.md</c>
/// (CLAUDE.md, "History retrieval"): 45 built-and-pinned rows read on
/// `0.2.3480+proto` against
/// a hand-built board, each one answered with the one screen or the one number
/// its acceptance sentence named. Every board in it was written by hand, so
/// nothing measured there is comparable to anything -- what it produced is a
/// list of sentences that are true or false in the running game, and this file
/// pins the ones that were false.
///
/// SOME OF THESE ARE SOURCE PINS and that is the headless boundary rather than
/// a preference (`KleeTests/README.md`). `DynamicVar.UpdateCardPreview`
/// reaches `CardModel.CombatState`, which this harness cannot build, and the
/// two bridge files named below carry Godot and game types this project does
/// not compile. What a source pin CAN say is which shape was emitted and which
/// call is on which line, which is where each of those defects lived.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class LiveLooks8bTests
{
    private static string Source(string relativePath,
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

    private sealed class StageArm : IDisposable
    {

        internal StageArm()
        {
            FurinaStageLedger.ResetAll();
        }

        public void Dispose()
        {
            FurinaStageLedger.ResetAll();
        }
    }


    // ==================================================================
    // `EB-670` -- the headline folds the carried-out condition
    // ==================================================================

    [Fact]
    public void Feints_headline_is_a_count_reading_var()
    {
        // `EB-670`'s find was a headline that printed the floor on a morning
        // whose hit was the branch. The Casket pass (2026-09-28) re-keyed
        // Feint off the yes/no onto the COUNT ("Deal 4 damage, plus 3 for each
        // Plan carried out this turn"), so the headline is the calculated
        // var over that count -- the preview reads the same ledger the hit
        // does, which is the property `EB-670` asked for. A base of 6 since
        // the cleanup pass (2026-09-29).
        var card = Source(Path.Combine(
            "klee-mod", "KleeCode", "Cards", "Prototype", "Generated",
            "ProtoKkFeint.cs"));
        Assert.Contains("new CalculationBaseVar(6m)", card);
        Assert.Contains("new ExtraDamageVar(3m)", card);
        Assert.Contains("new FrontFoldedDamageVar(ValueProp.Move)", card);
        Assert.Contains("DamageCmd.Attack(DynamicVars.CalculatedDamage)", card);
    }

    [Fact]
    public void The_headline_var_reads_the_same_ledger_count_the_play_reads()
    {
        // The face and the play ask one object: the calculated var's
        // multiplier is the ledger's per-turn carry-out count, and the play
        // deals that var.
        var card = Source(Path.Combine(
            "klee-mod", "KleeCode", "Cards", "Prototype", "Generated",
            "ProtoKkFeint.cs"));
        Assert.Contains(
            "KokomiOverhaulLedger.For(card.Owner.Creature).PlansCarriedOutThisTurn",
            card);

        var var_ = Source(Path.Combine(
            "klee-mod", "KleeCode", "Powers", "Prototype",
            "FrontFoldedDamageVar.cs"));
        // The condition-folding var stays for any row that prints the yes/no.
        Assert.Contains("class PlanCarriedDamageVar", var_);
    }

    [Fact]
    public void The_generator_only_folds_a_condition_the_preview_can_read()
    {
        // Every other condition keeps the plain var: a condition a preview
        // cannot evaluate honestly is one a headline must not pretend to have
        // evaluated.
        var gen = Source(Path.Combine("tools", "gen_klee_cards.py"));
        Assert.Contains("== \"plan_carried_out_this_turn\")", gen);
        Assert.Contains("PlanCarriedDamageVar", gen);
    }

    // ==================================================================
    // `EB-334` vs `EB-599` -- the Plan line prints what it will deal
    // ==================================================================

    [Fact]
    public void A_plan_of_ten_against_a_vulnerable_two_body_is_fifteen()
    {
        // THE FIND. Feint's Plan clause printed "Plan: Deal 10"; the carry-out
        // next morning, against a body wearing Vulnerable 2, was
        // "Bake-Kurage: Feint, 15" and 15 HP left the body.
        //
        // R246 pick 1 ([USER]): "the Plan line prints the number it will deal
        // against the enemy's current state". `EB-599` is the r22 packet's D
        // DEFAULT, which is what makes this a reversal and not a re-ask: a
        // ruling beats a default, and no later ruling touched it.
        var enemy = Seat.Kokomi(60).WithPower<VulnerablePower>(2).Creature;
        Assert.Equal(15, KokomiPlan.PlannedDamage(enemy, 10));
    }

    [Fact]
    public void The_plan_line_previews_the_target_fold_again()
    {
        // The line and the morning are one number again, which is the whole
        // of `EB-334`'s acceptance. A source pin for the same headless reason
        // `EB-670`'s is one: the preview call needs a combat.
        var plan = Source(Path.Combine("klee-mod", "KleeCode", "Powers",
                                       "Prototype", "KokomiPlan.cs"));
        Assert.Contains("PreviewValue = PlannedDamage(", plan);
        // Against the PLAN's own body and never the hovered one: `Aim
        // .FrontEnemy` is where a carry-out lands, and previewing against
        // whatever the cursor is over would print a number for a body the
        // morning will not hit.
        Assert.Contains("target, FrontEnemy(kokomi))", plan);
    }

    [Fact]
    public void Her_side_of_the_line_is_still_folded_at_writing_time()
    {
        // `EB-599`'s OTHER half stands: her Strength and this copy's
        // enchantment go into the number that is QUEUED, so the face, the
        // queue and the morning print one number. Only the target's half
        // moved.
        var plan = Source(Path.Combine("klee-mod", "KleeCode", "Powers",
                                       "Prototype", "KokomiPlan.cs"));
        Assert.Contains(
            "PreviewValue = Hers(kokomi, card, (int)BaseValue, _strengthTimes);",
            plan);
    }

    // ==================================================================
    // `EB-745` caveat 1 -- the GRANT site, not only the offer filter
    // ==================================================================

    // ==================================================================
    // `EB-745` caveat 2 -- the shipped Burst bar under the arm
    // ==================================================================

    // ==================================================================
    // `EB-739`'s second pair -- one printed name per card
    // ==================================================================

    // ==================================================================
    // Defect 6 -- the Kurage memory warning at every combat start
    // ==================================================================

    // ==================================================================
    // The bridge halves, source-pinned: Godot and game types, not compiled
    // ==================================================================

    [Fact]
    public void The_event_room_read_is_guarded()
    {
        // THE FIND. `get_state` answered twice with
        // `ArgumentOutOfRangeException at EventSynchronizer.GetEventForPlayer
        // at McpMod.BuildEventState` on the Event Room path, losing the whole
        // SCREEN rather than the options.
        var builder = Source(Path.Combine("vendor", "STS2_MCP",
                                          "McpMod.StateBuilder.cs"));
        Assert.Contains(
            "GitsLocalEvent.OrNothing(() => eventRoom.LocalMutableEvent)",
            builder);

        var guard = Source(Path.Combine("vendor", "STS2_MCP", "gits",
                                        "GitsLocalEvent.cs"));
        Assert.Contains("public static T? OrNothing<T>(", guard);
        // Logged once per process: a poller would print a line a frame.
        Assert.Contains("_reported", guard);
    }

    [Fact]
    public void The_debug_route_carries_the_three_run_grants()
    {
        // `EB-752` (The Boot), `EB-684` (Flex Potion) and `EB-116` (Pael's
        // Eye) came back NOT DONE for one reason -- "the bridge has no
        // relic-grant op" -- and `give_gold`'s absence held four
        // `IsAllowed` gates shut (proofs-8a).
        var route = Source(Path.Combine("vendor", "STS2_MCP", "gits",
                                        "GitsDebugState.cs"));
        Assert.Contains("\"give_relic\", \"give_potion\", \"give_gold\" }",
                        route);
        // Each is the GAME's own command. Nothing is reimplemented.
        Assert.Contains("RelicCmd.Obtain(", route);
        Assert.Contains("PotionCmd.TryToProcure(", route);
        Assert.Contains("PlayerCmd.GainGold(", route);
    }

    [Fact]
    public void The_python_client_knows_the_same_twelve_ops()
    {
        // The two lists are one contract: a client that can name an op the
        // route does not have is a refusal a round trip away, and a route
        // with an op no client can name is an op nobody uses.
        var client = Source(Path.Combine("understudy", "bridge.py"));
        Assert.Contains("\"give_relic\", \"give_potion\", \"give_gold\")",
                        client);
    }
}
