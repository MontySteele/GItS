using System.Collections.Generic;
using System.Globalization;
using KleeMod.Elements;
using KleeMod.Powers;

namespace KleeMod.Diagnostics;

/// <summary>
/// Errata Batch 2: the C# half of the NON-CARD parity checks (R116).
///
/// Built exactly like <see cref="FurinaParityVectors"/> and for the same
/// reason -- there is no C# test project, so the parity claim is assembled
/// from two halves:
///
///   * The Python suite
///     (tier0/tests/test_noncard_parity_vectors.py :: test_csharp_vectors_match_the_sim)
///     parses THIS FILE and asserts the tables below are exactly what the sim
///     produces. That is what stops the two copies drifting in the ordinary
///     way -- somebody edits one side.
///   * <see cref="Check"/>, called from KleeSelfCheck at boot, runs the real
///     C# arithmetic against those same tables and reports any row that
///     disagrees.
///
/// Neither half is load-bearing alone: the first proves the two QUESTION
/// SHEETS match, the second proves this side's ANSWERS match its sheet.
///
/// DO NOT hand-edit the vectors. Regenerate the fixture with
/// `python -m tier0.tests.test_noncard_parity_vectors` and copy the numbers
/// across; the Python test fails loudly until they agree.
///
/// THE REGISTER THESE TABLES SERVE, recorded by R116 because the two rulings
/// are adjacent, opposite, and will otherwise be misremembered as one:
///
///     Power-sourced DAMAGE runs the damage pipeline (NC-1).
///     Power-sourced BLOCK is raw (NC-11).
/// </summary>
internal static class NonCardParityVectors
{
    /// <summary>
    /// NC-1 (Errata Batch 2 item 3): Strength, then Weak x0.75, then
    /// Vulnerable x1.5, truncated ONCE at the end.
    ///
    /// (amount, strength, weak, vulnerable, dealt). Amounts 6 and 8 are
    /// Durin's Witch's Flame at base and upgraded -- NC-1's own line
    /// evidence, which R116 ruled becomes the regression vector.
    /// </summary>
    internal readonly record struct DamageVector(
        int Amount, int Strength, int Weak, int Vulnerable, int Dealt);

    internal static readonly DamageVector[] PowerDamageVectors =
    {
        new(6, 0, 0, 0, 6),
        new(6, 3, 0, 0, 9),
        new(6, 0, 1, 0, 4),
        new(6, 0, 0, 1, 9),
        new(6, 0, 1, 1, 6),
        new(6, 3, 1, 1, 10),
        new(6, 5, 1, 0, 8),
        new(6, 5, 1, 1, 12),
        new(8, 0, 0, 0, 8),
        new(8, 4, 0, 1, 18),
        new(8, 0, 1, 1, 9),
        new(8, -20, 0, 0, 0),
        new(1, 0, 1, 0, 0),
        new(1, 0, 0, 1, 1),
        new(3, 2, 1, 1, 5),
        new(25, 7, 1, 1, 36),
    };

    /// <summary>
    /// The pure form of what <see cref="SimDamagePipeline"/> does to an
    /// Unpowered power-sourced hit. The duplication is the thing being
    /// tested: this body is kept deliberately identical to
    /// DealerMods/TargetMods, because a Check that re-implemented something
    /// else would be worthless. The reason it cannot simply CALL them is that
    /// they take Creatures and there is no Creature at boot.
    /// </summary>
    private static int Damage(int amount, int strength, int weak, int vulnerable)
    {
        decimal dmg = amount + strength;
        if (weak > 0) dmg *= 0.75m;
        if (dmg < 0m) dmg = 0m;          // tier0 powers._floor, dealer end
        if (vulnerable > 0) dmg *= ReactionConstants.VulnerableTakenMult;
        if (dmg < 0m) dmg = 0m;          // tier0 powers._floor, target end
        return (int)dmg;
    }

    /// <summary>
    /// NC-11 (Errata Batch 2 item 4): power-sourced block is RAW.
    ///
    /// (amount, dexterity, frail, block). Every row carries a Dexterity and a
    /// Frail that WOULD move a card's block, so a row that came back scaled
    /// is a row that went back through the funnel. Amounts are the three
    /// named grants' own numbers -- Metallicize stacks, the Ceremonial
    /// Garment rider, the Kurage pulse plus ward.
    ///
    /// The C# side of this one is not arithmetic, it is a FLAG: the three
    /// grants pass <c>ValueProp.Unpowered</c>, which is the predicate
    /// FrailPower's multiplicative hook and DexterityPower's additive hook
    /// both gate on. <see cref="Check"/> can therefore only verify that the
    /// table says what the sim says; that the grants carry the right flag is
    /// verified by reading the three call sites, which is what the ruling's
    /// own citation does.
    /// </summary>
    internal readonly record struct BlockVector(
        int Amount, int Dexterity, int Frail, int Block);

    internal static readonly BlockVector[] PowerBlockVectors =
    {
        new(5, 0, 0, 5),
        new(5, 3, 0, 5),
        new(5, 0, 1, 5),
        new(5, 3, 1, 5),
        new(2, 2, 1, 2),
        new(8, -2, 0, 8),
        new(0, 4, 1, 0),
        new(12, 5, 1, 12),
    };

    /// <summary>
    /// Runs every vector and returns one human-readable finding per failure.
    /// Never throws: a validator that bricks the boot is the failure mode it
    /// exists to prevent.
    /// </summary>
    public static IEnumerable<string> Check()
    {
        var findings = new List<string>();

        foreach (var v in PowerDamageVectors)
        {
            var got = Damage(v.Amount, v.Strength, v.Weak, v.Vulnerable);
            if (got != v.Dealt)
            {
                findings.Add(string.Format(
                    CultureInfo.InvariantCulture,
                    "Power-damage pipeline parity (NC-1): {0} with strength "
                  + "{1}, weak {2}, vulnerable {3} -> {4}, sim says {5}",
                    v.Amount, v.Strength, v.Weak, v.Vulnerable, got, v.Dealt));
            }
        }

        foreach (var v in PowerBlockVectors)
        {
            // The raw grant is the identity on its amount, by definition of
            // the exemption. Stated as a check anyway, because the row that
            // would fail it is a row somebody edited by hand.
            if (v.Block != v.Amount)
            {
                findings.Add(string.Format(
                    CultureInfo.InvariantCulture,
                    "Power-block exemption parity (NC-11): {0} with dexterity "
                  + "{1}, frail {2} -> table says {3}, and raw block must be "
                  + "the amount",
                    v.Amount, v.Dexterity, v.Frail, v.Block));
            }
        }

        return findings;
    }
}
