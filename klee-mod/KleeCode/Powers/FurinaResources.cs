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
    public const int FanfarePerEncoreGained = 1;
    public const int FanfarePerEncoreSpent = 1;

    // --- "The Tide Turns" (F-A1/F-A3), ported by G-A1 2026-07-25. Mirrors
    // tier0/constants.py FANFARE_DECAY_FRACTION / FANFARE_FLOOR_PER_POWER*.
    // Fanfare is a READ-ONLY momentum stat: activity generates it, it fades
    // each turn, and permanent constellation grants give it a floor. No card
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

    /// <summary>Floor granted by playing a common/uncommon Power.</summary>
    public const int FanfareFloorPerPower = 5;

    /// <summary>Floor granted by playing a RARE Power. Ancient-rarity Powers
    /// take the common value, matching the sim's `rarity == "rare"` test.
    /// </summary>
    public const int FanfareFloorPerPowerRare = 8;

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
/// BEFORE card effects (combat.py play_card line 180, above the replay loop).
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
/// (retired grammar, no sheet user) stays expressible without a rewrite.
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
        return creature.MaxHp / 2 + (FanfareCapBonusFor(creature)?.Amount ?? 0);
    }

    public static void GainFanfare(Creature creature, int amount)
    {
        if (amount <= 0) return;
        var resource = FanfareResourceFor(creature);
        var cap = FanfareCap(creature);
        if (resource == null || cap <= 0) return;
        resource.Amount = Math.Min(cap, resource.Amount + amount);
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
        floor.ModifyAmount(amount);
        capBonus.ModifyAmount(amount);
        resource.Amount = Math.Min(FanfareCap(creature), resource.Amount + amount);
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
        return before - resource.Amount;
    }

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
        GainFanfare(
            creature, amount * FurinaResourceConstants.FanfarePerEncoreGained);
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
        GainFanfare(
            creature, spent * FurinaResourceConstants.FanfarePerEncoreSpent);
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
        CardModel cardSource)
    {
        var spent = SpendEncore(creature, amount);
        var shortfall = amount - spent;
        if (shortfall <= 0) return;
        await CreatureCmd.Damage(
            choiceContext, creature, shortfall,
            ValueProp.Unblockable | ValueProp.Unpowered, cardSource);
    }

    /// <summary>
    /// Damage remaining after Block may consume Encore before HP. True HP
    /// costs carry Unblockable and never enter this path.
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
        return Math.Max(0m, amount - absorbed);
    }

    /// <summary>
    /// RETIRED GRAMMAR. `raise_fanfare_cap` died with the kickoff §4 uncapper
    /// clause and no card on any sheet carries it -- `gain_fanfare_floor`
    /// replaced it, because raising a ceiling nobody reaches was measured at
    /// +0.2pt to the very archetype named after the stat.
    ///
    /// Kept rather than deleted because the cap is still a real quantity and
    /// this is its only writer; deleting it would leave
    /// <see cref="FanfareCapBonusResource"/> with no way to move except as a
    /// side effect of a floor grant. Do NOT reintroduce it on a sheet without
    /// reopening the ruling.
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
        // Sim order (combat.py play_card): the requires-full drain first,
        // then the skill-tag bonus, then the Encore cost line.
        FurinaBurstResource.DrainOnPlay(cardPlay.Card);
        if (cardPlay.Card is ISkillTagCard
            && FurinaResources.IsFurina(cardPlay.Card.Owner.Creature))
        {
            FurinaResources.GainBurst(
                cardPlay.Card.Owner.Creature,
                FurinaResourceConstants.BurstPerSkillTag);
        }
        var cost = CustomResources<EncoreResource>.Cost(cardPlay.Card)
            ?.GetAmountToSpend() ?? 0;
        if (cost > 0)
        {
            FurinaResources.SpendEncore(cardPlay.Card.Owner.Creature, cost);
        }
        SpotlightSystem.NotePlay(cardPlay);
        return Task.CompletedTask;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await SpotlightSystem.ResolvePendingDraw(choiceContext, cardPlay);
        // The Fanfare COST settle used to live here. Deleted by G-A1: Fanfare
        // is read-only and `fanfare_cost` has no meaning on any sheet.
        //
        // Constellation grant (F-A3), sim site combat.py play_card: playing a
        // POWER permanently raises the Fanfare floor by rarity.
        //
        // AFTER resolution, so a Power that ALSO grants a floor outright does
        // not double-count against its own read. Once per SERIES rather than
        // once per replay -- a Study Buddy'd Power is still one performance
        // the audience remembers, which is the same reason the retired spend
        // sat outside the sim's replay loop.
        if (cardPlay.IsLastInSeries
            && cardPlay.Card.Type == CardType.Power
            && FurinaResources.IsFurina(cardPlay.Card.Owner.Creature))
        {
            FurinaResources.GainFanfareFloor(
                cardPlay.Card.Owner.Creature,
                cardPlay.Card.Rarity == CardRarity.Rare
                    ? FurinaResourceConstants.FanfareFloorPerPowerRare
                    : FurinaResourceConstants.FanfareFloorPerPower);
        }
        // Quick Change (R85) counts this play; the flush resolves any draw an
        // Encore spend deferred during it (the cost settle runs in
        // BeforeCardPlayed, which has no context of its own).
        await CurtainCallHooks.NoteCardPlayed(choiceContext, cardPlay);
        await CurtainCallHooks.FlushPendingDraws(
            choiceContext, cardPlay.Card.Owner.Creature);
        await FurinaResources.SyncMeters(
            choiceContext, cardPlay.Card.Owner.Creature, cardPlay.Card);
        await FurinaKitGrant.GrantIfCharged(
            choiceContext, cardPlay.Card.Owner);
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
            await FurinaResources.SyncMeters(choiceContext, creature);
            await FurinaKitGrant.GrantIfCharged(choiceContext, player);
        }
    }

    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target,
        DamageResult result, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (!FurinaResources.IsFurina(target)) return;
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
            FurinaResources.GainFanfare(
                creature,
                (int)(-delta) * FurinaResourceConstants.FanfarePerHpLost);
            // Slip Backstage's predicate reads off the same funnel, so
            // "she lost HP" is one fact rather than two trackers.
            CurtainCallHooks.NoteHpLost(creature, (int)(-delta));
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
          + "Gaining or deliberately spending it creates Fanfare."),
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
        ("description",
            "Generated by HP loss, Encore activity, and Center Stage plays. "
          + "Cards read it; nothing spends it. It fades by 20% at the start "
          + "of each of your turns, never below the baseline your Powers "
          + "have built."),
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
            "Skill cards and Reactions grant 5; Salon attacks grant 2; "
          + "deliberately spent Encore grants 1 per point. At 70, "
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

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
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
        CardModel? cardSource)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        return Amount * (FurinaResources.Fanfare(Owner) / 10);
    }
}
