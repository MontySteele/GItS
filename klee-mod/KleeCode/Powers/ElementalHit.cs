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
    /// <paramref name="powered"/> is QUARANTINED (the Kokomi overhaul) and has
    /// exactly one caller: <c>KokomiPlan.Hit</c>, since <c>EB-334</c> ruled
    /// (R246 pick 1) that the BAKE-KURAGE deals a Plan's damage. False skips
    /// <see cref="SimDamagePipeline.DealerMods"/> -- the dealer's Strength and
    /// Weak, and with them every flat attack buff the mirror carries -- and
    /// changes nothing else: the aura still lands, the reaction still fires
    /// and its amplifier is still read off the applier, and the target's
    /// Vulnerable still multiplies through
    /// <see cref="SimDamagePipeline.TargetMods"/>.
    ///
    /// WHY A FLAG AND NOT "PASS THE PET AS THE APPLIER", which is how the
    /// Tamakushi Casket says the same thing one file over: the applier is also
    /// who applies the AURA and who owns the REACTION's debuff, and a
    /// Plan-caused Freeze has to stay a debuff SHE applied or the Casket would
    /// stop answering it and The Clouds Like Waves Rippling would stop paying
    /// for it. Draft 6 gives the jellyfish the arithmetic, not the authorship.
    /// It is also the exact sim twin: `deal_damage_to_enemy(...,
    /// powered=False)` keeps the applier and drops `modify_damage_dealt`, and
    /// tier0 has no pet object to hand over. Defaulted true, so every shipped
    /// caller is byte-identical.
    /// </summary>
    public static async Task<int> Deal(
        PlayerChoiceContext choiceContext, Creature target, Element element,
        decimal baseDamage, Creature? applier, bool ignoreBlock = false,
        bool powered = true)
    {
        var dealt = powered
            ? SimDamagePipeline.DealerMods(applier, baseDamage)
            : baseDamage;

        var aura = AuraCmd.Find(target);
        if (aura == null)
        {
            await AuraCmd.Apply(choiceContext, target, element, applier, cardSource: null);
        }
        else if (aura.Element == element)
        {
            await AuraCmd.Refresh(choiceContext, aura, applier, cardSource: null);
        }
        else
        {
            // Consume before resolving, same as AuraPower (Swirl must not
            // re-trigger off the aura it is spreading).
            var reaction = ReactionTable.Lookup(aura.Element, element);
            var consumed = aura.Element;
            dealt *= ReactionTable.AmplifierMultiplier(reaction, applier);
            await PowerCmd.Remove(aura);
            await ReactionEffects.Resolve(
                choiceContext, reaction, target, applier, null, consumed);
        }

        // The two halves and their order are the pipeline's, and they are what
        // `SimDamagePipeline.Resolve` composes so a FACE can predict this
        // number without re-deriving it (EB-265). Do not fold this call into
        // `Resolve`: `tier0/tests/test_reaction_phase_parity.py` pins the
        // TargetMods read as happening after `ReactionEffects.Resolve`, which
        // is what makes a Superconduct's Vulnerable amplify this same hit.
        var landed = (int)SimDamagePipeline.TargetMods(target, dealt);
        await CreatureCmd.Damage(
            choiceContext, target, landed,
            ignoreBlock ? ValueProp.Unpowered | ValueProp.Unblockable
                        : ValueProp.Unpowered,
            dealer: null, cardSource: null, cardPlay: null);
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
        var aura = AuraCmd.Find(target);
        if (aura == null)
        {
            await AuraCmd.Apply(choiceContext, target, element, applier, cardSource: null);
        }
        else if (aura.Element == element)
        {
            await AuraCmd.Refresh(choiceContext, aura, applier, cardSource: null);
        }
        else
        {
            var reaction = ReactionTable.Lookup(aura.Element, element);
            var consumed = aura.Element;
            await PowerCmd.Remove(aura);
            await ReactionEffects.Resolve(
                choiceContext, reaction, target, applier, null, consumed);
        }
    }
}
