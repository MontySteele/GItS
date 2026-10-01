using KleeMod.Powers;

namespace KleeMod.Elements;

/// <summary>
/// THE ELEMENT PORT, PHASE ONE: fresh and spent auras
/// (<c>review/ruled/element-home-review-2026-09-28.md</c> §3, §4, §7.1; ruled
/// §6, [USER]: "That makes sense").
///
/// Anemo and Geo no longer CONSUME the aura they act on. A trigger hit on a
/// FRESH aura reacts and leaves the aura standing, SPENT; a trigger hit on a
/// spent aura does nothing extra. A same-element hit refreshes the aura and
/// makes it fresh again; every other element reacts with a spent aura exactly
/// as with a fresh one; spending never touches the aura's duration.
///
/// TWO SWITCHES, one per change, so each is tested alone (§6 pick 4.4). The
/// shared fresh/spent rule rides with whichever is on: a trigger whose switch
/// is off consumes as it always did, spent aura or not.
///
///   <see cref="SwirlPays"/>            §4 A. Swirl keeps the aura, spreads
///                                      SPENT copies to every enemy lacking
///                                      it, and deals a flat
///                                      <see cref="ReactionConstants.SwirlDamage"/>
///                                      to every enemy.
///   <see cref="CrystallizeKeepsAura"/> §4 B. The 4 Block, and the aura stays.
///
/// Both are ON in every build that names neither property
/// (<c>klee-mod/Directory.Build.props</c>): <c>-p:SwirlPays=false</c> or
/// <c>-p:CrystallizeKeepsAura=false</c> turns one off, and
/// <c>-p:ShippedKits=true</c> turns both off. The sim twins
/// (<c>C.SWIRL_PAYS</c>, <c>C.CRYSTALLIZE_KEEPS_AURA</c>) ship <c>False</c>,
/// the arm convention, and pin both sides by flipping them.
///
/// Compiled in every build, not under <c>PROTOTYPE_CARDS</c>: this is the
/// shared reaction layer, which every kit and the shipped build react through.
/// </summary>
public static class TriggerRules
{
    /// <summary>§4 A's default, from <c>-p:SwirlPays</c>.</summary>
    public const bool DefaultSwirlPays =
#if SWIRL_PAYS
        true;
#else
        false;
#endif

    /// <summary>§4 B's default, from <c>-p:CrystallizeKeepsAura</c>.</summary>
    public const bool DefaultCrystallizeKeepsAura =
#if CRYSTALLIZE_KEEPS_AURA
        true;
#else
        false;
#endif

    /// <summary>Is §4 A live? Settable so a headless pin can assert both
    /// sides in one build; nothing in the mod writes it.</summary>
    public static bool SwirlPays { get; set; } = DefaultSwirlPays;

    /// <summary>Is §4 B live? Settable for the same reason.</summary>
    public static bool CrystallizeKeepsAura { get; set; } = DefaultCrystallizeKeepsAura;

    /// <summary>
    /// Does this trigger SPEND the aura rather than consume it? Only a trigger
    /// element can say yes, and only while its own switch is on. Sim twin:
    /// <c>reactions.trigger_keeps_aura</c>.
    /// </summary>
    public static bool TriggerKeepsAura(Element trigger) =>
        (trigger == Element.Anemo && SwirlPays)
        || (trigger == Element.Geo && CrystallizeKeepsAura);

    /// <summary>What a hit does to an aura that is already standing.</summary>
    public enum HitOutcome
    {
        /// <summary>No element, or a pair with no reaction: nothing.</summary>
        Nothing = 0,
        /// <summary>Same element: full duration, and fresh again.</summary>
        Refresh,
        /// <summary>The aura is removed and the reaction resolves (today's
        /// rule, and every aura element's).</summary>
        Consume,
        /// <summary>A switched trigger on a FRESH aura: the reaction
        /// resolves and the aura stays, spent.</summary>
        Spend,
        /// <summary>A switched trigger on a SPENT aura: no reaction, no
        /// change. The "pays nothing" the preview explains.</summary>
        SpentNothing,
    }

    /// <summary>
    /// THE ONE DECISION, for every site that resolves a hit on a standing
    /// aura (<c>AuraPower.ResolveLifecycle</c>, <c>ElementalHit.Deal</c>,
    /// <c>ElementalHit.ApplyOnly</c>) and every preview that forecasts one.
    /// Pure. Sim twin: the branch order of <c>reactions.resolve_hit</c>.
    /// </summary>
    public static HitOutcome Outcome(Element aura, bool spent, Element trigger)
    {
        if (aura == Element.None || trigger == Element.None) return HitOutcome.Nothing;
        if (aura == trigger) return HitOutcome.Refresh;
        if (ReactionTable.Lookup(aura, trigger) == Reaction.None) return HitOutcome.Nothing;
        if (TriggerKeepsAura(trigger))
        {
            return spent ? HitOutcome.SpentNothing : HitOutcome.Spend;
        }
        return HitOutcome.Consume;
    }

    /// <summary>
    /// The reaction this trigger would produce against this aura NOW:
    /// <see cref="ReactionTable.Lookup"/>, except <c>None</c> for a switched
    /// trigger on a spent aura. Pure; the damage pipeline's forecast
    /// (Courtroom Drama's first-reaction Vulnerable) reads it so a trigger
    /// that pays nothing forecasts nothing.
    /// </summary>
    public static Reaction ReactionFor(Element aura, bool spent, Element trigger) =>
        Outcome(aura, spent, trigger) is HitOutcome.Consume or HitOutcome.Spend
            ? ReactionTable.Lookup(aura, trigger)
            : Reaction.None;

    /// <summary>The <see cref="AuraPower"/> overload of
    /// <see cref="ReactionFor(Element, bool, Element)"/>.</summary>
    public static Reaction ReactionFor(AuraPower aura, Element trigger) =>
        ReactionFor(aura.Element, aura.Spent, trigger);

    /// <summary>What a Swirl's spread does to one other enemy.</summary>
    public enum SpreadOutcome
    {
        /// <summary>No aura, or another element: a SPENT copy replaces it,
        /// as today, and nothing reacts there (the deferred candidate).</summary>
        Copy,
        /// <summary>Already wearing the swirled element, fresh or spent: its
        /// aura goes back to full duration and FRESH, and nothing reacts.
        /// [USER], 2026-10-01: "reapplying the same element as a refresh
        /// mechanic feels fine and we shouldn't let that brick other
        /// reactions."</summary>
        Refresh,
    }

    /// <summary>
    /// What a Swirl of <paramref name="spread"/> does to an enemy wearing
    /// <paramref name="existing"/> (<see cref="Element.None"/> for no aura).
    /// §4 A, amended 2026-10-01: the same element refreshes, anything else
    /// takes a spent copy.
    /// </summary>
    public static SpreadOutcome SpreadOn(Element spread, Element existing) =>
        existing == spread ? SpreadOutcome.Refresh : SpreadOutcome.Copy;

    /// <summary>
    /// Which trigger elements a spent aura refuses, for the badge's words:
    /// "Anemo and Geo", "Anemo", "Geo", or empty with both switches off.
    /// </summary>
    public static string SpentTriggers() => (SwirlPays, CrystallizeKeepsAura) switch
    {
        (true, true) => "Anemo and Geo",
        (true, false) => "Anemo",
        (false, true) => "Geo",
        _ => string.Empty,
    };
}
