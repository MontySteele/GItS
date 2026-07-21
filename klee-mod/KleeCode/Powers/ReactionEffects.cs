using System.Linq;
using System.Threading.Tasks;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

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
    /// <summary>
    /// Monotonic count of named reactions resolved. Generated conditionals
    /// (reaction_triggered_by_this) diff it around a card play -- the sim
    /// resets reactions_this_card at resolve_card start and this funnel is
    /// the single place reactions resolve, so a snapshot diff is the same
    /// number. Counts EVERY named reaction, dealer or not (the sim
    /// increments before any dealer-gated credit); never reset -- only
    /// diffs are read.
    /// </summary>
    public static int TotalResolved { get; private set; }

    /// <summary>
    /// TotalResolved as of the start of the current player turn. The sim keeps
    /// an explicit state.reactions_this_turn and zeroes it at the top of the
    /// player turn (combat.py) BEFORE start-of-turn bomb detonation, so
    /// detonation-triggered reactions count toward the new turn. Mirrored as a
    /// snapshot rather than a second counter so there is still exactly one
    /// increment site.
    /// </summary>
    private static int _turnStartTotal;

    /// <summary>
    /// Reset the per-turn window. Called from KleeElementalHooks at
    /// AfterSideTurnEnd(Enemy) -- a strictly EARLIER broadcast than
    /// BeforeSideTurnStart(Player), where bombs detonate, so this needs no
    /// ordering assumption inside a single broadcast -- and at combat start,
    /// because the first player turn has no preceding enemy turn and the
    /// monotonic counter carries over between combats.
    /// </summary>
    public static void MarkTurnStart() => _turnStartTotal = TotalResolved;

    /// <summary>
    /// tier0 predicate reaction_triggered_this_turn (Chevreuse, Vanguard's
    /// Valor): `state.reactions_this_turn > 0`. RULED in the sheet as ANY
    /// reaction, not Overload-only.
    /// </summary>
    public static bool ReactionTriggeredThisTurn => TotalResolved > _turnStartTotal;

    public static async Task Resolve(
        PlayerChoiceContext choiceContext,
        Reaction reaction,
        Creature target,
        Creature? dealer,
        CardModel? cardSource,
        Element consumedAura)
    {
        if (reaction != Reaction.None)
        {
            TotalResolved++;
        }

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

            // Catalytic Conversion, right after the flat +5 exactly as in the
            // sim (reactions.py _react): +Amount Sparks and +Amount x 5 Burst
            // Energy per reaction. Same funnel, so it can neither miss a
            // reaction nor double-count one.
            var catalytic = dealer.Powers
                .OfType<ReactionBonusSparkEnergyPower>().FirstOrDefault()?.Amount ?? 0;
            if (catalytic > 0)
            {
                await SparkPower.Gain(choiceContext, dealer, catalytic, cardSource);
                await KleeBurstResource.Gain(
                    choiceContext, dealer,
                    ReactionKitConstants.CatalyticBurstPerReaction * catalytic,
                    cardSource);
            }
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

            // Completed with the companions batch (2026-07-21): the roster's
            // hydro/electro/cryo/anemo appliers make all four REACHABLE for
            // the first time -- until Oz there was no electro in the mod, so
            // the loud stubs never fired in play. Every API below is the
            // verified idiom from elsewhere in the codebase.

            case Reaction.Overload:
                // tier0 _react -> _splash: OVERLOAD_SPLASH flat to ALL living
                // enemies, ignores block (sim: raw `hp -=`), hence
                // Unblockable | Unpowered with no dealer -- which also keeps
                // splash from early-detonating bombs or counting as an attack.
                var splashTargets = target.CombatState?.HittableEnemies.ToList();
                if (splashTargets != null)
                {
                    foreach (var e in splashTargets)
                    {
                        await CreatureCmd.Damage(
                            choiceContext, e, ReactionConstants.OverloadSplash,
                            ValueProp.Unblockable | ValueProp.Unpowered,
                            dealer: null, cardSource: null);
                    }
                }
                break;

            case Reaction.ElectroCharged:
                // tier0: apply_power(enemy, "dot", ELECTROCHARGED_DOT). The
                // sim's dot IS poison (owner-turn-start tick of Amount, then
                // decrement -- powers.py on_turn_start), so the core's own
                // PoisonPower is the exact mirror; no custom power needed.
                await PowerCmd.Apply<PoisonPower>(
                    choiceContext, target, ReactionConstants.ElectroChargedDot,
                    applier: dealer, cardSource: cardSource);
                break;

            case Reaction.Swirl:
                // tier0 _react anemo branch: the consumed aura is applied to
                // EVERY living enemy -- the original target included (its own
                // aura was consumed first, so it gets a fresh copy).
                // apply_aura overwrites: same element refreshes, different
                // element is replaced outright, full duration either way.
                var swirlTargets = target.CombatState?.HittableEnemies.ToList();
                if (swirlTargets != null)
                {
                    foreach (var e in swirlTargets)
                    {
                        var existing = AuraCmd.Find(e);
                        if (existing != null)
                        {
                            if (existing.Element == consumedAura)
                            {
                                await AuraCmd.Refresh(
                                    choiceContext, existing, dealer, cardSource);
                                continue;
                            }
                            await PowerCmd.Remove(existing);
                        }
                        await AuraCmd.Apply(
                            choiceContext, e, consumedAura, dealer, cardSource);
                    }
                }
                break;

            case Reaction.Crystallize:
                // tier0: state.player.block += CRYSTALLIZE_BLOCK. The dealer
                // IS the player for every reachable path; a dealer-less
                // crystallize has no one to credit, so it logs loudly
                // instead of guessing (sim always has a player).
                if (dealer != null)
                {
                    await CreatureCmd.GainBlock(
                        dealer, ReactionConstants.CrystallizeBlock,
                        ValueProp.Unpowered, null, fast: true);
                }
                else
                {
                    Log.Warn($"[{KleeMod.ModId}] Crystallize with no dealer " +
                             "-- no one to credit the Block to; skipped.");
                }
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
