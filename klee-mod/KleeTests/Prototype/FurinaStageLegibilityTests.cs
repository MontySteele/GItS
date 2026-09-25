using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- THE LEGIBILITY PASS (2026-09-25).
///
/// THE FIND. The owner's friend played the arm in co-op on 0.2.3737+proto and
/// "found it very hard to understand what was going on from the tooltips, such
/// as what each summoned actor actually did", and "Double Casting doesn't seem
/// to do anything when all 3 minion slots are already filled". So:
///
///   * a random summon on a full stage works like a Defect orb ([USER]'s
///     rule): the lead takes a Bow and moves to the back seat, keeping its
///     Fanfare;
///   * every summoning card carries a Summon tip and each performer's tip;
///   * each performer's BODY wears a quiet badge saying what it does, the way
///     the base game gives Osty <c>DieForYouPower</c>;
///   * Furina wears a <c>The Stage</c> badge with the board's rules.
///
/// Pinned headlessly where the ledger answers and structurally where the verb
/// needs a live combat (a bow's Block, a body's fielding).
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype arm's arithmetic.
/// </summary>
public class FurinaStageLegibilityTests
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

    private static (Seat Seat, FurinaStageLedger Stage) Full() => Stage(
        (StagePerformer.Usher, 5), (StagePerformer.Chevalmarin, 2),
        (StagePerformer.Crabaletta, 4));

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

    // ---- the full-stage summon: the ledger's half -------------------------

    [Fact]
    public void A_full_stage_bows_the_lead_off_and_the_other_two_step_forward()
    {
        using var _ = new Arm();
        var (_, stage) = Full();

        var leaver = stage.BowFromFront();

        Assert.NotNull(leaver);
        Assert.Equal(StagePerformer.Usher, leaver!.Who);
        Assert.Equal(5, leaver.Fanfare);
        Assert.Equal(
            new[] { StagePerformer.Chevalmarin, StagePerformer.Crabaletta },
            stage.Seats.Select(s => s.Who).ToArray());
        var leave = stage.Beats.Last();
        Assert.Equal("leave", leave.Event);
        Assert.Equal("recast", leave.Reason);
        Assert.Equal(5, leave.Moved);
    }

    [Fact]
    public void The_lead_comes_back_to_the_back_seat_keeping_its_fanfare()
    {
        using var _ = new Arm();
        var (_, stage) = Full();

        var leaver = stage.BowFromFront()!;
        Seat.Set(leaver, "Resting", true);   // a returnee that bows again
        Assert.True(stage.RecastToBack(leaver));

        Assert.Equal(
            new[] { StagePerformer.Chevalmarin, StagePerformer.Crabaletta,
                    StagePerformer.Usher },
            stage.Seats.Select(s => s.Who).ToArray());
        Assert.Equal(new[] { 2, 4, 5 },
                     stage.Seats.Select(s => s.Fanfare).ToArray());
        // The SAME seat, so the same body walks to the back.
        Assert.Same(leaver, stage.Back);
        // It acts at the end of the turn like everyone else (`EB-738`).
        Assert.False(stage.Back!.Resting);
        var arrive = stage.Beats.Last();
        Assert.Equal("arrive", arrive.Event);
        Assert.Equal(5, arrive.Fanfare);
        Assert.Equal(2, arrive.Seat);
    }

    [Fact]
    public void A_stage_that_is_not_full_bows_nobody()
    {
        using var _ = new Arm();
        var (_, stage) = Stage(
            (StagePerformer.Usher, 5), (StagePerformer.Chevalmarin, 2));

        Assert.Null(stage.BowFromFront());
        Assert.Equal(2, stage.Seats.Count);
    }

    // ---- the full-stage summon: the verb's half ---------------------------

    [Fact]
    public void A_random_summon_on_a_full_stage_recasts_the_lead()
    {
        var calls = Il.Calls(Il.Method("FurinaStage", "Summon"));
        Assert.Contains("FurinaStageLedger.get_IsFull", calls);
        Assert.Contains("FurinaStage.RecastFromFront", calls);
    }

    [Fact]
    public void The_recast_bows_then_reads_then_arrives()
    {
        // THE ORDER IS BOW, READERS, ARRIVAL -- `AfterBow`'s own "applause
        // then return" -- so Thunderous Applause's Raise lands on the stage
        // of two the bow left, and the lead arrives after it holding its bar.
        var sequence = Il.CallSequence(Il.Method("FurinaStage",
                                                 "RecastFromFront"));
        var bowOff = sequence.ToList().IndexOf("FurinaStageLedger.BowFromFront");
        var bow = sequence.ToList().IndexOf("FurinaStage.Bow");
        var back = sequence.ToList().IndexOf("FurinaStageLedger.RecastToBack");
        var sync = sequence.ToList().IndexOf("FurinaStagePets.Sync");
        Assert.True(bowOff >= 0 && bow > bowOff && back > bow && sync > back,
                    string.Join(", ", sequence));

        // The Bow is a real Bow: its effect and every reader fire, through
        // `Bow` -> `AfterBow` (Thunderous Applause's draw and Raise).
        var after = Il.Calls(Il.Method("FurinaStage", "AfterBow"));
        Assert.Contains("CardPileCmd.Draw", after);
        Assert.Contains("FurinaStage.Raise", after);
    }

    [Fact]
    public void A_five_century_act_does_not_return_the_recast_performer()
    {
        // The summon is already bringing it back; a second return would put
        // two of it on the stage.
        var source = RepoFile(Path.Combine(
            "klee-mod", "KleeCode", "Powers", "Prototype", "FurinaStage.cs"));
        var recast = Between(source,
                             "private static async Task RecastFromFront(",
                             "public static void SceneChange(");
        Assert.Contains("mayReturn: false", recast);
        Assert.Contains("StageDeparture.Spent", recast);
        Assert.DoesNotContain("Perform(", recast);
    }

    [Fact]
    public void A_named_summon_is_unchanged_and_raises_on_a_performer_it_finds()
    {
        var source = RepoFile(Path.Combine(
            "klee-mod", "KleeCode", "Powers", "Prototype", "FurinaStage.cs"));
        var summon = Between(source,
                             "public static async Task Summon(",
                             "private static async Task RecastFromFront(");
        Assert.Contains("ledger.RaiseSeat(already, ifPresentRaise);", summon);
    }

    // ---- the tips ---------------------------------------------------------

    private static string Printed(string method) => string.Concat(
        Il.Strings(typeof(ArmKeywordTips).GetMethod(method, HeadlessGame.All)!));

    [Fact]
    public void The_summon_tip_has_a_random_and_a_named_variant()
    {
        // A random summon states the full-stage rule; a named one states only
        // the arrival, because the named Commons' face says what a performer
        // already on stage does ("Raise 3 on him instead").
        var body = Printed("ForSummon");
        Assert.Contains("A performer joins at the back with ", body);
        Assert.Contains(" [gold]Fanfare[/gold]. On a full stage, the lead "
                      + "takes a [gold]Bow[/gold] and moves to the back "
                      + "instead.", body);
        Assert.Contains(" [gold]Fanfare[/gold] and acts at the end of your "
                      + "turn.", body);
        var parameters = typeof(ArmKeywordTips).GetMethod("ForSummon")!
            .GetParameters();
        Assert.Equal("random", parameters.Last().Name);
    }

    [Fact]
    public void Each_performer_tip_and_its_badge_say_the_same_two_sentences()
    {
        // The tip is read in hand, the badge on the body; a player must not be
        // told two things. The badge's canonical face and the tip's literals
        // are compared piece by piece, with the law's numbers between them.
        var usher = Badge<UsherBadgePower>("description");
        Assert.Equal(
            $"End of your turn: gain {FurinaStageLaw.ActUsherBlock} "
          + "[gold]Block[/gold]. [gold]Bow[/gold]: gain "
          + $"{FurinaStageLaw.BowUsherBlock} [gold]Block[/gold].", usher);
        Assert.Contains("End of your turn: gain ", Printed("ForUsher"));
        Assert.Contains(" [gold]Block[/gold]. [gold]Bow[/gold]: gain ",
                        Printed("ForUsher"));

        var cheval = Badge<ChevalmarinBadgePower>("description");
        Assert.Equal(
            $"End of your turn: deal {FurinaStageLaw.ActChevalmarinDamage} "
          + "[gold]Hydro[/gold] damage to ALL enemies. [gold]Bow[/gold]: "
          + "apply [gold]Hydro[/gold] to ALL enemies.", cheval);
        Assert.Contains(" [gold]Hydro[/gold] damage to ALL enemies. "
                      + "[gold]Bow[/gold]: apply [gold]Hydro[/gold] to ALL "
                      + "enemies.", Printed("ForChevalmarin"));

        var crab = Badge<CrabalettaBadgePower>("description");
        Assert.Equal(
            $"End of your turn: deal {FurinaStageLaw.ActCrabalettaDamage} "
          + "[gold]Hydro[/gold] damage to a random enemy. [gold]Bow[/gold]: "
          + $"deal {FurinaStageLaw.BowCrabalettaDamage} [gold]Hydro[/gold] "
          + "damage to a random enemy.", crab);
        Assert.Contains(" [gold]Hydro[/gold] damage to a random enemy. "
                      + "[gold]Bow[/gold]: deal ", Printed("ForCrabaletta"));
    }

    [Fact]
    public void The_badges_are_titled_with_the_ledgers_names()
    {
        Assert.Equal("Gentilhomme Usher", Badge<UsherBadgePower>("title"));
        Assert.Equal("Surintendante Chevalmarin",
                     Badge<ChevalmarinBadgePower>("title"));
        Assert.Equal("Mademoiselle Crabaletta",
                     Badge<CrabalettaBadgePower>("title"));
        Assert.Equal(FurinaStageLedger.DisplayName(StagePerformer.Usher),
                     Badge<UsherBadgePower>("title"));
        Assert.Equal("The Stage", Badge<StageSummaryPower>("title"));
    }

    [Fact]
    public void The_stage_badge_is_the_ruled_text()
    {
        Assert.Equal(
            "Performers act at the end of your turn. Attacks hit your "
          + "[gold]Block[/gold], then the lead performer's "
          + "[gold]Fanfare[/gold], then you.",
            Badge<StageSummaryPower>("description"));
    }

    // ---- the badges change no number --------------------------------------

    [Fact]
    public void Every_badge_is_a_quiet_numberless_buff()
    {
        // `DieForYouPower`'s shape for Osty: Single (no amount on the badge,
        // so the wire's DisplayAmount is a constant 1), a Buff, no VFX.
        foreach (var type in new[] { typeof(UsherBadgePower),
                                     typeof(ChevalmarinBadgePower),
                                     typeof(CrabalettaBadgePower),
                                     typeof(StageSummaryPower) })
        {
            var power = (PowerModel)RuntimeHelpers.GetUninitializedObject(type);
            Assert.Equal(PowerStackType.Single, power.StackType);
            Assert.Equal(PowerType.Buff, power.Type);
            Assert.False(power.ShouldPlayVfx);
            // No hook: a badge is text on a body. Only the model's own
            // members are declared here -- nothing a combat hook calls.
            var hooks = type.GetMethods(BindingFlags.Instance
                                        | BindingFlags.Public
                                        | BindingFlags.DeclaredOnly)
                .Where(m => m.Name.StartsWith("After", StringComparison.Ordinal)
                         || m.Name.StartsWith("Before", StringComparison.Ordinal)
                         || m.Name.StartsWith("Modify", StringComparison.Ordinal));
            Assert.Empty(hooks);
        }
    }

    [Fact]
    public void A_performers_badge_reads_this_turns_arkhe_multiple()
    {
        using var _ = new Arm();
        var (seat, stage) = Full();

        var usher = PetBadge<UsherBadgePower>(seat);
        var crab = PetBadge<CrabalettaBadgePower>(seat);
        Assert.Equal(FurinaStageLaw.ActUsherBlock, LiveAct(usher));
        Assert.Equal(FurinaStageLaw.ActCrabalettaDamage, LiveAct(crab));

        // Pneuma doubles the Block act and Ousia the damage acts -- the same
        // two multipliers `FurinaStage.Perform` reads.
        stage.ActBlockMultiplier = 2;
        Assert.Equal(2 * FurinaStageLaw.ActUsherBlock, LiveAct(usher));
        Assert.Equal(FurinaStageLaw.ActCrabalettaDamage, LiveAct(crab));
        stage.ActDamageMultiplier = 3;
        Assert.Equal(3 * FurinaStageLaw.ActCrabalettaDamage, LiveAct(crab));

        // The smart face prints the live figure through `{Act}`.
        Assert.Contains("{Act}", Badge<UsherBadgePower>("smartDescription"));
        Assert.Contains("{Act}", Badge<CrabalettaBadgePower>("smartDescription"));
    }

    [Fact]
    public void A_badge_with_no_stage_behind_it_prints_the_law()
    {
        var canonical = (StagePerformerBadge)RuntimeHelpers
            .GetUninitializedObject(typeof(ChevalmarinBadgePower));
        Assert.Equal(FurinaStageLaw.ActChevalmarinDamage, LiveAct(canonical));
    }

    // ---- the wiring -------------------------------------------------------

    [Fact]
    public void Every_fielded_body_is_pinned_its_badge()
    {
        var field = Il.Calls(Il.Method("FurinaStagePets", "Field"));
        Assert.Contains("StagePerformerBadge.Pin", field);
    }

    [Fact]
    public void The_stage_badge_goes_on_at_combat_open_and_every_turn_start()
    {
        Assert.Contains("FurinaStage.InstallBadge",
                        Il.Calls(Il.Method("FurinaStage", "OpenCombat")));
        Assert.Contains("FurinaStage.InstallBadge",
                        Il.Calls(Il.Method("FurinaStageHooks",
                                           "AfterPlayerTurnStart")));
        Assert.Contains("PowerCmd.Apply<StageSummaryPower>",
                        Il.CallSequence(Il.Method("FurinaStage",
                                                  "InstallBadge")));
    }

    [Fact]
    public void Every_badge_wears_an_icon()
    {
        var source = RepoFile(Path.Combine(
            "klee-mod", "KleeCode", "Powers", "KleePowerIcons.cs"));
        foreach (var name in new[] { "UsherBadgePower", "ChevalmarinBadgePower",
                                     "CrabalettaBadgePower",
                                     "StageSummaryPower" })
        {
            Assert.Contains(name + " =>", source);
        }
    }

    // ---- helpers ----------------------------------------------------------

    private static string Badge<T>(string key) where T : PowerModel
    {
        var power = RuntimeHelpers.GetUninitializedObject(typeof(T));
        var rows = (List<(string, string)>)typeof(T)
            .GetProperty("Localization")!.GetValue(power)!;
        return rows.Single(r => r.Item1 == key).Item2;
    }

    /// <summary>A badge on a pet body whose owner is this seat's Furina --
    /// `Seat.WithPower`'s backing-field shape, one creature over.</summary>
    private static T PetBadge<T>(Seat seat) where T : StagePerformerBadge
    {
        var pet = (Creature)RuntimeHelpers.GetUninitializedObject(
            typeof(Creature));
        typeof(Creature).GetField("_petOwner", HeadlessGame.All)!
            .SetValue(pet, seat.Player);
        var power = (T)RuntimeHelpers.GetUninitializedObject(typeof(T));
        typeof(PowerModel).GetField("_owner", HeadlessGame.All)!
            .SetValue(power, pet);
        Seat.Set(power, "IsMutable", true);
        return power;
    }

    private static int LiveAct(StagePerformerBadge badge) =>
        (int)typeof(StagePerformerBadge)
            .GetMethod("LiveAct", HeadlessGame.All)!
            .Invoke(badge, Array.Empty<object>())!;
}
