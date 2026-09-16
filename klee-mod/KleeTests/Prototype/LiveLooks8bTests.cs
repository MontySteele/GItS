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
        private readonly bool _enabled = FurinaStage.Enabled;

        internal StageArm()
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

    // ==================================================================
    // `EB-287` -- the Bomb KEYWORD carries the merge
    // ==================================================================

    [Fact]
    public void The_bomb_tip_says_a_second_bomb_joins_the_first()
    {
        // THE FIND. Merging IS stated on the enemy BADGE -- "Bomb 9 ... sizes,
        // oldest first: 5 / 4" -- and the row records the KEYWORD as carrying
        // it. The keyword did not: "A charge on an enemy: grows 6 a turn, and
        // goes off when Set off or as a Mine. Block stops it. Only Vulnerable
        // and the HP cap move it. If the enemy dies with it on, it moves to a
        // survivor." The one reader the word exists for -- the one who has not
        // built a pile yet -- was never told a second placer ADDS.
        var tip = Source(Path.Combine("klee-mod", "KleeCode", "Cards",
                                      "Prototype", "ArmKeywordTips.cs"));
        Assert.Contains("a second Bomb joins the first", tip);
    }

    [Fact]
    public void The_merge_clause_rides_the_first_sentence()
    {
        // A CLAUSE AND NOT A SENTENCE: the tip is at the base game's
        // four-sentence cap (`lint_text_conventions.MAX_SENTENCES`), so a
        // fifth sentence would either break the lint or displace one of the
        // three ruled findings below it. It rides the clause it belongs to.
        var tip = Source(Path.Combine("klee-mod", "KleeCode", "Cards",
                                      "Prototype", "ArmKeywordTips.cs"));
        Assert.Contains("\"; a second Bomb joins the first. \"", tip);
    }

    // ==================================================================
    // `EB-670` -- the headline folds the carried-out condition
    // ==================================================================

    [Fact]
    public void Feints_headline_is_a_condition_reading_var()
    {
        // THE FIND. A Plan was written, the turn ended, the carry-out drew
        // nothing ("Bake-Kurage: War Council, 5"), and Feint read BEFORE any
        // play: "Deal 5 damage. If a Plan was carried out this turn, deal 10
        // damage instead." The headline was 5 on a morning whose hit was the
        // 10 -- it then killed an 8-HP body.
        //
        // A SOURCE PIN, at the headless boundary named in this file's summary:
        // the defect is which VAR the row declares for its headline, and the
        // preview call itself needs a combat.
        var card = Source(Path.Combine(
            "klee-mod", "KleeCode", "Cards", "Prototype", "Generated",
            "ProtoKkFeint.cs"));
        Assert.Contains(
            "new PlanCarriedDamageVar(\"PlainDamage\", 5m, \"BranchDamage\", "
            + "ValueProp.Move)", card);
        // And the branch it reads is still declared, still on its own upgrade
        // key -- the reason the headline reads the SIBLING rather than storing
        // a second copy of the number.
        Assert.Contains("new FoldedDamageVar(\"BranchDamage\", 10m", card);
        Assert.Contains("DynamicVars[\"BranchDamage\"].UpgradeValueBy(3m)",
                        card);
    }

    [Fact]
    public void The_headline_var_reads_the_same_ledger_flag_the_play_reads()
    {
        // The face and the play have to agree, so they ask one object. The
        // emitted `OnPlay` asks `KokomiOverhaulLedger.For(...)
        // .PlanCarriedOutThisTurn`; so does the var.
        var card = Source(Path.Combine(
            "klee-mod", "KleeCode", "Cards", "Prototype", "Generated",
            "ProtoKkFeint.cs"));
        Assert.Contains(
            "KokomiOverhaulLedger.For(Owner.Creature).PlanCarriedOutThisTurn",
            card);

        var var_ = Source(Path.Combine(
            "klee-mod", "KleeCode", "Powers", "Prototype",
            "FrontFoldedDamageVar.cs"));
        Assert.Contains("class PlanCarriedDamageVar", var_);
        Assert.Contains("KokomiOverhaulLedger.For(kokomi).PlanCarriedOutThisTurn",
                        var_);
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
        Assert.Contains("PreviewValue = Hers(kokomi, card, (int)BaseValue);",
                        plan);
    }

    // ==================================================================
    // Defect 4 -- `Final Bow` on an EMPTY stage
    // ==================================================================

    [Fact]
    public void Final_bows_forecast_on_an_empty_stage_is_zero()
    {
        // THE FIND. "`Final Bow` printed `Gain 2 Block, its Fanfare` on an
        // EMPTY stage, where Ousia Surge and Pneuma Refrain both correctly
        // printed 0 on the same board."
        //
        // The 2 was an EARLIER card's spend. The two neighbours read a BAR
        // (`LeadFanfare` / `BackFanfare`, 0 on an empty stage) and this one
        // reads the per-play spend record first -- which, on the build the
        // look read, was never closed between plays. `0d50a482` (PR #572,
        // round three item (f)) made that record a stack; this is the empty-
        // stage reading the look actually took, pinned on the far side of it.
        using var _ = new StageArm();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        stage.Summon(StagePerformer.Usher);
        stage.Raise(1);                        // a bar of 2, as the look had

        stage.BeginPlay();
        stage.Spend(2);                        // ... which this play empties
        stage.EndPlay();

        // The stage is empty and no play is in flight: every reader on the
        // board answers the same 0.
        Assert.Equal(0, FurinaStage.LeadFanfare(seat.Creature));
        Assert.Equal(0, FurinaStage.BackFanfare(seat.Creature));
        Assert.Equal(0, stage.SpentThisPlay);
    }

    // ==================================================================
    // `EB-745` caveat 1 -- the GRANT site, not only the offer filter
    // ==================================================================

    [Fact]
    public void The_stage_arm_retires_the_shipped_salon_at_the_grant_site()
    {
        // THE FIND. "A hand-granted shipped `Salon Début` DOES still grant
        // `Salon Member 3 (buff)` under the arm, with the full shipped Encore
        // glossary on it -- the arm's guard is the offer filter (`EB-736`),
        // not the grant site."
        //
        // An offer filter is not a rule about a HAND: a `give_card`, a
        // Conscript or any later route puts such a row on the board anyway.
        var deploy = Source(Path.Combine("klee-mod", "KleeCode", "Powers",
                                         "SalonPowers.cs"));
        Assert.Contains(
            "if (FurinaResources.StageRetiresTheShippedMeters(owner)) return 0;",
            deploy);
    }

    [Fact]
    public void The_gate_the_grant_site_takes_is_the_one_the_meters_take()
    {
        // One question with one answer, rather than two that can drift.
        using var _ = new StageArm();
        var furina = Seat.Furina().WithCombatState().Creature;
        Assert.True(FurinaResources.StageRetiresTheShippedMeters(furina));
    }

    // ==================================================================
    // `EB-745` caveat 2 -- the shipped Burst bar under the arm
    // ==================================================================

    [Fact]
    public void The_shipped_burst_gauge_does_not_draw_under_the_stage_arm()
    {
        // THE FIND. "The in-game HUD still draws the shipped Burst bar
        // (`0/70`, later `15/70`) above Furina under the arm, on a board with
        // no shipped card played." `EB-726` took the reframe out of the tree,
        // which left `BurstGaugeApplies` a bare `IsFurina`; the Stage brief
        // has no Burst bar in it at all (R269, rule 11).
        using var _ = new StageArm();
        var furina = Seat.Furina().WithCombatState().Creature;
        Assert.False(FurinaResources.BurstGaugeApplies(furina));
    }

    [Fact]
    public void The_shipped_burst_gauge_still_draws_with_the_arm_off()
    {
        // The release build is unchanged, which is the other half of every
        // arm guard in this file.
        var enabled = FurinaStage.Enabled;
        try
        {
            FurinaStage.Enabled = false;
            var furina = Seat.Furina().WithCombatState().Creature;
            Assert.True(FurinaResources.BurstGaugeApplies(furina));
        }
        finally
        {
            FurinaStage.Enabled = enabled;
        }
    }

    // ==================================================================
    // `EB-739`'s second pair -- one printed name per card
    // ==================================================================

    [Fact]
    public void The_stages_starter_no_longer_prints_the_shipped_salon_name()
    {
        // THE FIND (the `EB-739` caveat). "The shipped `Salon Début` and the
        // Stage's `Salon Début` are both live ids on this build and print the
        // same title (`Salon Début (1)` / `Salon Début (2)` when both are in
        // hand). They are held apart only by `EB-736`'s offer filter."
        //
        // An E default under R179 -- the brief's own card table says "Names
        // are provisional" -- and the same repair `EB-739` made to Standing
        // Ovation. The ID does not move.
        var generated = Source(Path.Combine(
            "klee-mod", "KleeCode", "Cards", "Prototype", "Generated",
            "ProtoFsSalonDebut.cs"));
        Assert.Contains("(\"title\", \"Take the Stage\")", generated);
        Assert.DoesNotContain("(\"title\", \"Salon Début\")", generated);
        Assert.Contains("id=proto_fs_salon_debut", generated);
    }

    // ==================================================================
    // Defect 6 -- the Kurage memory warning at every combat start
    // ==================================================================

    [Fact]
    public void The_kurage_seat_read_is_silent_on_a_table_with_nobody_at_it()
    {
        // THE FIND. "`kurage memory: no local seat in this combat
        // (InvalidOperationException: Local player not found in combat.);
        // drawing nothing.` -- seven times in the Klee run and at EVERY combat
        // start in the Kokomi run, logged BEFORE `Creating NCombatRoom`."
        //
        // It is the `Deactivate` postfix at the bottom of that file, running
        // while the INCOMING room is built: the combat holds no players yet,
        // `LocalContext.GetMe` throws, and a teardown with nothing to tear
        // down logs a warning about it. The loud warning is for the case it
        // was written for -- a combat with a table in it and no local seat at
        // that table -- and a line that fires on every fight is a line nobody
        // reads on the fight where it means something.
        //
        // A SOURCE PIN: `TryGetMe` takes a `CombatState`, which this harness
        // cannot build. What it CAN say is that the guard is asked before the
        // throwing call, which is the whole of the change.
        var card = Source(Path.Combine("klee-mod", "KleeCode", "Vfx",
                                       "Prototype", "KurageMemoryCard.cs"));
        var guard = card.IndexOf("if (!Seated(state)) return null;",
                                 StringComparison.Ordinal);
        var call = card.IndexOf("return LocalContext.GetMe(state);",
                                StringComparison.Ordinal);
        Assert.True(guard > 0, "the no-table guard is gone");
        Assert.True(call > 0);
        Assert.True(guard < call,
                    "the guard must be asked BEFORE the call that throws");
        // The warning itself stays, for the case it was written for.
        Assert.Contains("no local seat in this ", card);
    }

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
