using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;

namespace KleeMod.Powers;

/// <summary>
/// The detonation event bus (csharp-build-spec.md item 2). BombPower.Detonate
/// notifies, once PER BOMB (the sim grants Pounding Surprise's spark inside
/// the per-bomb loop, so a 3-bomb pop is 3 events, not 1).
///
/// Subscribers are discovered by interface test over the applying player's
/// relics and creature powers -- no registration step, so a listener cannot
/// be forgotten at wire-up. Known subscribers: PoundingSurprise (+1 Spark);
/// Blazing Delight's splash joins when its power lands (C3).
/// </summary>
public interface IBombDetonationListener
{
    /// <param name="choiceContext">Live context; effects may deal damage/apply powers.</param>
    /// <param name="applier">The creature whose card placed the bomb (Klee), if still known.</param>
    /// <param name="target">The enemy the bomb detonated on.</param>
    /// <param name="damage">That single bomb's payload.</param>
    Task OnBombDetonated(
        PlayerChoiceContext choiceContext, Creature? applier, Creature target, int damage);
}
