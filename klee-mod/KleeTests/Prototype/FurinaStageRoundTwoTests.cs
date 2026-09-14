using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- what round one sent back (`EB-737`, `EB-738`,
/// `EB-739`).
///
/// The read is <c>review/active/furina-stage-round-1-2026-09-08.md</c>. Three
/// blind seats played some 550 actions on the arm, and the three rows pinned
/// here are the ones that are about what the CARDS do rather than about what
/// the page draws:
///
///   * `EB-738` -- a summoned performer acts at the END of the turn with the
///     others, never on arrival. Both engines had read the brief's older
///     wording as an act on play, so every summon dealt damage and applied
///     Hydro with nothing on its face and a summon turn performed twice.
///   * `EB-737` -- a Spend rider's two printed numbers fold what the base
///     attack folds. Under Weak, <i>Soloist's Solicitation</i> printed 4 while
///     <i>Curtain Rise</i> printed 7/13; under Frail, <i>Interposition</i>
///     printed 5/10 and gained 3.
///   * `EB-739` -- the Stage's Refill is <i>Rising Applause</i>, since the
///     shipped Power <i>Standing Ovation</i> carries the old name and one seat
///     was offered both in one run (R179, cosmetic).
///
/// TWO OF THE THREE ARE SOURCE PINS, and that is the headless boundary rather
/// than a preference (KleeTests/README.md). <c>FurinaStage.Summon</c> needs a
/// <c>PlayerChoiceContext</c> and a live combat to be called at all, and
/// <c>DynamicVar.UpdateCardPreview</c> reaches <c>CardModel.CombatState</c>;
/// what a pin CAN say is which shape the generator emitted, which is where
/// both defects lived. The arithmetic they guard is the ledger's and is
/// exercised in <see cref="FurinaStageRuleTests"/>.
/// </summary>
public class FurinaStageRoundTwoTests
{
    private static string Source(string relativePath) =>
        RepoFile(relativePath);

    /// <summary>A file from the repo, found by walking up from this test's own
    /// source path -- the idiom <c>GeneratedGuestSpotlightTests</c> and its
    /// neighbours use, so a test run from any working directory reads the same
    /// tree the build compiled.</summary>
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

    private static string Generated(string type) =>
        Source(Path.Combine("klee-mod", "KleeCode", "Cards", "Prototype",
                            "Generated", type + ".cs"));

    // ==================================================================
    // `EB-738`. A SUMMON PERFORMS AT THE END OF THE TURN AND NOT ON ARRIVAL.
    // ==================================================================

    [Fact]
    public void A_summon_does_not_perform_on_arrival()
    {
        // THE ONE CALL THAT MADE IT AN ARRIVAL ACT, gone. `Summon` still
        // awaits, because the bodies do, and the newcomer still performs --
        // through `EndOfTurnActs`, which walks whoever is standing when it
        // fires. That is the whole of rule 3 and it needs no code, which is
        // exactly why its absence has to be pinned: "the rule needs no code"
        // and "the rule was dropped" look identical in a diff.
        var source = Source(Path.Combine(
            "klee-mod", "KleeCode", "Powers", "Prototype", "FurinaStage.cs"));
        var summon = Between(source,
                             "public static async Task Summon(",
                             "public static void SceneChange(");

        Assert.DoesNotContain("Perform(", summon);
        Assert.Contains("ledger.Summon(who);", summon);
        Assert.Contains("EndOfTurnActs", source);
    }

    [Fact]
    public void The_ledger_summon_moves_seats_and_pays_nothing()
    {
        // The rule half a headless pin CAN exercise: a summon is a seat and a
        // bar and no payout, on an empty stage and on a full one.
        using var _ = new StageArm();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();

        var arrived = stage.Summon(StagePerformer.Crabaletta);

        Assert.Equal(StagePerformer.Crabaletta, arrived.Arrived);
        Assert.Equal(FurinaStageLaw.SummonFanfare, arrived.AtFanfare);
        Assert.Null(arrived.Exit);
        Assert.Equal(0, seat.Creature.Block);
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
    // `EB-737`. BOTH NUMBERS OF A SPEND RIDER ARE LIVE.
    // ==================================================================

    [Theory]
    [InlineData("ProtoFsCurtainRise", "FoldedDamageVar", 7, 13, 3)]
    [InlineData("ProtoFsGrandEntrance", "FoldedDamageVar", 10, 20, 4)]
    [InlineData("ProtoFsTidalFlourish", "DamageVar", 5, 9, 3)]
    public void A_spend_riders_two_damage_numbers_are_vars_and_not_literals(
        string type, string varClass, int plain, int branch, int delta)
    {
        // AIMED ARMS FOLD THE TARGET TOO AND AREA ARMS DO NOT, which is the
        // reason the class differs: `FoldedDamageVar` adds the aimed body's
        // terms on top of the dealer's, and one number cannot stand for a
        // board that takes several (`debuff_calc_rider`'s rule, one kit over).
        // Either way the DEALER's side -- her Strength, her Weak -- is the
        // game's own `Hook.ModifyDamage(..., All)` call, which is what
        // Soloist's Solicitation folded while these four did not.
        var source = Generated(type);

        Assert.Contains("{PlainDamage:diff()}", source);
        Assert.Contains("{BranchDamage:diff()}", source);
        Assert.DoesNotContain("{IfUpgraded:show:", source);
        Assert.Contains(
            $"new {varClass}(\"PlainDamage\", {plain}m, ValueProp.Move)",
            source);
        Assert.Contains(
            $"new {varClass}(\"BranchDamage\", {branch}m, ValueProp.Move)",
            source);
        // THE HIT IS UNTOUCHED. Both vars are printed and nothing else; the
        // play stays the play-time `IsUpgraded` swap, so this row moved no
        // rule and can print no number the card does not deal.
        Assert.Contains($"IsUpgraded ? {plain + delta}m : {plain}m", source);
        Assert.Contains($"IsUpgraded ? {branch + delta}m : {branch}m", source);
        // And the smith moves the face with the hit, or the two disagree the
        // first time the card is upgraded.
        Assert.Contains(
            $"DynamicVars[\"PlainDamage\"].UpgradeValueBy({delta}m);", source);
        Assert.Contains(
            $"DynamicVars[\"BranchDamage\"].UpgradeValueBy({delta}m);", source);
    }

    [Fact]
    public void Interpositions_two_block_numbers_are_vars_and_not_literals()
    {
        // The block twin, and the clause round one measured: "Interposition
        // printed 5/10 and gave 3 under Frail". A named `BlockVar` is the
        // game's own var, whose preview runs the block hooks, under a token of
        // its own so two of them can stand on one face.
        var source = Generated("ProtoFsInterposition");

        Assert.Contains("{PlainBlock:diff()}", source);
        Assert.Contains("{BranchBlock:diff()}", source);
        Assert.DoesNotContain("{IfUpgraded:show:", source);
        Assert.Contains("new BlockVar(\"PlainBlock\", 5m, ValueProp.Move)",
                        source);
        Assert.Contains("new BlockVar(\"BranchBlock\", 10m, ValueProp.Move)",
                        source);
        Assert.Contains("DynamicVars[\"PlainBlock\"].UpgradeValueBy(3m);",
                        source);
        Assert.Contains("DynamicVars[\"BranchBlock\"].UpgradeValueBy(3m);",
                        source);
        // AND THE CARD STILL CLAIMS ITS BLOCK. The `GainsBlock => true`
        // override existed because a card whose Block sat inside a
        // `conditional` declared no BlockVar and BaseLib's auto-detect could
        // not see it (`EB-84`). It declares two now, so the auto-detect is the
        // answer and the override is gone -- Nimble's eligibility is
        // unchanged either way, which is the only thing that reads it.
        Assert.DoesNotContain("GainsBlock", source);
    }

    // ==================================================================
    // `EB-739`. RISING APPLAUSE.
    // ==================================================================

    [Fact]
    public void The_stages_refill_is_rising_applause()
    {
        // The id does NOT move -- a rename is cosmetic (R179) and an id is the
        // seam every table in both engines is keyed on. Only the printed name
        // changes, so no two offerable faces share one.
        var source = Generated("ProtoFsStandingOvation");

        Assert.Contains("(\"title\", \"Rising Applause\")", source);
        Assert.Contains("id=proto_fs_standing_ovation", source);
        Assert.DoesNotContain("\"Standing Ovation\"", source);
    }

    // ==================================================================
    // `EB-736`. THE OFFER IS STAGE-ONLY.
    // ==================================================================

    [Fact]
    public void The_filter_finds_the_retired_rows_by_text_and_not_by_a_list()
    {
        // ROUND ONE'S SECOND FINDING. Batch one swaps fourteen rows and no
        // more, so the draft was mixed by construction: seats were offered
        // Encore cards they could never pay, a Fortissimo Guard that never
        // fired on a summon, and a Casting Call whose gloss describes the old
        // three-member Salon. The filter asks every SHIPPED row the question a
        // seat asks of its face -- does it print a word this kit retired --
        // rather than carrying a copy of the sheet that goes stale.
        Assert.True(FurinaStageRoster.ReadsARetiredSystem(
            new global::KleeMod.Cards.Furina.Generated.FortissimoGuard()));
        Assert.True(FurinaStageRoster.ReadsARetiredSystem(
            new global::KleeMod.Cards.Furina.Generated.CastingCall()));
        Assert.True(FurinaStageRoster.ReadsARetiredSystem(
            new global::KleeMod.Cards.Furina.Generated.StandingOvation()));
        Assert.True(FurinaStageRoster.ReadsARetiredSystem(
            new global::KleeMod.Cards.Furina.Generated.HouseCall()));

        // A plain row survives: nothing about "Deal 6 damage" reads a system
        // this kit does not have.
        Assert.False(FurinaStageRoster.ReadsARetiredSystem(
            new global::KleeMod.Cards.Furina.Generated.SoloistsSolicitation()));
        Assert.False(FurinaStageRoster.ReadsARetiredSystem(
            new global::KleeMod.Cards.Furina.Generated.StagePresence()));
    }

    [Fact]
    public void The_arms_own_rows_are_never_asked()
    {
        // EVERY `proto_fs_` FACE PRINTS `Fanfare` -- it is the bar's name
        // (rule 1) -- so a filter that asked them the same question would
        // empty the arm's own offer. The namespace is the whole test, and a
        // release build compiles none of those types at all.
        Assert.False(FurinaStageRoster.ReadsARetiredSystem(
            new global::KleeMod.Cards.Prototype.Generated.ProtoFsStandingOvation()));
        Assert.False(FurinaStageRoster.ReadsARetiredSystem(
            new global::KleeMod.Cards.Prototype.Generated.ProtoFsCurtainRise()));
    }

    [Fact]
    public void With_the_arm_off_the_offer_is_byte_for_byte_the_shipped_offer()
    {
        // The acceptance condition the whole quarantine rests on. Nothing in
        // this row may reach a board that did not ask for the arm.
        using var _ = new StageArm();
        FurinaStage.Enabled = false;
        var shipped = new CardModel[]
        {
            new global::KleeMod.Cards.Furina.Generated.FortissimoGuard(),
            new global::KleeMod.Cards.Furina.Generated.SoloistsSolicitation(),
        };

        Assert.Equal(shipped,
                     FurinaStageRoster.SwapOfferedRows(shipped).ToArray());
    }

    [Fact]
    public void With_the_arm_on_the_retired_rows_leave_and_the_count_is_kept()
    {
        using var _ = new StageArm();
        var offered = new CardModel[]
        {
            new global::KleeMod.Cards.Furina.Generated.FortissimoGuard(),
            new global::KleeMod.Cards.Furina.Generated.CastingCall(),
            new global::KleeMod.Cards.Furina.Generated.SoloistsSolicitation(),
        };

        // `DropRetiredRows` AND NOT `SwapOfferedRows`, and it is the headless
        // boundary rather than a narrower claim: the outer method reaches
        // `ModelDb` for the fourteen rows it concatenates on, and this harness
        // registers no models (KleeTests/README.md). What the filter DROPS is
        // the whole of this row.
        var result = FurinaStageRoster.DropRetiredRows(offered).ToList();

        Assert.Equal(2, FurinaStageRoster.LastRetiredCount);
        Assert.DoesNotContain(
            result,
            card => card is global::KleeMod.Cards.Furina.Generated
                        .FortissimoGuard
                        or global::KleeMod.Cards.Furina.Generated.CastingCall);
        Assert.Contains(
            result,
            card => card is global::KleeMod.Cards.Furina.Generated
                .SoloistsSolicitation);
    }

    // ==================================================================
    // `EB-735`. THE STAGE ON THE WIRE.
    // ==================================================================

    [Fact]
    public void The_snapshot_carries_every_seat_with_its_index_and_its_bar()
    {
        using var _ = new StageArm();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        stage.Summon(StagePerformer.Usher);
        stage.Summon(StagePerformer.Chevalmarin);
        stage.Summon(StagePerformer.Crabaletta);
        stage.Raise(5);                       // the BACK seat, rule 5

        var snapshot = FurinaStageLedger.Snapshot(seat.Player);
        var seats = ((IEnumerable<object?>)snapshot["seats"]!)
            .Cast<Dictionary<string, object?>>().ToList();

        Assert.Equal(true, snapshot["live"]);
        Assert.Equal(new object?[] { 0, 1, 2 },
                     seats.Select(row => row["seat"]).ToArray());
        Assert.Equal(new object?[] { "usher", "chevalmarin", "crabaletta" },
                     seats.Select(row => row["member"]).ToArray());
        Assert.Equal("Gentilhomme Usher", seats[0]["name"]);
        // The Raise landed on the back-most and nowhere else.
        Assert.Equal(FurinaStageLaw.SummonFanfare, seats[0]["fanfare"]);
        Assert.Equal(FurinaStageLaw.SummonFanfare + 5, seats[2]["fanfare"]);
    }

    [Fact]
    public void A_klee_gets_the_empty_map_and_an_empty_stage_a_full_one()
    {
        // THE THREE-STATE CONTRACT. An empty map is "the rule is here and this
        // seat is not playing it"; a populated map with no seats is "the stage
        // is empty", which is the fact a seat about to spend a rider most
        // needs and the one an absent key cannot state.
        using var _ = new StageArm();
        Assert.Empty(FurinaStageLedger.Snapshot(
            Seat.Klee().WithCombatState().Player));

        var furina = Seat.Furina().WithCombatState();
        FurinaStageLedger.For(furina.Creature).Clear();
        var snapshot = FurinaStageLedger.Snapshot(furina.Player);

        Assert.Equal(true, snapshot["live"]);
        Assert.Empty((IEnumerable<object?>)snapshot["seats"]!);
    }

    [Fact]
    public void The_log_files_one_beat_per_arrival_departure_and_rotation()
    {
        using var _ = new StageArm();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        stage.OpenWith(StagePerformer.Usher);        // the relic's arrival
        stage.SceneChange();                         // a pure reorder
        stage.Summon(StagePerformer.Chevalmarin);
        stage.Spend(99);                             // empties the lead: a bow

        var log = FurinaStageLedger.Snapshot(seat.Player)["log"];
        var rows = ((IEnumerable<object?>)log!)
            .Cast<Dictionary<string, object?>>().ToList();

        Assert.Equal(new object?[] { "arrive", "rotate", "arrive", "leave" },
                     rows.Select(row => row["event"]).ToArray());
        // A DEPARTURE SAYS WHY, because that is the whole of rules 7 and 9: a
        // bow is earned by Spend and by nothing else, and the page prints the
        // difference.
        Assert.Equal("spend", rows[^1]["reason"]);
        Assert.Equal("usher", rows[^1]["member"]);
    }

    [Fact]
    public void The_log_clears_on_a_turn_boundary_and_the_stage_does_not()
    {
        using var _ = new StageArm();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        stage.Summon(StagePerformer.Usher);
        Assert.NotEmpty(stage.Beats);

        stage.ClearBeats();

        Assert.Empty(stage.Beats);
        // And the stage itself is untouched: the log is a receipt, not state.
        Assert.Single(stage.Seats);
    }

    private static string Between(string source, string from, string to)
    {
        var start = source.IndexOf(from, StringComparison.Ordinal);
        Assert.True(start >= 0, $"not found: {from}");
        var end = source.IndexOf(to, start, StringComparison.Ordinal);
        Assert.True(end > start, $"not found after {from}: {to}");
        return source[start..end];
    }
}
