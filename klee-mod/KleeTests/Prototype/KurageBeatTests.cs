using System.Collections;
using System.Linq;
using System.Reflection;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-316` and `EB-317`: THE BAKE-KURAGE'S BEAT.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, the split every prototype pin in
/// this directory makes. The LINE is real -- <c>KurageBeat.Line</c> is a pure
/// function over a string and a nullable int, so the ruled format
/// ("Bake-Kurage: Ambush, 12") is asserted by calling it. The WIRE'S SHAPE is
/// real for everything that does not need a live <c>Player</c>. Everything
/// else is a call-set pin, because the beat itself is three engine commands
/// against a combat scene and a creature node, which is outside the headless
/// boundary (KleeTests/README.md): a speech bubble needs a vfx container and
/// an animation needs a creature node, and neither exists in `dotnet test`.
///
/// WHY THE ORDER IS PINNED AND NOT JUST THE CALLS. Both rows are defects of
/// TIMING, not of arithmetic. The casket's 2 Hydro was always correct; it
/// arrived in the same frame as the card that caused it, so its damage number
/// landed on top of the card's own and the two read as one hit. A pin that
/// only said "Strike calls Act" would stay green if a refactor moved the lunge
/// after the hit, which is the exact state the row is open on. So the pins
/// below read <see cref="Il.CallSequence"/> and compare indices.
/// </summary>
public class KurageBeatTests
{
    private static Assembly Mod => typeof(KokomiPlan).Assembly;

    private static MethodBase Beat(string name) => Il.Method("KurageBeat", name);

    private static int First(System.Collections.Generic.IReadOnlyList<string> calls,
                             string needle)
    {
        for (var i = 0; i < calls.Count; i++)
        {
            if (calls[i] == needle) return i;
        }
        return -1;
    }

    /// <summary>
    /// How many `finally` blocks an async method's body carries (`EB-329`).
    ///
    /// An async method compiles to a state machine and the real body is
    /// `MoveNext`, so that is what is counted. The compiler's own machinery
    /// wraps the whole thing in a CATCH -- it has to set the exception on the
    /// task builder -- and never in a Finally, so a Finally clause here is
    /// user-written. Local to this file rather than in `Il`, because it is
    /// one row's question and not a harness the rest of the suite asks.
    /// </summary>
    private static int Finallys(MethodBase method)
    {
        var machine = method
            .GetCustomAttribute<System.Runtime.CompilerServices
                .AsyncStateMachineAttribute>()?.StateMachineType;
        var body = (machine?.GetMethod("MoveNext", HeadlessGame.All) ?? method)
            .GetMethodBody();
        return body?.ExceptionHandlingClauses.Count(
            c => c.Flags == ExceptionHandlingClauseOptions.Finally) ?? 0;
    }

    // ---- THE LINE, real ---------------------------------------------------

    [Fact]
    public void The_carry_out_line_is_the_ruled_format()
    {
        // The row's own words: `"Bake-Kurage: Ambush, 12"`.
        var line = Beat("Line").Invoke(null, new object[] { "Ambush", 12 });
        Assert.Equal("Bake-Kurage: Ambush, 12", line);
    }

    [Fact]
    public void A_clause_with_no_number_says_the_card_name_alone()
    {
        // "if a clause has no number, the card name alone" -- Moon's
        // Reflection's replay and Nereid's window are the two that produce
        // none, and a trailing comma with nothing after it is worse than no
        // number at all.
        var line = Beat("Line").Invoke(null, new object[] { "Stolen Chapter", null });
        Assert.Equal("Bake-Kurage: Stolen Chapter", line);
    }

    [Fact]
    public void The_pet_is_spelled_the_way_the_conventions_page_spells_it()
    {
        // `text-conventions.md`: always "Bake-Kurage", never "the jellyfish".
        // One constant, so the bubble, the page and the strip cannot drift.
        var name = Mod.GetTypes().Single(t => t.Name == "KurageBeat")
            .GetField("PetName", HeadlessGame.All)
            .GetRawConstantValue();
        Assert.Equal("Bake-Kurage", name);
    }

    // ---- THE CASKET (`EB-316`), structural --------------------------------

    [Fact]
    public void The_casket_lunges_and_names_itself_before_the_hit_lands()
    {
        var calls = Il.CallSequence(Il.Method("TamakushiCasket", "Strike"));
        var act = First(calls, "KurageBeat.Act");
        var say = First(calls, "KurageBeat.Say");
        var deal = First(calls, "ElementalHit.Deal");
        Assert.True(act >= 0, "the jellyfish does not animate");
        Assert.True(say >= 0, "nothing names the source on screen");
        Assert.True(deal >= 0, "the strike is gone");
        // THE WHOLE ROW IS THIS INEQUALITY. Both surfaces come BEFORE the hit,
        // which is what puts the hit's own damage number on its own frame
        // rather than inside the card's.
        Assert.True(act < deal, "the lunge must come before the strike");
        Assert.True(say < deal, "the line must come before the strike");
    }

    [Fact]
    public void The_line_the_casket_says_names_the_relic()
    {
        // A SECOND SPELLING OF THE RELIC'S TITLE is unavoidable --
        // `lint_unique_names.py` reads relic names out of the literal in the
        // `("title", "...")` tuple and nowhere else -- so the two are pinned
        // together here instead. A rename that edits one is red.
        var casket = Mod.GetTypes().Single(t => t.Name == "TamakushiCasket");
        var source = (string)casket.GetField("SourceName", HeadlessGame.All)
            .GetRawConstantValue();
        Assert.Contains(
            source, Il.Strings(Il.Method("TamakushiCasket", "get_Localization")));
        Assert.Contains("KurageBeat.Line",
                        Il.Calls(Il.Method("TamakushiCasket", "Strike")));
    }

    // ---- THE MORNING (`EB-317`), structural -------------------------------

    [Fact]
    public void Each_plan_carried_out_makes_the_pet_act_before_its_clauses()
    {
        var calls = Il.CallSequence(Il.Method("KokomiPlan", "ResolveEntry"));
        var act = First(calls, "KurageBeat.Act");
        var clause = First(calls, "KokomiPlan.ResolveOne");
        Assert.True(act >= 0, "the jellyfish does not act at carry-out");
        Assert.True(clause >= 0, "the clauses are gone");
        Assert.True(act < clause, "the pet acts, THEN the Plan lands");
        Assert.Contains("KokomiPlan.Announce", calls);
    }

    [Fact]
    public void The_announcement_says_the_line_and_records_it()
    {
        var calls = Il.Calls(Il.Method("KokomiPlan", "Announce"));
        Assert.Contains("KurageBeat.Line", calls);
        Assert.Contains("KurageBeat.Say", calls);
    }

    [Fact]
    public void The_strip_empties_one_entry_at_a_time_and_draws_the_drain()
    {
        // The seat report was "the panel simply reads empty". Two halves:
        // the strip reads `Showing` (the morning's remaining Plans) rather
        // than `Pending` (the real queue, empty for the whole drain), and the
        // drain refreshes it per entry rather than once.
        Assert.Contains("KokomiPlan.Showing",
                        Il.Calls(Il.Method("KokomiPlanStrip", "Paint")));
        var drain = Il.CallSequence(Il.Method("KokomiPlan", "ResolveAll"));
        Assert.True(drain.Count(c => c == "KokomiPlanStrip.Refresh") >= 2,
                    "the strip is redrawn once per Plan, not once per morning");
    }

    [Fact]
    public void The_morning_still_mints_exactly_one_ledger_row()
    {
        // `R101b` and `KokomiPlanLedgerTests`: the drain's price is ONE note of
        // the whole depth. The display list exists precisely so the strip can
        // shorten per entry WITHOUT the queue -- and therefore the ledger --
        // moving per entry. A second `Sync` in this method would be a second
        // row on a published instrument.
        var drain = Il.CallSequence(Il.Method("KokomiPlan", "ResolveAll"));
        Assert.Equal(1, drain.Count(c => c == "KokomiPlan.Sync"));
    }

    // ---- THE WIRE (`EB-317`), real where it can be --------------------------

    [Fact]
    public void The_snapshot_carries_the_carry_out_lines()
    {
        var snapshot = Il.Method("KokomiPlan", "Snapshot");
        Assert.Contains("KokomiPlan.CarriedOut", Il.Calls(snapshot));
        Assert.Contains("carried_out", Il.Strings(snapshot));
        // The field names ARE the contract with `understudy/blindplay.py`;
        // the bridge (gits/GitsKokomiPlan.cs) hands the dictionary straight
        // through, so a rename here is a silent hole on the page. They live in
        // a NAMED method for exactly this pin -- a lambda's literals sit in a
        // display class no test can name.
        var keys = Il.Strings(Il.Method("KokomiPlan", "CarriedOutRow"));
        Assert.Contains("card", keys);
        Assert.Contains("number", keys);
        Assert.Contains("line", keys);
    }

    [Fact]
    public void One_carried_out_plan_is_a_card_a_number_and_the_sentence()
    {
        var row = Mod.GetTypes().Single(t => t.Name == "CarriedOutPlan");
        Assert.Equal(typeof(string), row.GetProperty("Card").PropertyType);
        Assert.Equal(typeof(string), row.GetProperty("Line").PropertyType);
        // NULLABLE, because "no number" is a state the format has words for.
        Assert.Equal(typeof(int?), row.GetProperty("Number").PropertyType);
    }

    // ---- `EB-329`: THE MORNING LOG IS THE BOARD ---------------------------

    [Fact]
    public void The_board_is_read_before_the_clauses_and_again_after()
    {
        // STRUCTURAL PIN (Il), and the ORDER is the whole of it: a before-read
        // taken after the clauses would subtract a board from itself and
        // report that nothing happened, which is the state the row is open on
        // by a different route. `Moved` runs on the way out.
        var calls = Il.CallSequence(Il.Method("KokomiPlan", "ResolveEntry"));
        var read = First(calls, "KokomiPlan.BoardHp");
        var clause = First(calls, "KokomiPlan.ResolveOne");
        var subtract = First(calls, "KokomiPlan.Moved");
        Assert.True(read >= 0, "the board is never read");
        Assert.True(clause >= 0, "the clauses are gone");
        Assert.True(subtract >= 0, "nothing subtracts the two reads");
        Assert.True(read < clause, "the BEFORE read must precede the clauses");
        Assert.True(clause < subtract, "the AFTER read must follow them");
    }

    [Fact]
    public void The_line_is_recorded_even_when_a_plan_ends_the_fight()
    {
        // STRUCTURAL, and it is the only shape a headless test can see: a
        // combat that ends inside a clause UNWINDS `ResolveEntry`, so the
        // announcement has to sit on the unwind path. A `finally` in the
        // source is a Finally clause in the async state machine's MoveNext;
        // the compiler's own machinery adds Catch clauses, never a Finally,
        // so one being present is the user-written block.
        //
        // The round-5 act-1 seat banked an exactly lethal morning and got no
        // receipt: "the next screen was the reward screen".
        Assert.True(Finallys(Il.Method("KokomiPlan", "ResolveEntry")) >= 1,
                    "no finally in ResolveEntry -- a fight-ending Plan would "
                  + "unwind past its own announcement");
        Assert.Contains("KokomiPlan.Announce",
                        Il.Calls(Il.Method("KokomiPlan", "ResolveEntry")));
    }

    [Fact]
    public void The_mid_turn_door_goes_through_the_on_play_one()
    {
        // Change of Plans resolves a Plan in the MIDDLE of a turn and the
        // morning drain does not. A bare `true` at the call site is a fact no
        // structural pin can read, so the flag has a named door and the split
        // is in the call graph.
        //
        // ONE DOOR AND NOT TWO SINCE `EB-570`: The Moon Overlooks the Waters
        // was the other, and `Schedule` now only queues -- pinned from that
        // side in `KokomiOverhaulRuleTests`.
        Assert.Contains("KokomiPlan.ResolveNow",
                        Il.Calls(Il.Method("KokomiPlan", "ResolveFront")));
        Assert.DoesNotContain("KokomiPlan.ResolveNow",
                              Il.Calls(Il.Method("KokomiPlan", "Schedule")));
        var morning = Il.Calls(Il.Method("KokomiPlan", "ResolveAll"));
        Assert.Contains("KokomiPlan.ResolveEntry", morning);
        Assert.DoesNotContain("KokomiPlan.ResolveNow", morning);
        // And the parameter it sets defaults to the morning's reading, so a
        // third caller written tomorrow is not silently filed as on-play.
        var flag = Il.Method("KokomiPlan", "ResolveEntry").GetParameters()
                     .Single(p => p.Name == "onPlay");
        Assert.Equal(typeof(bool), flag.ParameterType);
        Assert.Equal(false, flag.DefaultValue);
    }

    [Fact]
    public void The_wire_carries_the_board_reading_and_the_door()
    {
        // The key names ARE the contract with `understudy/blindplay.py`, on
        // `CarriedOutRow`'s own argument: they live in NAMED methods so a
        // headless pin can read the literals.
        var keys = Il.Strings(Il.Method("KokomiPlan", "CarriedOutRow"));
        Assert.Contains("moved", keys);
        Assert.Contains("on_play", keys);
        var moved = Il.Strings(Il.Method("KokomiPlan", "MovedRow"));
        Assert.Contains("target", moved);
        Assert.Contains("combat_id", moved);
        Assert.Contains("amount", moved);
        Assert.Contains("dead", moved);
    }

    [Fact]
    public void One_moved_row_is_a_target_an_id_an_amount_and_a_death()
    {
        var row = Mod.GetTypes().Single(t => t.Name == "MovedOn");
        Assert.Equal(typeof(string), row.GetProperty("Target").PropertyType);
        Assert.Equal(typeof(string), row.GetProperty("CombatId").PropertyType);
        Assert.Equal(typeof(int), row.GetProperty("Amount").PropertyType);
        Assert.Equal(typeof(bool), row.GetProperty("Dead").PropertyType);
        // And the carry-out row carries the list plus the door. The list is
        // NULLABLE: null is "this beat could not be measured" and an empty
        // list is "measured, and no enemy lost HP", which the page reads as
        // two different things.
        var said = Mod.GetTypes().Single(t => t.Name == "CarriedOutPlan");
        Assert.Equal(typeof(bool), said.GetProperty("OnPlay").PropertyType);
        Assert.Equal(
            typeof(System.Collections.Generic.IReadOnlyList<>).MakeGenericType(row),
            said.GetProperty("Moved").PropertyType);
    }

    [Fact]
    public void An_unreadable_board_answers_null_rather_than_a_clean_sweep()
    {
        // REAL, and it is the arithmetic that matters most: `Moved` is handed
        // the before-read and asks for the after-read itself, and a combat
        // torn down between the two would otherwise subtract the whole board
        // from nothing and report every enemy dead of the Plan. Headless
        // there is no combat at all, which is exactly that case.
        var moved = Il.Method("KokomiPlan", "Moved");
        Assert.Null(moved.Invoke(null, new object[] { null, null }));
    }

    [Fact]
    public void A_seat_with_no_player_reads_an_empty_record_not_a_null()
    {
        // Every reader on this wire is entitled to enumerate without a null
        // check, the same promise `Pending` makes.
        foreach (var name in new[] { "CarriedOut", "Showing" })
        {
            var got = Il.Method("KokomiPlan", name).Invoke(null, new object[] { null });
            Assert.NotNull(got);
            Assert.Empty((IEnumerable)got);
        }
    }
}
