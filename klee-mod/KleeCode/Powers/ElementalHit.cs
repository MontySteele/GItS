using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// The one element-tagged non-attack hit: tier0 deal_damage_to_enemy for
/// every source that is not a powered attack card (bombs, the Burst volley,
/// Oz) plus the damage-less element ops (apply_aura, swirl --
/// sim resolve_hit with damage 0).
///
/// Pipeline, in sim order: Strength/Weak on the applier (pre-amp) -> element
/// resolve (apply / refresh / consume+react, Vaporize/Melt amplify THIS hit)
/// -> Vulnerable on the target (post-amp) -> ONE truncation -> Unpowered
/// damage (no attack hooks, no early bomb detonation, no Strength scaling
/// from the native gate -- the sim's modifiers came from SimDamagePipeline
/// above). BombPower.Detonate and the SparksNSplash volley route here so
/// the pipeline cannot drift between sources.
/// </summary>
internal static class ElementalHit
{
    /// <summary>Element-tagged damage hit (tier0 deal_damage_to_enemy).
    ///
    /// <paramref name="ignoreBlock"/> is QUARANTINED (the Inazuma companion
    /// overhaul) and has exactly one caller: Chiori's Tamoto, whose printed
    /// text is "deal 6 Geo damage to a random enemy, IGNORING BLOCK". It adds
    /// <c>ValueProp.Unblockable</c> to the <c>Unpowered</c> every hit through
    /// here already carries, and changes nothing else -- the hit still reacts,
    /// still counts as a hit, and is still capped by Intangible, because
    /// unblockable is not uncappable (R128). Defaulted false, so every shipped
    /// caller is byte-identical. Sim twin: `deal_damage_to_enemy(...,
    /// ignore_block=True)`.
    ///
    /// IT RETURNS THE NUMBER IT DEALT -- the truncated amount handed to
    /// <c>CreatureCmd.Damage</c>: after Strength/Weak, after the reaction
    /// amplifier, after Vulnerable. <c>EB-270</c> is why. Klee's overhaul Bomb
    /// prints a number on the badge, a number in the tooltip and a number on
    /// Big Badda Boom's bonus line, and the only way all three can be the SAME
    /// number is for the one that LANDED to be readable from the one place
    /// that computes it -- rather than each surface re-deriving its own
    /// arithmetic and disagreeing under Weak. Every existing caller ignores the
    /// result and is behaviour-identical; nothing in the pipeline moved.
    ///
    /// <paramref name="powered"/> is QUARANTINED and, since `EB-343`,
    /// has TWO callers -- one per Klee-and-Kokomi prototype arm, asking
    /// the same thing for two different reasons. False skips
    /// <see cref="SimDamagePipeline.DealerMods"/> -- the dealer's Strength
    /// and Weak, and with them every flat attack buff the mirror carries --
    /// and changes nothing else: the aura still lands, the reaction still
    /// fires and its amplifier is still read off the applier, and the
    /// target's Vulnerable still multiplies through
    /// <see cref="SimDamagePipeline.TargetMods"/>. Defaulted true, so every
    /// shipped caller is byte-identical.
    ///
    ///   * <c>KokomiPlan.Hit</c>, since <c>EB-334</c> ruled (R246 pick 1)
    ///     that the BAKE-KURAGE deals a Plan's damage.
    ///   * <see cref="DealWithoutDealerMods"/>, the overhaul Bomb's own
    ///     door, since <c>EB-343</c> ruled (R248) that a Bomb carries the
    ///     TARGET's modifiers only -- the placer's Strength and Weak never
    ///     enter it, at placement or at set-off.
    ///
    /// ONE FLAG AND NOT TWO, which is worth saying because the two arms
    /// reached it a day apart and each could have spelled its own: what
    /// they want is the same edit to the same pipeline stage, and a second
    /// parameter meaning the same thing is a second thing to keep in step
    /// with `deal_damage_to_enemy(..., powered=False)` on the sim side.
    ///
    /// WHY A FLAG AND NOT "PASS THE PET AS THE APPLIER", which is how the
    /// Tamakushi Casket says the same thing one file over: the applier is
    /// also who applies the AURA and who owns the REACTION's debuff, and a
    /// Plan-caused Freeze has to stay a debuff SHE applied or the Casket
    /// would stop answering it and The Clouds Like Waves Rippling would
    /// stop paying for it. Draft 6 gives the jellyfish the arithmetic, not
    /// the authorship. It is also the exact sim twin:
    /// `deal_damage_to_enemy(..., powered=False)` keeps the applier and
    /// drops `modify_damage_dealt`, and tier0 has no pet object to hand
    /// over.
    /// </summary>
    public static async Task<int> Deal(
        PlayerChoiceContext choiceContext, Creature target, Element element,
        decimal baseDamage, Creature? applier, bool ignoreBlock = false,
        bool powered = true)
    {
        var dealt = powered
            ? SimDamagePipeline.DealerMods(applier, baseDamage)
            : baseDamage;
        // DURIN, PRINCIPLE OF PURITY / DARK (AoE trim, 2026-10-03): "Your Pyro
        // damage deals 4 more", Bombs and Mines included (this door is theirs,
        // `powered` or not), before the amplifier -- the sim's additive phase
        // in `deal_damage_to_enemy`.
        dealt += PurityDarkPower.BonusFor(applier, element);

        // VARKA (the Oath rework, sec.3): an application of his credits Oath.
        await VarkaOath.NoteApplication(choiceContext, applier, element,
            target: target);
        var aura = AuraCmd.Find(target);
        // TELEMETRY ONLY: the amplifier this hit carries, for `NoteAmplified`.
        var ampReaction = Reaction.None;
        var amp = 1m;
        if (aura == null)
        {
            await AuraCmd.Apply(choiceContext, target, element, applier, cardSource: null);
        }
        else
        {
            // Consume before resolving, same as AuraPower (Swirl must not
            // re-trigger off the aura it is spreading).
            var reaction = ReactionTable.Lookup(aura.Element, element);
            amp = ReactionTable.AmplifierMultiplier(reaction, applier);
            ampReaction = reaction;
            dealt *= amp;
            await ResolveOnAura(choiceContext, target, aura, element, applier);
        }

        // The two halves and their order are the pipeline's, and they are what
        // `SimDamagePipeline.Resolve` composes so a FACE can predict this
        // number without re-deriving it (EB-265). Do not fold this call into
        // `Resolve`: `tier0/tests/test_reaction_phase_parity.py` pins the
        // TargetMods read as happening after `ReactionEffects.Resolve`, which
        // is what makes a Superconduct's Vulnerable amplify this same hit.
        var landed = (int)SimDamagePipeline.TargetMods(target, dealt);
        // TELEMETRY ONLY: the dealer stays null for the engine; the scope
        // names the seat for `PlayTelemetry` (an outer Bomb or pet scope wins).
        using var credit = Diagnostics.DamageCredit.OpenIfNone(
            applier, Diagnostics.DamageCredit.Element);
        // 2026-10-02 (combat visual audit, gap 3): the element's hit effect,
        // the same one an Attack card of that element draws. Visual only.
        ElementHitFx.SpawnOn(target, element);
        var results = await CreatureCmd.Damage(
            choiceContext, target, landed,
            ignoreBlock ? ValueProp.Unpowered | ValueProp.Unblockable
                        : ValueProp.Unpowered,
            dealer: null, cardSource: null, cardPlay: null);
        NoteAmplified(target, applier, ampReaction, amp, results);
        await CreditBlockBreak(choiceContext, target, applier, results);
        return landed;
    }

    /// <summary>
    /// TELEMETRY ONLY (2026-10-06): file the amplifier's share of a hit that
    /// already landed -- what reached <paramref name="target"/>'s HP plus
    /// Block, less that over <paramref name="mult"/>. A read of the results;
    /// <c>ReactionTally</c> swallows its own errors, and so does this.
    /// </summary>
    internal static void NoteAmplified(
        Creature target, Creature? applier, Reaction reaction, decimal mult,
        IEnumerable<DamageResult>? results)
    {
        try
        {
            if (results == null || mult <= 1m) return;
            if (reaction is not (Reaction.Vaporize or Reaction.Melt)) return;
            var dealt = 0;
            foreach (var r in results)
            {
                if (r.Receiver != target) continue;
                dealt += (int)r.UnblockedDamage + (int)r.BlockedDamage;
            }
            Diagnostics.ReactionTally.NoteAmplified(
                target.CombatState, applier, reaction, mult, dealt);
        }
        catch (System.Exception)
        {
            // Measurement never throws into the damage path.
        }
    }

    /// <summary>
    /// THE OVERHAUL BOMB'S DOOR INTO <see cref="Deal"/> (`EB-343`, R248), and
    /// it is a named method rather than a named argument for one reason: an
    /// argument's value is invisible to every check the headless suite can
    /// make. An explosion needs a live <c>CombatState</c>, so no test can watch
    /// one land; what a test CAN read is which method a call site calls
    /// (<c>KleeTests.Harness.Il</c>). Spelling the exception as a method makes
    /// "a Bomb does not carry Klee's Strength and Weak" a fact about the call
    /// graph, so deleting it fails a pin instead of quietly restoring the old
    /// rule.
    ///
    /// TWO CALLERS, <c>ProtoBombPower.Explode</c> and, since 2026-09-25,
    /// Sparks 'n' Splash's echo (<c>BombEchoPower.Fire</c>), which pays a
    /// Bomb's size on a Bomb's terms without setting it off. Everything else
    /// in the mod goes through <see cref="Deal"/> and keeps the dealer's
    /// terms.
    ///
    /// THE KOKOMI ARM PASSES <c>powered: false</c> DIRECTLY and does not need a
    /// door, which is not an inconsistency: a Plan's hit is reachable from the
    /// headless suite through <c>KokomiPlan</c>'s own pins, and this one is
    /// not. The door buys a structural pin where no value pin can exist.
    public static Task<int> DealWithoutDealerMods(
        PlayerChoiceContext choiceContext, Creature target, Element element,
        decimal baseDamage, Creature? applier) =>
        Deal(choiceContext, target, element, baseDamage, applier,
             ignoreBlock: false, powered: false);

    /// <summary>
    /// A NON-ATTACK HIT WITH NO ELEMENT: tier0 <c>deal_damage_to_enemy(...,
    /// element=None)</c>, whose <c>resolve_hit</c> returns the damage untouched.
    /// <see cref="Deal"/>'s pipeline less its aura step -- the dealer's
    /// Strength and Weak, then the target's Vulnerable, ONE truncation,
    /// Unpowered damage -- so the hit applies no aura, consumes none and
    /// triggers no reaction. Witch's Flame's hit
    /// (<c>CompanionPowers.WitchsFlamePower</c>) is the same arithmetic written
    /// inline.
    ///
    /// QUARANTINED CALLERS, two: the Klee overhaul's Spark Knight (R276), and
    /// since draft 3 (2026-09-25) the Furina Stage's two damage acts, which
    /// pass <paramref name="powered"/> false exactly as <see cref="Deal"/>'s
    /// callers do (a performance carries no Strength, `EB-495` D3). A named
    /// door rather than <c>Element.None</c> passed to <see cref="Deal"/>,
    /// which would hand <c>None</c> to the reaction table as a trigger, and
    /// because a call site is what the headless suite can pin. Defaulted true,
    /// so Spark Knight is byte-identical.
    /// </summary>
    /// <summary>
    /// QUARANTINED (the Klee arm's Alice's Teapot): a hit that reacts as if
    /// the target held <paramref name="assumedAura"/>, and touches the aura it
    /// really holds not at all -- nothing real is consumed, refreshed or
    /// applied. The reaction still resolves through the one site every
    /// reaction passes (<see cref="ReactionEffects.Resolve"/>), so the
    /// amplifier, the Burst credit and every listener see an ordinary
    /// reaction. With no reaction between the two elements it is
    /// <see cref="DealWithoutDealerMods"/> unchanged.
    /// </summary>
    public static async Task<int> DealAsIfAura(
        PlayerChoiceContext choiceContext, Creature target, Element element,
        Element assumedAura, decimal baseDamage, Creature? applier)
    {
        var reaction = ReactionTable.Lookup(assumedAura, element);
        if (reaction == Reaction.None)
        {
            return await DealWithoutDealerMods(
                choiceContext, target, element, baseDamage, applier);
        }
        // Principle of Purity's Dark, as in `Deal` (a Teapot Bomb is still her
        // Pyro damage).
        var amp = ReactionTable.AmplifierMultiplier(reaction, applier);
        var dealt = (baseDamage + PurityDarkPower.BonusFor(applier, element))
            * amp;
        await ReactionEffects.Resolve(
            choiceContext, reaction, target, applier, null, assumedAura);
        var landed = (int)SimDamagePipeline.TargetMods(target, dealt);
        using var credit = Diagnostics.DamageCredit.OpenIfNone(
            applier, Diagnostics.DamageCredit.Element);
        ElementHitFx.SpawnOn(target, element);
        var results = await CreatureCmd.Damage(
            choiceContext, target, landed, ValueProp.Unpowered,
            dealer: null, cardSource: null, cardPlay: null);
        NoteAmplified(target, applier, reaction, amp, results);
        await CreditBlockBreak(choiceContext, target, applier, results);
        return landed;
    }

    public static async Task<int> DealUnelemented(
        PlayerChoiceContext choiceContext, Creature target,
        decimal baseDamage, Creature? applier, bool powered = true)
    {
        var dealt = powered
            ? SimDamagePipeline.DealerMods(applier, baseDamage)
            : baseDamage;
        var landed = (int)SimDamagePipeline.TargetMods(target, dealt);
        using var credit = Diagnostics.DamageCredit.OpenIfNone(
            applier, Diagnostics.DamageCredit.Power);
        var results = await CreatureCmd.Damage(
            choiceContext, target, landed, ValueProp.Unpowered,
            dealer: null, cardSource: null, cardPlay: null);
        await CreditBlockBreak(choiceContext, target, applier, results);
        return landed;
    }

    /// <summary>
    /// Damage-less element application: tier0 resolve_hit(enemy, element, 0)
    /// -- the apply_aura and swirl ops. Identical lifecycle, no damage call
    /// (the sim deals 0; amplifiers of 0 are 0). Anemo/Geo never stick
    /// (AuraCmd.Apply's own rule), so swirl on an aura-less enemy is a no-op
    /// exactly as in the sim.
    /// </summary>
    public static async Task ApplyOnly(
        PlayerChoiceContext choiceContext, Creature target, Element element,
        Creature? applier)
    {
        // VARKA (the Oath rework, sec.3): an application of his credits Oath.
        await VarkaOath.NoteApplication(choiceContext, applier, element,
            target: target);
        var aura = AuraCmd.Find(target);
        if (aura == null)
        {
            await AuraCmd.Apply(choiceContext, target, element, applier, cardSource: null);
        }
        else
        {
            await ResolveOnAura(choiceContext, target, aura, element, applier);
        }
    }

    /// <summary>
    /// A hit of <paramref name="element"/> on a STANDING aura, for both doors
    /// above: refresh, consume and react, or nothing -- <see cref="TriggerRules.Outcome"/> decides, the one decision
    /// <see cref="AuraPower"/>'s own lifecycle takes too. Sim twin:
    /// <c>reactions.resolve_hit</c> below its no-aura branch.
    /// </summary>
    /// <summary>The reaction row's detail for a Vaporize or Melt an
    /// element-only application set off: nothing to multiply.</summary>
    public const string NoHitToAmplify =
        "No hit came with it, so there was nothing to amplify.";

    /// <summary>
    /// After each of this funnel's <c>CreatureCmd.Damage</c> calls, whose
    /// dealer stays null for the engine (the hit is Unpowered and already
    /// carries the sim's modifiers, so no dealer-side hook may touch it
    /// again): the Block break CREDITED to the applier all the same.
    ///
    /// HAND DRILL (Klee final-pass round, lane 2, 2026-10-02): "gave no
    /// Vulnerable when a Bomb broke the boss's Block, only when a Pyro card's
    /// hit did." The base relic's hook is
    /// <c>AfterBlockBroken(target, breaker)</c> and its condition is
    /// <c>breaker == Owner.Creature || breaker?.PetOwner == Owner</c> (0.111.0
    /// decompile) -- not "a card attack": every base power that deals damage
    /// (Juggernaut, Inferno, Black Hole) passes its owner as the dealer, so its
    /// break counts. The game reports the breaker as the dealer, which here is
    /// null, so the relic never saw a Bomb, a Burst volley or a performance
    /// break anything.
    ///
    /// SO THE BREAK IS REPORTED A SECOND TIME, WITH THE BREAKER, TO THE
    /// APPLIER'S RELICS ONLY. The null-breaker dispatch the game already made
    /// reached every listener; the only listeners in the game are Hand Drill
    /// (which ignores a null breaker) and the Tunneler's Burrowed (an enemy
    /// power, not a relic, so it is not called twice). The mod declares none.
    /// </summary>
    private static async Task CreditBlockBreak(
        PlayerChoiceContext choiceContext, Creature target, Creature? applier,
        IEnumerable<DamageResult> results)
    {
        if (applier?.Player is not { } player || target.IsPlayer) return;
        if (!results.Any(r => r.WasBlockBroken && r.Receiver == target)) return;
        foreach (var relic in player.Relics.ToList())
        {
            await relic.AfterBlockBroken(choiceContext, target, applier);
            relic.InvokeExecutionFinished();
        }
    }

    /// <summary>2026-10-01 (a Varka seat): Barbara's Hydro printed "Vaporize
    /// ... off Varka" and the seat saw nothing happen. Vaporize and Melt
    /// amplify a HIT, and an application carries none, so the row says so.
    /// </summary>
    private static void NoteNoHit(Element aura, Element element)
    {
        if (ReactionTable.Lookup(aura, element) is Reaction.Vaporize or Reaction.Melt)
            ReactionLog.DetailNext(NoHitToAmplify);
    }

    private static async Task ResolveOnAura(
        PlayerChoiceContext choiceContext, Creature target, AuraPower aura,
        Element element, Creature? applier)
    {
        switch (TriggerRules.Outcome(aura.Element, element))
        {
            case TriggerRules.HitOutcome.Refresh:
                await AuraCmd.Refresh(choiceContext, aura, applier, cardSource: null);
                break;

            case TriggerRules.HitOutcome.Consume:
            {
                var reaction = ReactionTable.Lookup(aura.Element, element);
                var consumed = aura.Element;
                await PowerCmd.Remove(aura);
                NoteNoHit(consumed, element);
                await ReactionEffects.Resolve(
                    choiceContext, reaction, target, applier, null, consumed);
                break;
            }

            default:
                break;   // no reaction between these elements
        }
    }
}
