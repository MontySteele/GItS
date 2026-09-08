using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND TWENTY-FOUR -- the Kokomi cap lane of 2026-09-07
/// (`review/active/kokomi-overhaul-round-24-2026-09-07.md`) and the two rows
/// it left on the C# side.
///
/// `EB-653`: THE CAP PRINTS WHERE IT BINDS. The lane ran with
/// `GITS_KOKOMI_PLAN_CAP=2`, the jellyfish carried out two of four written
/// Plans four mornings running, and no screen said a cap existed -- while the
/// blind page printed "not a limit". Three of the four occurrences were read
/// as a wall.
///
/// `EB-654`: A SUMMON'S HIT SAYS SO. "Yae Miko's Sakura took 10 HP off an
/// enemy with no line in the log", on a board where a Plan carry-out prints a
/// line and the Tamakushi Casket names itself inside the beat it lands in.
///
/// WHAT IS PINNED HERE is <see cref="Round22Tests"/>' rule: a number in this
/// mod needs a live `CombatState` (the README's headless boundary), so a face
/// is read off its own `Localization` and a rule is read off the calls its
/// site makes. NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class Round24Tests
{
    private const BindingFlags All = HeadlessGame.All;

    // ==================================================================
    // `EB-653` -- the cap prints on the two badges that hold the Plans
    // ==================================================================

    [Fact]
    public void A_declared_cap_prints_its_rule_on_both_badges()
    {
        // The sentence the round asked for, in the words the packet's sec.4
        // item 1 uses, on the two surfaces that describe holding Plans: the
        // jellyfish's own marker and the `Plan` badge that counts them.
        WithCap("2", () =>
        {
            const string sentence =
                "Carries out at most 2 a turn; the rest wait in order.";
            Assert.Contains(sentence, Description<ProtoBakeKuragePower>());
            Assert.Contains(sentence, Description<PendingPlansPower>());
        });
    }

    [Fact]
    public void And_an_unconfigured_build_prints_nothing_extra()
    {
        // ZERO IS THE DEFAULT AND ZERO IS UNLIMITED (`EB-643`, R265), so a
        // lane that did not ask for the trial must not be told about it.
        // Seen to FAIL: with `CapSentence` returning the sentence
        // unconditionally, both of these go.
        WithCap(null, () =>
        {
            Assert.DoesNotContain("at most", Description<ProtoBakeKuragePower>());
            Assert.DoesNotContain("at most", Description<PendingPlansPower>());
            Assert.Equal(string.Empty, KokomiPlan.CapSentence);
        });
    }

    [Fact]
    public void The_cap_reads_its_own_number_and_not_a_literal()
    {
        // The number in the sentence is `PlanCap`'s, so a lane that declares
        // 3 is told 3 -- the whole point of a rule that prints where it binds.
        WithCap("3", () =>
            Assert.Contains("at most 3 a turn", KokomiPlan.CapSentence));
    }

    [Fact]
    public void The_sentence_is_spelled_once_for_both_faces()
    {
        // One format string in `KokomiPlan`, appended by both badges: two
        // spellings is how two surfaces come to disagree about one rule, and
        // it is also what `lint_text_conventions` reads to measure the capped
        // face.
        Assert.Contains("CapSentenceFormat",
                        Source("Powers/Prototype/KokomiPlan.cs"));
        Assert.Contains("KokomiPlan.CapSentence",
                        Source("Powers/Prototype/ProtoBakeKuragePower.cs"));
    }

    // ==================================================================
    // `EB-654` -- a Companion summon's hit writes the log's own line
    // ==================================================================

    [Fact]
    public void A_summons_line_is_the_source_and_the_number()
    {
        // The words the seats already read -- a carry-out's "Ambush, 12" and a
        // rider's "Tamakushi Casket 2" -- with no `Bake-Kurage:` prefix,
        // because the jellyfish did not do this.
        // Through reflection, this suite's standing call for an internal:
        // the mod carries no `InternalsVisibleTo`.
        Assert.Equal("Sesshou Sakura, 10",
                     typeof(KokomiPlan).GetMethod("SummonLine", All)!
                         .Invoke(null, new object[] { "Sesshou Sakura", 10 }));
    }

    [Fact]
    public void A_summons_hit_is_measured_off_the_board_and_filed()
    {
        // The number is what the BOARD lost across the volley -- the same
        // measurement a Plan's own receipt takes -- so a hit into Vulnerable
        // and a reaction it set off are inside it, and a volley that granted
        // only Block files nothing.
        var calls = Il.Calls(typeof(KokomiPlan).GetMethod("Summon", All)!);
        Assert.Contains(calls, c => c.Contains("KokomiPlan.BoardHp"));
        Assert.Contains(calls, c => c.Contains("KokomiPlan.Moved"));
        Assert.Contains(calls, c => c.Contains("KokomiPlan.RecordSummon"));
        Assert.Contains(calls, c => c.Contains("KokomiPlan.SummonLine"));
    }

    [Fact]
    public void The_log_survives_the_turn_boundary_it_is_read_across()
    {
        // A summon fires at the END of the turn and `ResolveAll` clears the
        // morning's list at the START of the next one, so a row filed with
        // the carry-outs would be written after the last page of one turn and
        // erased before the first page of the next. This list is emptied
        // where the volleys FIRE instead.
        //
        // Seen to FAIL: with the clear moved into `ResolveAll`, the second
        // assertion goes.
        var walk = Il.Calls(Il.Method("CompanionOverhaulTurnEnd",
                                      "AfterSideTurnEnd"));
        Assert.Contains(walk, c => c.Contains("KokomiPlan.OpenSummonLog"));
        Assert.DoesNotContain(
            Il.Calls(typeof(KokomiPlan).GetMethod("ResolveAll", All)!),
            c => c.Contains("OpenSummonLog"));
    }

    [Fact]
    public void Every_end_of_turn_actor_goes_through_the_one_door()
    {
        // Sixteen actors, one wrapper: instrumenting sixteen volley bodies is
        // sixteen chances to forget one, and an actor added later joins the
        // log by being called through this door. So no bare `await x.FireVolley`
        // or `await x.Tick(choiceContext)` may remain in the walk.
        var walk = TurnEndWalk();
        Assert.DoesNotContain("await sakura.FireVolley(choiceContext);", walk);
        Assert.Empty(System.Text.RegularExpressions.Regex.Matches(
            walk, @"await \w+\.(FireVolley|Tick)\(choiceContext\);"));
        // And every one of them is wrapped: thirteen volleys plus the three
        // ticks that take a context.
        Assert.Equal(16, System.Text.RegularExpressions.Regex.Matches(
            walk, @"await Act\(creature, ").Count);
    }

    [Fact]
    public void The_wire_carries_the_summon_log_beside_the_carry_outs()
    {
        // The key `understudy/blindplay_board.kokomi_plans` reads. A named
        // literal in `Snapshot`, which is what a headless pin can see.
        Assert.Contains("summon_hits",
                        Il.Strings(typeof(KokomiPlan)
                            .GetMethod("Snapshot", All)!));
    }

    // ------------------------------------------------------------ helpers --

    /// <summary>Run <paramref name="body"/> with the lane's cap declared (or
    /// not), and put the environment back afterwards. `ResetAll` is what
    /// clears `PlanCap`'s once-per-session cache (`EB-643`).</summary>
    private static void WithCap(string? cap, Action body)
    {
        var was = Environment.GetEnvironmentVariable("GITS_KOKOMI_PLAN_CAP");
        try
        {
            Environment.SetEnvironmentVariable("GITS_KOKOMI_PLAN_CAP", cap);
            KokomiPlan.ResetAll();
            body();
        }
        finally
        {
            Environment.SetEnvironmentVariable("GITS_KOKOMI_PLAN_CAP", was);
            KokomiPlan.ResetAll();
        }
    }

    /// <summary>A power's printed face. `KurageBuffFaceTests`' idiom: the
    /// model is allocated uninitialised because its real constructor
    /// registers with the game's model tables, and `Localization` is a pure
    /// string builder that reads nothing off the instance.</summary>
    private static string Description<T>() where T : notnull
    {
        var model = RuntimeHelpers.GetUninitializedObject(typeof(T));
        var rows = (List<(string, string)>)model.GetType()
            .GetProperty("Localization", All)!
            .GetValue(model)!;
        return rows.First(r => r.Item1 == "description").Item2;
    }

    /// <summary>The body of `CompanionOverhaulTurnEnd.AfterSideTurnEnd`, read
    /// out of the source: the pin is about which CALL each actor is reached
    /// through, and the walk is one method.</summary>
    private static string TurnEndWalk()
    {
        var src = Source("Powers/Prototype/CompanionOverhaulPowers.cs");
        var start = src.IndexOf("public override async Task AfterSideTurnEnd(",
                                StringComparison.Ordinal);
        Assert.True(start > 0);
        var end = src.IndexOf("private static Task Act(", start,
                              StringComparison.Ordinal);
        Assert.True(end > start);
        return src.Substring(start, end - start);
    }

    /// <summary>A source file under `klee-mod/KleeCode`.
    /// <see cref="Round22Tests"/>' helper, verbatim.</summary>
    private static string Source(string relativePath) =>
        Read(System.IO.Path.Combine("klee-mod", "KleeCode",
            relativePath.Replace('/', System.IO.Path.DirectorySeparatorChar)));

    private static string Read(string relative)
    {
        var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = System.IO.Path.Combine(dir.FullName, relative);
            if (System.IO.File.Exists(candidate))
            {
                return System.IO.File.ReadAllText(candidate);
            }

            dir = dir.Parent;
        }

        throw new System.IO.FileNotFoundException(relative);
    }
}
