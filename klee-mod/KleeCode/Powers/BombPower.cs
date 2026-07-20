using System.Collections.Generic;
using BaseLib.Abstracts;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// Klee's signature Bomb: a delayed charge on an enemy.
///
/// Canonical rules (klee-character-design.md line 22, tier0-simulator-spec.md
/// line 115, reference implementation tier0/engine/effects.py):
///   - Detonates at the start of Klee's next turn for its damage, applying Pyro.
///   - Detonates EARLY if that enemy is hit by an Attack card.
///   - Multiple bombs STACK INDEPENDENTLY, each carrying its own damage.
///   - Detonations fire relic/power hooks (Pounding Surprise, Blazing Delight).
///
/// The independent-stacking rule is why this is not a plain counter power: Pop
/// places a 5, Jumpy Dumpty a 6, Trip Wire a 7, and each must detonate for its
/// own value. Amount tracks the COUNT (that is what the UI shows); _damages
/// carries the values.
/// </summary>
public sealed class BombPower : PowerModel, ILocalizationProvider
{
    /// <summary>
    /// BaseLib's AddModelLoc keys off Id.Entry for ANY model implementing this
    /// interface -- it is not restricted to Custom*Model subclasses. Declaring
    /// loc here rather than in a hand-written table is what stops the key from
    /// drifting out of sync with the id (see Kaboom.Localization).
    /// </summary>
    public List<(string, string)>? Localization => new()
    {
        ("title", "Bomb"),
        ("description",
            "Detonates at the start of your turn for its damage. "
          + "Detonates early if this enemy is hit by an [gold]Attack[/gold]."),
    };

    public override PowerType Type => PowerType.Debuff;

    /// <summary>Counter, not Duration: bombs are consumed by detonation, not by time.</summary>
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// One entry per live bomb, in placement order.
    ///
    /// MUST be deep-cloned -- see DeepCloneFields. AbstractModel.MutableClone
    /// uses MemberwiseClone, so without that override every bombed enemy would
    /// share ONE list with each other and with the canonical model.
    /// </summary>
    private List<int> _damages = new();

    /// <summary>
    /// AbstractModel.MutableClone is a shallow MemberwiseClone; the base class
    /// exposes this hook precisely so reference-typed fields get their own copy.
    /// Omitting it is a silent cross-enemy corruption bug, not a crash.
    /// </summary>
    protected override void DeepCloneFields()
    {
        base.DeepCloneFields();
        _damages = new List<int>(_damages);
    }

    /// <summary>Total damage sitting on this enemy, for intent/tooltip display.</summary>
    public int PendingDamage => _damages.Sum();

    /// <summary>
    /// Places a bomb on <paramref name="target"/>, stacking with any already there.
    /// </summary>
    public static async Task Place(
        PlayerChoiceContext choiceContext, Creature target, int damage,
        Creature applier, CardModel? cardSource)
    {
        var power = await PowerCmd.Apply<BombPower>(
            choiceContext, target, 1, applier: applier, cardSource: cardSource);

        if (power is BombPower bomb)
        {
            bomb._damages.Add(damage);
        }
        else
        {
            Log.Warn($"[{KleeMod.ModId}] BombPower.Place: could not resolve applied power instance; "
                   + "bomb damage not recorded.");
        }
    }

    /// <summary>
    /// Start-of-turn detonation. Tier 0 orders the player turn as
    /// "bombs detonate -> auras tick -> power hooks -> draw + energy", so this
    /// uses BeforeSideTurnStart -- which is also the only turn-start hook that
    /// carries a PlayerChoiceContext, and dealing damage requires one.
    /// </summary>
    public override async Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side != CombatSide.Player) return;
        await Detonate(choiceContext);
    }

    /// <summary>
    /// Early detonation: being hit by an Attack card pops every bomb on this
    /// enemy immediately.
    ///
    /// The source guard is load-bearing. Bomb damage is dealt below with
    /// ValueProp.Unpowered and no card source, so it is not a "powered attack"
    /// and cannot re-enter here -- which, combined with clearing the list
    /// before dealing damage, is what stops a bomb from detonating itself.
    /// </summary>
    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, DamageResult result,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (target != Owner) return;
        if (!props.IsPoweredAttack()) return;
        if (cardSource is not { Type: CardType.Attack }) return;

        // Tier 0 only pops on damage that actually landed on HP, so an attack
        // fully absorbed by Block does not trigger an early detonation.
        if (result.UnblockedDamage <= 0) return;

        await Detonate(choiceContext);
    }

    /// <summary>
    /// Detonates every bomb on this enemy.
    ///
    /// Clears the list BEFORE dealing any damage. Tier 0 does the same
    /// (`bombs, enemy.bombs = enemy.bombs, []`) and it is the recursion guard:
    /// detonation damage can kill, trigger hooks, and re-enter combat logic, so
    /// the charges must already be spent by then.
    /// </summary>
    private async Task Detonate(PlayerChoiceContext choiceContext)
    {
        if (_damages.Count == 0) return;

        var payloads = _damages.ToList();
        _damages.Clear();

        var target = Owner;
        var applier = Applier;
        await PowerCmd.Remove(this);

        foreach (var damage in payloads)
        {
            // Unpowered so bomb damage is not scaled by Strength and does not
            // read as an attack; bombs are a fixed charge, and this is also
            // what keeps them from chain-detonating each other.
            await CreatureCmd.Damage(
                choiceContext, target, damage,
                ValueProp.Unpowered, dealer: null, cardSource: null);

            // TODO(C2): bombs apply Pyro on detonation, which is what makes the
            // demolition deck feed the reaction system. Deliberately not wired
            // yet -- nothing applies auras at all, so doing it here alone would
            // be untestable. Lands with the aura-application pass.

            await NotifyDetonationListeners(choiceContext, applier, target, damage);
        }
    }

    /// <summary>
    /// The detonation event bus. Once per bomb (sim parity: the spark grant
    /// sits inside the per-bomb loop in tier0/engine/effects.py). Listeners
    /// are the applying player's relics and creature powers implementing
    /// <see cref="IBombDetonationListener"/> -- snapshot with ToList() because
    /// a listener may add or remove powers while handling the event.
    /// </summary>
    private static async Task NotifyDetonationListeners(
        PlayerChoiceContext choiceContext, Creature? applier, Creature target, int damage)
    {
        var player = applier?.Player;
        if (player == null) return;

        foreach (var relic in player.Relics.ToList())
        {
            if (relic is IBombDetonationListener listener)
            {
                await listener.OnBombDetonated(choiceContext, applier, target, damage);
            }
        }

        foreach (var power in applier!.Powers.ToList())
        {
            if (power is IBombDetonationListener listener)
            {
                await listener.OnBombDetonated(choiceContext, applier, target, damage);
            }
        }
    }
}
