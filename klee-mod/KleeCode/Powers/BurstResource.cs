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

    /// <summary>tier0 klee.yaml burst_max: 40.</summary>
    public const int KleeMax = 40;
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
///   accrual is UNCAPPED past 40 (the sim never clamps; the grant check is
///     >=, and casting resets to 0 -- overflow is lost at cast, not at gain).
///
/// The kit half (landed with the kit-grant machinery, standing-plan item):
/// Sparks 'n' Splash carries this resource as a BaseLib CustomResourceCost
/// (SetCanonicalCost 40 -- the CanAfford override below gates playability on
/// the CANONICAL 40, the sim's requires: burst_energy_full), KitGrant grants
/// the card to hand at a full meter, and DrainOnPlay empties the WHOLE meter
/// on the play hook -- overflow is lost at cast, never at gain (combat.py:
/// playing the Burst sets burst_energy = 0). The cost object exists for the
/// gate and the cost visual only; it no longer performs the spend.
///
/// Display: the Track C overhead gauge (Vfx.GaugeBridge) is the meter's only
/// ambient surface. It renders through the <see cref="AmountFor"/> read and
/// the Refresh calls in the mutation funnels below; SyncGauge() in
/// AfterCardPlayed catches the one mutation outside them (the kit card's
/// whole-meter Spend inside the cost machinery). The old status-strip badge
/// (<see cref="BurstMeterPower"/>) was retired as redundant with the gauge --
/// C4 playtest feedback 2026-07-23. Anything that RULES on the meter (the
/// cast gate included) must read the resource.
/// </summary>
public sealed class KleeBurstResource : BasicCustomResource
{
    public KleeBurstResource() : base("KLEEMOD_BURST")
    {
    }

    /// <summary>
    /// The Burst meter is not an energy cost and must not be discounted like
    /// one. BaseLib forwards the game's SetToFreeThisTurn / SetToFreeThisCombat
    /// onto every custom-resource cost unless the resource opts out here
    /// (CustomResources&lt;T&gt;.SetToFreeThis*, gated on this flag). A
    /// "this card is free" effect landing on the kit card would otherwise
    /// zero the meter cost -- see <see cref="DrainOnPlay"/> for why that was
    /// catastrophic rather than merely generous.
    /// </summary>
    public override bool ApplySharedModification => false;

    /// <summary>
    /// The cast gate is `requires: burst_energy_full` (tier0 card_playable):
    /// it reads the CANONICAL 40, never a discounted number.
    ///
    /// BaseLib's default CanAfford compares against the cost AFTER modifiers,
    /// and CustomResourceCost.GetWithModifiers pipes custom costs through
    /// Hook.ModifyEnergyCostInCombat -- the very hook SparkPower uses to zero
    /// attack costs. Any cost reducer in range would otherwise make the Burst
    /// castable on an empty meter. ApplySharedModification closes the
    /// SetToFree half of that exposure; this closes the hook half.
    ///
    /// Falls through to the base comparison for cards with no canonical burst
    /// cost (CanonicalCost returns -1), which is every card but the kit one.
    /// </summary>
    public override bool CanAfford(CardModel card, int cost)
    {
        var canonical = CustomResources<KleeBurstResource>.CanonicalCost(card);
        return canonical < 0 ? base.CanAfford(card, cost) : Amount >= canonical;
    }

    /// <summary>
    /// DELIBERATE NO-OP; the drain lives in <see cref="DrainOnPlay"/>. Same
    /// early-spend idiom EncoreResource already uses, and for a stronger
    /// reason -- see that method.
    /// </summary>
    public override Task<bool> Spend<T>(
        MegaCrit.Sts2.Core.Combat.ICombatState combatState,
        AbstractModel? spender, int amount, bool optional)
    {
        return Task.FromResult(true);
    }

    /// <summary>
    /// Sim law, verbatim (combat.py play_card): `p.burst_energy = 0` on a
    /// requires-full play. Overflow past 40 is lost at CAST, never clamped at
    /// gain, so this zeroes the meter rather than subtracting the cost.
    /// Called from KleeElementalHooks.BeforeCardPlayed -- pre-resolution, and
    /// ahead of the skill-tag bonus, which is exactly where the sim drains
    /// (before the replay loop, before resolve_card).
    ///
    /// WHY IT IS NOT IN THE COST MACHINERY (playtest 2026-07-24, the
    /// infinite-Burst bug). The drain used to ride BaseLib's Spend, which runs
    /// inside CardModel.SpendResources(). Two paths skip or defang that:
    ///   - CardCmd.AutoPlay does NOT call SpendResources. The base game's own
    ///     Vakuu relic has to call it by hand before auto-playing
    ///     (sts2 decompile :377742), so an auto-played Burst never paid its
    ///     meter at all;
    ///   - a cost zeroed through either exposure above made the card playable
    ///     on an empty meter, and BaseLib still called Spend with amount 0.
    /// Either way the meter survived the cast. KitGrant checks after EVERY
    /// play, so it then saw a full meter and no copy in hand (a played Power
    /// leaves combat), granted a fresh one, and the loop ran as many times as
    /// the turn allowed -- the reported "burst infinite times per turn".
    ///
    /// The play hook is unconditional by construction: BeforeCardPlayed fires
    /// inside OnPlayWrapper, which every play path goes through, auto-plays
    /// included. Gating on the card carrying a burst cost (rather than on the
    /// concrete card type) keeps this correct for any future kit card.
    /// </summary>
    public static void DrainOnPlay(CardModel card)
    {
        if (CustomResources<KleeBurstResource>.Cost(card) == null) return;
        var owner = card.Owner;
        if (owner == null) return;
        var resource = Find(owner.Creature);
        if (resource == null) return;
        resource.Amount = 0;
        Vfx.GaugeBridge.Refresh(owner.Creature);
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
    /// Current meter value for display surfaces (the Track C gauge). Reads
    /// the canonical resource, 0 for non-Klee owners.
    /// </summary>
    public static int AmountFor(Creature player) => Find(player)?.Amount ?? 0;

    /// <summary>
    /// The gain path for every context-carrying source (reactions, the
    /// burst_energy op, and future powers) -- mirrors SparkPower.Gain so the
    /// economy stays easy to instrument. The context/cardSource parameters
    /// stay in the signature even though the badge apply they fed is retired:
    /// every call site carries them, and a future instrumented gain (VFX,
    /// telemetry) wants them back.
    /// </summary>
    public static Task Gain(
        PlayerChoiceContext choiceContext, Creature player, int amount,
        CardModel? cardSource)
    {
        if (amount <= 0) return Task.CompletedTask;
        var resource = Find(player);
        if (resource == null) return Task.CompletedTask;

        resource.ModifyAmount(amount);
        Vfx.GaugeBridge.Refresh(player);
        return Task.CompletedTask;
    }

    /// <summary>
    /// The gain path for the skill-tag bonus, which fires in BeforeCardPlayed
    /// where the game hands hooks no PlayerChoiceContext. Refreshes the gauge
    /// immediately; the paired SyncGauge call in AfterCardPlayed exists for
    /// the cast drain, not for this.
    /// </summary>
    public static void GainPreResolution(Creature player, int amount)
    {
        if (amount <= 0) return;
        var resource = Find(player);
        if (resource == null) return;
        resource.ModifyAmount(amount);
        Vfx.GaugeBridge.Refresh(player);
    }

    /// <summary>
    /// The gauge's catch-up site: runs after EVERY card play, which is what
    /// makes the cast drain visible -- the kit card's whole-meter Spend
    /// happens inside the cost machinery, outside our mutation funnels.
    /// (Successor to the retired SyncBadge; the badge half is gone, the
    /// after-every-play timing is unchanged.)
    /// </summary>
    public static void SyncGauge(Creature player)
    {
        if (Find(player) == null) return;
        Vfx.GaugeBridge.Refresh(player);
    }
}

/// <summary>
/// RETIRED display badge for the Burst meter -- superseded by the Track C
/// overhead gauge and no longer applied anywhere (C4 playtest feedback
/// 2026-07-23: redundant with the gauge). The class stays registered for
/// save compatibility: a run saved mid-combat before the retirement carries
/// BurstMeterPower stacks, and deleting the model would break that load.
/// Never apply this again; it renders one stale combat at most.
/// </summary>
public sealed class BurstMeterPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Burst Energy"),
        ("description",
            "Cards with [gold]Elemental Skill[/gold] grant 5 [gold]Burst "
          + "Energy[/gold]; Elemental Reactions grant 5. At 40, [gold]Sparks "
          + "'n' Splash[/gold] is added to your hand; casting it spends ALL "
          + "Burst Energy."),
    };

    public override PowerType Type => PowerType.Buff;

    /// <summary>Counter: energy is spent by casting, never ticked by time.</summary>
    public override PowerStackType StackType => PowerStackType.Counter;
}
