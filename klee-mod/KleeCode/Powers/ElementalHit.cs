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
    /// <paramref name="applyDealerMods"/> is QUARANTINED (the Klee overhaul) and
    /// has exactly one caller: <c>ProtoBombPower.Explode</c>. `EB-343` / R248
    /// ruled that a Bomb carries the TARGET's modifiers only -- the placer's
    /// Strength and Weak never enter it, at placement or at set-off -- so the
    /// explosion asks for the pipeline WITHOUT
    /// <see cref="SimDamagePipeline.DealerMods"/>. Everything else about the hit
    /// is unchanged: the aura still lands, the reaction still fires and
    /// amplifies, and the target's Vulnerable and cap still apply. Defaulted
    /// true, so every other caller -- the Burst volley, the echo, the companion
    /// arms, Oz -- is byte-identical. Sim twin: `deal_damage_to_enemy(...,
    /// powered=False)`, which the sheet's other quarantined arm already used.
    /// </summary>
    public static async Task<int> Deal(
        PlayerChoiceContext choiceContext, Creature target, Element element,
        decimal baseDamage, Creature? applier, bool ignoreBlock = false,
        bool applyDealerMods = true)
    {
        var dealt = applyDealerMods
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
    /// ONE CALLER, <c>ProtoBombPower.Explode</c>. Everything else in the mod
    /// goes through <see cref="Deal"/> and keeps the dealer's terms.
    /// </summary>
    public static Task<int> DealWithoutDealerMods(
        PlayerChoiceContext choiceContext, Creature target, Element element,
        decimal baseDamage, Creature? applier) =>
        Deal(choiceContext, target, element, baseDamage, applier,
             ignoreBlock: false, applyDealerMods: false);

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
