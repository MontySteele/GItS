using System;
using System.Collections.Generic;
using System.Globalization;
using KleeMod.Powers;

namespace KleeMod.Diagnostics;

/// <summary>
/// G-A5(a): the C# half of the Fanfare sim-parity check.
///
/// "Run both implementations and diff" is not available and never will be:
/// the two implementations are in two languages and two processes.
/// `klee-mod/KleeTests` (EB-105) does now execute this DLL's arithmetic
/// headlessly, but it cannot run the SIM, so it moves neither half of what
/// follows. The parity claim is assembled from two halves instead:
///
///   * The Python suite
///     (tier0/tests/test_furina_fanfare_parity.py :: test_csharp_vectors_match_the_sim)
///     parses THIS FILE and asserts the tables below are exactly what the sim
///     produces. That is what stops the two copies drifting in the ordinary
///     way -- somebody edits one side.
///   * <see cref="Check"/>, called from KleeSelfCheck at boot, runs the real
///     C# arithmetic (<see cref="FurinaResources.DecayFanfare"/> and
///     <see cref="FurinaResources.GainFanfareFloor"/>'s pure forms) against
///     those same tables and reports any row that disagrees.
///
/// Neither half is load-bearing alone: the first proves the two QUESTION
/// SHEETS match, the second proves this side's ANSWERS match its sheet.
///
/// DO NOT hand-edit the vectors. Regenerate the fixture with
/// `python -m tier0.tests.test_furina_fanfare_parity` and copy the numbers
/// across; the Python test fails loudly until they agree.
///
/// The arithmetic is duplicated here as pure static functions rather than
/// calling the Creature-based API, because the vectors describe values, not
/// combats, and there is no Creature at boot. The duplication is the thing
/// being tested -- <see cref="Check"/> is worthless if it re-implements
/// something other than what FurinaResources does, so the two bodies below
/// are kept deliberately identical to their counterparts and any change to
/// one is a change to both.
/// </summary>
internal static class FurinaParityVectors
{
    /// <summary>Mirrors tier0.constants.FANFARE_DECAY_FRACTION = 0.2.</summary>
    private const double DecayFraction = FurinaResourceConstants.FanfareDecayFraction;

    internal readonly record struct DecayVector(int Before, int Floor, int After);

    internal readonly record struct GrantVector(
        int Before, int Floor, int Cap, int Grant,
        int After, int AfterFloor, int AfterCap);

    /// <summary>(fanfare before, floor, fanfare after one decay).</summary>
    internal static readonly DecayVector[] DecayVectors =
    {
        new(0, 0, 0),
        new(1, 0, 0),
        new(2, 0, 1),
        new(3, 0, 2),
        new(5, 0, 4),
        new(7, 0, 6),
        new(12, 10, 10),
        new(13, 0, 10),
        new(10, 8, 8),
        new(10, 9, 9),
        new(9, 9, 9),
        new(2, 2, 2),
        new(25, 0, 20),
        new(30, 0, 24),
        new(45, 0, 36),
        new(110, 0, 88),
    };

    /// <summary>(before, floor, cap, grant, after, afterFloor, afterCap).</summary>
    internal static readonly GrantVector[] FloorGrantVectors =
    {
        new(0, 0, 40, 5, 5, 5, 45),
        new(38, 0, 40, 5, 43, 5, 45),
        new(40, 0, 40, 8, 48, 8, 48),
        new(12, 5, 45, 8, 20, 13, 53),
        new(0, 15, 55, 5, 5, 20, 60),
        new(20, 10, 50, 15, 35, 25, 65),
    };

    internal readonly record struct RiderVector(
        int Bank, int Per, int Div, int Bonus);

    internal readonly record struct ThresholdVector(
        int Bank, int Bar, bool Holds);

    /// <summary>
    /// Curtain Call's card-body READS: `N_per_M_fanfare` / `N_per_M_encore`
    /// damage riders. Meter-agnostic on purpose -- the arithmetic is the same
    /// whichever bank the formula names, so one table covers both and the
    /// Python side generates the rows for each meter from the same cases.
    ///
    /// What these actually pin is integer division at the step boundaries.
    /// Python's `//` floors; C#'s int `/` truncates. Both banks are
    /// non-negative by construction so the two agree, but that is a fact
    /// worth a fixture rather than a comment: it stops being true the moment
    /// anything can drive a meter below zero.
    /// </summary>
    internal static readonly RiderVector[] RiderVectors =
    {
        new(0, 1, 2, 0),
        new(1, 1, 2, 0),
        new(2, 1, 2, 1),
        new(3, 1, 2, 1),
        new(40, 1, 2, 20),
        new(41, 1, 2, 20),
        new(0, 1, 3, 0),
        new(2, 1, 3, 0),
        new(3, 1, 3, 1),
        new(5, 1, 3, 1),
        new(9, 1, 3, 3),
        new(22, 1, 3, 7),
    };

    /// <summary>
    /// `fanfare_at_least_N` / `encore_at_least_N`. A `>` written where the
    /// sheet says `>=` is a one-character slip that no winrate would surface
    /// and that mis-prices Flood of Emotion's second 14-damage hit.
    /// </summary>
    internal static readonly ThresholdVector[] ThresholdVectors =
    {
        new(19, 20, false),
        new(20, 20, true),
        new(21, 20, true),
        new(0, 20, false),
        new(7, 8, false),
        new(8, 8, true),
        new(9, 8, true),
        new(0, 8, false),
    };

    /// <summary>Pure form of the generated rider expression
    /// (<c>CalculatedDamageVar.WithMultiplier(... bank / div)</c> times the
    /// ExtraDamage term), stated the same way the emitted C# states it.</summary>
    private static int Rider(int bank, int per, int div) => per * (bank / div);

    /// <summary>Pure form of the generated threshold predicate.</summary>
    private static bool Threshold(int bank, int bar) => bank >= bar;

    /// <summary>
    /// Pure form of <see cref="FurinaResources.DecayFanfare"/>. Kept
    /// character-for-character identical to it; see the class remarks.
    /// </summary>
    private static int Decay(int before, int floor)
    {
        if (before <= floor) return before;
        var fall = Math.Max(
            1, (int)Math.Round(before * DecayFraction, MidpointRounding.ToEven));
        return Math.Max(floor, before - fall);
    }

    /// <summary>
    /// Pure form of <see cref="FurinaResources.GainFanfareFloor"/>. The ORDER
    /// is the whole point: the cap takes the grant before the current value is
    /// clamped against it.
    /// </summary>
    private static (int Current, int Floor, int Cap) Grant(
        int before, int floor, int cap, int n)
    {
        floor += n;
        cap += n;
        return (Math.Min(cap, before + n), floor, cap);
    }

    /// <summary>
    /// Runs every vector and returns one human-readable finding per failure.
    /// Never throws: a validator that bricks the boot is the failure mode it
    /// exists to prevent.
    /// </summary>
    public static IEnumerable<string> Check()
    {
        var findings = new List<string>();

        foreach (var v in DecayVectors)
        {
            var got = Decay(v.Before, v.Floor);
            if (got != v.After)
            {
                findings.Add(string.Format(
                    CultureInfo.InvariantCulture,
                    "Fanfare decay parity: {0} on floor {1} -> {2}, sim says {3}",
                    v.Before, v.Floor, got, v.After));
            }
        }

        foreach (var v in FloorGrantVectors)
        {
            var (current, floor, cap) = Grant(v.Before, v.Floor, v.Cap, v.Grant);
            if (current != v.After || floor != v.AfterFloor || cap != v.AfterCap)
            {
                findings.Add(string.Format(
                    CultureInfo.InvariantCulture,
                    "Fanfare floor-grant parity: {0}/floor {1}/cap {2} +{3} -> "
                  + "{4}/{5}/{6}, sim says {7}/{8}/{9}",
                    v.Before, v.Floor, v.Cap, v.Grant,
                    current, floor, cap,
                    v.After, v.AfterFloor, v.AfterCap));
            }
        }

        foreach (var v in RiderVectors)
        {
            var got = Rider(v.Bank, v.Per, v.Div);
            if (got != v.Bonus)
            {
                findings.Add(string.Format(
                    CultureInfo.InvariantCulture,
                    "Fanfare/Encore rider parity: {0} per {1} off a bank of "
                  + "{2} -> {3}, sim says {4}",
                    v.Per, v.Div, v.Bank, got, v.Bonus));
            }
        }

        foreach (var v in ThresholdVectors)
        {
            var got = Threshold(v.Bank, v.Bar);
            if (got != v.Holds)
            {
                findings.Add(string.Format(
                    CultureInfo.InvariantCulture,
                    "Fanfare/Encore threshold parity: bank {0} vs bar {1} -> "
                  + "{2}, sim says {3}",
                    v.Bank, v.Bar, got, v.Holds));
            }
        }

        // No rarity-ordering check here. It was tried and removed: both
        // operands are const, so the compiler proved the comparison false and
        // emitted CS0162 (unreachable code) -- a runtime check on compile-time
        // constants is theatre. The real guard is Python-side, in
        // test_csharp_constants_match_the_sim, which reads the C# literals and
        // compares them to tier0/constants.py. That catches a drifted number,
        // which is the failure that can actually happen.
        return findings;
    }
}
