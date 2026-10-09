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
    /// <summary>Rule 5: three guest seats (four with Ensemble Cast). Mirrors
    /// <c>furina_stage.SEATS</c>.</summary>
    public const int Seats = 3;

    /// <summary>Rule 4: Salon Solitaire, "At the end of your turn, Repay 1."
    /// (2026-10-09 playtest trim, was 2.)
    /// Mirrors <c>furina_stage.SINGER_REPAY</c>.</summary>
    public const int SingerRepay = 1;

    /// <summary>Salon Solitaire upgraded ([2], 2026-10-09 trim, was 3): The Curtain Never Falls, its
    /// Touch of Orobas replacement. Mirrors
    /// <c>furina_stage.SINGER_REPAY_UPGRADED</c>.</summary>
    public const int SingerRepayUpgraded = 2;

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
    /// It may Drain past the line (2026-10-09); it skips only when the Drain
    /// would take her to 0 HP.</summary>
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

    /// <summary>THE DRAIN FLOOR (the Drain line rule, 2026-10-09): a Drain
    /// is never refused for the line, but it cannot take her to 0 HP -- the
    /// lowest HP a Drain may reach is 1. Also the floor Lyney's line cannot
    /// push the line below.</summary>
    public const int DrainFloor = 1;

    /// <summary>Fountain of Lucine: "At the start of your next 3 turns,
    /// Repay 3."</summary>
    public const int FountainTurns = 3;

    // ---- the pool to 75 (review/active/furina-pool-growth-2026-10-09.md) --
    // Sec.3's guest rule: a guest's upgrade raises its line or its act,
    // never its cost (the table of seven built guests, and sec.5's four).

    /// <summary>Charlotte upgraded: "Act: Repay 4."</summary>
    public const int CharlotteActRepayUpgraded = 4;

    /// <summary>Sigewinne upgraded: "Act: Repay 4."</summary>
    public const int SigewinneActRepayUpgraded = 4;

    /// <summary>Wriothesley upgraded: "Act: 7."</summary>
    public const int WriothesleyActDamageUpgraded = 7;

    /// <summary>Lyney upgraded: "Act: 11."</summary>
    public const int LyneyActDamageUpgraded = 11;

    /// <summary>Lynette upgraded: "Act: 6."</summary>
    public const int LynetteActDamageUpgraded = 6;

    /// <summary>Chevreuse upgraded: "Line: also 1 Weak."</summary>
    public const int ChevreuseLineWeakUpgraded = 1;

    /// <summary>Clorinde upgraded: "Act: 9."</summary>
    public const int ClorindeActDamageUpgraded = 9;

    /// <summary>Freminet's act: "Deal 5 Cryo damage to a random enemy."
    /// [8] (His line gives the Block of every Drain.)</summary>
    public const int FreminetActDamage = 5;

    public const int FreminetActDamageUpgraded = 8;

    /// <summary>Freminet's act also gives Block (the pool-75 round's card
    /// numbers, ruled 2026-10-09): "gain 6 Block." [9]</summary>
    public const int FreminetActBlock = 6;

    public const int FreminetActBlockUpgraded = 9;

    /// <summary>Navia's line: "Your first Spend each turn costs 2 less (a
    /// spend-all keeps 2)." [3] (Her act deals the Fanfare spent this turn
    /// as Geo.)</summary>
    public const int NaviaLineDiscount = 2;

    public const int NaviaLineDiscountUpgraded = 3;

    /// <summary>Neuvillette's line: "Your Hydro damage deals 2 more." [3]
    /// (His act deals the HP she lost since her last turn -- Drained or
    /// taken -- to ALL as Hydro; 2026-10-09.)</summary>
    public const int NeuvilletteHydroBonus = 2;

    public const int NeuvilletteHydroBonusUpgraded = 3;

    /// <summary>Escoffier's act: "Deal 4 Cryo damage to ALL enemies." [6]
    /// </summary>
    public const int EscoffierActDamage = 4;

    public const int EscoffierActDamageUpgraded = 6;

    /// <summary>Escoffier's line: "Whenever a guest acts, Repay 1."</summary>
    public const int EscoffierLineRepay = 1;

    /// <summary>Ensemble Cast: "You have 4 guest seats."</summary>
    public const int EnsembleSeats = 4;

    /// <summary>Showstopper: "At the end of your turn, Spend 5: your guests
    /// act again."</summary>
    public const int ShowstopperSpend = 5;

    /// <summary>Against the Tide and High Stakes: "within 5 HP of your Drain
    /// line".</summary>
    public const int NearLine = 5;

    /// <summary>Hymn of Renewal: "Whenever you Repay 4 or more HP at once,
    /// gain 1 Strength." (HP actually repaid.)</summary>
    public const int HymnThreshold = 4;

    /// <summary>Prima Donna: "if you have 10 or more Fanfare, gain 1
    /// Energy."</summary>
    public const int PrimaDonnaFanfare = 10;

    /// <summary>Regina of All Waters: "At the start of your turn, Drain 3.
    /// If you do, gain 1 Strength."</summary>
    public const int ReginaDrain = 3;

    /// <summary>Star Turn: "Costs 1 less for every 6 Fanfare you have."
    /// </summary>
    public const int StarTurnFanfarePer = 6;

    /// <summary>Is <paramref name="hp"/> within <see cref="NearLine"/> HP of
    /// <paramref name="line"/>: at most 5 over it, or at or below it (a Drain
    /// may go past the line since 2026-10-09, and any HP at or below the line
    /// counts).</summary>
    public static bool NearTheLine(int hp, int line) => hp - line <= NearLine;

    /// <summary>
    /// Rule 1: THE LINE (the Drain line rule, ruled 2026-10-09): 3/4 of the
    /// HP she started this combat with, rounded UP as the half line was: 59
    /// from 78, 58 from 77. A Drain may go past it; HP drained past it is
    /// lost at the curtain call unless Repaid. The sim compares in floats
    /// (<c>furina_tide.half_line</c>), so the lowest HP above the line is
    /// the float line rounded up.
    /// </summary>
    public static int LineOf(int entryHp) =>
        (LineNumerator * System.Math.Max(0, entryHp) + LineDenominator - 1)
        / LineDenominator;

    /// <summary>The line's share of the entry HP: 3/4. Mirrors
    /// <c>furina_tide.LINE_SHARE</c>.</summary>
    public const int LineNumerator = 3;

    public const int LineDenominator = 4;

    /// <summary>The line with its one mover: Lyney on stage lowers it by 10,
    /// never below 1. (A Five-Century Act no longer moves it: it returns the
    /// HP drained past it instead.)</summary>
    public static int LineOf(int entryHp, bool lyney)
    {
        var line = LineOf(entryHp);
        return lyney ? System.Math.Max(DrainFloor, line - LyneyLineDrop)
                     : line;
    }

    /// <summary>Where the line comes from, in words, for its hover and the
    /// seat page (2026-10-05: seats connected the line to their entry HP
    /// only late). The same two branches as
    /// <see cref="LineOf(int, bool)"/>.</summary>
    public static string LineWhy(bool lyney) =>
        lyney ? "3/4 of the HP you started this fight with, "
                + LyneyLineDrop + " lower with Lyney on stage"
              : "3/4 of the HP you started this fight with";
}
