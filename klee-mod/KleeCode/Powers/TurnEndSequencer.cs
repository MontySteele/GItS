using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// THE END-OF-TURN ORDER, MADE EXPLICIT (EB-19/races-a + EB-19/races-c).
///
/// Four powers used to override <c>BeforeSideTurnEnd</c> independently:
/// MasqueRedDeathPower's Bond-of-Life payment, and the three elemental
/// volleys (SparksNSplashPower = Pyro, OzSummonPower = Electro,
/// KurageSummonPower = Hydro + Block). Same-side co-tenants of one broadcast
/// have NO guaranteed relative order, and these four are not commutative:
///
///   * races-a -- the Bond consumes the first 5 Block of the turn, and the
///     Kurage pulse GRANTS Block. Paying after the pulse eats the mending;
///     paying before it does not. A 5-Block-per-turn swing on any
///     Kokomi+Arlecchino board, decided by listener iteration.
///   * races-c -- the three volleys apply Pyro, Electro and Hydro to enemies
///     that already carry auras, so their order picks WHICH reactions fire;
///     and each one draws its target from the shared
///     <c>Rng.CombatTargets</c> stream, so their order also decides every
///     later roll in the run.
///
/// The two-broadcast staging idiom the co-tenancy ledger prescribes cannot
/// separate four tenants (turn end has only BeforeSideTurnEnd and
/// AfterSideTurnEnd, and AfterSideTurnEnd is already spoken for -- it is where
/// WitchsFlamePower eats what the volleys applied). So the order is imposed
/// directly instead: ONE broadcast tenant that drives the four in the sim's
/// sequence.
///
/// THE SEQUENCE IS tier0 `effects.player_turn_end_triggers`, read top to
/// bottom:
///
///     masque_red_death  (Bond of Life, `p.block -= paid`)
///     sparks_n_splash   (Pyro volley)
///     oz_summon         (Electro volley)
///     kurage_summon     (Hydro pulse + Block)
///
/// ...and as of EB-53/N1 it is written down exactly once, in
/// <see cref="TurnEndAttribution.Order"/>, which this loop walks. The four
/// hand-written statements that used to live here are now that table's
/// <c>Resolve</c> delegates, lifted verbatim. The move is not tidying: the
/// attribution display has to name these four in FIRING order, and a display
/// built from a second hand-written list would be able to disagree with this
/// one. Now it cannot, because there is no second list.
///
/// Per CREATURE, not per step: each player-side creature runs the whole
/// sequence before the next one does. The sim models one seat, so it states
/// nothing about interleaving between two co-op players; grouping by creature
/// keeps each seat's four steps in the pinned order and is the reading that
/// makes a solo table byte-identical to the sim.
///
/// The powers keep their own tick-down (volley first, THEN decrement -- the
/// AuraPower own-decay idiom), so a stack count still means what it meant.
/// </summary>
public sealed class TurnEndSequencer : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static TurnEndSequencer? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<TurnEndSequencer>(
            ModelDb.GetId<TurnEndSequencer>());
        yield return _instance;
    }

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        foreach (var creature in participants.ToList())
        {
            if (creature.Player == null) continue;

            foreach (var source in TurnEndAttribution.Order)
            {
                // The docket slot for this source flashes as it fires, so an
                // off-seat volley resolves on top of the widget that names it
                // (EB-53/N1: "off-seat bursts are invisible inside end-of-turn
                // noise"). Pure draw -- no state, no RNG -- so it takes no
                // position in the race this class exists to settle, and a
                // headless/co-op peer that renders nothing is unaffected.
                Vfx.TurnEndPreviewBridge.NoteFiring(creature, source);
                await source.Resolve(creature, choiceContext);
            }
        }

        // The volleys have spent their turn and ticked down; redraw before the
        // player looks at the board again.
        RefreshAll(participants);
    }

    /// <summary>
    /// Redraw funnels for the attribution docket. All three are PURE redraws
    /// with no stake in any ordering -- they read the same accessors the
    /// resolution reads and write nothing -- so co-tenancy in these broadcasts
    /// (WitchsFlamePower owns AfterSideTurnEnd's real work) is safe by
    /// construction.
    ///
    /// They live on the sequencer rather than in a new hooks model because the
    /// sequencer already owns the end-of-turn concept and is already
    /// registered; a second AbstractModel would be one more subscription to
    /// keep alive for a display.
    ///
    /// AfterCardPlayed is the one that matters: fielding a jellyfish, casting
    /// a Burst and banking Charge all happen inside a play, and none of them
    /// has a funnel this class could otherwise watch.
    /// </summary>
    public override Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        Vfx.TurnEndPreviewBridge.Refresh(cardPlay.Card?.Owner?.Creature);
        return Task.CompletedTask;
    }

    public override Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        Vfx.TurnEndPreviewBridge.Refresh(player.Creature);
        return Task.CompletedTask;
    }

    public override Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side == CombatSide.Player) RefreshAll(participants);
        return Task.CompletedTask;
    }

    private static void RefreshAll(IEnumerable<Creature> participants)
    {
        foreach (var creature in participants.ToList())
        {
            Vfx.TurnEndPreviewBridge.Refresh(creature);
        }
    }
}
