using System.Linq;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// The sim's damage pipeline for Unpowered mirror hits (bomb detonations,
/// the Burst volley).
///
/// tier0 deal_damage_to_enemy runs EVERY hit through modify_damage_dealt
/// (add Strength, then Weak x0.75) before reaction amplification and through
/// modify_damage_taken (Vulnerable x1.5) after it, truncating ONCE at the
/// end. The game's native Weak/Vulnerable/Strength powers gate on
/// IsPoweredAttack(), which our Unpowered hits deliberately fail (that flag
/// is also what stops early detonation and attack-hooks), so the modifiers
/// the sim DOES apply to these hits must be mirrored here explicitly.
///
/// Found live (2026-07-20, weak/vulnerable card batch): Explosive Frags'
/// Vulnerable amplified follow-up detonations in the sim but not in the
/// game -- the Unpowered idiom had silently opted bombs out of the pipeline.
///
/// Multipliers mirror tier0 constants WEAK_DEALT_MULT (0.75) and
/// VULNERABLE_TAKEN_MULT (1.5) -- NOT the native DynamicVars, because relic
/// hooks (Paper Krane/Phrog) modify those and the sim has no such relics.
/// Callers keep the value decimal through the chain and truncate once, the
/// sim's single int() at the end of the pipeline.
/// </summary>
public static class SimDamagePipeline
{
    /// <summary>Pre-amplification: tier0 modify_damage_dealt.</summary>
    public static decimal DealerMods(Creature? dealer, decimal damage)
    {
        if (dealer == null) return damage;
        damage += dealer.Powers.OfType<StrengthPower>().FirstOrDefault()?.Amount ?? 0;
        if ((dealer.Powers.OfType<WeakPower>().FirstOrDefault()?.Amount ?? 0) > 0)
        {
            damage *= 0.75m;
        }
        return damage;
    }

    /// <summary>Post-amplification: tier0 modify_damage_taken.</summary>
    public static decimal TargetMods(Creature target, decimal damage)
    {
        if ((target.Powers.OfType<VulnerablePower>().FirstOrDefault()?.Amount ?? 0) > 0)
        {
            damage *= ReactionConstants.VulnerableTakenMult;
        }
        return damage;
    }

    /// <summary>
    /// The per-hit damage CAP the target itself imposes, <c>decimal.MaxValue</c>
    /// when it imposes none. `EB-343`.
    ///
    /// NOT A NEW RULE -- IT IS THE ENGINE'S OWN, READ EARLY. `CreatureCmd.Damage`
    /// already runs <c>Hook.ModifyDamage(..., ModifyDamageHookType.All, ...)</c>,
    /// whose Cap phase takes the MINIMUM <see cref="AbstractModel.ModifyDamageCap"/>
    /// over every hook listener, and unlike the Weak/Vulnerable/Strength hooks it
    /// carries NO <c>IsPoweredAttack()</c> gate -- so a cap already bites an
    /// Unpowered elemental hit today. What this adds is a way for a FACE to know
    /// it: a badge that promised 17 into an <c>Exoskeleton</c>'s Hard To Kill 3
    /// was promising three times what would land.
    ///
    /// THE TARGET'S OWN POWERS, and that is exact rather than an approximation:
    /// the 0.111.0 decompile carries exactly two <c>ModifyDamageCap</c> overrides,
    /// <c>HardToKillPower</c> and <c>IntangiblePower</c>, and BOTH answer
    /// <c>decimal.MaxValue</c> unless <c>target == Owner</c>. So scanning the
    /// target's powers finds every cap the engine's full sweep would find, and
    /// anything a future build adds elsewhere is still applied by the engine --
    /// this read would simply not predict it, which is the safe direction.
    ///
    /// <c>ValueProp.Unpowered</c> and null dealer/card are what
    /// <see cref="ElementalHit.Deal"/> passes to <c>CreatureCmd.Damage</c>, so
    /// the question asked here is the question the hit will ask. Neither cap
    /// power reads any of them.
    /// </summary>
    public static decimal TargetCap(Creature target)
    {
        var cap = decimal.MaxValue;
        foreach (var power in target.Powers)
        {
            var one = power.ModifyDamageCap(
                target, ValueProp.Unpowered, dealer: null, cardSource: null,
                cardPlay: null);
            if (one < cap) cap = one;
        }
        return cap;
    }

    /// <summary>
    /// THE OVERHAUL BOMB'S PIPELINE (`EB-343`, R248): the TARGET'S modifiers and
    /// nothing of the dealer's.
    ///
    /// A Bomb is the enemy's burden. Its printed size is its size -- Klee's
    /// Strength and Weak are hers and do not travel to a charge sitting on an
    /// enemy -- and what a Set off pays is that size through the target's own
    /// terms: <see cref="TargetMods"/>'s Vulnerable, then
    /// <see cref="TargetCap"/>'s cap.
    ///
    /// THE ORDER AND THE TRUNCATION ARE <see cref="ElementalHit.Deal"/>'s, not a
    /// second arithmetic: Deal truncates once at <see cref="TargetMods"/> and
    /// hands the int to <c>CreatureCmd.Damage</c>, whose own Cap phase then
    /// clamps it. So the cap is applied to the TRUNCATED number here for the same
    /// reason, and per charge, because the explosion loop calls this once per
    /// charge.
    ///
    /// The amplifier is the one term a face cannot know -- the first explosion of
    /// a Set off consumes the aura the rest would have reacted with -- so callers
    /// predicting a pile pass 1.
    /// </summary>
    public static int ResolveOnTarget(
        Creature target, decimal baseDamage, decimal amplifier)
    {
        var landed = (int)TargetMods(target, baseDamage * amplifier);
        var cap = TargetCap(target);
        return landed > cap ? (int)cap : landed;
    }

    /// <summary>
    /// What a hit of <paramref name="baseDamage"/> from
    /// <paramref name="dealer"/> lands on <paramref name="target"/> for, given
    /// a reaction <paramref name="amplifier"/> -- 1 for no reaction.
    ///
    /// THE WHOLE PIPELINE IN ONE CALL, and it exists for <c>EB-265</c>: the
    /// overhaul Bomb's face printed the raw charge sizes while the explosion
    /// applied Strength PER Bomb, so a Strength-2 pair of Bombs printed 10 and
    /// dealt 14 and the tester stopped trusting the character's central number.
    /// <c>ProtoBombPower.PredictedSetOffDamage</c> asks THIS rather than
    /// re-deriving Strength on the face's side.
    ///
    /// IT IS <c>ElementalHit.Deal</c>'S OWN THREE STEPS, in Deal's own order:
    /// <see cref="DealerMods"/>, the amplifier, then the single truncation of
    /// <see cref="TargetMods"/>. Deal spells them out inline rather than
    /// calling this, because `tier0/tests/test_reaction_phase_parity.py` pins
    /// the TargetMods read as happening AFTER `ReactionEffects.Resolve` -- the
    /// ordering that lets a Superconduct's Vulnerable amplify the same hit.
    /// `KleeOverhaulRoundOneFixTests` pins the two against each other so the
    /// two spellings cannot drift into two pipelines.
    ///
    /// The amplifier is the one term a face cannot know: the first explosion
    /// of a Set off consumes the aura the rest would have reacted with, so
    /// there is no single multiplier for a pile.
    /// </summary>
    public static int Resolve(
        Creature? dealer, Creature target, decimal baseDamage, decimal amplifier) =>
        (int)TargetMods(target, DealerMods(dealer, baseDamage) * amplifier);
}
