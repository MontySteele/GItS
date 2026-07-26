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
    /// <summary>Element-tagged damage hit (tier0 deal_damage_to_enemy).</summary>
    public static async Task Deal(
        PlayerChoiceContext choiceContext, Creature target, Element element,
        decimal baseDamage, Creature? applier)
    {
        var dealt = SimDamagePipeline.DealerMods(applier, baseDamage);

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

        await CreatureCmd.Damage(
            choiceContext, target, (int)SimDamagePipeline.TargetMods(target, dealt),
            ValueProp.Unpowered, dealer: null, cardSource: null);
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
