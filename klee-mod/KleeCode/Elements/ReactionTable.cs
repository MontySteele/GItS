using System.Linq;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Logging;

namespace KleeMod.Elements;

/// <summary>The reactions the resolver can produce.</summary>
public enum Reaction
{
    None = 0,
    Vaporize,       // Pyro  x Hydro   -- amplifier
    Melt,           // Pyro  x Cryo    -- amplifier
    Overload,       // Pyro  x Electro -- splash to all
    Superconduct,   // Electro x Cryo  -- Vulnerable
    ElectroCharged, // Hydro x Electro -- DoT
    Frozen,         // Hydro x Cryo    -- soft control (v2)
    Swirl,          // Anemo trigger   -- spreads the aura
    Crystallize,    // Geo trigger     -- player gains Block
}

/// <summary>
/// Ratified reaction values. These MIRROR tier0/constants.py, which is the
/// single source of truth -- the Tier 0 simulator ran the balance passes that
/// produced these numbers, and they are frozen per the errata pass ("v0.1
/// locked"). Do not retune here; change the sim, re-run, then port.
/// </summary>
public static class ReactionConstants
{
    public const int AuraDurationTurns = 2;      // AURA_DURATION_TURNS

    public const decimal VaporizeMult = 1.5m;    // VAPORIZE_MULT
    public const decimal MeltMult = 1.75m;       // MELT_MULT

    /// <summary>VULNERABLE_TAKEN_MULT. The sim's modify_damage_taken applies a
    /// flat x1.5 on ANY nonzero vulnerable stack -- never per stack. Named here
    /// because two sites mirror it: SimDamagePipeline.TargetMods and
    /// AuraPower's Superconduct self-amplification.</summary>
    public const decimal VulnerableTakenMult = 1.5m;

    public const int OverloadSplash = 6;         // OVERLOAD_SPLASH, flat, all enemies
    public const int OverloadWeak = 1;            // OVERLOAD_WEAK
    public const int SuperconductVuln = 2;       // SUPERCONDUCT_VULN
    public const int ElectroChargedDot = 4;      // ELECTROCHARGED_DOT
    public const int ElectroChargedDotTurns = 2; // ELECTROCHARGED_DOT_TURNS
    public const int CrystallizeBlock = 4;       // CRYSTALLIZE_BLOCK

    // Frozen v2 (principles v1.5 section 2.2 errata): no skip/stun at base.
    public const decimal FrozenDamageMult = 0.5m; // FROZEN_DAMAGE_MULT
    public const int ShatterDamage = 6;           // SHATTER_DAMAGE
    public const int FrozenBossVuln = 2;          // FROZEN_BOSS_VULN

    // Degeneracy guard carried over from the sim as a debug-log warning
    // (spec C2.1). A single hit exceeding this multiple of base damage means
    // the amp stack has run away and we want the provenance in the log.
    public const decimal AmpStackLimit = 4.0m;    // AMP_STACK_LIMIT
}

/// <summary>
/// Pure lookup: which reaction does (aura, trigger) produce? Order-independent,
/// matching the sim's frozenset pair keys. Anemo/Geo are trigger-only and win
/// over the pair table, exactly as in _react().
/// </summary>
public static class ReactionTable
{
    public static Reaction Lookup(Element aura, Element trigger)
    {
        if (aura == Element.None || trigger == Element.None || aura == trigger)
        {
            return Reaction.None;
        }

        // Trigger-only elements are checked first: they react with ANY aura.
        if (trigger == Element.Anemo) return Reaction.Swirl;
        if (trigger == Element.Geo) return Reaction.Crystallize;

        return (aura, trigger) switch
        {
            (Element.Pyro, Element.Hydro) or (Element.Hydro, Element.Pyro) => Reaction.Vaporize,
            (Element.Pyro, Element.Cryo) or (Element.Cryo, Element.Pyro) => Reaction.Melt,
            (Element.Pyro, Element.Electro) or (Element.Electro, Element.Pyro) => Reaction.Overload,
            (Element.Electro, Element.Cryo) or (Element.Cryo, Element.Electro) => Reaction.Superconduct,
            (Element.Hydro, Element.Electro) or (Element.Electro, Element.Hydro) => Reaction.ElectroCharged,
            (Element.Hydro, Element.Cryo) or (Element.Cryo, Element.Hydro) => Reaction.Frozen,
            _ => Reaction.None,
        };
    }

    /// <summary>
    /// Amplifiers multiply ONE hit and are consumed with the aura.
    /// IRON RULE from the sim: they must never persist.
    /// Returns 1.0 for every non-amplifying reaction.
    /// </summary>
    public static decimal AmplifierMultiplier(Reaction reaction) => reaction switch
    {
        Reaction.Vaporize => ReactionConstants.VaporizeMult,
        Reaction.Melt => ReactionConstants.MeltMult,
        _ => 1m,
    };

    /// <summary>
    /// Dealer-aware amplifier: percent amp boosts on the dealer (Vermillion
    /// Pact; Durin's witchs_flame joins when companions land) are additive
    /// with each other and multiplicative on the base -- sim law,
    /// reactions.py _amp_mult: `base * (1 + pct / 100)`.
    ///
    /// This overload also owns the sim's amp-cap detector (AMP_STACK_LIMIT):
    /// the boosted multiplier is the one that can run away, so the guard
    /// lives beside the boost. Pure -- callable from preview paths.
    /// </summary>
    public static decimal AmplifierMultiplier(Reaction reaction, Creature? dealer)
    {
        var baseMult = AmplifierMultiplier(reaction);
        if (baseMult == 1m || dealer == null) return baseMult;

        // Additive with each other, multiplicative on the base (sim
        // _amp_mult): Vermillion Pact's +25 and Durin's +30 stack to +55.
        var pct = dealer.Powers.OfType<AmpReactionUpPower>().FirstOrDefault()?.Amount ?? 0;
        pct += dealer.Powers.OfType<WitchsFlamePower>()
            .FirstOrDefault()?.Amount ?? 0;
        var mult = baseMult * (1m + pct / 100m);

        if (mult > ReactionConstants.AmpStackLimit)
        {
            Log.Warn($"[{KleeMod.ModId}] AMP_STACK guard: multiplier {mult} exceeds " +
                     $"{ReactionConstants.AmpStackLimit} on {reaction} " +
                     $"(amp boost {pct}%).");
        }

        return mult;
    }
}
