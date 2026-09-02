using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Furina;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// Marker for Furina's eventual CharacterModel. Keeping the resource hooks
/// behind character identity prevents a generated Furina card obtained by
/// another character from silently granting them Furina's HP-loss engine.
/// </summary>
public interface IFurinaCharacter
{
}

/// <summary>
/// The sim constants that define Furina's two combat resources.
/// </summary>
public static class FurinaResourceConstants
{
    public const int FanfarePerHpLost = 1;
    public const int FanfarePerEncoreSpent = 1;

    /// <summary>
    /// SINGLE-LEG Fanfare (rework 2026-07-28, Track A, RULED). Mirrors
    /// tier0/constants.py FANFARE_PER_ENCORE_ABSORBED.
    ///
    /// Fanfare prints when Encore goes DOWN and never when it goes up.
    /// FanfarePerEncoreGained is DELETED, not zeroed: the gain leg made every
    /// Encore point pay the meter twice, which the pilot-gap battery measured
    /// at 47% of all generation under the greedy pilot and 61.6% under the
    /// stoker.
    ///
    /// Absorption is the third Encore reduction path and used to be the only
    /// one worth nothing. It pays now because absorbed Encore is deferred
    /// Block that will never block a future hit -- cashing it is a real cost.
    ///
    /// The three FanfarePer* constants above are NOT independently tunable:
    /// together they say "every point of damage past Block prints exactly 1
    /// Fanfare", via absorption if the buffer eats it and via HP loss if HP
    /// does. Change one and that sentence stops being true.
    /// </summary>
    public const int FanfarePerEncoreAbsorbed = 1;

    // --- "The Tide Turns" (F-A1/F-A3), ported by G-A1 2026-07-25. Mirrors
    // tier0/constants.py FANFARE_DECAY_FRACTION; floor/cap movement is the
    // two printed keywords ("Fanfare +X" gain_fanfare_floor, "Fanfare Cap +X"
    // raise_fanfare_cap) since the 2026-07-28 Fanfare rework.
    // Fanfare is a READ-ONLY momentum stat: activity generates it, it fades
    // each turn, and printed floor grants give it a floor. No card
    // spends it -- that grammar (fanfare_cost) was retired by F-A4 and no
    // sheet carries it any more.

    /// <summary>
    /// PROPORTIONAL decay, taken as a fraction of the WHOLE meter and then
    /// clamped at the floor (not a fraction of the amount above the floor) --
    /// "Fanfare fades by 20% each turn" has to stay a one-line rule.
    ///
    /// double, and rounded with the default MidpointRounding.ToEven, because
    /// the sim's `round()` is Python's banker's rounding. The two languages
    /// agree only because both default to half-to-even; that coincidence is
    /// load-bearing for trace parity, so it is pinned here rather than left
    /// to a reader to rediscover.
    /// </summary>
    public const double FanfareDecayFraction = 0.20;

    /// <summary>
    /// The Fanfare ceiling's BASE term, as a fraction of LIVE MaxHp.
    /// Mirrors tier0/constants.py FANFARE_CAP_FRACTION.
    ///
    /// EXTRACTED, NOT INTRODUCED (EB-97, 2026-08-13). The fraction was an
    /// inline `/ 2` inside FanfareCap, which meant it was absent from BOTH
    /// halves of tools/lint_constant_parity.py -- neither MIRRORED nor
    /// declared UNMIRRORED -- so the gate could not see the number at all
    /// and a one-sided retune of LAW.md:189's "%maxHP" would have drifted
    /// silently. That is the exact failure the gate exists to prevent.
    ///
    /// double with an `(int)` cast at the use site, to match the sim's
    /// `int(C.FANFARE_CAP_FRACTION * max_hp)`: both TRUNCATE, so an odd
    /// max HP rounds the ceiling down in both engines (67 -> 33). Do not
    /// switch this to Math.Round -- unlike FanfareDecayFraction, which is
    /// half-to-even on both sides on purpose, this one is floor-on-both.
    /// The behaviour is byte-identical to the `/ 2` it replaced for every
    /// non-negative MaxHp.
    /// </summary>
    public const double FanfareCapFraction = 0.5;

    // FanfareFloorPerPower / FanfareFloorPerPowerRare: DELETED by the Fanfare
    // rework (2026-07-28, Track B, RULED), together with the grant block in
    // FurinaResourceHooks.AfterCardPlayed that read them. Playing a Power no
    // longer grants anything the card does not print.
    //
    // The value moved onto the faces as two printed keywords -- "Fanfare Cap
    // +X" (FurinaResources.RaiseFanfareCap, un-retired for the job) and
    // "Fanfare +X" (FurinaResources.GainFanfareFloor, rare Powers only).
    // Deleted rather than left at 0 so nothing can quietly re-arm the
    // automatic, and so the constant-parity gate has nothing to compare
    // against a sim constant that no longer exists either.

    public const int BurstPerSkillTag = 5;
    public const int BurstPerReaction = 5;
    public const int BurstPerEncoreSpent = 1;
    public const int BurstPerSalonTick = 2;
    public const int BurstMax = 70;
}

/// <summary>
/// Furina's unbounded, per-combat Encore buffer.
///
/// BaseLib owns reset, affordability, cloning, and card-cost visuals. Encore
/// card costs are exceptional only in their timing: the sim spends them
/// BEFORE card effects (combat.py play_card :236-241, right after the energy
/// debit and above the replay loop).
/// <see cref="FurinaResourceHooks.BeforeCardPlayed"/> performs that spend, so
/// BaseLib's own is a deliberate no-op here.
///
/// This class's spend was always correct; only its old wording -- "BaseLib's
/// normal post-resolution spend" -- was wrong, and that same wrong belief is
/// what let the Fanfare bug sit. BaseLib spends inside CardModel.SpendResources,
/// which runs BEFORE OnPlayWrapper. See <see cref="FanfareResource"/>.
/// </summary>
public sealed class EncoreResource : BasicCustomResource
{
    public EncoreResource() : base("KLEEMOD_ENCORE")
    {
    }

    /// <summary>A gate the buffer has to satisfy, not energy. See
    /// <see cref="FanfareResource.ApplySharedModification"/> -- card_playable
    /// compares against the printed encore_cost, so a "free" effect must not
    /// waive it.</summary>
    public override bool ApplySharedModification => false;

    public override Task<bool> Spend<T>(
        ICombatState combatState, AbstractModel? spender, int amount, bool optional)
    {
        return Task.FromResult(true);
    }
}

/// <summary>
/// Furina's Fanfare: a READ-ONLY momentum stat since "The Tide Turns"
/// (F-A1/F-A4, ported to C# by G-A1 2026-07-25).
///
/// Generation is activity-based only -- HP lost, Encore gained, Encore spent,
/// a Center Stage card played. It DECAYS each turn from the player's second
/// turn (<see cref="FurinaResources.DecayFanfare"/>), and it rests on a
/// permanent per-combat floor built from constellation grants
/// (<see cref="FurinaResources.GainFanfareFloor"/>). Cards READ it
/// (<c>bonus_formula: N_per_M_fanfare</c>) and GATE on it
/// (<c>if: fanfare_at_least_N</c>).
///
/// **No card spends it.** The <c>fanfare_cost</c> grammar was retired by
/// F-A4 because Encore already is Furina's spendable resource and a second
/// one was a redundant system; no sheet carries a fanfare_cost today. The
/// whole payment path that used to live here -- BaseLib's transpiled
/// SpendResources, the deliberate no-op that displaced it, and the
/// AfterCardPlayed settle that paid at the sim's moment -- is DELETED rather
/// than left dormant, so a future card cannot quietly re-arm it.
///
/// <see cref="Spend{T}"/> survives as a defensive no-op only: if anything
/// ever attaches a cost to this resource, the meter must not silently drain.
/// </summary>
public sealed class FanfareResource : BasicCustomResource
{
    public FanfareResource() : base("KLEEMOD_FANFARE")
    {
    }

    /// <summary>
    /// A meter the audience fills, not energy: a "this card is free" effect
    /// must not waive the applause. Retained after the spend retirement
    /// because BaseLib's SetToFree forwarding is about the RESOURCE, not
    /// about any particular card's cost, and a read-only meter that a free
    /// effect could zero would break every reader on the sheet.
    /// </summary>
    public override bool ApplySharedModification => false;

    /// <summary>DEFENSIVE NO-OP. Fanfare is read-only; nothing may spend it.
    /// Left in place so that attaching a cost to this resource fails
    /// harmlessly instead of draining the meter behind the design.</summary>
    public override Task<bool> Spend<T>(
        ICombatState combatState, AbstractModel? spender, int amount, bool optional)
    {
        return Task.FromResult(true);
    }
}

/// <summary>
/// The cap half of a constellation grant. <see cref="FanfareFloorResource"/>
/// is the floor half; <see cref="FurinaResources.GainFanfareFloor"/> raises
/// both by the same amount, exactly as the sim's `gain_fanfare_floor` raises
/// `fanfare_cap` and `fanfare_floor` together.
///
/// Raising the cap alongside the floor is load-bearing rather than
/// bookkeeping: a floor that pushed the current value up toward an UNMOVED
/// ceiling would simply re-pin the meter, and keeping the two apart is what
/// preserves the gradient every Fanfare reader is built on.
///
/// Kept as its own resource rather than folded into the floor because the sim
/// models cap and floor as two independent fields that merely happen to move
/// together today. Mirroring that shape means <see cref="FurinaResources.RaiseFanfareCap"/>
/// (un-retired by Track B -- the "Fanfare Cap +X" keyword's runtime, ~16
/// sheet users) stays expressible without a rewrite.
/// </summary>
public sealed class FanfareCapBonusResource : BasicCustomResource
{
    public FanfareCapBonusResource() : base("KLEEMOD_FANFARE_CAP_BONUS")
    {
    }
}

/// <summary>
/// Furina's permanent-for-the-combat Fanfare floor (F-A3). Decay never takes
/// the meter below this value.
///
/// LEGAL under the no-passive-accrual law (kickoff §4): a floor is STATIC
/// value, not accrual -- it does not grow with time, so stalling still earns
/// nothing. Stated here because a floor superficially resembles the per-turn
/// accrual §4 bans forever, and the distinction is the whole reason this
/// mechanic is allowed to exist.
///
/// PER-COMBAT, like every other Furina resource: a Power is replayed each
/// fight and re-earns its grant. This is free here in a way it was not in the
/// sim -- BaseLib's BasicCustomResource.PrepForCombat() sets Amount = 0 for
/// every custom resource at combat start, so the floor and the cap bonus both
/// rewind by construction. The sim needed an explicit `cap -= floor` rewind
/// because its Player object is reused across every fight; without it the
/// ceiling ratcheted upward all run. That failure mode is structurally
/// impossible here -- but it is impossible because of a BaseLib default, not
/// because of anything this file does, so the citation is recorded rather
/// than the conclusion assumed: BaseLib.decompiled.cs, BasicCustomResource
/// (`public override void PrepForCombat() { Amount = 0; }`), reached through
/// CustomResources&lt;T&gt;.PrepForCombat per PlayerCombatState.
/// </summary>
public sealed class FanfareFloorResource : BasicCustomResource
{
    public FanfareFloorResource() : base("KLEEMOD_FANFARE_FLOOR")
    {
    }
}

/// <summary>
/// Furina's 70-point Burst meter. Like Klee's meter it may overflow and is
/// emptied completely when the kit Burst is cast.
/// </summary>
public sealed class FurinaBurstResource : BasicCustomResource
{
    public FurinaBurstResource() : base("KLEEMOD_FURINA_BURST")
    {
    }

    /// <summary>
    /// The meter's ceiling, on the wire (`EB-181`). The bridge's resource
    /// snapshot is an id and an amount, so a meter reached a blind page with
    /// no maximum and the render had to say so on every meter row it printed.
    /// A ceiling is the MOD's fact and never BaseLib's, so the bridge asks for
    /// a public int `Max` and reports `null` for any resource that declares
    /// none (`vendor/STS2_MCP/gits/GitsResources.cs`, `GitsResourceInfo`).
    /// This exposes the constant that is already the gate; it decides nothing.
    /// </summary>
    public int Max => FurinaResourceConstants.BurstMax;

    /// <summary>Meter, not energy: opt out of BaseLib's SetToFree forwarding.
    /// See <see cref="KleeBurstResource.ApplySharedModification"/>.</summary>
    public override bool ApplySharedModification => false;

    /// <summary>Gate on the CANONICAL 70, never a discounted number. See
    /// <see cref="KleeBurstResource.CanAfford"/> for the full reasoning.</summary>
    public override bool CanAfford(CardModel card, int cost)
    {
        var canonical = CustomResources<FurinaBurstResource>.CanonicalCost(card);
        return canonical < 0 ? base.CanAfford(card, cost) : Amount >= canonical;
    }

    /// <summary>DELIBERATE NO-OP; the drain lives in <see cref="DrainOnPlay"/>.</summary>
    public override Task<bool> Spend<T>(
        ICombatState combatState, AbstractModel? spender, int amount, bool optional)
    {
        return Task.FromResult(true);
    }

    /// <summary>
    /// Sim law (combat.py play_card): a requires-full play zeroes the meter,
    /// pre-resolution. Called from FurinaResourceHooks.BeforeCardPlayed.
    /// See <see cref="KleeBurstResource.DrainOnPlay"/> for why this cannot
    /// ride the cost machinery -- the infinite-Burst bug, 2026-07-24.
    /// </summary>
    public static void DrainOnPlay(CardModel card)
    {
        if (CustomResources<FurinaBurstResource>.Cost(card) == null) return;
        var owner = card.Owner;
        if (owner == null || !FurinaResources.IsFurina(owner.Creature)) return;
        var combatState = owner.PlayerCombatState;
        if (combatState == null) return;
        CustomResources<FurinaBurstResource>.Get(combatState).Amount = 0;
        Vfx.GaugeBridge.Refresh(owner.Creature);
    }
}

/// <summary>
/// Canonical accessors and mutations for Encore/Fanfare. Every generated
/// Furina card goes through these methods so gain/spend activity and the
/// Fanfare cap cannot drift between individual card implementations.
/// </summary>
public static class FurinaResources
{
    public static bool IsFurina(Creature creature) =>
        creature.Player?.Character is IFurinaCharacter;

    /// <summary>
    /// Are the FOUR SHIPPED FANFARE MINT LEGS retired for this creature?
    ///
    /// The Furina reframe's §4.1 states its rule positively -- "Fanfare is
    /// minted by a member PERFORMING and by nothing else" -- and the four legs
    /// it retires are HP lost, Encore spent, Encore absorbed and a Spotlighted
    /// card played. Three of those are in this file and the fourth is in
    /// <c>SpotlightSystem.NotePlay</c>; all four ask THIS question, once,
    /// rather than each carrying its own copy of the flag read, because a rule
    /// stated once should be asked once. It is the same argument
    /// <see cref="BurstResource"/>'s gauge guard makes and the same shape
    /// <c>KokomiResources.BurstGaugeApplies</c> has.
    ///
    /// FALSE IN A RELEASE BUILD BY CONSTRUCTION: the arm's switch lives under
    /// <c>Powers/Prototype/</c>, which is <c>Compile Remove</c>d, so without
    /// the quarantine property there is nothing to ask and every leg mints
    /// exactly as it ships.
    /// </summary>
    public static bool ReframeRetiresTheShippedMintLegs(Creature? creature)
    {
#if PROTOTYPE_CARDS
        return FurinaReframe.MeterLiveFor(creature);
#else
        return false;
#endif
    }

    private static EncoreResource? EncoreResourceFor(Creature creature)
    {
        var combatState = creature.Player?.PlayerCombatState;
        return combatState == null
            ? null
            : CustomResources<EncoreResource>.Get(combatState);
    }

    private static FanfareResource? FanfareResourceFor(Creature creature)
    {
        var combatState = creature.Player?.PlayerCombatState;
        return combatState == null
            ? null
            : CustomResources<FanfareResource>.Get(combatState);
    }

    private static FanfareCapBonusResource? FanfareCapBonusFor(Creature creature)
    {
        var combatState = creature.Player?.PlayerCombatState;
        return combatState == null
            ? null
            : CustomResources<FanfareCapBonusResource>.Get(combatState);
    }

    private static FanfareFloorResource? FanfareFloorFor(Creature creature)
    {
        var combatState = creature.Player?.PlayerCombatState;
        return combatState == null
            ? null
            : CustomResources<FanfareFloorResource>.Get(combatState);
    }

    private static FurinaBurstResource? BurstResourceFor(Creature creature)
    {
        var combatState = creature.Player?.PlayerCombatState;
        return combatState == null
            ? null
            : CustomResources<FurinaBurstResource>.Get(combatState);
    }

    public static int Encore(Creature creature) =>
        EncoreResourceFor(creature)?.Amount ?? 0;

    public static int Fanfare(Creature creature) =>
        FanfareResourceFor(creature)?.Amount ?? 0;

    public static int Burst(Creature creature) =>
        BurstResourceFor(creature)?.Amount ?? 0;

    /// <summary>The permanent-for-the-combat baseline the meter rests on.
    /// Decay never takes Fanfare below it.</summary>
    public static int FanfareFloor(Creature creature) =>
        IsFurina(creature) ? FanfareFloorFor(creature)?.Amount ?? 0 : 0;

    /// <summary>
    /// The ceiling. DEMOTED by F-A5 from a first-order design dial to a high
    /// safety rail: under decay the ceiling does not bind (the cap-1000 sweep
    /// cells reported 0.0% at-cap). Kept, not deleted, so a degenerate
    /// floor-stack still has a stop.
    /// </summary>
    public static int FanfareCap(Creature creature)
    {
        if (!IsFurina(creature)) return 0;
        return (int)(FurinaResourceConstants.FanfareCapFraction * creature.MaxHp)
               + (FanfareCapBonusFor(creature)?.Amount ?? 0);
    }

    public static void GainFanfare(Creature creature, int amount)
    {
        if (amount <= 0) return;
        var resource = FanfareResourceFor(creature);
        var cap = FanfareCap(creature);
        if (resource == null || cap <= 0) return;
        var before = resource.Amount;
        resource.Amount = Math.Min(cap, resource.Amount + amount);
        NoteFanfareChanged(creature, before, resource.Amount);
    }

    // ------------------------------------------------------------------
    // A7 -- Unheard Confession: Block whenever the meter MOVES
    // ------------------------------------------------------------------

    /// <summary>
    /// Block that a Fanfare change has EARNED but not yet been handed over,
    /// per creature. One entry per player, never per card.
    ///
    /// THIS IS THE WHOLE A7 IDIOM, and it is a deferral rather than a direct
    /// grant because the mutators above are synchronous by design while every
    /// Block grant in this mod is `await CreatureCmd.GainBlock`. The two
    /// alternatives were both rejected twice before, and still are: threading
    /// async through the resource surface drags GainEncore/SpendEncore and
    /// every generated Encore card into a co-op-critical refactor, and
    /// Creature.GainBlockInternal has no precedent here and no decompile
    /// evidence about which hooks it skips.
    ///
    /// The precedent this DOES copy is CurtainCallHooks.NoteEncoreSpent: note
    /// synchronously, settle at the next awaited Furina hook. That idiom has
    /// shipped since R85 on the same funnel (SpendEncore), so this adds no new
    /// co-op exposure -- the write happens at exactly the points a vetted one
    /// already happens, and the settle happens at points both peers reach
    /// deterministically in the lockstep.
    /// </summary>
    private static readonly Dictionary<Creature, int> PendingDeltaBlock = new();

    /// <summary>
    /// Mirrors resources.note_fanfare_change. Called from all FOUR mutation
    /// funnels -- gain, floor-raise, decay, crash -- which is the entire
    /// trigger surface in both engines; a fifth mutator added without a call
    /// here is the only way to break the parity.
    ///
    /// FLAT per change EVENT, either direction, exactly like the sim: the
    /// amount of Block does not scale with how far the meter moved.
    ///
    /// INERT AT SATURATION. A gain that lands entirely at the cap moved
    /// nothing (before == after), so it is not a change and pays nothing. That
    /// is the sim's `applied == 0` case and it is deliberate, not an oversight.
    /// </summary>
    private static void NoteFanfareChanged(
        Creature creature, int before, int after)
    {
        if (before == after) return;
        var amount = FanfareDeltaBlockPower.AmountFor(creature);
        if (amount <= 0) return;
        PendingDeltaBlock[creature] =
            (PendingDeltaBlock.TryGetValue(creature, out var held) ? held : 0)
            + amount;
    }

    /// <summary>
    /// Hand over whatever the meter earned. Idempotent: the counter is taken
    /// and cleared, so extra calls are free and a hook that fires on a turn
    /// with no Fanfare movement costs nothing.
    ///
    /// Unscaled and Unpowered, following SalonBowBlockPower: this is a
    /// power's activity payout rather than a card's printed Block, so
    /// Spotlight does not read it -- the same rule the sim states in
    /// note_fanfare_change.
    ///
    /// Several change events inside one hook window settle as ONE GainBlock
    /// call for their SUM rather than as N calls. With Unpowered that is
    /// arithmetically identical to the sim's N separate adds; it is recorded
    /// because it would stop being identical the day this payout gains a
    /// per-grant modifier.
    /// </summary>
    public static async Task FlushFanfareDeltaBlock(
        PlayerChoiceContext choiceContext, Creature creature)
    {
        PurgeDeltaBlock();
        if (!PendingDeltaBlock.TryGetValue(creature, out var pending)) return;
        PendingDeltaBlock.Remove(creature);
        if (pending <= 0) return;
        await CreatureCmd.GainBlock(
            creature, pending, ValueProp.Unpowered, null, fast: true);
    }

    /// <summary>Drop keys whose combat is gone. A creature that died holding a
    /// pending settle would otherwise leave one entry per combat behind for
    /// the length of a run; same cheap sweep CurtainCallHooks.Purge does.</summary>
    private static void PurgeDeltaBlock()
    {
        foreach (var stale in PendingDeltaBlock.Keys
                     .Where(c => c.CombatState == null)
                     .ToList())
        {
            PendingDeltaBlock.Remove(stale);
        }
    }

    /// <summary>
    /// resources.gain_fanfare_floor (F-A3): a permanent constellation grant.
    ///
    /// Raises floor, cap AND current together, in that order -- the cap must
    /// already carry the new headroom before the current value is clamped
    /// against it, or the grant would be silently truncated at the old
    /// ceiling. Mirrors the sim exactly:
    /// <code>
    ///   p.fanfare_floor += n
    ///   p.fanfare_cap   += n
    ///   p.fanfare        = min(p.fanfare_cap, p.fanfare + n)
    /// </code>
    ///
    /// Inert for anyone without the resource, so a generated Furina card that
    /// somehow reaches another character grants them nothing.
    /// </summary>
    public static void GainFanfareFloor(Creature creature, int amount)
    {
        if (amount <= 0 || !IsFurina(creature)) return;
        var floor = FanfareFloorFor(creature);
        var capBonus = FanfareCapBonusFor(creature);
        var resource = FanfareResourceFor(creature);
        if (floor == null || capBonus == null || resource == null) return;
        var before = resource.Amount;
        floor.ModifyAmount(amount);
        capBonus.ModifyAmount(amount);
        resource.Amount = Math.Min(FanfareCap(creature), resource.Amount + amount);
        NoteFanfareChanged(creature, before, resource.Amount);
    }

    /// <summary>
    /// resources.decay_fanfare (F-A1): the meter fades each turn, never below
    /// the floor. Returns how much fell, for the parity trace.
    ///
    /// This is the load-bearing half of the read-only rework: without it the
    /// pool sits pinned at its ceiling and every card that "scales with
    /// Fanfare" is a constant wearing a meter. It is also precisely what the
    /// 2026-07-25 playtest was reporting when it said "fanfare still capped".
    ///
    /// PROPORTIONAL, ruled 20% by [USER] 2026-07-24 on measurement, reversing
    /// the plan's flat-over-proportional direction: a flat subtraction is one
    /// number for every meter level, so it barely dents a full meter while
    /// driving a low one to zero. Proportional is asymptotic and never empties
    /// the pool, so it beats flat at BOTH tails at once.
    ///
    /// Always removes at least 1 while above the floor, so a small meter
    /// cannot stall at a value that rounds down to nothing.
    /// </summary>
    public static int DecayFanfare(Creature creature)
    {
        if (!IsFurina(creature)) return 0;
        var resource = FanfareResourceFor(creature);
        if (resource == null) return 0;
        var floor = FanfareFloor(creature);
        var before = resource.Amount;
        if (before <= floor) return 0;      // already resting on its baseline
        var fall = Math.Max(
            1,
            (int)Math.Round(
                before * FurinaResourceConstants.FanfareDecayFraction,
                MidpointRounding.ToEven));
        resource.Amount = Math.Max(floor, before - fall);
        NoteFanfareChanged(creature, before, resource.Amount);
        return before - resource.Amount;
    }

    /// <summary>
    /// Fill the buffer. Prints NO Fanfare (Track A, RULED 2026-07-28) --
    /// Fanfare prints when Encore goes DOWN, never when it goes up. Mirrors
    /// resources.gain_encore, which likewise lost its GainFanfare call.
    /// </summary>
    /// <summary>
    /// The Hyperbeam settle (Fanfare rework Track C.2, 2026-07-28), mirroring
    /// resources.drop_fanfare_to_floor. Fanfare falls to its floor, then the
    /// FLOOR falls by <paramref name="floorDrop"/>. Returns what the meter
    /// fell by, for the parity trace.
    ///
    /// THE FLOOR MAY GO NEGATIVE, and that is RULED rather than tolerated: a
    /// negative floor is a hole the player climbs out of with activity, decay
    /// still clamps to it, and generation counts against the debt.
    ///
    /// READERS CLAMP AT ZERO -- see <see cref="ReadableFanfare"/>, which is
    /// the single chokepoint every consumer goes through so "effects shut
    /// off, they do not invert" is one fact in one place. PROPOSED semantics,
    /// flagged for review; the harsher StS-style inversion is a one-line flip
    /// there, exactly as it is in the sim.
    ///
    /// The cap is deliberately NOT lowered: the floor falling is the price,
    /// and a falling ceiling would make the card quietly worse the second
    /// time it is played in a combat, which is a different card.
    ///
    /// FanfareFloorResource is a BasicCustomResource whose Amount is a plain
    /// int, so ModifyAmount by a negative delta is the whole implementation;
    /// nothing here needs to defend a zero floor that the design does not
    /// want defended.
    /// </summary>
    public static int DropFanfareToFloor(Creature creature, int floorDrop)
    {
        if (!IsFurina(creature)) return 0;
        var floor = FanfareFloorFor(creature);
        var resource = FanfareResourceFor(creature);
        if (floor == null || resource == null) return 0;
        var before = resource.Amount;
        floor.ModifyAmount(-floorDrop);
        resource.Amount = Math.Min(before, floor.Amount);
        NoteFanfareChanged(creature, before, resource.Amount);
        return before - resource.Amount;
    }

    /// <summary>
    /// What a Fanfare READER sees: the meter, clamped at zero. Mirrors
    /// resources.readable. Every reader goes through here so the Track C.2
    /// negative-floor semantics live in one place.
    /// </summary>
    public static int ReadableFanfare(Creature creature) =>
        Math.Max(0, Fanfare(creature));

    public static void GainEncore(Creature creature, int amount)
    {
        if (amount <= 0) return;
        var resource = EncoreResourceFor(creature);
        if (resource == null) return;
        resource.ModifyAmount(amount);
        Vfx.GaugeBridge.Refresh(creature);
        // Encore's display moved to the Salon stage ribbon (animation sprint 2,
        // D3). Funnels unchanged -- only the surface it draws on.
        Vfx.SalonVisualsBridge.Refresh(creature);
    }

    public static void GainBurst(Creature creature, int amount)
    {
        if (amount <= 0 || !IsFurina(creature)) return;
        BurstResourceFor(creature)?.ModifyAmount(amount);
    }

    /// <summary>
    /// Spend available Encore without overdraw and return the amount moved.
    /// Deliberate spends create Fanfare; damage absorption uses a separate
    /// method because the sim does not classify absorption as Encore activity.
    /// </summary>
    public static int SpendEncore(Creature creature, int amount)
    {
        if (amount <= 0) return 0;
        var resource = EncoreResourceFor(creature);
        if (resource == null) return 0;
        var spent = Math.Min(resource.Amount, amount);
        if (spent <= 0) return 0;
        resource.ModifyAmount(-spent);
        Vfx.GaugeBridge.Refresh(creature);
        // Encore's display moved to the Salon stage ribbon (animation sprint 2,
        // D3). Funnels unchanged -- only the surface it draws on.
        Vfx.SalonVisualsBridge.Refresh(creature);
        // RETIRED UNDER THE REFRAME'S METER LEG (packet §4.1, leg 2 of 4):
        // only a member PERFORMING mints Fanfare, so a deliberate Encore spend
        // pays nothing. Burst is untouched -- the reframe retires the FANFARE
        // legs and says nothing about the Burst particle. Inert with the arm
        // off; mirrors tier0 `resources.spend_encore`, whose Fanfare limb the
        // slice's `test_the_shipped_generation_legs_mint_nothing` empties.
        if (!ReframeRetiresTheShippedMintLegs(creature))
        {
            GainFanfare(
                creature, spent * FurinaResourceConstants.FanfarePerEncoreSpent);
        }
        GainBurst(
            creature, spent * FurinaResourceConstants.BurstPerEncoreSpent);
        SpotlightSystem.OnEncoreSpent(creature);
        // The Gallery Stirs (R85). Records the first-spend window here and
        // defers the draw itself: this method is synchronous and holds no
        // PlayerChoiceContext. See CurtainCallHooks.NoteEncoreSpent.
        CurtainCallHooks.NoteEncoreSpent(creature);
        return spent;
    }

    /// <summary>
    /// The spend_encore op: drain what is available, then pay the shortfall
    /// as true HP loss. The HP-loss hook creates Fanfare for the shortfall.
    /// </summary>
    public static async Task SpendEncoreOrHp(
        PlayerChoiceContext choiceContext, Creature creature, int amount,
        CardModel cardSource, CardPlay? cardPlay = null)
    {
        var spent = SpendEncore(creature, amount);
        var shortfall = amount - spent;
        if (shortfall <= 0) return;
        await CreatureCmd.Damage(
            choiceContext, creature, shortfall,
            ValueProp.Unblockable | ValueProp.Unpowered, cardSource, cardPlay);
    }

    /// <summary>
    /// Damage remaining after Block may consume Encore before HP. True HP
    /// costs carry Unblockable and never enter this path.
    ///
    /// PRINTS FANFARE since Track A (RULED 2026-07-28). Absorption is the
    /// third Encore reduction path and was the only one that paid nothing --
    /// an asymmetry, not a rule: absorbed Encore is deferred Block that will
    /// never block a future hit, so cashing it is a real cost.
    ///
    /// Together with <see cref="AfterCurrentHpChanged"/> this makes the whole
    /// rule one line: every point of damage past Block prints exactly 1
    /// Fanfare, through here if the buffer eats it and through HP loss if HP
    /// does. Mirrors resources.absorb_into_encore.
    /// </summary>
    public static decimal AbsorbDamage(Creature creature, decimal amount)
    {
        if (amount <= 0m) return 0m;
        var resource = EncoreResourceFor(creature);
        if (resource == null || resource.Amount <= 0) return amount;
        var absorbed = Math.Min(resource.Amount, (int)Math.Ceiling(amount));
        resource.ModifyAmount(-absorbed);
        Vfx.GaugeBridge.Refresh(creature);
        // Encore's display moved to the Salon stage ribbon (animation sprint 2,
        // D3). Funnels unchanged -- only the surface it draws on.
        Vfx.SalonVisualsBridge.Refresh(creature);
        // RETIRED UNDER THE REFRAME'S METER LEG (packet §4.1, leg 3 of 4). The
        // ABSORPTION still happens -- the buffer still eats the hit, which is
        // what the buffer is for; what stops is the Fanfare it printed. Inert
        // with the arm off; mirrors tier0 `resources.absorb_into_encore`.
        if (!ReframeRetiresTheShippedMintLegs(creature))
        {
            GainFanfare(
                creature,
                absorbed * FurinaResourceConstants.FanfarePerEncoreAbsorbed);
        }
        return Math.Max(0m, amount - absorbed);
    }

    /// <summary>
    /// The **Fanfare Cap +X** keyword: headroom only, nothing granted.
    /// Mirrors resources.raise_fanfare_cap and the sim's op of the same name.
    ///
    /// UN-RETIRED by the Fanfare rework (2026-07-28, Track B, RULED). It died
    /// with the kickoff §4 uncapper clause because a ceiling nobody reached
    /// was worth nothing; it returns for a different job, as the SMALL half
    /// of the keyword pair -- what a common or uncommon Power prints instead
    /// of the 5 free floor points it used to receive silently.
    ///
    /// The old note said "do NOT reintroduce it on a sheet without reopening
    /// the ruling." The ruling was reopened, on 2026-07-28, and this is the
    /// reintroduction.
    ///
    /// STATED PLAINLY: the cap has been a non-binding safety rail since F-A5
    /// and read-at-cap measured under 1% in every arm of the pilot-gap
    /// battery, so a card printing only "Fanfare Cap +X" is close to inert at
    /// current constants. Recorded so a flat result off these cards reads as
    /// the measurement it is, not as a wiring bug.
    /// </summary>
    public static void RaiseFanfareCap(Creature creature, int amount)
    {
        if (amount <= 0 || !IsFurina(creature)) return;
        FanfareCapBonusFor(creature)?.ModifyAmount(amount);
    }

    /// <summary>
    /// Resource values are canonical; these powers are the ambient in-combat
    /// display, because BaseLib only renders custom resources on card costs.
    ///
    /// BADGE DIET (animation sprint 2, Track E1). Her strip failed the
    /// 2026-07-24 legibility pass: too many badges, all wearing Klee-register
    /// icons. The rule applied is the Burst-badge precedent from sprint 1 —
    /// a meter that gains an AMBIENT home loses its badge, because two
    /// surfaces for one number is what made the strip unreadable:
    ///
    ///   Encore  -> RETIRED. Ambient home: the Salon stage ribbon (D3).
    ///   Burst   -> RETIRED. Ambient home: the overhead gauge (C1).
    ///   Fanfare -> KEPT. It has no ambient surface, and the parallel kit
    ///              redesign is turning it into a read-only momentum stat,
    ///              which makes a badge the RIGHT home for it rather than a
    ///              consolation prize.
    ///
    /// Three badges become one. Both retired classes stay registered below for
    /// save compatibility with mid-combat saves written before the retirement.
    /// </summary>
    public static async Task SyncMeters(
        PlayerChoiceContext choiceContext, Creature creature,
        CardModel? cardSource = null)
    {
        if (!IsFurina(creature)) return;
        await SyncMeter<FanfareMeterPower>(
            choiceContext, creature, Fanfare(creature), cardSource);
        // Salon stage sync (Track D): every meter-sync moment is also a
        // dry-state moment, and the stage reads composition + Encore here.
        // The member tooltip's live cap rides the same moment, which is what
        // makes a Casting Call raise visible as soon as the card resolves.
        SalonMemberPower.SyncSlotsDisplay(creature);
        Vfx.SalonVisualsBridge.Refresh(creature);
        // Burst's gauge refresh used to ride the badge apply; now it is
        // explicit, so the overhead meter still tracks every sync moment.
        Vfx.GaugeBridge.Refresh(creature);
    }

    private static async Task SyncMeter<T>(
        PlayerChoiceContext choiceContext, Creature creature, int target,
        CardModel? cardSource)
        where T : PowerModel
    {
        var current = creature.Powers.OfType<T>().FirstOrDefault()?.Amount ?? 0;
        var delta = target - current;
        if (delta == 0) return;
        await PowerCmd.Apply<T>(
            choiceContext, creature, delta,
            applier: creature, cardSource: cardSource);
    }
}

/// <summary>
/// Global hook bridge for phases that do not carry a PlayerChoiceContext:
/// early Encore costs, post-Block Encore absorption, and true HP-loss
/// Fanfare. The model is registered exactly once through ModHelper.
/// </summary>
public sealed class FurinaResourceHooks : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static FurinaResourceHooks? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<FurinaResourceHooks>(
            ModelDb.GetId<FurinaResourceHooks>());
        yield return _instance;
    }

    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        if (!cardPlay.IsFirstInSeries) return Task.CompletedTask;
        // SIM ORDER (combat.py play_card), corrected EB-19/M8. The three
        // lines below used to run drain -> skill-tag -> cost under a comment
        // asserting that WAS the sim's order. It is the reverse of it. The
        // sim spends the Encore cost line first, at :236-241, immediately
        // after the energy debit and well before resolution; the requires-full
        // Burst drain (`p.burst_energy = 0`) is at :293-295 and the skill-tag
        // bonus at :296-297, both at the far end of the same function.
        //
        // LATENT at the time of the fix -- no sheet card carries an
        // `encore_cost` AND `requires: burst_energy_full`, so no play today
        // reaches both lines. Fixed anyway because the trigger for it becoming
        // reachable is a SHEET edit, which is not a place anyone would think
        // to check a C# hook's statement order. The two orders differ for
        // exactly that card: the drain zeroes Burst, and an Encore spend can
        // print Fanfare and feed Burst back (FurinaResources.SpendEncore), so
        // drain-then-spend leaves Burst the spend's income where the sim
        // leaves it zero.
        //
        // An OWNERLESS play is a real state: autoplay and token paths hand a
        // card to this broadcast with no Player attached. This hook fires for
        // every card every player plays, and it runs inside CombatManager's
        // async continuation, where an NRE is not an exception the player ever
        // sees -- it is a black screen. DrainOnPlay self-guards, which is why
        // it is the one line that still runs for an ownerless card.
        var card = cardPlay.Card;
        if (card?.Owner?.Creature is not { } owner)
        {
            // The drain self-guards and is the only one of the four lines
            // that needs no owner; the other three do, so an ownerless play
            // ends here exactly as it did before the reorder.
            FurinaBurstResource.DrainOnPlay(cardPlay.Card);
            return Task.CompletedTask;
        }
        var cost = CustomResources<EncoreResource>.Cost(card)
            ?.GetAmountToSpend() ?? 0;
        if (cost > 0)
        {
            FurinaResources.SpendEncore(owner, cost);
        }
        FurinaBurstResource.DrainOnPlay(card);
        if (card is ISkillTagCard && FurinaResources.IsFurina(owner))
        {
            FurinaResources.GainBurst(
                owner,
                FurinaResourceConstants.BurstPerSkillTag);
        }
        SpotlightSystem.NotePlay(cardPlay);
        return Task.CompletedTask;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await SpotlightSystem.ResolvePendingDraw(choiceContext, cardPlay);
        // Two things used to live here and both are gone.
        //
        // The Fanfare COST settle: deleted by G-A1: Fanfare is read-only and
        // `fanfare_cost` has no meaning on any sheet.
        //
        // The by-rarity POWER FLOOR GRANT: deleted by the Fanfare rework
        // (2026-07-28, Track B, RULED), mirroring the deleted block in the
        // sim's combat._finish_play. Playing a Power silently raised floor,
        // cap and current by 5 (rares 8) -- a mechanic worth ~4% of her power
        // that appeared on no card and in no tooltip. Powers now grant
        // exactly what they print, via the "Fanfare Cap +X" and "Fanfare +X"
        // keywords, and there is deliberately no card-type branch left in
        // this method.
        // Quick Change (R85) counts this play; the flush resolves any draw an
        // Encore spend deferred during it (the cost settle runs in
        // BeforeCardPlayed, which has no context of its own).
        await CurtainCallHooks.NoteCardPlayed(choiceContext, cardPlay);
        // Owner-guarded for the same reason BeforeCardPlayed is: an ownerless
        // autoplay/token card reaching these four calls throws inside
        // CombatManager's continuation, and that soft-locks the run.
        // NoteCardPlayed above takes the same guard itself.
        var player = cardPlay.Card?.Owner;
        if (player?.Creature is not { } owner) return;
        await CurtainCallHooks.FlushPendingDraws(choiceContext, owner);
#if PROTOTYPE_CARDS
        // FURINA REFRAME (§4.3, `F3` (1) / `F4` (1)): a Companion play makes
        // the FRONT Salon member perform, then rotates it to the back.
        //
        // BESIDE KLEE'S MINT AND GATED THE SAME WAY, for the same two reasons
        // (see `KleeCompanionSpark`): once per PLAY, because
        // `IsFirstInSeries` is the phase that means "once per play_card call"
        // and a replay is one card resolved twice; and AFTER a resolution has
        // run, which is what this broadcast is. The sim gates the identical
        // call on `replay_index == 0 and card.is_companion` inside
        // `combat._finish_play` and puts Klee's mint on the very next line.
        //
        // PLACED BEFORE THE TWO FLUSHES BELOW so the performance's Block and
        // its Fanfare mint settle inside the play that caused them rather than
        // waiting for the next one. Inert unless the arm's MANUAL leg is on,
        // and inert for every other character.
        if (cardPlay.IsFirstInSeries)
        {
            await SalonMemberPower.CompanionPlayTrigger(
                choiceContext, owner, cardPlay.Card);
        }
#endif
        // A7: the play's Encore spend, Center Stage credit and floor grant all
        // moved the meter from BeforeCardPlayed, which has no context of its
        // own. Settling here puts the Block on the board before the enemy can
        // swing, which is where the sim puts it.
        await FurinaResources.FlushFanfareDeltaBlock(choiceContext, owner);
        await FurinaResources.SyncMeters(
            choiceContext, owner, cardPlay.Card);
        await FurinaKitGrant.GrantIfCharged(choiceContext, player);
    }

    /// <summary>
    /// Fanfare decay, at the TRUE TOP of the player turn (F-A1).
    ///
    /// Site chosen to match the sim, which applies decay before the block
    /// clear, the draw, Salon upkeep and every other turn-start generator.
    /// Order is a design choice, not an accident: decay eats what was CARRIED
    /// OVER, and then this turn's activity builds on the remainder. Applying
    /// it after turn-start generation would tax income instead of inventory.
    ///
    /// BeforeSideTurnStart is the earliest hook available and the only
    /// turn-start hook carrying a PlayerChoiceContext. CombatManager awaits it
    /// to completion, THEN AfterBlockCleared, THEN AfterSideTurnStart -- so
    /// this is guaranteed ahead of Salon upkeep (AfterPlayerTurnStart) and the
    /// aura tick, without any intra-broadcast ordering assumption.
    ///
    /// The one residual ordering caveat, recorded rather than hidden: bomb
    /// detonation also rides BeforeSideTurnStart, and order BETWEEN models in
    /// a single broadcast is not guaranteed. A bomb that damages Furina mints
    /// Fanfare from HP loss, so in the rare Klee-bombs-Furina co-op case the
    /// decay may see that income or not. The sim decays strictly first.
    ///
    /// PlayerCombatState.TurnNumber is per-PLAYER and 1-based (its own doc
    /// comment: "This starts at 1, so it should never be 0"), which is exactly
    /// the sim's `state.turn` and exactly what co-op wants -- Furina decays on
    /// HER second turn, not on the table's second turn. The `<= 1` guard is
    /// the same idiom a dozen vanilla powers use for "not on the first turn".
    /// </summary>
    public override async Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side != CombatSide.Player) return;
        // Salon's static company map has no other clearing path: its own
        // stale-list check empties a list but never drops the key, so a run's
        // worth of dead combats accumulated (each pinning a whole combat's
        // Creature). Swept once per player turn -- the same lifecycle site
        // CurtainCallHooks.Purge rides, one line below.
        SalonMemberPower.PurgeCompany();
        foreach (var creature in participants)
        {
            // Curtain Call's per-turn windows reset BEFORE the decay guard:
            // the guard skips turn 1, but the windows must be clear on every
            // turn including the first. This broadcast is strictly earlier
            // than AfterPlayerTurnStart, where Salon upkeep spends Encore --
            // so the Gallery Stirs latch is guaranteed clear before anything
            // can set it. See CurtainCallHooks.ResetTurn.
            if (FurinaResources.IsFurina(creature))
            {
                CurtainCallHooks.ResetTurn(creature);
            }
            if (creature.Player is not { } player
                || !FurinaResources.IsFurina(creature)
                || player.PlayerCombatState is not { } playerCombatState
                || playerCombatState.TurnNumber <= 1)
            {
                continue;
            }
            FurinaResources.DecayFanfare(creature);
            // A7, and the SITE IS LOAD-BEARING: settle the decay's Block HERE,
            // inside BeforeSideTurnStart, because the sim grants it here too --
            // combat._player_turn calls decay_fanfare at line 424 and clears
            // Block at line 430, six lines later. AfterBlockCleared runs after
            // this broadcast, so both engines wipe the decay grant on any turn
            // without Barricade, and they wipe it identically.
            //
            // Moving this flush to AfterPlayerTurnStart would look like a fix
            // and would in fact be a C#-only buff worth ~1 Block/turn that the
            // sim never pays and no measurement has ever priced. If the decay
            // half is supposed to survive, that is a RULING about the sim's
            // ordering first; see the sprint log's A7 finding.
            await FurinaResources.FlushFanfareDeltaBlock(
                choiceContext, creature);
            await FurinaResources.SyncMeters(choiceContext, creature);
        }
    }

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (FurinaResources.IsFurina(player.Creature))
        {
            SpotlightSystem.ResetTurn(player.Creature);
            // Salon upkeep spends Encore in this same broadcast, so flush
            // here as well as after card plays -- a turn-start spend must not
            // wait for the player to play something before it draws.
            await CurtainCallHooks.FlushPendingDraws(
                choiceContext, player.Creature);
            // Salon upkeep spends Encore in this same broadcast, and a spend
            // mints Fanfare -- so this settles UPKEEP's movement, not decay's.
            // Decay already settled (and was already cleared) one broadcast
            // earlier; the counter is taken and cleared, so this cannot pay it
            // a second time.
            await FurinaResources.FlushFanfareDeltaBlock(
                choiceContext, player.Creature);
            await FurinaResources.SyncMeters(
                choiceContext, player.Creature);
            await FurinaKitGrant.GrantIfCharged(
                choiceContext, player);
        }
    }

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        foreach (var creature in participants)
        {
            if (creature.Player is not { } player
                || !FurinaResources.IsFurina(creature))
            {
                continue;
            }
            // Last chance in the turn: anything an end-of-turn spend deferred
            // resolves here rather than stranding into the next turn.
            await CurtainCallHooks.FlushPendingDraws(choiceContext, creature);
            await FurinaResources.FlushFanfareDeltaBlock(
                choiceContext, creature);
            await FurinaResources.SyncMeters(choiceContext, creature);
            await FurinaKitGrant.GrantIfCharged(choiceContext, player);
        }
    }

    /// <summary>
    /// The this-turn Spotlight windows close here (EB-19/races-b).
    ///
    /// AfterSideTurnEnd is StS2 site M, which the sim names as the site of
    /// `powers.on_turn_end` -- the function that pops powers.EXPIRING, i.e.
    /// `spotlight_mult_bonus_turn`. SpotlightSpendBoostResource is that
    /// power's C# twin, so it expires here rather than in the turn-start
    /// broadcast that mints it. The two POWER-shaped members of the same
    /// tuple (SpotlightMultBonusTurnPower, SpotlightFlatDamageTurnPower)
    /// already self-expire in this broadcast; this puts the resource-shaped
    /// third member alongside them.
    ///
    /// No co-tenant of AfterSideTurnEnd reads the Spotlight multiplier: it is
    /// a printed-value modifier for CARD plays, and no card is played from a
    /// turn-end broadcast.
    /// </summary>
    public override Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return Task.CompletedTask;
        foreach (var creature in participants)
        {
            if (!FurinaResources.IsFurina(creature)) continue;
            SpotlightSystem.ClearSpendBoost(creature);
        }
        return Task.CompletedTask;
    }

    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target,
        DamageResult result, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (!FurinaResources.IsFurina(target)) return;
        // A7's ENEMY-TURN settle, and the one that actually matters for a
        // defensive power. Absorption and true HP loss both mint Fanfare from
        // synchronous hooks (ModifyHpLostBeforeOsty, AfterCurrentHpChanged);
        // this hook fires per damage instance, so the Block is on the board
        // before the NEXT hit of the same turn -- which is exactly what the
        // sim does, where the grant lands mid-resolution and the hit that
        // caused it has already been paid for.
        await FurinaResources.FlushFanfareDeltaBlock(choiceContext, target);
        await FurinaResources.SyncMeters(
            choiceContext, target, cardSource);
        await FurinaKitGrant.GrantIfCharged(
            choiceContext, target.Player);
    }

    public override decimal ModifyHpLostBeforeOsty(
        Creature target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (!FurinaResources.IsFurina(target)
            || (props & ValueProp.Unblockable) != 0)
        {
            return amount;
        }
        return FurinaResources.AbsorbDamage(target, amount);
    }

    public override Task AfterCurrentHpChanged(Creature creature, decimal delta)
    {
        if (delta < 0m && FurinaResources.IsFurina(creature))
        {
            // Ceiling, matching AbsorbDamage's sibling cast. The stated rule
            // is "every point of damage past Block prints exactly 1 Fanfare",
            // and the two halves of that rule must round the same way -- a
            // truncating (int) cast made a fractional HP loss print nothing
            // through this half while the absorption half paid for it. One
            // local, so the mint and Slip Backstage's predicate can never
            // disagree about how much she lost.
            var lost = (int)Math.Ceiling(-delta);
            // RETIRED UNDER THE REFRAME'S METER LEG (packet §4.1, leg 1 of 4),
            // and with it the shipped invariant "every point of damage past
            // Block prints exactly 1 Fanfare". Slip Backstage's predicate on
            // the line below is NOT retired: it reads "she lost HP", which is
            // still true. Inert with the arm off; mirrors tier0
            // `resources.note_player_hp_loss`.
            if (!FurinaResources.ReframeRetiresTheShippedMintLegs(creature))
            {
                FurinaResources.GainFanfare(
                    creature, lost * FurinaResourceConstants.FanfarePerHpLost);
            }
            // Slip Backstage's predicate reads off the same funnel, so
            // "she lost HP" is one fact rather than two trackers.
            CurtainCallHooks.NoteHpLost(creature, lost);
        }
        return Task.CompletedTask;
    }
}

/// <summary>
/// RETIRED as a display 2026-07-24 (animation sprint 2, E1) — Encore's ambient
/// home is the Salon stage ribbon. Nothing applies this power any more. The
/// class stays registered so a mid-combat save written before the retirement
/// still loads; same pattern as Klee's BurstMeterPower.
/// </summary>
public sealed class EncoreMeterPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Encore"),
        ("description",
            "After Block, Encore absorbs incoming damage before HP. "
          + "Losing it — spent, absorbed or paid as upkeep — creates Fanfare; "
          + "gaining it does not."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
}

public sealed class FanfareMeterPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Fanfare"),
        // Player-facing rule, one line per the decay ruling's own legibility
        // argument. The CAP is deliberately NOT mentioned: F-A5 demoted it to
        // a safety rail that never binds under decay, and naming a ceiling
        // nobody reaches is what made the old tooltip misleading.
        // SINGLE-LEG wording (Track A). "Encore activity" was true of the old
        // two-leg rule and is now actively misleading -- gaining Encore
        // prints nothing. The player-facing rule is one clause: Encore going
        // DOWN pays, by any of the three routes.
        //
        // "the baseline your cards have built", not "your Powers": Track B
        // deleted the by-rarity automatic, so the baseline is whatever the
        // "Fanfare +X" faces in the deck printed, and a Power that prints
        // nothing builds nothing.
        ("description",
            "Generated by losing HP, and by spending, absorbing or paying out "
          + "[gold]Encore[/gold] — and by Center Stage plays. Cards read it; "
          + "nothing spends it. It fades by 20% at the start of each of your "
          + "turns, never below the baseline your cards have built."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// RETIRED as a display 2026-07-24 (animation sprint 2, E1) — Burst's ambient
/// home is the standardised overhead gauge. Kept registered for save
/// compatibility, exactly as <see cref="EncoreMeterPower"/> is.
/// </summary>
public sealed class FurinaBurstMeterPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Burst Energy"),
        ("description",
            // EB-89: every rate here is interpolated from the constant
            // the resolution actually reads.
            $"Skill cards and Reactions grant "
          + $"{FurinaResourceConstants.BurstPerSkillTag}; Salon attacks "
          + $"grant {FurinaResourceConstants.BurstPerSalonTick}; "
          + "deliberately spent Encore grants "
          + $"{FurinaResourceConstants.BurstPerEncoreSpent} per point. At "
          + $"{FurinaResourceConstants.BurstMax}, "
          + "Let the People Rejoice is added to your hand."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
}

public static class FurinaKitGrant
{
    public static async Task GrantIfCharged(
        PlayerChoiceContext choiceContext, Player? owner)
    {
        if (owner?.Character is not IFurinaCharacter) return;
        var playerCombatState = owner.PlayerCombatState;
        var combatState = owner.Creature.CombatState;
        if (playerCombatState == null || combatState == null) return;

        var resource =
            CustomResources<FurinaBurstResource>.Get(playerCombatState);
        if (resource.Amount < FurinaResourceConstants.BurstMax) return;

        var hand = CardPile.Get(PileType.Hand, owner);
        if (hand == null
            || hand.Cards.Any(card => card is LetThePeopleRejoice)
            || hand.Cards.Count >= CardPile.MaxCardsInHand)
        {
            return;
        }

        var burst = combatState.CreateCard<LetThePeopleRejoice>(owner);
        await CardPileCmd.AddGeneratedCardToCombat(
            burst, PileType.Hand, owner);
    }
}

/// <summary>
/// The Encore engine behind All the World's a Stage (Furina's Ancient card):
/// Amount Encore at the start of every player turn, routed through
/// FurinaResources.GainEncore so the Fanfare mint, gauge refresh and salon
/// dry-badge all behave exactly like any other gain. The explicit SyncMeters
/// keeps the status-strip counters current in the same beat -- hook order
/// between powers and FurinaResourceHooks is not guaranteed.
/// </summary>
public sealed class EncorePerTurnPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "All the World's a Stage"),
        ("description",
            "At the start of your turn, gain {Amount} [gold]Encore[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// STAGED INTO BeforeSideTurnStart, NOT AfterPlayerTurnStart. THIS IS THE
    /// EB-2 FIX and it must not be tidied back.
    ///
    /// The race: SalonMemberPower's upkeep SPENDS Encore from
    /// AfterPlayerTurnStart, and this power MINTS it. Two same-side co-tenants
    /// of one broadcast have no guaranteed relative order, so the Salon either
    /// ran on this turn's income or on last turn's leftovers depending on
    /// listener iteration -- a nondeterministic tick rate that fixed-seed
    /// parity cannot catch.
    ///
    /// The sim states which way it falls: `effects.player_turn_start_triggers`
    /// places `encore_per_turn` ABOVE `salon_tick` (and above the whole
    /// per-turn income group below it) so that the card's printed "at the
    /// start of your turn" funds the SAME turn's member ticks. Pinned at the
    /// site by tier0/tests/test_eb30m_ancients.py::
    /// test_ancient_income_is_sourced_above_the_salon_upkeep, with the
    /// behavioural half in test_the_stage_funds_the_same_turn_s_salon_ticks.
    ///
    /// BeforeSideTurnStart is the strictly earlier broadcast (see
    /// TURN_START_BROADCAST_ORDER in
    /// tier0/tests/test_reaction_phase_parity.py -- AfterSideTurnStart is the
    /// LAST turn-start broadcast, not the first, so "earlier" is this one and
    /// only this one). The same staging idiom CurtainCallHooks.ResetTurn and
    /// EtherealSpotlightRelic already use, for the same reason.
    ///
    /// PRE-DRAW AND PRE-BLOCK-CLEAR is inert for this power: GainEncore prints
    /// no Fanfare (Track A ruling -- Fanfare prints on the way DOWN), grants
    /// no Block and reads no hand, so no BeforeSideTurnStart co-tenant sees a
    /// resource it touches. FurinaResourceHooks' decay + delta-block settle in
    /// this same broadcast is therefore unaffected either way.
    /// </summary>
    public override async Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side != CombatSide.Player) return;
        if (Owner?.Player == null) return;
        FurinaResources.GainEncore(Owner, (int)Amount);
        await FurinaResources.SyncMeters(choiceContext, Owner);
    }
}

/// <summary>
/// "Attacks deal +Amount per 10 Fanfare". Fanfare is read per hit, so
/// spending or gaining it changes later attacks immediately.
///
/// The two-stack cap was dropped 2026-07-24 (uncap-all ruling): +1/copy per
/// 10 Fanfare is additive in copies, so uncapping just lets dupes stack like
/// any base-StS Power. See <see cref="SpotlightPower"/> for the A/B.
/// </summary>
public sealed class FanfareAttackPer10Power : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Rising Ovation"),
        ("description",
            "Your Attacks deal {Amount} more damage per 10 [gold]Fanfare[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        return Amount * (FurinaResources.ReadableFanfare(Owner) / 10);
    }
}

/// <summary>
/// Unheard Confession (A7, RULED 2026-07-28): gain Amount Block whenever
/// Fanfare CHANGES AMOUNT, in either direction.
///
/// Mirrors the sim's `fanfare_delta_block` power, read by
/// resources.note_fanfare_change. The power itself is deliberately a pure
/// marker with no hooks of its own: the trigger cannot live here, because the
/// four things that move the meter are static methods on FurinaResources and
/// none of them is a broadcast a PowerModel can subscribe to. FurinaResources
/// asks this class for its Amount instead -- see NoteFanfareChanged.
///
/// PAYS ON THE WAY DOWN, WITH ONE MEASURED CAVEAT the sheet does not state:
/// decay is the only downward mover, it fires at the top of the player turn,
/// and BOTH engines clear Block immediately afterward. So the downward half
/// pays into a bucket that is emptied a moment later on every turn without
/// Barricade. That is the sim's behaviour, faithfully reproduced here rather
/// than quietly improved; it is written up in the 2026-07-29 sprint log for
/// red-pen because changing it is a ruling about the sim's turn order.
/// </summary>
public sealed class FanfareDeltaBlockPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Unheard Confession"),
        ("description",
            "Whenever your [gold]Fanfare[/gold] changes amount, gain "
          + "{Amount} [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static int AmountFor(Creature creature) =>
        creature.Powers.OfType<FanfareDeltaBlockPower>()
            .FirstOrDefault()?.Amount ?? 0;
}
