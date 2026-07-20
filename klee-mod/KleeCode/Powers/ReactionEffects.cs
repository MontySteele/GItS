using System.Threading.Tasks;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Powers;

/// <summary>
/// Side effects for each reaction, ported from _react() in
/// tier0/engine/reactions.py.
///
/// Vaporize and Melt are absent by design: they are amplifiers, handled
/// entirely in AuraPower.ModifyDamageMultiplicative. The sim's IRON RULE is
/// that they multiply exactly one hit and are consumed with the aura, so they
/// must never appear as a lingering effect here.
/// </summary>
internal static class ReactionEffects
{
    public static async Task Resolve(
        PlayerChoiceContext choiceContext,
        Reaction reaction,
        Creature target,
        Creature? dealer,
        CardModel? cardSource,
        Element consumedAura)
    {
        // Burst economy, reaction half: +5 for EVERY named reaction --
        // amplifiers included (the sim credits BURST_PER_REACTION whenever
        // resolve_hit names a reaction, and Vaporize/Melt are named). This is
        // the single funnel: AuraPower.AfterDamageReceived and
        // BombPower.Detonate both route here, so no gain site is missed and
        // none double-counts. Dealer-credited; Gain gates on Klee (sim:
        // `if p.burst_max`), so a dealer-less detonation edge case no-ops
        // harmlessly rather than crediting the wrong side.
        if (reaction != Reaction.None && dealer != null)
        {
            await KleeBurstResource.Gain(
                choiceContext, dealer, BurstConstants.PerReaction, cardSource);
        }

        switch (reaction)
        {
            case Reaction.Vaporize:
            case Reaction.Melt:
                // Amplifiers: damage already multiplied, aura already consumed.
                break;

            case Reaction.Superconduct:
                await PowerCmd.Apply<VulnerablePower>(
                    choiceContext, target,
                    ReactionConstants.SuperconductVuln,
                    applier: dealer, cardSource: cardSource);
                break;

            case Reaction.Frozen:
                // TODO(C2.1): bosses must take Vulnerable FROZEN_BOSS_VULN
                // instead of Frozen (round-3 ruling, stands post-errata). Not
                // implemented -- I have not yet verified how to identify a boss
                // from a Creature, and guessing at that predicate is how the
                // "is_boss" branch silently never fires. Until then every
                // enemy, boss included, gets the soft-control version, which is
                // WRONG for bosses and will skew any boss playtest.
                await PowerCmd.Apply<FrozenPower>(
                    choiceContext, target, 1,
                    applier: dealer, cardSource: cardSource);
                break;

            // ---------------------------------------------------------------
            // NOT YET IMPLEMENTED. Each of these needs an API I have not
            // verified against the decompiled assembly yet, and after this
            // session's run of "it compiled so I assumed it worked" bugs I am
            // not guessing at them. They log loudly rather than failing silently
            // so a playtest cannot mistake them for balance.
            //
            //  - Overload       needs the live enemy list + CreatureCmd.Damage
            //                   splash (OVERLOAD_SPLASH = 6, all enemies,
            //                   ignores block per sim simplification)
            //  - ElectroCharged needs a stacking DoT power (4 dmg, 2 turns);
            //                   check whether a base-game poison-like power can
            //                   be reused before writing one
            //  - Swirl          needs the live enemy list to copy `consumedAura`
            //                   onto every other enemy
            //  - Crystallize    needs the player Creature + a block-gain path
            //                   that does not require a CardPlay
            // ---------------------------------------------------------------
            case Reaction.Overload:
            case Reaction.ElectroCharged:
            case Reaction.Swirl:
            case Reaction.Crystallize:
                Log.Warn($"[{KleeMod.ModId}] Reaction {reaction} triggered " +
                         $"({consumedAura} aura consumed) but its effect is NOT " +
                         $"IMPLEMENTED yet -- no effect applied.");
                break;

            case Reaction.None:
            default:
                break;
        }

        if (reaction != Reaction.None)
        {
            Log.Info($"[{KleeMod.ModId}] REACTION {reaction} on {target.Name} " +
                     $"(consumed {consumedAura}).");
        }
    }
}
