using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.Rooms;
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
    ///
    /// THAT JUSTIFICATION WAS INCOMPLETE, and knowing why is the reason
    /// <see cref="MarkExtraTurnStart"/> exists. "Earlier broadcast" only
    /// orders the two hooks WHEN BOTH FIRE. On an extra player turn (Pael's
    /// Eye) no enemy side turn happens at all: `CombatManager.SwitchSides`
    /// keeps `CurrentSide == Player` while `_playersTakingExtraTurn` is
    /// non-empty, and `EndEnemyTurnInternal` is the only path to
    /// `Hook.AfterTurnEnd(Enemy)`. So this never ran, and the window carried
    /// across two player turns. This is the sole per-turn window in the mod
    /// keyed to the enemy-side broadcast; every other one resets on
    /// `BeforeSideTurnStart(Player)`, which DOES fire on an extra turn.
    /// </summary>
    public static void MarkTurnStart()
    {
        _turnStartTotal = TotalResolved;
        // Fully cleared rather than purged: every key is written and read
        // inside a single player turn, so there is nothing to carry over and
        // no way for this map to grow across a run.
        DealerReactionsThisTurn.Clear();
    }

    /// <summary>
    /// Reopen the window for a player taking an EXTRA turn.
    ///
    /// WHY A SEPARATE ENTRY POINT, AND WHY NOT AT BeforeSideTurnStart. The
    /// obvious move -- rekey the whole window to `BeforeSideTurnStart(Player)`
    /// like every other per-turn reset in the mod -- is wrong: bombs detonate
    /// inside that same broadcast (`BombPower.BeforeSideTurnStart` ->
    /// `Detonate`), so an unordered reset could zero out detonation-triggered
    /// reactions belonging to the turn that just started. That intra-broadcast
    /// hazard is exactly what the enemy-turn-end siting was avoiding. The
    /// clean slot is `AbstractModel.AfterTakingExtraTurn(Player)`, which
    /// `CombatManager.SwitchFromPlayerToEnemySide` broadcasts AFTER
    /// `SwitchSides()` and strictly BEFORE `StartTurn()` -- i.e. the same slot
    /// the enemy-turn-end site occupies on a normal round. (Decompile read
    /// pinned to the build: `klee-mod/KleeTests/bin/Debug/sts2.dll`.)
    ///
    /// WHAT WAS WRONG WITHOUT IT, and it pointed both ways at once. On the
    /// extra turn `ReactionTriggeredThisTurn` still read true off the previous
    /// turn, so Chevreuse / Vanguard's Valor and Furina's Audience
    /// Participation paid a rider with no reaction behind it (a windfall --
    /// both are `buff_next_attack`); and `DealerReactionsThisTurn[dealer]` was
    /// still 1, so the first real reaction saw `already == 1`,
    /// `NoteFirstReaction` was skipped, and Courtroom Drama's once-per-turn
    /// Vulnerable never applied -- dropping the x1.5 from both the preview and
    /// the dealt damage. `ReactionsThisTurn` accumulated across both turns.
    ///
    /// CO-OP SCOPING IS RATIFIED AS SHIPPED (R205, 2026-08-24). An extra turn
    /// is a new turn FOR THE BOARD and only for the player taking it:
    /// board-global turn facts are RE-TAKEN (`_turnStartTotal`, and
    /// `ReactionTriggeredThisTurn` stays global across the extra turn exactly
    /// as red-pen R1 made it -- a Reaction is a fact about the board), while
    /// the per-dealer map clears ONLY the extra-turn player's own key. A
    /// partner who is not taking the extra turn keeps their once-per-turn
    /// window, because their count is legitimately current and `Clear()` would
    /// wipe it; and the partner does NOT receive another turn. Solo this is
    /// byte-identical to `Clear()`, where there is one player.
    /// </summary>
    public static void MarkExtraTurnStart(Creature? extraTurnCreature)
    {
        _turnStartTotal = TotalResolved;
        if (extraTurnCreature != null)
        {
            DealerReactionsThisTurn.Remove(extraTurnCreature);
        }
    }

    /// <summary>
    /// Reactions this player turn, PER DEALER. The global counters above are
    /// deliberately shared (red-pen R1: a Reaction is a fact about the board);
    /// Courtroom Drama is not, because it is a POWER and a power belongs to
    /// somebody. Split out 2026-07-29: the once-per-turn gate used to read
    /// the global <see cref="ReactionsThisTurn"/>, so in co-op a partner's
    /// reaction spent your window -- flatly contradicting the contract written
    /// on <see cref="CurtainCallHooks.NoteFirstReaction"/> ("your partner's
    /// reaction does not spend your once-per-turn window"). Solo, where the
    /// dealer is the only player, this is byte-for-byte the sim's
    /// <c>state.reactions_this_turn == 1</c>.
    /// </summary>
    private static readonly Dictionary<Creature, int> DealerReactionsThisTurn =
        new();

    /// <summary>
    /// tier0 predicate reaction_triggered_this_turn (Chevreuse, Vanguard's
    /// Valor): `state.reactions_this_turn > 0`. RULED in the sheet as ANY
    /// reaction, not Overload-only.
    ///
    /// CO-OP SCOPE, SEALED 2026-07-26 (red-pen R1). This counter and
    /// <see cref="TotalResolved"/> are deliberately GLOBAL, not per-player:
    /// in co-op your partner's Overload satisfies your Chevreuse, and a
    /// reaction landing inside your card's resolution window satisfies your
    /// Boom Goes the Dynamite. **That is intended, not the G-B1 leak.**
    ///
    /// The G-B2 census flagged it as needs-ruling precisely because it LOOKS
    /// like the Best Friends Forever bug -- a "this combat/turn" tracker that
    /// is correct solo and divergent in co-op. The distinction is what the
    /// tracker is a claim ABOUT. BFF's list answered "which cards did YOU
    /// play", so an unowned entry was simply wrong. This one answers "did a
    /// Reaction happen", and a Reaction is a fact about the BOARD that both
    /// players are standing on. Elements are the shared system in this mod;
    /// making reaction payoffs private would mean two players applying auras
    /// to the same enemy could not cooperate, which is the opposite of the
    /// design.
    ///
    /// So: do NOT "fix" this by scoping it to an owner. If the intent ever
    /// changes, it changes at the ruling, not in the code -- see
    /// docs/archive/red-pen-2026-07-26.md R1 and the co-op section of
    /// docs/archive/playtest-2026-07-25-coop-a0.md.
    /// </summary>
    public static bool ReactionTriggeredThisTurn => TotalResolved > _turnStartTotal;

    /// <summary>
    /// How many reactions have resolved this player turn, on the shared board.
    /// The sim's `state.reactions_this_turn`. Derived from the same snapshot
    /// as <see cref="ReactionTriggeredThisTurn"/> rather than kept as a second
    /// counter, so there is still exactly one increment site.
    ///
    /// NOT the Courtroom Drama gate. That reads
    /// <see cref="DealerReactionsThisTurn"/> -- see the note there for why a
    /// board-wide count is the wrong question to ask about an owned power.
    /// This stays public as the board-scoped reading the sim mirrors.
    /// </summary>
    public static int ReactionsThisTurn => TotalResolved - _turnStartTotal;

    /// <summary>
    /// Would the NEXT reaction this dealer causes be their first this turn?
    ///
    /// The read-only twin of the gate inside <see cref="Resolve"/> (`already
    /// == 0`), pulled out so the damage pipeline can ASK the question one
    /// phase before Resolve ANSWERS it -- see
    /// <see cref="CurtainCallHooks.CourtroomDramaWillAmplify"/>. Pure: it
    /// only reads the map, and the increment stays in Resolve so there is
    /// still exactly one write site.
    /// </summary>
    public static bool NextReactionIsFirstFor(Creature? dealer) =>
        dealer != null
        && (DealerReactionsThisTurn.TryGetValue(dealer, out var seen)
            ? seen : 0) == 0;

    /// <summary>
    /// PURE forecast of the boss-room Frozen substitution (EB-19/M1b): would a
    /// Frozen reaction on this target apply Vulnerable instead of Frozen?
    ///
    /// The read-only twin of the predicate inside <see cref="Resolve"/>'s
    /// Frozen branch -- and its ONLY statement, so the question the damage
    /// pipeline asks one phase early and the answer Resolve acts on can never
    /// drift apart. The substitution itself (the PowerCmd.Apply) stays in
    /// Resolve: this decides nothing, it only reports.
    ///
    /// Why the pipeline needs to ask: the sim applies FROZEN_BOSS_VULN from
    /// INSIDE `_react` (reactions.py:147-150) and only then runs
    /// modify_damage_taken, so tier0's triggering hit is itself x1.5. C#
    /// reaches Resolve from AuraPower.AfterDamageReceived, one hook after that
    /// hit's number is final -- exactly the Superconduct / Courtroom Drama
    /// shape, one reaction over. See AuraPower.ModifyDamageMultiplicative.
    ///
    /// UNCONDITIONAL sim-side, unlike Courtroom Drama: there is no
    /// first-reaction gate on the boss branch, so every boss-room Frozen on a
    /// non-minion amplifies its own hit.
    ///
    /// Called from AuraPower.ModifyDamageMultiplicative, which the UI calls
    /// speculatively for damage previews -- so every read is null-tolerant
    /// (no combat, no encounter, no target during preview enumeration all
    /// answer `false`) and nothing here writes.
    /// </summary>
    public static bool FrozenBossVulnWillApply(Creature? target) =>
        target != null
        && target.CombatState?.Encounter?.RoomType == RoomType.Boss
        && !target.Powers.OfType<MinionPower>().Any();

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

            // Courtroom Drama (R85): the FIRST reaction of the turn puts its
            // target on the stand. Counted PER DEALER -- the sim's
            // `reactions_this_turn == 1` in the only configuration it models
            // (solo), and the written co-op contract everywhere else.
            if (dealer != null)
            {
                var already = DealerReactionsThisTurn.TryGetValue(
                    dealer, out var seen) ? seen : 0;
                DealerReactionsThisTurn[dealer] = already + 1;
                if (already == 0)
                {
                    await CurtainCallHooks.NoteFirstReaction(
                        choiceContext, target, dealer, cardSource);
                }
            }
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
            FurinaResources.GainBurst(
                dealer, FurinaResourceConstants.BurstPerReaction);
            // Kokomi takes the same +5. The sim's gate is `if p.burst_max`
            // (reactions.py), i.e. UNIVERSAL for anyone who owns a meter --
            // not a Klee rule that Furina was granted an exception to. She is
            // a catalyst, so every attack she plays applies Hydro and reaction
            // income is a large share of her fill rate; leaving her off this
            // line left the Burst reachable on paper and rare in play.
            KokomiResources.GainBurst(
                dealer, KokomiConstants.BurstPerReaction);

            // Catalytic Converter (R120 rename), right after the flat +5
            // exactly as in the
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
                // Boss rooms consume the aura but receive Vulnerable rather
                // than Frozen. This preserves the intended boss immunity to
                // action control while retaining a useful reaction payoff.
                //
                // NC-7 alpha (Q13 / R117, verbatim "I'd say A"), completing
                // the half Errata Batch 2 stopped: the substitution is
                // per-CREATURE inside the boss room, keyed on the game's
                // MinionPower -- the assembly's only per-creature
                // "secondary enemy" fact (reflection findings in
                // review/parity-sweep/noncard-triage-memo.md, NC-7). A
                // boss-room creature carrying MinionPower gets Frozen;
                // every other creature gets Vulnerable. Kaiser Crab's claws
                // are slotted monsters, NOT minions, so under alpha the
                // second claw takes Vulnerable -- R116's stated consequence,
                // deliberately overridden by [USER]'s alpha selection.
                // The sim's mirror predicate is reactions.py's
                // `boss_room and not enemy.is_minion`.
                //
                // The predicate lives in FrozenBossVulnWillApply so the damage
                // pipeline can ask it one phase earlier (EB-19/M1b) without a
                // second copy to keep in sync. This is still the only site
                // that ACTS on the answer.
                if (FrozenBossVulnWillApply(target))
                {
                    await PowerCmd.Apply<VulnerablePower>(
                        choiceContext, target,
                        ReactionConstants.FrozenBossVuln,
                        applier: dealer, cardSource: cardSource);
                }
                else
                {
                    await PowerCmd.Apply<FrozenPower>(
                        choiceContext, target, 1,
                        applier: dealer, cardSource: cardSource);
                }
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
                            dealer: null, cardSource: null, cardPlay: null);
                    }
                }
                // Survival sprint: the explosion staggers the reacted target.
                // Ordinary Weak composes naturally with Bomb suppression: the
                // Bomb hook detects a real stack and does not multiply 0.75 twice.
                await PowerCmd.Apply<WeakPower>(
                    choiceContext, target, ReactionConstants.OverloadWeak,
                    applier: dealer, cardSource: cardSource);
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
