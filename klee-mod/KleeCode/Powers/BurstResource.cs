using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Powers;

/// <summary>
/// Burst-energy constants. The sim's particle economy is LAW (R23 note):
/// these mirror tier0/constants.py and tier0/content/characters/klee.yaml
/// verbatim -- never re-derive them C#-side.
/// </summary>
public static class BurstConstants
{
    /// <summary>tier0 constants.py BURST_PER_SKILL_TAG = 5.</summary>
    public const int PerSkillTag = 5;

    /// <summary>tier0 constants.py BURST_PER_REACTION = 5.</summary>
    public const int PerReaction = 5;

    /// <summary>tier0 klee.yaml burst_max: 60.</summary>
    public const int KleeMax = 60;
}

/// <summary>
/// Carried by cards the sheet tags `skill_tag` -- Klee's Elemental-Skill-
/// flavored cards, worth <see cref="BurstConstants.PerSkillTag"/> burst energy
/// when played. Same out-of-band idiom as IElementalCard: the tag has to
/// travel on the card, and first-party precedent inspects cardSource for
/// exactly this kind of marker.
/// </summary>
public interface ISkillTagCard
{
}

/// <summary>
/// Klee's Burst-energy meter (Burst-energy spike, standing plan item 2).
///
/// A BaseLib CustomResource: BaseLib auto-scans the mod assembly at early
/// post-init and registers every concrete CustomResource subclass itself
/// (Activator.CreateInstance -> CustomResources&lt;T&gt;.Register), so -- same
/// lesson as ModelDb and finding 28 -- we only define the class, never
/// register it. Per-player per-combat instances are created lazily by
/// BaseLib's SpireField and PrepForCombat zeroes them, which matches the
/// sim's per-fight state reset.
///
/// Port of tier0's burst economy (engine/combat.py, engine/reactions.py):
///   +5 per skill-tagged card played, BEFORE its effects resolve and once
///     per play regardless of replays (play_card adds the tag bonus ahead of
///     its replay loop -- KleeElementalHooks.BeforeCardPlayed gated on
///     IsFirstInSeries is the matching phase; the game fires card hooks once
///     per replay, so an unguarded hook would double-grant where the sim
///     grants once);
///   +5 per Elemental Reaction, amplifiers included (ReactionEffects.Resolve
///     is the single funnel every reaction passes through, mid-resolution
///     like the sim's resolve_hit);
///   +N from the burst_energy card op (codegen, mid-resolution like the
///     sim's effect loop);
///   accrual is UNCAPPED past 60 (the sim never clamps; the grant check is
///     >=, and casting resets to 0 -- overflow is lost at cast, not at gain).
///
/// The kit half (landed with the kit-grant machinery, standing-plan item):
/// Sparks 'n' Splash carries this resource as a BaseLib CustomResourceCost
/// (SetCanonicalCost 60 -- CanAfford >= 60 gates playability, the sim's
/// requires: burst_energy_full), KitGrant grants the card to hand at a full
/// meter, and the Spend override below drains the WHOLE meter at cast --
/// overflow is lost at cast, never at gain (combat.py: playing the Burst
/// sets burst_energy = 0).
///
/// The badge: BaseLib ships NO ambient on-screen meter (its resource UI is
/// cost-side card visuals only; BasicResourceVisualsHandler is an empty
/// marker), so the meter renders through <see cref="BurstMeterPower"/> on
/// Klee -- the SparkPower display idiom. The resource is canonical; the
/// badge is display. Two writers, one invariant: Gain() moves both together
/// (every context-carrying site), GainPreResolution() moves the resource
/// alone -- BeforeCardPlayed has no PlayerChoiceContext, so the skill-tag
/// bonus lands resource-first and SyncBadge() restores badge == resource in
/// AfterCardPlayed. The badge may lag the resource only WITHIN a single card
/// play, never across plays. Anything that RULES on the meter (the future
/// cast gate included) must read the resource.
/// </summary>
public sealed class KleeBurstResource : BasicCustomResource
{
    public KleeBurstResource() : base("KLEEMOD_BURST")
    {
    }

    /// <summary>
    /// Casting the Burst empties the METER, not just the canonical cost --
    /// sim law (combat.py): `p.burst_energy = 0` on a requires-full play;
    /// overflow past 60 is lost at cast, never clamped at gain. The cost
    /// machinery passes amount = 60 (GetAmountToSpend); this resource's only
    /// spender is the kit card, so the full drain is the rule, not a special
    /// case.
    ///
    /// BASELIB SIGNATURE CHANGE (2026-07-21): the Workshop auto-updated
    /// BaseLib.dll under us and CustomResource.Spend changed shape --
    ///   was: Task       Spend&lt;T&gt;(ICombatState, AbstractModel?, int)
    ///   now: Task&lt;bool&gt; Spend&lt;T&gt;(ICombatState, AbstractModel?, int, bool optional)
    /// The bool return reports whether the spend happened; `optional` makes
    /// an unaffordable spend a no-op returning false instead of a clamped
    /// spend with a warning. We forward `optional` unchanged rather than
    /// hardcoding it, so the caller's intent survives. The forwarded amount
    /// stays `Amount` (not `amount`) -- that IS the whole-meter drain, and
    /// because Amount is never > Amount the new insufficient-funds branch
    /// cannot fire here, so this always reports a true spend. The sim law
    /// above is unchanged by any of it.
    /// </summary>
    public override async Task<bool> Spend<T>(
        MegaCrit.Sts2.Core.Combat.ICombatState combatState,
        AbstractModel? spender, int amount, bool optional)
    {
        return await base.Spend<T>(combatState, spender, Amount, optional);
    }

    /// <summary>
    /// Klee's meter for this combat, or null when no gain should happen.
    /// Gates on the owner being Klee: the sim guards every gain site with
    /// `if p.burst_max`, i.e. characters without a meter gain nothing.
    /// </summary>
    private static KleeBurstResource? Find(Creature player)
    {
        var owner = player.Player;
        if (owner?.Character is not Klee) return null;
        var combatState = owner.PlayerCombatState;
        if (combatState == null) return null;
        return CustomResources<KleeBurstResource>.Get(combatState);
    }

    /// <summary>
    /// The gain path for every context-carrying source (reactions, the
    /// burst_energy op, and future powers) -- mirrors SparkPower.Gain so the
    /// economy stays easy to instrument. Moves resource and badge together.
    /// </summary>
    public static async Task Gain(
        PlayerChoiceContext choiceContext, Creature player, int amount,
        CardModel? cardSource)
    {
        if (amount <= 0) return;
        var resource = Find(player);
        if (resource == null) return;

        resource.ModifyAmount(amount);
        await PowerCmd.Apply<BurstMeterPower>(
            choiceContext, player, amount, applier: player, cardSource: cardSource);
    }

    /// <summary>
    /// The gain path for the skill-tag bonus, which fires in BeforeCardPlayed
    /// where the game hands hooks no PlayerChoiceContext. Resource only; the
    /// paired SyncBadge call in AfterCardPlayed catches the display up.
    /// </summary>
    public static void GainPreResolution(Creature player, int amount)
    {
        if (amount <= 0) return;
        Find(player)?.ModifyAmount(amount);
    }

    /// <summary>
    /// Re-establish badge == resource (sync-to-truth, so it also self-heals
    /// any drift rather than replaying a remembered delta).
    /// </summary>
    public static async Task SyncBadge(
        PlayerChoiceContext choiceContext, Creature player, CardModel? cardSource)
    {
        var resource = Find(player);
        if (resource == null) return;

        var badge = player.Powers.OfType<BurstMeterPower>().FirstOrDefault();
        decimal delta = resource.Amount - (badge?.Amount ?? 0m);
        if (delta == 0m) return;
        await PowerCmd.Apply<BurstMeterPower>(
            choiceContext, player, delta, applier: player, cardSource: cardSource);
    }
}

/// <summary>
/// Display badge for the Burst meter (see KleeBurstResource: BaseLib has no
/// ambient resource UI, so the meter shows the way Sparks do). Amount equals
/// the resource's Amount between card plays; within a skill-tagged play it
/// may lag by the tag bonus until SyncBadge runs in AfterCardPlayed. Rules
/// read the resource, never this.
/// </summary>
public sealed class BurstMeterPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Burst Energy"),
        ("description",
            "Cards with [gold]Elemental Skill[/gold] grant 5 [gold]Burst "
          + "Energy[/gold]; Elemental Reactions grant 5. At 60, [gold]Sparks "
          + "'n' Splash[/gold] is added to your hand; casting it spends ALL "
          + "Burst Energy."),
    };

    public override PowerType Type => PowerType.Buff;

    /// <summary>Counter: energy is spent by casting, never ticked by time.</summary>
    public override PowerStackType StackType => PowerStackType.Counter;
}
