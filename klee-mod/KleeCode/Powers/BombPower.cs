using System.Collections.Generic;
using BaseLib.Abstracts;
using BaseLib.Utils;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
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
///
/// ONE PILE PER PLACER (R205): see <see cref="InstanceType"/>. A bombed enemy
/// carries one BombPower INSTANCE per placing creature, so in co-op the badge
/// count is the pile count and each pile detonates under its own name. Every
/// "all the bombs on this enemy" verb below therefore iterates instances --
/// <see cref="DetonateOn"/>, <see cref="ModifyAll"/>, <see cref="MoveAllTo"/>
/// -- and never takes the first one it finds.
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

    // ARTIFACT COEXISTENCE ([USER] ruling 2026-08-23; LAW "Combat --
    // elements & reactions"): elemental application coexists with Artifact
    // rather than consuming it. ArtifactPower negates on
    // GetTypeForAmount(amount) == PowerType.Debuff (decompile-verified,
    // sts2.dll v0.107.1); Buff takes Bomb out of that gate. Rider included:
    // Bomb's "first attack -25%" now lands through Artifact too -- ruled
    // acceptable under "Auras and Bombs" coexist. Frozen and
    // reaction-applied Vulnerable/Weak/Poison stay real debuffs.
    public override PowerType Type => PowerType.Buff;

    /// <summary>Counter, not Duration: bombs are consumed by detonation, not by time.</summary>
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// ONE BOMB BADGE PER PLACER -- [USER] ruling R205, shape (a).
    ///
    /// Without this the power is PowerInstanceType.None, and the base game's
    /// stacking search (PowerCmd.FindExistingInstanceForStacking, sts2.dll
    /// v0.107.1) resolves that case to `target.GetPower(id)`: ONE instance per
    /// enemy no matter who placed. Both Klees' bombs merged into it, and a
    /// power carries ONE Applier -- so the second Klee's bombs detonated under
    /// the first Klee's name, feeding her Big One counter, her Pounding
    /// Surprise sparks, her Blazing Delight, her Explosive Frags.
    ///
    /// InstancedPerApplier resolves the same search to
    /// `GetPowerInstances(id).FirstOrDefault(p => p.Applier == applier)`, so
    /// each placer stacks into their OWN pile and gets their own badge, their
    /// own detonation credit and their own listeners. The reading is
    /// mechanically honest -- two Klees really have placed two separate piles
    /// -- and the clutter it costs is confined to the two-Klee case, which is
    /// the only case that can produce it. Shape (b), a placer field threaded
    /// through BombCharge, was REJECTED at the same ruling: more code, no
    /// visible change, and the display keeps lying about how many piles exist.
    ///
    /// SOLO IS BIT-IDENTICAL BY CONSTRUCTION. One player is one applier is one
    /// instance, and the per-applier search then finds exactly what the
    /// unscoped search found. Every consequence below is a co-op consequence.
    ///
    /// Base-game precedent: OblivionPower and StranglePower are the two
    /// shipped InstancedPerApplier powers.
    /// </summary>
    public override PowerInstanceType InstanceType =>
        PowerInstanceType.InstancedPerApplier;

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
    // It lives ON the enemy (sim: state.py Enemy.bomb_suppression_spent) via
    // BaseLib's SpireField, the same attached-per-instance idiom the resource
    // layer uses: creatures are per-combat objects, so a second live combat
    // can never read this one's latch, and the weak keying frees each entry
    // with its creature -- no reset hook, no reference-equality combat check.
    private static readonly SpireField<Creature, bool> SuppressionSpent =
        new(() => false);

    /// <summary>
    /// THE SUPPRESSION ARBITER. A forced consequence of R205, not a new rule.
    ///
    /// ModifyDamageMultiplicative is a PER-INSTANCE override and the engine
    /// FOLDS it: Hook.ModifyDamageInternal walks every hook listener doing
    /// `num *= num3`, and every power instance on the creature is a listener.
    /// So the moment bombs instance per placer, two piles would each return
    /// 0.75m and the enemy's first attack would land at 0.5625. Nobody chose
    /// that. The printed rule is one enemy, one combat, one 25%.
    ///
    /// The per-Creature SuppressionSpent latch cannot arbitrate on its own,
    /// because it is only WRITTEN in AfterAttack -- by then all N instances
    /// have already armed and already multiplied. So exactly one instance is
    /// ELECTED, and the election is a pure function of the enemy's own power
    /// list: the FIRST BombPower on the owner that still has live charges.
    /// Creature.Powers is the creature's _powers list in application order, so
    /// this is deterministic, needs no extra state to keep in sync, and cannot
    /// drift from what the badges show.
    ///
    /// BOTH READERS RUN IT, which is what makes the preview and the hit agree:
    /// BeforeAttack latches it into _suppressionArmedForAttack for the whole
    /// action, and the intent-preview branch evaluates it live.
    ///
    /// Solo: one instance, trivially the first with charges, so this predicate
    /// is a no-op and the reduction is the same single 0.75 it always was.
    /// </summary>
    private bool IsSuppressionArbiter =>
        ReferenceEquals(
            this,
            Owner.Powers.OfType<BombPower>()
                 .FirstOrDefault(bomb => bomb._damages.Count > 0));

    // The enemy action in flight, latched at the attack-command boundary.
    // Compared by reference so a nested AttackCommand fired by a hook
    // mid-action (a retaliation, a detonation) can neither re-arm nor clear
    // the snapshot before AfterAttack sees the original command.
    private AttackCommand? _suppressionAttack;
    private bool _suppressionArmedForAttack;

    /// <summary>
    /// AbstractModel.MutableClone is a shallow MemberwiseClone; the base class
    /// exposes this hook precisely so reference-typed fields get their own copy.
    /// Omitting it is a silent cross-enemy corruption bug, not a crash.
    /// </summary>
    protected override void DeepCloneFields()
    {
        base.DeepCloneFields();
        _damages = new List<BombCharge>(_damages);
        _suppressionAttack = null;
        _suppressionArmedForAttack = false;
    }

    /// <summary>
    /// Snapshot at the attack-command boundary, not per hit. That keeps every
    /// hit of a multi-hit enemy intent at the Weak rate, then spends the latch
    /// only after the whole action -- sim law (combat.py _enemy_turn):
    /// eligibility is read BEFORE the action resolves, so bombs detonating
    /// mid-action never strip later hits. A real Weak stack shares the same
    /// branch below, so the two reductions never multiply.
    ///
    /// EVERY instance latches the command, but only the elected arbiter arms.
    /// The latch on the non-arbiters is load-bearing, not bookkeeping: it is
    /// what keeps them in the snapshot branch below for the whole action, so a
    /// retaliation that pops the arbiter's pile mid-action cannot promote a
    /// second instance into the arbiter role and land a second 0.75 on a later
    /// hit. That is the same invariant this hook already existed to hold.
    /// </summary>
    public override Task BeforeAttack(AttackCommand attack)
    {
        if (attack.Attacker != Owner || _suppressionAttack != null)
        {
            return Task.CompletedTask;
        }
        _suppressionAttack = attack;
        _suppressionArmedForAttack =
            _damages.Count > 0 && !SuppressionSpent[Owner] && IsSuppressionArbiter;
        return Task.CompletedTask;
    }

    public override decimal ModifyDamageMultiplicative(
        Creature? target, decimal amount, ValueProp props,
        Creature? dealer, CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || !props.IsPoweredAttack())
        {
            return 1m;
        }
        // Inside an action the BeforeAttack snapshot rules every hit. Outside
        // one (intent preview -- same idiom as GigantificationPower's null
        // branch) the live state IS the snapshot the next action will take.
        //
        // IsSuppressionArbiter appears in BOTH branches on purpose: the
        // preview must show the same one-pile-only 0.75 the hit will apply, or
        // a two-Klee enemy's intent number would disagree with the damage.
        var suppressed = _suppressionAttack != null
            ? _suppressionArmedForAttack
            : _damages.Count > 0 && !SuppressionSpent[Owner] && IsSuppressionArbiter;
        if (!suppressed) return 1m;

        var hasRealWeak = Owner.Powers.OfType<WeakPower>()
            .Any(power => power.Amount > 0);
        return hasRealWeak ? 1m : 0.75m;
    }

    public override Task AfterAttack(
        PlayerChoiceContext choiceContext, AttackCommand attack)
    {
        if (attack != _suppressionAttack) return Task.CompletedTask;
        // Only the elected arbiter ever armed, so only the arbiter spends the
        // creature-keyed latch -- N instances still spend it exactly once.
        if (_suppressionArmedForAttack)
        {
            SuppressionSpent[Owner] = true;
        }
        _suppressionAttack = null;
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
    ///
    /// EVERY PILE, not the first one found. "Detonate this enemy's bombs"
    /// means all of them, and under InstancedPerApplier a co-op enemy carries
    /// one pile per placer -- so Quick Fuse, Chained Reactions, Remote
    /// Detonator and Sparkly Explosion move exactly the totals they moved when
    /// the two placers shared one merged pile. Each pile detonates under its
    /// OWN Applier, which is the point of the ruling.
    ///
    /// Snapshot before iterating: Detonate calls PowerCmd.Remove(this), so the
    /// live power list mutates under the loop.
    /// </summary>
    public static async Task<int> DetonateOn(
        PlayerChoiceContext choiceContext, Creature target, int bonus = 0)
    {
        var total = 0;
        foreach (var bomb in target.Powers.OfType<BombPower>().ToList())
        {
            total += await bomb.Detonate(choiceContext, bonus);
        }
        return total;
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
    ///
    /// EVERY PILE on every enemy: Chain Fuse buffs "every live bomb", and
    /// under InstancedPerApplier the second placer's bombs are live bombs on
    /// the same enemy. Taking the first instance would silently halve the card
    /// on a co-op board.
    /// </summary>
    public static void ModifyAll(
        IEnumerable<Creature> enemies, int bonus, bool placedThisRoundOnly,
        int currentRound)
    {
        foreach (var enemy in enemies)
        {
            foreach (var bomb in enemy.Powers.OfType<BombPower>().ToList())
            {
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
    }

    /// <summary>
    /// move_bombs (Careful Arrangement): gather every bomb from OTHER enemies
    /// onto <paramref name="dest"/>, +bonus each; round stamps travel with
    /// the charges (tier0 keeps turn_placed on moved bombs). Source powers
    /// are removed once emptied.
    ///
    /// EVERY PILE on every source enemy, for the same reason as ModifyAll:
    /// "gather every bomb" means every bomb, whoever placed it.
    ///
    /// GATHER TRANSFERS OWNERSHIP TO THE GATHERER. The re-apply below passes
    /// the MOVER as applier, so under InstancedPerApplier the gathered charges
    /// land in the mover's own pile on dest -- creating it if the mover had no
    /// bombs there yet. That is the ruled default and it falls straight out of
    /// the existing call; picking up someone else's bombs makes them yours.
    ///
    /// A PRE-EXISTING OTHER-PLAYER PILE ON DEST SURVIVES INTACT, badge and
    /// all, because dest is skipped as a source. That is not an oversight
    /// carried forward -- it is shape (a) working as ruled: the other Klee's
    /// bombs on the destination were never gathered, so they are still hers.
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
            // Snapshot: PowerCmd.Remove takes the source out of this list.
            foreach (var source in enemy.Powers.OfType<BombPower>().ToList())
            {
                if (source._damages.Count == 0) continue;
                moved.AddRange(source._damages);
                source._damages.Clear();
                source.SyncDisplay();
                await PowerCmd.Remove(source);
            }
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
    /// One Bomb pile as it stood BEFORE any of the turn's detonation damage:
    /// what it will deal, who placed it, and the combat it belongs to.
    ///
    /// EB-138. The whole point of taking this is that it OUTLIVES the power.
    /// Once a pile is claimed, nothing the resolution does -- a kill, a
    /// teardown, a hook that strips powers off a corpse -- can take the pile's
    /// credit or its listeners away, because none of that is still stored on
    /// the power.
    /// </summary>
    public readonly record struct TurnStartPile(
        BombPower Power, IReadOnlyList<int> Payload, Creature? Applier,
        ICombatState? Combat);

    /// <summary>
    /// Take THIS pile's charges: empty the list, refresh the badge, and hand
    /// back what it was carrying (null if it was already empty).
    ///
    /// PURE -- no commands, nothing that can kill -- which is what lets the
    /// take run across EVERY pile before the first hit lands. It is also the
    /// recursion guard the single-pile path has always had: detonation damage
    /// can kill, fire hooks and re-enter combat logic, so the charges must
    /// already be spent by then. Tier 0 does the same
    /// (`bombs, enemy.bombs = enemy.bombs, []`).
    ///
    /// Applier and CombatState are read HERE rather than at resolution: the
    /// power is about to be detached and its state references may not survive
    /// removal.
    /// </summary>
    private TurnStartPile? Take()
    {
        if (_damages.Count == 0) return null;

        var taken = new TurnStartPile(
            this, _damages.Select(charge => charge.Damage).ToList(),
            Applier, CombatState);
        _damages.Clear();
        SyncDisplay();
        return taken;
    }

    /// <summary>
    /// EB-138 -- THE COMPENSATION, and it is one step: TAKE every pile on this
    /// enemy BEFORE any damage begins.
    ///
    /// `EB-130` made a bombed enemy carry one pile per placing creature, and
    /// that took something away that the old merged payload had. The base
    /// game's own machinery is what takes it (decompile-established, sts2.dll
    /// v0.107.1, and forced -- not a choice made here):
    ///
    ///   Hook.BeforeSideTurnStart walks a listener list snapshotted when the
    ///   broadcast opened, but re-tests CombatState.Contains(model) before
    ///   yielding each one, and for a power that test is
    ///   `Owner.CombatState != null`. A killing blow runs INLINE inside the
    ///   damage command (CreatureCmd.Damage ends `await Kill(killedCreatures)`),
    ///   and CreatureCmd.KillWithoutCheckingWinCondition detaches the corpse
    ///   (`combatState.RemoveCreature`, unattach: true) and then strips its
    ///   powers. So if the first pile reached killed the enemy, every later
    ///   placer's instance was torn down before its slot arrived and never
    ///   detonated -- losing that placer's detonation-listener grants (Pounding
    ///   Surprise, Blazing Delight, Explosive Frags, Touch of Orobas) and their
    ///   Big One credit.
    ///
    /// IN THE OLD MERGED-PAYLOAD WORLD THOSE BOMBS WERE CONSUMED, CREDITED AND
    /// FED TO LISTENERS after a kill, because they were trailing entries in one
    /// list that had already been spent. Instancing is what took that away, so
    /// this is a co-op REGRESSION and not a new rule, and the repair restores
    /// the old parity rather than inventing one (R211, [USER] 2026-08-25).
    ///
    /// HOW: take first, resolve second. Every pile is emptied while the enemy
    /// is still alive, and resolution then runs off the returned SNAPSHOT
    /// under each pile's ORIGINAL owner. A kill mid-resolution therefore
    /// fizzles the later piles' DAMAGE against the corpse -- which is what
    /// tier0 does too, where the clamp makes a hit on a dead enemy count for
    /// nothing (`effects.detonate_bombs`) -- while their bombs are still
    /// consumed, still credit their own placer's counters, and still fire
    /// their own placer's listeners.
    ///
    /// IDEMPOTENT BY CONSTRUCTION, which is what lets any instance be the one
    /// that runs it: the first instance reached takes ALL the piles, so every
    /// later instance finds nothing to take and no-ops. A teardown that
    /// removes those later instances can no longer remove anything still owed
    /// -- there is nothing left ON them to remove.
    ///
    /// Solo is unchanged by construction: one player is one applier is one
    /// pile, so take-then-resolve is the single-pile order it always was.
    /// </summary>
    public static IReadOnlyList<TurnStartPile> TakeTurnStartPiles(Creature enemy)
    {
        var taken = new List<TurnStartPile>();
        // Snapshot the instance list too, so the loop reads one fixed set of
        // piles in the enemy's own application order -- which is what makes
        // the resolution below deterministic.
        foreach (var pile in enemy.Powers.OfType<BombPower>().ToList())
        {
            if (pile.Take() is { } charge)
            {
                taken.Add(charge);
            }
        }
        return taken;
    }

    /// <summary>Take every pile (above), then detach the emptied powers. The
    /// two halves are separate because only the FIRST is allowed to matter: by
    /// the time anything that can run a command happens, every pile's payload
    /// is already off the power and in the returned list.</summary>
    public static async Task<IReadOnlyList<TurnStartPile>> ClaimTurnStartPiles(
        Creature enemy)
    {
        var claimed = TakeTurnStartPiles(enemy);
        foreach (var pile in claimed)
        {
            await PowerCmd.Remove(pile.Power);
        }
        return claimed;
    }

    /// <summary>Claim every pile on this enemy, then resolve each one under its
    /// own placer. Returns how many bombs detonated. See
    /// <see cref="ClaimTurnStartPiles"/> for why the two halves are separate.
    /// </summary>
    public static async Task<int> ResolveTurnStartPiles(
        PlayerChoiceContext choiceContext, Creature enemy)
    {
        var total = 0;
        foreach (var pile in await ClaimTurnStartPiles(enemy))
        {
            total += await ResolvePayload(choiceContext, enemy, pile, bonus: 0);
        }
        return total;
    }

    /// <summary>
    /// Start-of-turn detonation. Tier 0 orders the player turn as
    /// "bombs detonate -> auras tick -> power hooks -> draw + energy", so this
    /// uses BeforeSideTurnStart -- which is also the only turn-start hook that
    /// carries a PlayerChoiceContext, and dealing damage requires one.
    ///
    /// THE HOOK IS STILL PER INSTANCE -- that is the game's broadcast, not ours
    /// -- but what it does is not per instance any more: whichever pile's slot
    /// arrives FIRST resolves the whole enemy (EB-138). The card-driven verbs
    /// were never affected: DetonateOn snapshots the instances first and
    /// iterates the snapshot, so Quick Fuse and friends already reached every
    /// pile.
    /// </summary>
    public override async Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side != CombatSide.Player) return;
        await ResolveTurnStartPiles(choiceContext, Owner);
    }

    /// <summary>
    /// Early detonation: being hit by an Attack card pops every bomb on this
    /// enemy immediately.
    ///
    /// The source guard is load-bearing. Bomb damage is dealt below with
    /// ValueProp.Unpowered and no card source, so it is not a "powered attack"
    /// and cannot re-enter here -- which, combined with clearing the list
    /// before dealing damage, is what stops a bomb from detonating itself.
    ///
    /// DEATH TEARDOWN DOES NOT REACH THIS HOOK. The base game does not
    /// broadcast AfterDamageReceived at all for a blow that killed
    /// (CreatureCmd.Damage: `if (!WasTargetKilled || !originalTarget.IsDead)`),
    /// so no pile sees it on a killing hit -- first or second, before this
    /// change or after it. Instancing changes nothing here.
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
    /// Per-combat, PER-PLAYER detonation total (sim: state.detonations_total),
    /// read by The Big One's (grand_finale) bonus_formula. Keyed to the
    /// combat-state instance so a new combat starts at zero without a reset
    /// hook; every detonation path funnels through Detonate, so the count
    /// cannot miss one. A mid-combat reload restarts the combat (and this
    /// count with it).
    ///
    /// EPOCH 2 / D2 (audit sec.5, tracked since 2026-07-25 as "NEEDS FIX --
    /// blocked"). This was ONE team-wide integer. In co-op that meant a second
    /// player's detonations inflated your Big One: two Klees each throwing five
    /// bombs both read ten, and the card's damage roughly doubled for free.
    /// D2 scoped the TRACKER: the dictionary is keyed per player, using the
    /// ownership idiom ExplosiveFrags.OnBombDetonated states two files over
    /// ("own bombs only: in co-op another player's detonations are theirs").
    ///
    /// THAT WAS HALF THE DEFECT, AND UNTIL R205 THIS COMMENT READ AS THOUGH IT
    /// WERE ALL OF IT. The key is the applier's Player -- but while BombPower
    /// merged both placers into one instance there was only ever ONE Applier
    /// to key on, so the second Klee's bombs still counted toward the first
    /// Klee's Big One through a dictionary that looked correctly scoped and
    /// was. InstanceType above closes the other half: one instance per placer
    /// is one Applier per pile, so this key finally separates what it names.
    ///
    /// The sim still cannot see any of it -- tier 0.5 models one seat -- and
    /// KleeTests (EB-105) reaches per-seat ownership but not a live
    /// CombatState, so the two-seat DETONATION itself stays play-derived.
    ///
    /// Solo behaviour is unchanged by construction: with one player the
    /// per-player count and the team-wide count are the same number.
    ///
    /// Not a leak. The dictionary is cleared whenever the combat instance
    /// changes, so it holds at most the current combat's players -- unlike
    /// SpotlightSystem.PendingDraws, which retains dead run graphs on abnormal
    /// exits (audit sec.5, still open).
    /// </summary>
    private static ICombatState? _countCombat;
    private static readonly Dictionary<Player, int> _detonationsByPlayer = new();

    /// <summary>
    /// EB-18 — CORPSE DETONATIONS, the same count keyed the same way.
    ///
    /// A corpse detonation is a detonation that resolved on a target that was
    /// ALREADY DEAD when the charge went off. The test is read PER BOMB and
    /// BEFORE that bomb's damage lands (see <see cref="Detonate"/>), which
    /// fixes the semantics: within one payload, the bomb that lands the kill
    /// detonated on a LIVE enemy and is NOT counted; every bomb behind it in
    /// the same payload detonated on a corpse and IS counted. A single-bomb
    /// killing blow therefore records zero. Probe (e) (R118 / Q11) had to
    /// script a fixed two-arm run to ask this once; the counter answers the
    /// payload-trailing case on every fight anybody plays, for the price of
    /// one bool.
    ///
    /// REPORTS, NEVER GRADES, and touches nothing. It is read only by
    /// `PlayTelemetry` — no card, relic or formula reads it, and in particular
    /// The Big One's bonus still reads
    /// <see cref="DetonationsThisCombat"/>, which counts corpse detonations
    /// among its total exactly as it did before this counter existed.
    ///
    /// R205 MOVES THE BOUNDARY THIS COUNTER IS DRAWN AROUND, in co-op only.
    /// "The payload" used to be every bomb on the enemy in one merged list;
    /// it is now one placer's pile. So the trailing-corpse split is taken
    /// GROUPED BY PLACER rather than in one interleaved run, and the placer
    /// whose pile lands the kill is the only one who can record a live-target
    /// detonation for that enemy. Solo the two readings are the same list.
    /// </summary>
    private static readonly Dictionary<Player, int> _corpseDetonationsByPlayer = new();

    public static int DetonationsThisCombat(ICombatState combatState, Player? player)
    {
        if (!ReferenceEquals(combatState, _countCombat) || player == null)
        {
            return 0;
        }
        return _detonationsByPlayer.TryGetValue(player, out var count) ? count : 0;
    }

    public static int CorpseDetonationsThisCombat(ICombatState combatState, Player? player)
    {
        if (!ReferenceEquals(combatState, _countCombat) || player == null)
        {
            return 0;
        }
        return _corpseDetonationsByPlayer.TryGetValue(player, out var count) ? count : 0;
    }

    private static void RecordDetonation(ICombatState? combatState, Creature? applier,
                                         bool onCorpse)
    {
        if (combatState == null) return;
        if (!ReferenceEquals(combatState, _countCombat))
        {
            _countCombat = combatState;
            _detonationsByPlayer.Clear();
            _corpseDetonationsByPlayer.Clear();
        }
        // An applier with no Player is an enemy-sourced or orphaned detonation.
        // It still happened, but it is nobody's Big One bonus.
        var player = applier?.Player;
        if (player == null) return;
        _detonationsByPlayer[player] =
            (_detonationsByPlayer.TryGetValue(player, out var n) ? n : 0) + 1;
        if (!onCorpse) return;
        _corpseDetonationsByPlayer[player] =
            (_corpseDetonationsByPlayer.TryGetValue(player, out var c) ? c : 0) + 1;
    }

    /// <summary>
    /// Detonates every bomb in THIS pile; returns how many detonated.
    /// <paramref name="bonus"/> is the card-carried detonation bonus (tier0
    /// detonate_bombs: `dmg = bomb.damage + bonus + bomb_damage_up` -- Remote
    /// Detonator's +2 rides here, before amplification, exactly like the
    /// Explosives Workshop bonus).
    ///
    /// Claim then resolve, which is where the recursion guard lives: the
    /// charges are spent and the power detached BEFORE any damage, because
    /// detonation damage can kill, fire hooks and re-enter combat logic. Tier 0
    /// does the same (`bombs, enemy.bombs = enemy.bombs, []`). The turn-start
    /// path splits those two halves across every pile on the enemy rather than
    /// doing them one pile at a time -- see <see cref="ClaimTurnStartPiles"/>.
    /// </summary>
    private async Task<int> Detonate(PlayerChoiceContext choiceContext, int bonus = 0)
    {
        // Read before the take: PowerCmd.Remove detaches the power, and the
        // target is who the payload is resolving against.
        var target = Owner;
        if (Take() is not { } pile) return 0;
        await PowerCmd.Remove(this);
        return await ResolvePayload(choiceContext, target, pile, bonus);
    }

    /// <summary>
    /// Resolve one CLAIMED pile against <paramref name="target"/>: per bomb,
    /// credit its placer, deal its Pyro hit, and ring its placer's listeners.
    ///
    /// Static and snapshot-driven on purpose (EB-138): everything it needs
    /// travels in the <see cref="TurnStartPile"/>, so a pile resolves the same
    /// whether its power still exists, whether the enemy is still alive, and
    /// whether some earlier pile already killed it.
    /// </summary>
    private static async Task<int> ResolvePayload(
        PlayerChoiceContext choiceContext, Creature target, TurnStartPile pile,
        int bonus)
    {
        var applier = pile.Applier;
        var combatState = pile.Combat;

        // Explosives Workshop: flat bonus per detonation, added BEFORE
        // amplification -- the sim totals `bomb.damage + bonus + bomb_damage_up`
        // and only then enters the elemental pipeline (effects.py detonate_bombs).
        //
        // R205, co-op: `applier` is now THIS PILE's placer rather than whoever
        // happened to bomb the enemy first, so the Workshop bonus and every
        // dealer-side amplification below read the right Klee's board. That is
        // a detonation-DAMAGE move, forced by the ruling and stated here so it
        // is not mistaken for drift.
        var damageUp =
            applier?.Powers.OfType<BombDamageUpPower>().FirstOrDefault()?.Amount ?? 0;

        // One VFX per detonation EVENT, not per bomb stack (sprint plan E2's
        // spam guard) — this method is the per-event funnel. R205 makes "event"
        // mean "one placer's pile", so a two-Klee enemy lobs two: the spam
        // guard still holds per pile, and two piles are two events.
        Vfx.KleeCombatVfx.SpawnBombLob(applier, target);

        foreach (var damage in pile.Payload)
        {
            // Sim order: detonations_total increments before the damage
            // lands (effects.py detonate_bombs).
            //
            // The corpse test is read PER BOMB and BEFORE this bomb's damage,
            // which is the only reading that says what it means: the bomb that
            // lands the kill detonated on a live enemy, and every bomb behind
            // it detonated on a corpse. EB-138 widens what "behind it" reaches
            // without changing the test: on a co-op board the bombs behind the
            // kill can now be a LATER PLACER'S pile, and they record against
            // that placer rather than being lost with their power.
            RecordDetonation(combatState, applier, onCorpse: target is { IsDead: true });

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

        return pile.Payload.Count;
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
