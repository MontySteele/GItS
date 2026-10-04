using KleeMod.Powers;

namespace KleeMod.Elements;

/// <summary>
/// THE ELEMENT PORT (<c>review/ruled/element-home-review-2026-09-28.md</c>
/// §3, §4 A, ruled §6), AS AMENDED 2026-10-03: EVERY REACTION CONSUMES ITS
/// AURA. [USER]: "Should we get rid of the concept of elements being 'spent'
/// after a swirl? It seems to generate confusion." then "agreed ... please
/// proceed". Swirl and Crystallize remove the aura they act on, as every
/// other reaction does and as in Genshin; there is no spent aura any more.
///
/// <see cref="SwirlPays"/> is the one switch left (§4 A): a Swirl spreads
/// ordinary FRESH copies of the swirled element to every OTHER enemy (one
/// already wearing it refreshes to full duration, one wearing another aura
/// has it replaced; nothing reacts where a copy lands) and deals a flat
/// <see cref="ReactionConstants.SwirlDamage"/> to every enemy. A copy is an
/// application without a trigger, so it never reacts and never Swirls again:
/// no recursion. Because copies are fresh, a Swirl that hits ALL enemies pays
/// once per enemy whose aura is still standing when its Anemo hit lands.
///
/// On in every build that does not name it (<c>klee-mod/Directory.Build.props</c>);
/// <c>-p:SwirlPays=false</c> turns it off, and a Swirl then copies the aura
/// onto every enemy, the struck one included, with no flat damage. The sim
/// twin <c>C.SWIRL_PAYS</c> ships <c>False</c>, the arm convention, and pins
/// both sides by flipping it.
///
/// Compiled in every build, not under <c>PROTOTYPE_CARDS</c>: this is the
/// shared reaction layer, which every kit reacts through.
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

    /// <summary>Is §4 A live? Settable so a headless pin can assert both
    /// sides in one build; nothing in the mod writes it.</summary>
    public static bool SwirlPays { get; set; } = DefaultSwirlPays;

    /// <summary>What a hit does to an aura that is already standing.</summary>
    public enum HitOutcome
    {
        /// <summary>No element, or a pair with no reaction: nothing.</summary>
        Nothing = 0,
        /// <summary>Same element: full duration.</summary>
        Refresh,
        /// <summary>The aura is removed and the reaction resolves. Every
        /// reaction, Swirl and Crystallize included (2026-10-03).</summary>
        Consume,
    }

    /// <summary>
    /// THE ONE DECISION, for every site that resolves a hit on a standing
    /// aura (<c>AuraPower.ResolveLifecycle</c>, <c>ElementalHit.Deal</c>,
    /// <c>ElementalHit.ApplyOnly</c>) and every preview that forecasts one.
    /// Pure. Sim twin: the branch order of <c>reactions.resolve_hit</c>.
    /// </summary>
    public static HitOutcome Outcome(Element aura, Element trigger)
    {
        if (aura == Element.None || trigger == Element.None) return HitOutcome.Nothing;
        if (aura == trigger) return HitOutcome.Refresh;
        if (ReactionTable.Lookup(aura, trigger) == Reaction.None) return HitOutcome.Nothing;
        return HitOutcome.Consume;
    }

    /// <summary>What a Swirl's spread does to one other enemy.</summary>
    public enum SpreadOutcome
    {
        /// <summary>No aura, or another element: a fresh copy replaces it,
        /// and nothing reacts there.</summary>
        Copy,
        /// <summary>Already wearing the swirled element: its aura goes back
        /// to full duration, and nothing reacts. [USER], 2026-10-01:
        /// "reapplying the same element as a refresh mechanic feels fine and
        /// we shouldn't let that brick other reactions."</summary>
        Refresh,
    }

    /// <summary>
    /// What a Swirl of <paramref name="spread"/> does to an enemy wearing
    /// <paramref name="existing"/> (<see cref="Element.None"/> for no aura).
    /// §4 A, amended 2026-10-01: the same element refreshes, anything else
    /// takes a fresh copy.
    /// </summary>
    public static SpreadOutcome SpreadOn(Element spread, Element existing) =>
        existing == spread ? SpreadOutcome.Refresh : SpreadOutcome.Copy;
}
