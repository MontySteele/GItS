namespace KleeMod.Powers;

/// <summary>
/// FURINA, THE SALON'S TAB -- the kit's numbers, and nothing else.
///
/// <para>THE DESIGN is <c>review/active/furina-research-proposal-2026-10-05.md</c>:
/// sec.2's rules with sec.16's Repay and curtain call, sec.16's slice and
/// sec.17's two edits. The sim's Furina arm (<c>tier0/engine/furina_stage.py</c>,
/// on the rules of <c>tier0/engine/furina_tide.py</c>) declares every number
/// below under the same name, and <c>tools/lint_constant_parity.py</c>
/// compares the two by value.</para>
///
/// <para>PROTOTYPE SEEDS, not ruled balance: measurement law binds only at
/// Balance (<c>docs/current/EXPERIMENTS.md</c>).</para>
/// </summary>
public static class FurinaStageLaw
{
    /// <summary>Rule 5: three guest seats. Mirrors <c>furina_stage.SEATS</c>.
    /// </summary>
    public const int Seats = 3;

    /// <summary>Rule 4: Salon Solitaire, "At the end of your turn, Repay 2."
    /// Mirrors <c>furina_stage.SINGER_REPAY</c>.</summary>
    public const int SingerRepay = 2;

    /// <summary>Salon Solitaire upgraded ([3]): The Curtain Never Falls, its
    /// Touch of Orobas replacement. Mirrors
    /// <c>furina_stage.SINGER_REPAY_UPGRADED</c>.</summary>
    public const int SingerRepayUpgraded = 3;

    // ---- the first four guests (sec.16) ------------------------------------------

    /// <summary>Charlotte's act: "Repay 2."</summary>
    public const int CharlotteActRepay = 2;

    /// <summary>Charlotte's line: "The first time you Repay each turn, draw 1
    /// card."</summary>
    public const int CharlotteLineDraw = 1;

    /// <summary>Wriothesley's act: "Deal 4 Cryo damage to a random enemy."
    /// (His line deals the HP drained.)</summary>
    public const int WriothesleyActDamage = 4;

    /// <summary>Lynette's act: "Deal 3 Anemo damage to an enemy with an
    /// aura." (Her line pays the first HP an enemy takes each turn again.)
    /// </summary>
    public const int LynetteActDamage = 3;

    /// <summary>Clorinde's act: "Deal 6 Electro damage to a random enemy."
    /// </summary>
    public const int ClorindeActDamage = 6;

    /// <summary>Clorinde's line: "Whenever you Repay, deal twice that much
    /// Electro damage to a random enemy."</summary>
    public const int ClorindePerRepay = 2;

    // ---- the pool to 39 (review/active/furina-pool-40-2026-10-05.md) ------

    /// <summary>Lyney's line: "Your Drain line is 10 HP lower."</summary>
    public const int LyneyLineDrop = 10;

    /// <summary>Lyney's act: "Drain 2: deal 8 Pyro damage to ALL enemies."
    /// Below the line the act skips (no Drain, no damage).</summary>
    public const int LyneyActDrain = 2;

    /// <summary>Lyney's act's damage.</summary>
    public const int LyneyActDamage = 8;

    /// <summary>Sigewinne's act: "Repay 2." (Her line gives the Block of
    /// every Repay.)</summary>
    public const int SigewinneActRepay = 2;

    /// <summary>Chevreuse's act: "Deal 4 damage to a random enemy."</summary>
    public const int ChevreuseActDamage = 4;

    /// <summary>Chevreuse's line: "Whenever you Spend, apply 1 Vulnerable to
    /// a random enemy."</summary>
    public const int ChevreuseLineVulnerable = 1;

    /// <summary>A Five-Century Act: "You can Drain down to 1 HP." Also the
    /// floor Lyney's line cannot push the line below.</summary>
    public const int FiveCenturyLine = 1;

    /// <summary>Fountain of Lucine: "At the start of your next 3 turns,
    /// Repay 3."</summary>
    public const int FountainTurns = 3;

    /// <summary>
    /// Rule 1: THE LINE. A Drain cannot take her below half the HP she
    /// started this combat with. The sim compares <c>hp - n &gt;= entry / 2</c>
    /// in floats, so the lowest HP a Drain may reach is half the entry HP
    /// rounded UP: 39 from 78, 39 from 77.
    /// </summary>
    public static int LineOf(int entryHp) => (System.Math.Max(0, entryHp) + 1) / 2;

    /// <summary>The line with its two movers: A Five-Century Act puts it at
    /// 1 HP; Lyney on stage lowers it by 10, never below 1.</summary>
    public static int LineOf(int entryHp, bool lyney, bool fiveCentury)
    {
        if (fiveCentury) return FiveCenturyLine;
        var line = LineOf(entryHp);
        return lyney ? System.Math.Max(FiveCenturyLine, line - LyneyLineDrop)
                     : line;
    }
}
