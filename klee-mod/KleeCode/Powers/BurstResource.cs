using System.Collections.Generic;
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
///   +5 per skill-tagged card played, AFTER its effects resolve
///     (KleeElementalHooks.AfterCardPlayed -- same post-resolution order as
///     play_card's tag check);
///   +5 per Elemental Reaction, amplifiers included (ReactionEffects.Resolve
///     is the single funnel every reaction passes through);
///   +N from the burst_energy card op (codegen);
///   accrual is UNCAPPED past 60 (the sim never clamps; the grant check is
///     >=, and casting resets to 0 -- overflow is lost at cast, not at gain).
///
/// What this spike deliberately does NOT ship: the kit-grant machinery and
/// the Burst card itself. Sparks 'n' Splash lands LAST in the power-card
/// pass (standing plan), where the meter becomes its CustomResourceCost
/// (SetCanonicalCost 60 gates playability via CanAfford) and casting empties
/// the meter. Until then a full meter is visible but spends nothing.
///
/// The badge: BaseLib ships NO ambient on-screen meter (its resource UI is
/// cost-side card visuals only; BasicResourceVisualsHandler is an empty
/// marker), so the meter renders through <see cref="BurstMeterPower"/> on
/// Klee -- the SparkPower display idiom. The resource is canonical; the
/// badge is display. Gain() is the ONLY mutation path in the spike and
/// writes both, which is the sync invariant to preserve when cast lands.
/// </summary>
public sealed class KleeBurstResource : BasicCustomResource
{
    public KleeBurstResource() : base("KLEEMOD_BURST")
    {
    }

    /// <summary>
    /// The single gain path for every source (skill tags, reactions, the
    /// burst_energy op, and future powers) -- mirrors SparkPower.Gain so the
    /// economy stays one line to instrument.
    ///
    /// Gates on the owner being Klee: the sim guards every gain site with
    /// `if p.burst_max`, i.e. characters without a meter gain nothing.
    /// </summary>
    public static async Task Gain(
        PlayerChoiceContext choiceContext, Creature player, int amount,
        CardModel? cardSource)
    {
        if (amount <= 0) return;
        var owner = player.Player;
        if (owner?.Character is not Klee) return;
        var combatState = owner.PlayerCombatState;
        if (combatState == null) return;

        CustomResources<KleeBurstResource>.Get(combatState).ModifyAmount(amount);
        await PowerCmd.Apply<BurstMeterPower>(
            choiceContext, player, amount, applier: player, cardSource: cardSource);
    }
}

/// <summary>
/// Display badge for the Burst meter (see KleeBurstResource: BaseLib has no
/// ambient resource UI, so the meter shows the way Sparks do). Amount always
/// equals the resource's Amount -- KleeBurstResource.Gain is the only writer.
/// </summary>
public sealed class BurstMeterPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Burst Energy"),
        ("description",
            "Skill-tagged cards grant 5 [gold]Burst Energy[/gold]; Elemental "
          + "Reactions grant 5. At 60, Klee's Burst is charged."),
    };

    public override PowerType Type => PowerType.Buff;

    /// <summary>Counter: energy is spent by casting, never ticked by time.</summary>
    public override PowerStackType StackType => PowerStackType.Counter;
}
