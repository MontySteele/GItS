using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Creatures;
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

            // 1. Bond of Life, before anything can grant Block.
            foreach (var masque in creature.Powers
                         .OfType<MasqueRedDeathPower>().ToList())
            {
                await masque.PayBondOfLife();
            }

            // 2-4. Pyro -> Electro -> Hydro. ToList() each time: a volley can
            // kill, and a power can remove itself on the tick-down, so the
            // collection is re-read rather than held across an await.
            foreach (var pyro in creature.Powers
                         .OfType<SparksNSplashPower>().ToList())
            {
                await pyro.FireVolley(choiceContext);
            }

            foreach (var electro in creature.Powers
                         .OfType<OzSummonPower>().ToList())
            {
                await electro.FireVolley(choiceContext);
            }

            foreach (var hydro in creature.Powers
                         .OfType<KurageSummonPower>().ToList())
            {
                await hydro.FirePulse(choiceContext);
            }
        }
    }
}
