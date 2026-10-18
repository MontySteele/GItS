namespace KleeMod.Powers;

/// <summary>
/// The four numbers the overhaul's rules carry. Placeholders, not claims
/// (slice packet sec.1) -- and MIRRORED BY VALUE from tier0, which is why they
/// are named constants rather than literals at the call sites
/// (<c>tools/lint_constant_parity.py</c>).
/// </summary>
public static class KleeOverhaulLaw
{
    /// <summary>Rule 1: every Bomb grows by this at the start of Klee's turn.
    /// Mirrors <c>C.KLEE_OVERHAUL_BOMB_GROWTH</c>. 2 since the Klee design
    /// review (2026-10-08, sec.4.6, ruled; it was 4).</summary>
    public const int BombGrowth = 2;

    /// <summary>Rule 4, and Pounding Surprise's whole body under this arm.
    /// Mirrors <c>C.KLEE_OVERHAUL_SPARK_PER_EXPLOSION</c>.</summary>
    public const int SparkPerExplosion = 1;

    /// <summary>
    /// Rule 4's OTHER half, ruled R242 pick 1: Klee starts every combat with
    /// this many Sparks. Mirrors <c>C.KLEE_OVERHAUL_OPENING_SPARK</c>.
    ///
    /// [USER]: "Regent starts with 3 stars and has to generate more through
    /// cards, so 1 is a reasonable compromise." It answers the r4 seat's
    /// structural find -- "Spark-priced cards cannot open a fight, by
    /// construction: Sparks exist only after a Bomb goes off; no Bomb can have
    /// gone off before your first play of a combat" -- and it is what pays for
    /// draft 4's plainer starter, which has no Spark sink of its own: the first
    /// Spark card drafted is live on arrival.
    ///
    /// A KIT RULE, NOT A RELIC CLAUSE, which is why it is here and not on
    /// <c>PoundingSurprise</c>. The brief's rule 4 carries the line (R242), and
    /// a relic clause would vanish the moment Touch of Orobas upgraded the
    /// relic into <c>ExplosiveFrags</c> -- whose own opening bank this arm
    /// deliberately gates OFF. The grant site is
    /// <c>KleeElementalHooks.AfterPlayerTurnStart</c>, turn 1.
    ///
    /// 3 SINCE THE KLEE DESIGN REVIEW (2026-10-08, sec.4.6, ruled; it was 1):
    /// Regent's own 3 Stars, so a Spark card is live on turn one.
    /// </summary>
    public const int OpeningSpark = 3;

    /// <summary>
    /// Damage Report's Spark per status drawn (Klee pre-Balance sweep,
    /// 2026-10-03). Flat at both levels: the upgrade moves the Block (4 to 6),
    /// as Grounded's does. Mirrors <c>C.KLEE_OVERHAUL_DAMAGE_REPORT_SPARK</c>.
    /// </summary>
    public const int DamageReportSpark = 1;
}

/// <summary>
/// A SET OFF CARD, AS A TYPE (R276). The codegen puts this on every row whose
/// body prints a Set off, anywhere in it, and nothing else implements it.
///
/// A MARKER WITH NO MEMBERS, because it answers exactly one question -- "is
/// this a Set off card" (<c>KleeExpansion.IsSetOffCard</c>). By interface rather
/// than by a list of ids, so a row deleted from the surface takes its class
/// with it. Sim twin: <c>klee_overhaul.is_set_off_card</c>, off the same
/// <c>set_off</c> op.
/// </summary>
public interface ISetOffCard
{
}
