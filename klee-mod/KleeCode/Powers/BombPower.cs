using System.Collections.Generic;
using BaseLib.Abstracts;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
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
/// own value. Amount tracks the COUNT (stack semantics, multiplayer sync);
/// _damages carries the values.
///
/// DISPLAY (worknote ruling 2026-07-20 item 3): the number under the enemy is
/// TOTAL pending detonation damage, not the bomb count. Enemy-side status
/// numbers read as incoming damage (Poison trains this), and a count display
/// makes per-bomb buffs (Chain Fuse, Careful Arrangement) invisible. This is
/// display-layer only -- DisplayAmount is the game's own virtual for exactly
/// this split, and the NPower badge renders DisplayAmount and refreshes on
/// DisplayAmountChanged (verified in the NPower decompile). Detonation still
/// iterates bombs individually; every listener sees per-bomb events.
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
          + "Detonates early if this enemy takes unblocked [gold]Attack[/gold] damage. "
          + "The first attack this enemy makes while Bombed each combat "
          + "deals 25% less damage."),
        // The smart (in-combat, mutable-instance) tooltip carries the count;
        // the badge already shows the total. {Damage} is our DynamicVar,
        // {Amount} is the stack count the game adds to every smart tip.
        ("smartDescription",
            "Detonates at the start of your turn for {Damage} total damage "
          + "({Amount} Bomb{Amount:plural:|s}). "
          + "Detonates early if this enemy takes unblocked [gold]Attack[/gold] damage. "
          + "The first attack this enemy makes while Bombed each combat "
          + "deals 25% less damage."),
    };

    public override PowerType Type => PowerType.Debuff;

    /// <summary>Counter, not Duration: bombs are consumed by detonation, not by time.</summary>
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// One live bomb: its charge and the combat round it was placed in.
    /// The round stamp mirrors tier0's Bomb.turn_placed and exists for
    /// modify_bombs scope 'placed_this_turn' (Chain Fuse). Today every live
    /// bomb was necessarily placed this round -- BeforeSideTurnStart
    /// detonates them all -- but the stamp keeps the semantics exact if a
    /// future mechanic ever places bombs outside the player's own turn.
    /// </summary>
    private readonly record struct BombCharge(int Damage, int RoundPlaced);

    /// <summary>
    /// One entry per live bomb, in placement order.
    ///
    /// MUST be deep-cloned -- see DeepCloneFields. AbstractModel.MutableClone
    /// uses MemberwiseClone, so without that override every bombed enemy would
    /// share ONE list with each other and with the canonical model.
    /// </summary>
    private List<BombCharge> _damages = new();

    // Survival sprint: one armed-Bomb suppression per enemy per combat. The
    // spent latch must outlive this power because early detonation removes the
    // Bomb, and a later Bomb must not incorrectly reset an already-spent proc.
    private static ICombatState? _suppressionCombat;
    private static readonly HashSet<Creature> SuppressionSpent = new();
    private bool _suppressionArmedForAttack;

    private static bool HasSpentSuppression(Creature enemy, ICombatState? combat)
    {
        if (!ReferenceEquals(combat, _suppressionCombat))
        {
            _suppressionCombat = combat;
            SuppressionSpent.Clear();
        }
        return SuppressionSpent.Contains(enemy);
    }

    /// <summary>
    /// AbstractModel.MutableClone is a shallow MemberwiseClone; the base class
    /// exposes this hook precisely so reference-typed fields get their own copy.
    /// Omitting it is a silent cross-enemy corruption bug, not a crash.
    /// </summary>
    protected override void DeepCloneFields()
    {
        base.DeepCloneFields();
        _damages = new List<BombCharge>(_damages);
        _suppressionArmedForAttack = false;
    }

    /// <summary>
    /// Snapshot at the attack-command boundary, not per hit. That keeps every
    /// hit of a multi-hit enemy intent at the Weak rate, then spends the latch
    /// only after the whole action. A real Weak stack shares the same branch
    /// below, so the two reductions never multiply.
    /// </summary>
    public override Task BeforeAttack(AttackCommand attack)
    {
        _suppressionArmedForAttack = attack.Attacker == Owner
            && _damages.Count > 0
            && !HasSpentSuppression(Owner, CombatState);
        return Task.CompletedTask;
    }

    public override decimal ModifyDamageMultiplicative(
        Creature? target, decimal amount, ValueProp props,
        Creature? dealer, CardModel? cardSource)
    {
        if (dealer != Owner || !props.IsPoweredAttack() || _damages.Count == 0)
        {
            return 1m;
        }
        if (HasSpentSuppression(Owner, CombatState)) return 1m;

        var hasRealWeak = Owner.Powers.OfType<WeakPower>()
            .Any(power => power.Amount > 0);
        return hasRealWeak ? 1m : 0.75m;
    }

    public override Task AfterAttack(
        PlayerChoiceContext choiceContext, AttackCommand attack)
    {
        if (_suppressionArmedForAttack && attack.Attacker == Owner)
        {
            HasSpentSuppression(Owner, CombatState); // resets on combat change
            SuppressionSpent.Add(Owner);
        }
        _suppressionArmedForAttack = false;
        return Task.CompletedTask;
    }

    /// <summary>Total damage sitting on this enemy, for intent/tooltip display.</summary>
    public int PendingDamage => _damages.Sum(c => c.Damage);

    /// <summary>The badge under the enemy shows total pending damage; Amount
    /// itself stays the bomb count (see class doc). Ruled 2026-07-20.</summary>
    public override int DisplayAmount => PendingDamage;

    /// <summary>{Damage} in the smart tooltip. Kept in sync by SyncDisplay.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new[] { new DynamicVar("Damage", 0m) };

    /// <summary>
    /// MUST be called after every _damages mutation (there is exactly one
    /// grow site and one clear site today; modify_bombs / move_bombs land
    /// here too when those cards arrive). The badge and the tooltip both
    /// derive from _damages -- the same list detonation consumes -- so the
    /// displayed number can never diverge from what will actually hit.
    /// _damages itself is client-local; the count (Amount) is what the stack
    /// system syncs, which is the pre-existing multiplayer situation for the
    /// per-bomb values and unchanged by this display ruling.
    /// </summary>
    private void SyncDisplay()
    {
        var damage = DynamicVars["Damage"];
        damage.BaseValue = PendingDamage;
        damage.ResetToBase();
        InvokeDisplayAmountChanged();
    }

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
            // Round stamp read off the applied instance (PowerModel exposes
            // CombatState) so no call site has to thread it through.
            bomb._damages.Add(new BombCharge(
                damage, bomb.CombatState?.RoundNumber ?? 0));
            bomb.SyncDisplay();
        }
        else
        {
            Log.Warn($"[{KleeMod.ModId}] BombPower.Place: could not resolve applied power instance; "
                   + "bomb damage not recorded.");
        }
    }

    /// <summary>
    /// Card-triggered detonation of one enemy's bombs (tier0 _op_detonate:
    /// only enemies that HAVE bombs detonate; bonus rides each bomb).
    /// Returns the number of bombs detonated -- Chained Reactions prices its
    /// re-bomb chance per detonation caused by the play (the sim diffs its
    /// detonations counter around the card; here the count is returned
    /// directly).
    /// </summary>
    public static async Task<int> DetonateOn(
        PlayerChoiceContext choiceContext, Creature target, int bonus = 0)
    {
        var bomb = target.Powers.OfType<BombPower>().FirstOrDefault();
        if (bomb == null) return 0;
        return await bomb.Detonate(choiceContext, bonus);
    }

    /// <summary>Detonate across enemies (tier0 detonate target all_enemies);
    /// returns total bombs detonated.</summary>
    public static async Task<int> DetonateAll(
        PlayerChoiceContext choiceContext, IEnumerable<Creature> targets,
        int bonus = 0)
    {
        var total = 0;
        foreach (var target in targets.ToList())
        {
            total += await DetonateOn(choiceContext, target, bonus);
        }
        return total;
    }

    /// <summary>
    /// modify_bombs (Chain Fuse): +bonus to every live bomb, optionally only
    /// those placed this round (tier0 scope 'placed_this_turn' -- runs BEFORE
    /// the card's own place_bomb in effect order, so the new bomb is not
    /// buffed; effect order preserves that here too). Pure mutation, no
    /// commands -- synchronous by design.
    /// </summary>
    public static void ModifyAll(
        IEnumerable<Creature> enemies, int bonus, bool placedThisRoundOnly,
        int currentRound)
    {
        foreach (var enemy in enemies)
        {
            var bomb = enemy.Powers.OfType<BombPower>().FirstOrDefault();
            if (bomb == null) continue;
            for (var i = 0; i < bomb._damages.Count; i++)
            {
                var charge = bomb._damages[i];
                if (placedThisRoundOnly && charge.RoundPlaced != currentRound)
                {
                    continue;
                }
                bomb._damages[i] = charge with { Damage = charge.Damage + bonus };
            }
            bomb.SyncDisplay();
        }
    }

    /// <summary>
    /// move_bombs (Careful Arrangement): gather every bomb from OTHER enemies
    /// onto <paramref name="dest"/>, +bonus each; round stamps travel with
    /// the charges (tier0 keeps turn_placed on moved bombs). Source powers
    /// are removed once emptied.
    /// </summary>
    public static async Task MoveAllTo(
        PlayerChoiceContext choiceContext, Creature dest,
        IEnumerable<Creature> enemies, int bonus,
        Creature? applier, CardModel? cardSource)
    {
        var moved = new List<BombCharge>();
        foreach (var enemy in enemies.ToList())
        {
            if (enemy == dest) continue;
            var source = enemy.Powers.OfType<BombPower>().FirstOrDefault();
            if (source == null || source._damages.Count == 0) continue;
            moved.AddRange(source._damages);
            source._damages.Clear();
            source.SyncDisplay();
            await PowerCmd.Remove(source);
        }
        if (moved.Count == 0) return;

        var power = await PowerCmd.Apply<BombPower>(
            choiceContext, dest, moved.Count, applier: applier,
            cardSource: cardSource);
        if (power is BombPower bomb)
        {
            foreach (var charge in moved)
            {
                bomb._damages.Add(charge with { Damage = charge.Damage + bonus });
            }
            bomb.SyncDisplay();
        }
        else
        {
            Log.Warn($"[{KleeMod.ModId}] BombPower.MoveAllTo: could not resolve "
                   + "applied power instance; moved bombs lost their charges.");
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
    /// Detonates every bomb on this enemy; returns how many detonated.
    /// <paramref name="bonus"/> is the card-carried detonation bonus (tier0
    /// detonate_bombs: `dmg = bomb.damage + bonus + bomb_damage_up` -- Remote
    /// Detonator's +2 rides here, before amplification, exactly like the
    /// Explosives Workshop bonus).
    ///
    /// Clears the list BEFORE dealing any damage. Tier 0 does the same
    /// (`bombs, enemy.bombs = enemy.bombs, []`) and it is the recursion guard:
    /// detonation damage can kill, trigger hooks, and re-enter combat logic, so
    /// the charges must already be spent by then.
    /// </summary>
    /// <summary>
    /// Per-combat detonation total (sim: state.detonations_total), read by
    /// The Big One's (grand_finale) bonus_formula. Keyed to the combat-state instance so a
    /// new combat starts at zero without a reset hook; every detonation path
    /// funnels through Detonate, so the count cannot miss one. A mid-combat
    /// reload restarts the combat (and this count with it).
    /// </summary>
    private static ICombatState? _countCombat;
    private static int _detonationsThisCombat;

    public static int DetonationsThisCombat(ICombatState combatState)
        => ReferenceEquals(combatState, _countCombat) ? _detonationsThisCombat : 0;

    private static void RecordDetonation(ICombatState? combatState)
    {
        if (combatState == null) return;
        if (!ReferenceEquals(combatState, _countCombat))
        {
            _countCombat = combatState;
            _detonationsThisCombat = 0;
        }
        _detonationsThisCombat++;
    }

    private async Task<int> Detonate(PlayerChoiceContext choiceContext, int bonus = 0)
    {
        if (_damages.Count == 0) return 0;

        var payloads = _damages.Select(c => c.Damage).ToList();
        _damages.Clear();
        SyncDisplay();

        var target = Owner;
        var applier = Applier;
        // Snapshot before Remove: the power's state references may not
        // survive removal, and RecordDetonation below needs the combat.
        var combatState = CombatState;
        await PowerCmd.Remove(this);

        // Explosives Workshop: flat bonus per detonation, added BEFORE
        // amplification -- the sim totals `bomb.damage + bonus + bomb_damage_up`
        // and only then enters the elemental pipeline (effects.py detonate_bombs).
        var damageUp =
            applier?.Powers.OfType<BombDamageUpPower>().FirstOrDefault()?.Amount ?? 0;

        foreach (var damage in payloads)
        {
            // Sim order: detonations_total increments before the damage
            // lands (effects.py detonate_bombs).
            RecordDetonation(combatState);

            // R23: each detonation is a Pyro-tagged hit (tier0 detonate_bombs
            // -> deal_damage_to_enemy(element=bomb.element), default pyro).
            // ElementalHit.Deal owns the whole pipeline -- Strength/Weak
            // pre-amp, element resolve (amplifiers scale THIS detonation),
            // Vulnerable post-amp, one truncation, Unpowered damage (which
            // is what keeps bombs from chain-detonating each other).
            await ElementalHit.Deal(
                choiceContext, target, Element.Pyro,
                damage + bonus + damageUp, applier);

            await NotifyDetonationListeners(choiceContext, applier, target, damage);
        }

        return payloads.Count;
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
