using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers.Prototype;

/// <summary>
/// THE OVERHAUL'S BOMB (rules 1, 2, 3 and 6 of the ruled brief's sec.3).
///
/// A numbered charge on an enemy that GROWS by
/// <see cref="KleeOverhaulLaw.BombGrowth"/> at the start of Klee's turn and
/// NEVER goes off by itself. Only a card that says <i>Set off</i> pops one, and
/// when it does, every Bomb on the target goes off ONE AT A TIME, each a Pyro
/// hit for its own size, BEFORE the rest of the card resolves. A Bomb whose
/// enemy dies JUMPS to a random living enemy at its current size. A MINE is a
/// Bomb that ALSO goes off when its enemy attacks Klee, before the hit lands.
///
/// WHY THIS IS A SEPARATE POWER AND NOT A MODE ON <see cref="BombPower"/>.
/// Rule 7 is "nothing fires by itself", and the shipped Bomb's whole lifecycle
/// is two automatic detonations -- <c>BeforeSideTurnStart</c> and the
/// early pop in <c>AfterDamageReceived</c>. Teaching one class to be both would
/// put a runtime branch inside every one of those hooks, in the file whose
/// per-placer instancing, suppression arbiter and death-teardown compensation
/// are the mod's most load-bearing co-op work. A second power costs a class and
/// buys the acceptance condition outright: under the flag no card places a
/// <see cref="BombPower"/>, so "no automatic detonation of any kind" is a
/// property of what is on the board rather than of a branch somebody remembers.
/// The shipped Bomb is not edited by this arm in any build.
///
/// WHAT IS INHERITED FROM THE SHIPPED BOMB, DELIBERATELY, because these are its
/// decisions and not this arm's to re-take:
///   * <see cref="PowerInstanceType.InstancedPerApplier"/> -- R205, one pile
///     per placer, so two Klees never spend each other's charges or credit;
///   * <see cref="DeepCloneFields"/> -- <c>AbstractModel.MutableClone</c> is a
///     shallow <c>MemberwiseClone</c>, so an un-cloned list is a silent
///     cross-enemy corruption bug rather than a crash;
///   * TAKE-THEN-RESOLVE -- charges leave the power before any damage lands, so
///     a kill mid-payload can neither re-enter the pile nor lose what is owed
///     (EB-138), which is also exactly what rule 3's jump needs;
///   * <see cref="PowerType.Buff"/> -- Artifact coexists with an application
///     rather than eating it ([USER] 2026-08-23).
///
/// WHAT IS NOT INHERITED: the shipped Bomb's "first attack while Bombed deals
/// 25% less" suppression. It is not in the brief's seven rules, so under rule 7
/// it is not a rule -- it would be a card.
/// </summary>
public sealed class ProtoBombPower : PowerModel, ILocalizationProvider
{
    /// <summary>
    /// BaseLib's AddModelLoc keys off Id.Entry for any model implementing this
    /// interface, so the loc lives here and cannot drift from the id.
    ///
    /// THE BADGE IS THE WHOLE UI (slice packet sec.5, last bullet): the number
    /// under the enemy is the total size sitting there, and the fuse mark is
    /// the Mine count in the smart tooltip. Nothing new is drawn -- this is the
    /// same <c>DisplayAmount</c> + <c>DynamicVar</c> rendering the shipped Bomb
    /// already uses, which is what "reuse the existing badge" means here.
    /// </summary>
    public List<(string, string)>? Localization => new()
    {
        ("title", "Bomb"),
        ("description",
            "A charge on this enemy. It grows at the start of your turn and "
          + "never goes off by itself. A card that says [gold]Set off[/gold] "
          + "pops every Bomb here, one at a time, each dealing its own size as "
          + "Pyro damage. A [gold]Mine[/gold] also goes off when this enemy "
          + "attacks you, before the hit lands."),
        ("smartDescription",
            "[gold]Set off[/gold] deals {Size} total Pyro damage here "
          + "({Amount} Bomb{Amount:plural:|s}, {Mines} of them "
          + "[gold]Mine{Mines:plural:|s}[/gold]). Grows at the start of your "
          + "turn; never goes off by itself."),
    };

    public override PowerType Type => PowerType.Buff;

    /// <summary>Counter: charges are spent by going off, not ticked by time.</summary>
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>R205's ruling, inherited unchanged: one pile per placer.</summary>
    public override PowerInstanceType InstanceType =>
        PowerInstanceType.InstancedPerApplier;

    /// <summary>
    /// ONE live charge.
    ///
    /// <c>Size</c> is rule 1's number -- what it grows and what it deals.
    /// <c>IsMine</c> is rule 6's flag, and it is a flag on a Bomb rather than a
    /// second power because the brief says so in as many words ("A Mine is a
    /// Bomb that ALSO goes off when...") and because Mines have to grow, merge
    /// and jump exactly like Bombs.
    /// <c>PayloadMineAll</c> is the Bomb payload the build list names: Jumpy
    /// Dumpty's charge, when it goes off, puts a Mine of this size on every
    /// enemy. 0 is "no payload", which is every other charge in the slice.
    /// </summary>
    public readonly record struct ProtoCharge(int Size, bool IsMine, int PayloadMineAll);

    /// <summary>Charges in placement order. MUST be deep-cloned: see
    /// <see cref="DeepCloneFields"/>.</summary>
    private List<ProtoCharge> _charges = new();

    protected override void DeepCloneFields()
    {
        base.DeepCloneFields();
        _charges = new List<ProtoCharge>(_charges);
    }

    // ---- the pure reads -----------------------------------------------

    /// <summary>Total size on this pile: what a Set off will deal here.</summary>
    public int TotalSize => _charges.Sum(c => c.Size);

    /// <summary>How many of this pile's charges are Mines -- the fuse mark.</summary>
    public int MineCount => _charges.Count(c => c.IsMine);

    /// <summary>The charges, for the pins. Never handed out to a mutator.</summary>
    internal IReadOnlyList<ProtoCharge> Charges => _charges;

    /// <summary>The badge shows the total size, not the count -- the shipped
    /// Bomb's ruling (2026-07-20), for its own reason: an enemy-side number
    /// reads as incoming damage, and a count hides what growing did.</summary>
    public override int DisplayAmount => TotalSize;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new[] { new DynamicVar("Size", 0m), new DynamicVar("Mines", 0m) };

    /// <summary>Called after EVERY mutation of <see cref="_charges"/>. The badge
    /// and the tooltip both derive from the list the explosions consume, so the
    /// number shown can never diverge from the number that will land.</summary>
    private void SyncDisplay()
    {
        var size = DynamicVars["Size"];
        size.BaseValue = TotalSize;
        size.ResetToBase();
        var mines = DynamicVars["Mines"];
        mines.BaseValue = MineCount;
        mines.ResetToBase();
        InvokeDisplayAmountChanged();
    }

    // ---- the pure mutations (no commands, nothing that can kill) -------

    /// <summary>Rule 1's growth, applied to this pile. PURE.</summary>
    internal void GrowBy(int amount)
    {
        if (amount == 0 || _charges.Count == 0) return;
        for (var i = 0; i < _charges.Count; i++)
        {
            _charges[i] = _charges[i] with { Size = _charges[i].Size + amount };
        }
        SyncDisplay();
    }

    /// <summary>Add one charge. PURE -- the APPLY that creates the pile is the
    /// caller's.</summary>
    internal void AddCharge(ProtoCharge charge)
    {
        _charges.Add(charge);
        SyncDisplay();
    }

    /// <summary>
    /// Empty this pile and hand back what it carried, null if it was already
    /// empty. PURE, and that is the point: the charges are off the power before
    /// anything that can kill runs, so a kill mid-payload cannot re-enter the
    /// pile (the shipped Bomb's EB-138 discipline, and rule 3's jump needs the
    /// same guarantee for the same reason).
    /// </summary>
    internal List<ProtoCharge>? TakeAll()
    {
        if (_charges.Count == 0) return null;
        var taken = new List<ProtoCharge>(_charges);
        _charges.Clear();
        SyncDisplay();
        return taken;
    }

    /// <summary>Empty only the MINES, leaving plain Bombs where they are.
    /// Rule 6: an attack on Klee pops the Mines and nothing else. PURE.</summary>
    internal List<ProtoCharge>? TakeMines()
    {
        var mines = _charges.Where(c => c.IsMine).ToList();
        if (mines.Count == 0) return null;
        _charges.RemoveAll(c => c.IsMine);
        SyncDisplay();
        return mines;
    }

    /// <summary>Remove ONE charge by index and hand it back. Sorry, Jean...'s
    /// primitive. PURE.</summary>
    internal ProtoCharge? TakeAt(int index)
    {
        if (index < 0 || index >= _charges.Count) return null;
        var charge = _charges[index];
        _charges.RemoveAt(index);
        SyncDisplay();
        return charge;
    }

    /// <summary>
    /// Rule 1's growth NUMBER for one Klee, right now. PURE, and it is one
    /// function because the two modifiers compose in one printed way:
    /// Explosives Workshop ADDS <see cref="KleeOverhaulLaw.WorkshopGrowth"/>
    /// per stack ("your Bombs grow by 1 more"), Alice's Recipe REPLACES the
    /// base with <see cref="KleeOverhaulLaw.AliceGrowth"/> ("grow by 4 instead
    /// of 2"). Replace-then-add is the only reading that leaves both faces
    /// true, and the brief's own gloss on Alice is "Breaks rule 1".
    /// </summary>
    internal static int GrowthFor(Creature? klee)
    {
        if (klee == null) return KleeOverhaulLaw.BombGrowth;
        var baseGrowth = klee.Powers.OfType<AlicesRecipePower>().Any()
            ? KleeOverhaulLaw.AliceGrowth
            : KleeOverhaulLaw.BombGrowth;
        var workshop = klee.Powers.OfType<ExplosivesWorkshopGrowthPower>()
            .Sum(p => p.Amount) * KleeOverhaulLaw.WorkshopGrowth;
        return baseGrowth + workshop;
    }

    // ---- rule 1: growth at the start of Klee's turn ---------------------

    /// <summary>
    /// RULE 1's growth, and rule 7's whole point: this hook GROWS and does not
    /// detonate. The shipped Bomb's identical hook is what fires its start-of-
    /// turn payload; under this arm there is nothing to fire, because nothing
    /// fires by itself.
    ///
    /// <c>BeforeSideTurnStart</c> for the same reason the shipped Bomb uses it:
    /// it is the turn-start hook that carries a <c>PlayerChoiceContext</c>, and
    /// the corpse sweep below can place a Bomb.
    /// </summary>
    public override async Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side != CombatSide.Player) return;

        // Jumps first: a Bomb owed a jump is a Bomb that should GROW on its new
        // enemy this turn, not next. See SweepJumps for why a sweep exists.
        await SweepJumps(choiceContext, combatState);
        GrowBy(GrowthFor(Applier));
    }

    // ---- rule 2: Set off ------------------------------------------------

    /// <summary>
    /// RULE 2. Every Bomb on <paramref name="target"/> goes off, ONE AT A TIME,
    /// each a Pyro hit for its own size -- and the caller's own damage has not
    /// run yet, because the generated card body emits this ahead of it.
    /// Returns how many charges went off.
    ///
    /// THE ORDER IS THE RULE, not an implementation detail: "one at a time"
    /// is what makes a three-Bomb pile three separate Pyro hits, so three
    /// separate reactions, three separate Sparks, and a kill on the second one
    /// leaves the third to jump rather than to fizzle (rule 3, the brief's own
    /// worked example).
    ///
    /// TAKE-THEN-RESOLVE: the whole pile leaves the power first (EB-138's
    /// discipline), so the loop below owns charges that no teardown can take.
    /// </summary>
    public static async Task<int> SetOff(
        PlayerChoiceContext choiceContext, Creature? target, Creature applier,
        CardModel? cardSource)
    {
        if (target == null) return 0;

        var taken = new List<ProtoCharge>();
        foreach (var pile in target.Powers.OfType<ProtoBombPower>().ToList())
        {
            if (pile.Applier != applier) continue;   // R205: your pile only
            if (pile.TakeAll() is { } charges) taken.AddRange(charges);
        }
        foreach (var pile in target.Powers.OfType<ProtoBombPower>().ToList())
        {
            if (pile.Applier == applier && pile.TotalSize == 0)
            {
                await PowerCmd.Remove(pile);
            }
        }
        if (taken.Count == 0) return 0;

        var ledger = KleeOverhaulLedger.For(applier);
        var doubled = ledger.TakeDoubling();
        var exploded = 0;

        for (var i = 0; i < taken.Count; i++)
        {
            // RULE 3, the brief's worked example: "The second of three Bombs
            // killed the enemy: the third jumps." The test is read per charge
            // and BEFORE the charge resolves, so the Bomb that lands the kill
            // still goes off on a live enemy and every Bomb behind it jumps.
            if (target.IsDead)
            {
                await JumpCharges(choiceContext, target, taken.Skip(i).ToList(),
                                  applier, cardSource);
                break;
            }
            await Explode(choiceContext, target, taken[i], applier, cardSource,
                          doubled);
            exploded++;
        }

        await SweepJumps(choiceContext, applier.CombatState);
        return exploded;
    }

    /// <summary>
    /// ONE explosion, which is the unit every other rule is priced in: one Pyro
    /// hit for the charge's size, one Spark, one payload, one entry in both of
    /// rule 7's counters.
    ///
    /// PYRO, THROUGH <see cref="ElementalHit"/>, is rule 5 and it is why the
    /// reaction half needs no card text at all: the shared pipeline resolves
    /// the aura, the amplifier and the reaction, so a cooked Bomb Vaporizes
    /// exactly as one of Klee's Attacks would. The reaction is DETECTED by
    /// diffing <c>ReactionEffects.TotalResolved</c> across the hit, because
    /// that counter is the one place every reaction in the mod passes through.
    /// </summary>
    private static async Task Explode(
        PlayerChoiceContext choiceContext, Creature target, ProtoCharge charge,
        Creature applier, CardModel? cardSource, bool doubled)
    {
        var ledger = KleeOverhaulLedger.For(applier);
        var size = doubled ? charge.Size * 2 : charge.Size;

        Vfx.KleeCombatVfx.SpawnBombLob(applier, target);

        var reactionsBefore = ReactionEffects.TotalResolved;
        await ElementalHit.Deal(choiceContext, target, Element.Pyro, size, applier);
        var reacted = ReactionEffects.TotalResolved > reactionsBefore;

        ledger.NoteExplosion(reacted, size);

        // THE BOMB PAYLOAD (Jumpy Dumpty). It rides the explosion rather than
        // the card, which is the whole of what makes the starter's promise
        // legible: the Mines arrive when the big Bomb finally goes off, not
        // when it was planted.
        if (charge.PayloadMineAll > 0 && applier.CombatState != null)
        {
            foreach (var enemy in applier.CombatState.HittableEnemies.ToList())
            {
                await Place(choiceContext, enemy, charge.PayloadMineAll,
                            isMine: true, payloadMineAll: 0, applier, cardSource);
            }
        }

        await NotifyExplosionListeners(choiceContext, applier, target, size, reacted);
    }

    /// <summary>
    /// The explosion bus, once PER EXPLOSION. Same shape and same reason as the
    /// shipped Bomb's detonation bus: subscribers are the applying player's
    /// relics and creature powers, discovered by interface test so a listener
    /// cannot be forgotten at wire-up. Rule 4's Spark arrives here, through
    /// Pounding Surprise, which is the brief's own arrangement -- the relic IS
    /// the Spark rule (sec.8).
    /// </summary>
    private static async Task NotifyExplosionListeners(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        int size, bool reacted)
    {
        var player = applier.Player;
        if (player == null) return;

        foreach (var relic in player.Relics.ToList())
        {
            if (relic is IProtoExplosionListener listener)
            {
                await listener.OnBombExploded(
                    choiceContext, applier, target, size, reacted);
            }
        }
        foreach (var power in applier.Powers.ToList())
        {
            if (power is IProtoExplosionListener listener)
            {
                await listener.OnBombExploded(
                    choiceContext, applier, target, size, reacted);
            }
        }
    }

    // ---- rule 3: Jump ---------------------------------------------------

    /// <summary>
    /// RULE 3, for charges already in hand: each moves to a random LIVING enemy
    /// at its current size. Nothing is lost and nothing grows -- a jump is a
    /// move, so the size, the Mine flag and the payload all travel.
    ///
    /// Each charge rolls its own destination (the shipped Bomb's per-bomb
    /// target pick, same stream), so three jumping Bombs can land on three
    /// different enemies. With no living enemy left there is nowhere to go and
    /// the charges are dropped, which is the only answer available: the fight
    /// is over.
    /// </summary>
    private static async Task JumpCharges(
        PlayerChoiceContext choiceContext, Creature from,
        IReadOnlyList<ProtoCharge> charges, Creature applier,
        CardModel? cardSource)
    {
        var combat = applier.CombatState;
        if (combat == null) return;

        foreach (var charge in charges)
        {
            var candidates = combat.HittableEnemies
                .Where(e => e != from && !e.IsDead).ToList();
            if (candidates.Count == 0) return;
            var dest = combat.RunState.Rng.CombatTargets.NextItem(candidates);
            if (dest == null) return;
            await Place(choiceContext, dest, charge.Size, charge.IsMine,
                        charge.PayloadMineAll, applier, cardSource);
        }
    }

    /// <summary>
    /// RULE 3 for the death this arm did NOT cause: "A partner or a poison
    /// killed the enemy: all of them jump."
    ///
    /// WHY A SWEEP AND NOT A DEATH HOOK. The base game does not broadcast
    /// <c>AfterDamageReceived</c> for a blow that killed
    /// (<c>CreatureCmd.Damage</c>: <c>if (!WasTargetKilled || !target.IsDead)</c>,
    /// the same fact <c>BombPower</c> records), and the kill runs INLINE inside
    /// the damage command, detaching the corpse and stripping its powers before
    /// control returns. There is no hook on the dying enemy's own power that
    /// can be trusted to fire. What survives a teardown is the POWER OBJECT and
    /// the charge list on it, so the arm keeps a per-combat register of live
    /// piles and sweeps it: any pile whose enemy is dead or gone hands its
    /// charges to <see cref="JumpCharges"/>.
    ///
    /// WHEN IT RUNS, and the brief does not say, so this is the arm's default
    /// and it is the earliest set of moments that need no new machinery: at the
    /// start of Klee's turn (before growth, so a jumped Bomb grows on its new
    /// enemy this turn), at the end of every Set off, and after a Mine fires.
    /// A jump is therefore always observed before the player's next decision.
    /// </summary>
    public static async Task SweepJumps(
        PlayerChoiceContext choiceContext, ICombatState? combatState)
    {
        if (combatState == null) return;
        foreach (var pile in Register.Claim(combatState))
        {
            if (pile.Applier == null) continue;
            await JumpCharges(choiceContext, pile.Owner, pile.Charges,
                              pile.Applier, cardSource: null);
        }
    }

    // ---- rule 6: the Mine ----------------------------------------------

    /// <summary>
    /// RULE 6. When this enemy's attack is about to land on the Klee who placed
    /// the Mine, every Mine here goes off first; plain Bombs stay put.
    ///
    /// <c>BeforeDamageReceived</c> is the hook because it is the one that fires
    /// before the hit lands AND carries a <c>PlayerChoiceContext</c> -- an
    /// explosion deals damage, and dealing damage needs one. The hook is fanned
    /// to every model in the combat (<c>Hook.IterateCombatHookListeners</c>),
    /// which is what lets a power on the ENEMY see the enemy's own outgoing
    /// damage; <c>CompanionPowers</c> reads it from the other side the same way.
    ///
    /// NO PER-ACTION LATCH IS NEEDED, unlike the shipped Bomb's suppression:
    /// the Mines are CONSUMED, so the second hit of a multi-hit intent finds
    /// none. The rule is self-limiting.
    ///
    /// <c>target != Applier</c> is the co-op clause and it falls out of R205:
    /// this pile belongs to one Klee, and it is her attack to answer.
    /// </summary>
    public override async Task BeforeDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, decimal amount,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (dealer != Owner || target != Applier) return;
        if (!props.IsPoweredAttack()) return;
        if (Applier == null) return;

        var mines = TakeMines();
        if (mines == null) return;
        if (_charges.Count == 0) await PowerCmd.Remove(this);

        var ledger = KleeOverhaulLedger.For(Applier);
        var doubled = ledger.PeekDoubling();
        var enemy = Owner;
        for (var i = 0; i < mines.Count; i++)
        {
            if (enemy.IsDead)
            {
                await JumpCharges(choiceContext, enemy, mines.Skip(i).ToList(),
                                  Applier, cardSource: null);
                break;
            }
            await Explode(choiceContext, enemy, mines[i], Applier,
                          cardSource: null, doubled);
        }
        await SweepJumps(choiceContext, Applier.CombatState);
    }

    // ---- placement, and the card verbs -----------------------------------

    /// <summary>
    /// Plant one charge on <paramref name="target"/>, stacking into this
    /// placer's own pile (R205). The single entry point for every source:
    /// a card's <c>plant_bomb</c>, a jump's landing, a payload's Mines and
    /// Chained Reactions' re-bomb all arrive here, so the register below cannot
    /// miss a pile.
    /// </summary>
    public static async Task Place(
        PlayerChoiceContext choiceContext, Creature target, int size,
        bool isMine, int payloadMineAll, Creature applier, CardModel? cardSource)
    {
        var power = await PowerCmd.Apply<ProtoBombPower>(
            choiceContext, target, 1, applier: applier, cardSource: cardSource);

        if (power is ProtoBombPower bomb)
        {
            bomb.AddCharge(new ProtoCharge(size, isMine, payloadMineAll));
            Register.Note(bomb);
        }
        else
        {
            Log.Warn($"[{KleeMod.ModId}] ProtoBombPower.Place: could not resolve "
                   + "the applied power instance; the charge was not recorded.");
        }
    }

    /// <summary>
    /// Chain Fuse: every Bomb on ONE enemy grows by <paramref name="amount"/>.
    /// This placer's piles only, for the same reason Set off reads only hers.
    /// </summary>
    public static void GrowOn(Creature? target, Creature applier, int amount)
    {
        if (target == null) return;
        foreach (var pile in target.Powers.OfType<ProtoBombPower>().ToList())
        {
            if (pile.Applier == applier) pile.GrowBy(amount);
        }
    }

    /// <summary>
    /// Careful Arrangement: move ALL of this placer's Bombs onto one enemy AS
    /// ONE Bomb, which then grows by <paramref name="growth"/>.
    ///
    /// TWO THINGS THE CARD TEXT DOES NOT SAY, chosen as the simplest reading
    /// that loses nothing (and reported as defaults):
    ///   * the merged Bomb is a MINE if any merged charge was one -- merging
    ///     must not silently delete the defence the player set up;
    ///   * it carries the payloads of every merged charge, summed, for the same
    ///     reason: a merge is a move, and a move loses nothing.
    /// </summary>
    public static async Task MergeAllTo(
        PlayerChoiceContext choiceContext, Creature? dest, Creature applier,
        int growth, CardModel? cardSource)
    {
        if (dest == null || applier.CombatState == null) return;

        var size = 0;
        var isMine = false;
        var payload = 0;
        foreach (var enemy in applier.CombatState.HittableEnemies.ToList())
        {
            foreach (var pile in enemy.Powers.OfType<ProtoBombPower>().ToList())
            {
                if (pile.Applier != applier) continue;
                if (pile.TakeAll() is not { } charges) continue;
                foreach (var charge in charges)
                {
                    size += charge.Size;
                    isMine |= charge.IsMine;
                    payload += charge.PayloadMineAll;
                }
                await PowerCmd.Remove(pile);
            }
        }
        if (size == 0) return;
        await Place(choiceContext, dest, size + growth, isMine, payload,
                    applier, cardSource);
    }

    /// <summary>
    /// Sorry, Jean...: remove ONE of your Bombs and gain Block equal to its
    /// size. Returns the size removed, 0 if there was nothing to remove.
    ///
    /// WHICH Bomb, the card does not say. THE LARGEST, which is the simplest
    /// deterministic answer and the only one a player can plan around: an
    /// emergency exit whose size is a coin flip is not an exit.
    /// </summary>
    public static async Task<int> RemoveLargestForBlock(
        PlayerChoiceContext choiceContext, Creature applier)
    {
        if (applier.CombatState == null) return 0;

        ProtoBombPower? best = null;
        var bestIndex = -1;
        var bestSize = 0;
        foreach (var enemy in applier.CombatState.HittableEnemies.ToList())
        {
            foreach (var pile in enemy.Powers.OfType<ProtoBombPower>())
            {
                if (pile.Applier != applier) continue;
                for (var i = 0; i < pile._charges.Count; i++)
                {
                    if (pile._charges[i].Size <= bestSize) continue;
                    best = pile;
                    bestIndex = i;
                    bestSize = pile._charges[i].Size;
                }
            }
        }
        if (best == null || best.TakeAt(bestIndex) is not { } removed) return 0;
        if (best.TotalSize == 0 && best.Charges.Count == 0)
        {
            await PowerCmd.Remove(best);
        }
        return removed.Size;
    }

    /// <summary>Big Badda Boom's second clause reads this: the total size this
    /// play has already set off. Kept on the ledger, not here, because the card
    /// asks about the PLAY and a pile is gone by the time it asks.</summary>
    public static int SizeSetOffThisPlay(Creature applier) =>
        KleeOverhaulLedger.For(applier).SizeSetOffThisPlay;

    // ---- the per-combat register of live piles ---------------------------

    /// <summary>
    /// Every pile this combat has seen, so a JUMP can still find the charges of
    /// an enemy the game has already torn down. See <see cref="SweepJumps"/>
    /// for why a register is the only shape available.
    ///
    /// NOT A SECOND COPY OF THE STATE, which is the trap here: it holds power
    /// REFERENCES, so the charges it reaches are the same list the badge shows
    /// and the same list an explosion consumes. Cleared whenever the combat
    /// instance changes, so it holds at most this combat's piles.
    /// </summary>
    internal static class Register
    {
        private static ICombatState? _combat;
        private static readonly List<ProtoBombPower> _piles = new();

        internal static void Note(ProtoBombPower pile)
        {
            Rebase(pile.CombatState);
            if (!_piles.Contains(pile)) _piles.Add(pile);
        }

        /// <summary>Piles whose enemy is dead or gone AND that still carry
        /// charges: what a jump owes. Emptied as it is claimed, so a second
        /// sweep in the same beat finds nothing.</summary>
        internal static List<Claimed> Claim(ICombatState combatState)
        {
            Rebase(combatState);
            var owed = new List<Claimed>();
            foreach (var pile in _piles.ToList())
            {
                var owner = pile.Owner;
                var alive = owner is { IsDead: false }
                            && combatState.HittableEnemies.Contains(owner);
                if (alive) continue;
                _piles.Remove(pile);
                if (pile.TakeAll() is { } charges)
                {
                    owed.Add(new Claimed(owner, pile.Applier, charges));
                }
            }
            return owed;
        }

        internal static void Rebase(ICombatState? combatState)
        {
            if (ReferenceEquals(_combat, combatState)) return;
            _combat = combatState;
            _piles.Clear();
        }

        /// <summary>Charges taken off a pile whose enemy is gone.</summary>
        internal readonly record struct Claimed(
            Creature Owner, Creature? Applier, IReadOnlyList<ProtoCharge> Charges);
    }
}

/// <summary>
/// The explosion event bus (rule 4's carrier, and Chained Reactions' and
/// Catalytic Converter's). Once PER EXPLOSION, so a three-Bomb Set off is three
/// events -- which is what makes "1 Spark per explosion" a rule about
/// explosions rather than about cards.
///
/// <paramref name="reacted"/> is the half the React loop is built on: it says
/// whether THIS explosion consumed an off-element aura, which no listener could
/// work out for itself after the fact.
/// </summary>
public interface IProtoExplosionListener
{
    /// <param name="choiceContext">Live context; a listener may deal damage.</param>
    /// <param name="applier">The Klee whose card planted the Bomb.</param>
    /// <param name="target">The enemy it went off on.</param>
    /// <param name="size">What that single explosion dealt, doubling included.</param>
    /// <param name="reacted">Did this explosion trigger an Elemental Reaction?</param>
    Task OnBombExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        int size, bool reacted);
}
