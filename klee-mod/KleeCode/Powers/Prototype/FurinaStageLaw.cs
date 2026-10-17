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

    /// <summary>Charlotte's act: "Repay 3."</summary>
    public const int CharlotteActRepay = 3;

    /// <summary>Charlotte's line: "The first time one of your cards Repays
    /// each turn, draw 1 card." (The Spend round 2, 2026-10-10: her own act
    /// and Salon Solitaire no longer count.)</summary>
    public const int CharlotteLineDraw = 1;

    /// <summary>Wriothesley's act: "Deal 5 Cryo damage to a random enemy."
    /// (His line deals the HP drained.)</summary>
    public const int WriothesleyActDamage = 5;

    /// <summary>Lynette's act: "Deal 5 Anemo damage to an enemy with an
    /// aura." (Her line pays the first HP an enemy takes each turn again.)
    /// </summary>
    public const int LynetteActDamage = 5;

    /// <summary>Clorinde's act: "Deal 6 Electro damage to a random enemy."
    /// </summary>
    public const int ClorindeActDamage = 6;

    /// <summary>Clorinde's line: "Whenever you Repay, deal twice that much
    /// Electro damage to a random enemy."</summary>
    public const int ClorindePerRepay = 2;

    // ---- the pool to 39 (review/ruled/furina-pool-40-2026-10-05.md) ------

    /// <summary>Lyney's line: "Your Drain buffer is 10 HP larger." (Furina
    /// round 5, 2026-10-11; it read "Your Drain line is 10 HP lower" before
    /// the Drain buffer.) He adds 10 to her buffer, which puts the line 10
    /// HP lower.</summary>
    public const int LyneyLineDrop = 10;

    /// <summary>Lyney's act: "Drain 2, never past your line (none at or below
    /// it). Deal 5 Pyro
    /// damage to ALL enemies." A guest's Drain stops at the line (the
    /// drain-line round, 2026-10-09): it drains only the room above it, and
    /// the damage lands either way.</summary>
    public const int LyneyActDrain = 2;

    /// <summary>Lyney's act's damage.</summary>
    public const int LyneyActDamage = 5;

    /// <summary>Sigewinne's act: "Repay 3." (Her line gives the Block of
    /// every Repay.)</summary>
    public const int SigewinneActRepay = 3;

    /// <summary>Chevreuse's act: "Deal 5 damage to a random enemy."</summary>
    public const int ChevreuseActDamage = 5;

    /// <summary>Chevreuse's line: "Whenever you Spend, apply 1 Vulnerable to
    /// a random enemy."</summary>
    public const int ChevreuseLineVulnerable = 1;

    /// <summary>THE DRAIN FLOOR (the Drain line rule, 2026-10-09): a Drain
    /// is never refused for the line, but it cannot take her to 0 HP -- the
    /// lowest HP a Drain may reach is 1. Also the floor Lyney's line cannot
    /// push the line below.</summary>
    public const int DrainFloor = 1;

    // ---- the pool to 75 (review/ruled/furina-pool-growth-2026-10-09.md) --
    // Sec.3's guest rule: a guest's upgrade raises its line or its act,
    // never its cost (the table of seven built guests, and sec.5's four).

    /// <summary>Charlotte upgraded: "Act: Repay 5."</summary>
    public const int CharlotteActRepayUpgraded = 5;

    /// <summary>Sigewinne upgraded: "Act: Repay 5."</summary>
    public const int SigewinneActRepayUpgraded = 5;

    /// <summary>Wriothesley upgraded: "Act: 8."</summary>
    public const int WriothesleyActDamageUpgraded = 8;

    /// <summary>Lyney upgraded: "Act: 7."</summary>
    public const int LyneyActDamageUpgraded = 7;

    /// <summary>Lynette upgraded: "Act: 8."</summary>
    public const int LynetteActDamageUpgraded = 8;

    /// <summary>Chevreuse upgraded: "Line: also 1 Weak."</summary>
    public const int ChevreuseLineWeakUpgraded = 1;

    /// <summary>Clorinde upgraded: "Act: 9."</summary>
    public const int ClorindeActDamageUpgraded = 9;

    /// <summary>Freminet's act (the Spend paper, 2026-10-10,
    /// <c>review/ruled/furina-spend-paper-2026-10-10.md</c> pick 2, ruled
    /// 2026-10-10): "Gain 3 Block. Spend a quarter of your Fanfare (rounded
    /// down): gain that much more Block." [6] (His line gives the Block of
    /// every Drain.) The 5 [8] Cryo hit left with this act.</summary>
    public const int FreminetActBlock = 4;

    public const int FreminetActBlockUpgraded = 7;

    /// <summary>Navia's act Spends a third of your Fanfare, rounded down (the
    /// guest package, ruled 2026-10-13; a half before). Mirrors
    /// <c>furina_stage.NAVIA_SPEND_DIVISOR</c>.</summary>
    public const int NaviaSpendDivisor = 3;

    /// <summary>... and deals twice that much Geo damage. Mirrors
    /// <c>furina_stage.NAVIA_ACT_MULTIPLIER</c>.</summary>
    public const int NaviaActMultiplier = 2;

    /// <summary>Freminet's act Spends a quarter of your Fanfare, rounded down
    /// (the Spend paper, pick 2, ruled 2026-10-10: "I don't like artificial
    /// limits, so I'd prefer to just fiddle with the ratio"). Mirrors
    /// <c>furina_stage.FREMINET_SPEND_DIVISOR</c>.</summary>
    public const int FreminetSpendDivisor = 4;

    /// <summary>"Spend up to X" (the Spend paper, pick 1): Spirited Aria's
    /// "Draw 1 for every 4 spent" and Crashing Waves' "hit once more for
    /// every 4". Mirrors <c>furina_stage.SPEND_UP_TO_EVERY</c>.</summary>
    public const int SpendUpToEvery = 4;

    /// <summary>Navia's line: "Your first Spend each turn costs 2 less (a
    /// spend-all keeps 2)." [3] On a "Spend up to X" the first 2 points are
    /// free: they count as spent and are not taken. (Her act Spends half your
    /// Fanfare and deals that much as Geo, the Spend paper 2026-10-10.)
    /// </summary>
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

    /// <summary>Escoffier's line (ruled 2026-10-13): "Your guests' acts deal
    /// 2 [3] more damage."</summary>
    public const int EscoffierLineBonus = 2;

    public const int EscoffierLineBonusUpgraded = 3;

    /// <summary>Ensemble Cast: "You have 4 guest seats."</summary>
    public const int EnsembleSeats = 4;

    /// <summary>Showstopper: "At the end of your turn, Spend 5: your guests
    /// act again."</summary>
    public const int ShowstopperSpend = 5;

    /// <summary>High Stakes (the Spend round 2, 2026-10-10,
    /// <c>review/records/furina-spend-round-2-2026-10-10.md</c>): "Your
    /// Attacks deal 1 additional damage for every 5 HP you have Drained this
    /// combat." The Spend rounds review (2026-10-10,
    /// <c>review/records/furina-spend-rounds-review-2026-10-10.md</c>, change 1)
    /// made it every 4 [3], round 2's pre-registered fallback. The card's power
    /// amount is this divisor. Mirrors
    /// <c>furina_stage.HIGH_STAKES_EVERY</c>.</summary>
    public const int HighStakesEvery = 4;

    /// <summary>High Stakes upgraded: "for every 3".</summary>
    public const int HighStakesEveryUpgraded = 3;

    /// <summary>High Stakes' bonus a hit: the HP drained this combat, gross
    /// (no Repay lowers it), over <paramref name="every"/>, rounded down. 0
    /// for a divisor below 1.</summary>
    public static int HighStakesBonus(int drained, int every) =>
        every > 0 && drained > 0 ? drained / every : 0;

    /// <summary>What a hit's High Stakes bonus counts for the telemetry: the
    /// bonus, never more than the hit dealt (HP and Block).</summary>
    public static int HighStakesCredit(int bonus, int dealt) =>
        System.Math.Max(0, System.Math.Min(bonus, dealt));

    /// <summary>Hymn of Renewal: "Whenever you Repay 4 or more HP at once,
    /// gain 1 Strength." (HP actually repaid.)</summary>
    public const int HymnThreshold = 4;

    /// <summary>Regina of All Waters: "At the start of your turn, Drain 3,
    /// never past your line. If you do, gain 1 Strength." (2026-10-10)
    /// </summary>
    public const int ReginaDrain = 3;

    /// <summary>Star Turn: "Costs 1 less for every 6 Fanfare you have."
    /// </summary>
    public const int StarTurnFanfarePer = 6;

    // ---- the diversity pass (review/ruled/furina-diversity-pass-2026-10-11.md,
    // ruled 2026-10-11) -----------------------------------------------------

    /// <summary>Bravura: "Deal 7 Hydro damage for every 3 spent." Mirrors
    /// <c>furina_stage.BRAVURA_SPENT_PER</c>.</summary>
    public const int BravuraSpentPer = 3;

    /// <summary>Packed House: "plus 1 for every 4 Fanfare you have" (the
    /// Spend outlet paper, ruled 2026-10-12; was 5).
    /// Mirrors <c>furina_stage.PACKED_HOUSE_FANFARE_PER</c>.</summary>
    public const int PackedHouseFanfarePer = 4;

    /// <summary>
    /// Rule 1: THE DRAIN BUFFER (2026-10-11; [USER]: "There should be a
    /// buffer for drain equal to 1/4 my max HP which should be restore-able,
    /// but getting hurt should not disqualify it. Say my max HP is 80 and my
    /// current HP is 50. Then the drain line is 20 below, aka 30. If I take
    /// 15 normal damage and Drain 15, I expect to be at 20 hp with my Drain
    /// line at 15 and be able to Repay to 35."). Each combat her buffer is
    /// 1/4 of the Max HP she entered it with, rounded DOWN (80 takes 20, 85
    /// takes 21); Lyney on stage adds <see cref="LyneyLineDrop"/>. It is
    /// counted in HP DRAINED, never in HP position: a Drain fills it first,
    /// what it drains beyond it is drained past the line, and an enemy's hit
    /// never touches it. A Repay of drained HP within it refills it. (Until
    /// 2026-10-11 the line was fixed at her entry HP minus the quarter, so a
    /// hit used up the room.) Integer throughout, so the sim
    /// (<c>furina_tide.shipped_buffer</c>) computes the same number.
    /// </summary>
    public static int BufferOf(int maxHp, bool lyney = false) =>
        System.Math.Max(0, maxHp) / LineMaxHpDivisor
      + (lyney ? LyneyLineDrop : 0);

    /// <summary>Epiclese Season Pass (Furina's card pass, 2026-10-15): "You
    /// have 1 more guest seat." Copies add.</summary>
    public const int SeasonPassSeats = 1;

    /// <summary>Bouquet of Roses: "Whenever you Spend 10 or more at once,
    /// gain [E]."</summary>
    public const int BouquetSpend = 10;

    /// <summary>The buffer is 1/4 of her Max HP, rounded down. Mirrors
    /// <c>furina_tide.LINE_MAX_HP_DIVISOR</c>.</summary>
    public const int LineMaxHpDivisor = 4;

    /// <summary>THE LINE AS SHOWN (2026-10-11): her HP now minus the buffer
    /// she has left, never below 0. At 20 HP with 5 of buffer left it is 15.
    /// It moves with her HP; a Drain within the buffer leaves it where it
    /// was, and so does a Repay of that Drain.</summary>
    public static int LineAt(int hp, int bufferLeft) =>
        System.Math.Max(0, System.Math.Max(0, hp) - System.Math.Max(0, bufferLeft));

    /// <summary>Where the line comes from, in words, for its hover and the
    /// seat page (2026-10-05: seats connected the line to their entry HP
    /// only late; the buffer's words since 2026-10-11).</summary>
    public static string LineWhy(bool lyney) =>
        LineWhyBase + (lyney ? ", plus " + LyneyLineDrop
                               + " with Lyney on stage" : "")
      + LineWhyTail;

    /// <summary>The line's source, in the base game's words (2026-10-11).
    /// </summary>
    public const string LineWhyBase =
        "your HP minus your Drain buffer: 1/4 of your Max HP";

    /// <summary>The buffer's last clause: what she has drained into it.
    /// </summary>
    public const string LineWhyTail = ", less what you have drained";

    /// <summary>A line of 0 explains itself (the Spend round 2, 2026-10-10:
    /// a seat read a line of 0 as "every Drain is permanent", which is
    /// backwards). At 0 every Drain stays above the line, so all of it
    /// returns. Plain words; the counter's hover golds the verb.</summary>
    public const string LineZeroReturns =
        "all your Drain returns after combat";
}
