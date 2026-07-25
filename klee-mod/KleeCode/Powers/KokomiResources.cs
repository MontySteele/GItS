using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// Marker for Kokomi's CharacterModel. Same reason Furina has one: a generated
/// Kokomi card acquired by another character must not silently grant them her
/// Charge engine.
/// </summary>
public interface IKokomiCharacter
{
}

/// <summary>
/// TRANSCRIPTION SURFACE. Every number here is copied verbatim from the sim;
/// none is re-derived C#-side. The transcription checklist lives in the PR
/// body, one row per constant, because a number that exists in two hand-typed
/// places without a checklist is a number that will drift.
///
/// | C# constant        | sim source                              |
/// |--------------------|-----------------------------------------|
/// | ChargePerExhaust   | constants.py CHARGE_PER_EXHAUST = 1      |
/// | BurstPerExhaust    | constants.py KOKOMI_BURST_PER_EXHAUST=2  |
/// | KurageDuration     | constants.py KURAGE_DURATION = 1         |
/// | KuragePulseBase    | constants.py KURAGE_PULSE_BASE = 4       |
/// | KuragePulsePerChg  | constants.py KURAGE_PULSE_PER_CHARGE = 4 |
/// | KuragePulseBlock   | constants.py KURAGE_PULSE_BLOCK = 0      |
/// | GarmentAttackBlock | constants.py GARMENT_ATTACK_BLOCK = 2    |
/// | GarmentTurns       | constants.py CEREMONIAL_GARMENT_TURNS=3  |
/// | ConscriptCostDelta | constants.py CONSCRIPT_COST_DELTA = -1   |
/// | BurstMax           | characters/kokomi.yaml burst_max: 20     |
/// </summary>
public static class KokomiConstants
{
    public const int ChargePerExhaust = 1;
    public const int BurstPerExhaust = 2;
    public const int KurageDuration = 1;
    public const int KuragePulseBase = 4;

    /// <summary>
    /// A MULTIPLIER, not a divisor -- the pulse gains this much per POINT of
    /// Charge. [USER]-ratified over the assistant's objection (Necrobinder
    /// precedent, R56): unbounded starting-deck scaling is what the designers
    /// actually ship. The standing caveat is that Osty's HP can drop while
    /// Charge only climbs, so act 3 is the cell to watch; sim-side that is
    /// now a report column (tier05/kurage_telemetry.py, R57 P2).
    /// </summary>
    public const int KuragePulsePerCharge = 4;

    /// <summary>
    /// Zero since the v0.4b starter rework: the pulse is damage now, not
    /// mending. The mending half is DRAFTED, via Kurage's Oath. Kept as a
    /// named constant rather than inlined so restoring the baseline stays a
    /// one-constant change on both sides of the bridge.
    /// </summary>
    public const int KuragePulseBlock = 0;

    public const int GarmentAttackBlock = 2;
    public const int GarmentTurns = 3;
    public const int ConscriptCostDelta = -1;
    public const int BurstMax = 20;
}

/// <summary>
/// Kokomi's Charge: her scaling bank.
///
/// READ, NEVER SPENT -- this is the whole shape of the character, and it is
/// why <see cref="Spend{T}"/> below is a no-op rather than an oversight.
/// Nothing in her kit consumes Charge; cards READ it (the Kurage pulse, the
/// Garment's attack rider) and the bank keeps climbing. That is deliberate
/// asymmetry against Furina, who pays her Encore back out.
///
/// It is modelled as a BaseLib CustomResource for the gauge: BaseLib scans the
/// assembly and registers every concrete subclass itself, so this class is
/// DEFINED and never registered by hand (the ModelDb lesson). Per-combat
/// instances are created lazily and zeroed by PrepForCombat, matching the
/// sim's per-fight reset.
/// </summary>
public sealed class ChargeResource : BasicCustomResource
{
    public ChargeResource() : base("KLEEMOD_CHARGE")
    {
    }

    /// <summary>
    /// No card has a Charge cost, so there is no shared cost modification to
    /// apply. False keeps cost-reduction effects from pretending otherwise.
    /// </summary>
    public override bool ApplySharedModification => false;

    /// <summary>
    /// Charge is never spent. Returning true without decrementing is the
    /// contract, not a stub: if this ever starts subtracting, every scaling
    /// number in her sheet was measured against a bank that only grows and is
    /// silently wrong. See tier0/engine/resources.py -- there is no
    /// spend_charge, by design.
    /// </summary>
    public override Task<bool> Spend<T>(
        ICombatState combatState, AbstractModel? spender, int amount, bool optional)
    {
        return Task.FromResult(true);
    }
}

/// <summary>
/// Static accessors for Kokomi's bank. Mirrors KleeBurstResource's shape --
/// one private Find() that gates on character identity, everything else on
/// top of it -- so the two meters stay easy to compare and instrument.
/// </summary>
public static class KokomiResources
{
    public static bool IsKokomi(Creature? creature) =>
        creature?.Player?.Character is IKokomiCharacter;

    private static ChargeResource? Find(Creature? creature)
    {
        var owner = creature?.Player;
        if (owner?.Character is not IKokomiCharacter) return null;
        var combatState = owner.PlayerCombatState;
        if (combatState == null) return null;
        return CustomResources<ChargeResource>.Get(combatState);
    }

    /// <summary>Current bank, 0 for non-Kokomi owners. The display surfaces
    /// and the pulse arithmetic both read this, so they cannot drift.</summary>
    public static int GetCharge(Creature? creature) => Find(creature)?.Amount ?? 0;

    /// <summary>
    /// Grants Charge. Gated on identity inside Find() rather than at each call
    /// site: the sim accrues at a single chokepoint
    /// (refpowers.after_card_exhausted) and card-side gain_charge lines are
    /// premiums on top, so both paths land here.
    /// </summary>
    public static void GainCharge(Creature? creature, int amount)
    {
        if (amount <= 0) return;
        var resource = Find(creature);
        if (resource == null) return;
        resource.ModifyAmount(amount);
        Vfx.GaugeBridge.Refresh(creature!);
    }

    internal static KokomiBurstResource? FindBurst(Creature? creature)
    {
        var owner = creature?.Player;
        if (owner?.Character is not IKokomiCharacter) return null;
        var combatState = owner.PlayerCombatState;
        if (combatState == null) return null;
        return CustomResources<KokomiBurstResource>.Get(combatState);
    }
}

/// <summary>
/// The two engine-level rules that are NOT card text.
///
/// 1. The exhaust funnel. Every owned-card exhaust pays Charge and Burst
///    energy. In the sim this is the relic hook (`tamakushi_casket`, shipped
///    as "Pearl of Wisdom"), and it is universal -- it is deliberately not
///    written on any card face, because "exhaust pays" is the character, not a
///    card's rider. FeelNoPainPower / DarkEmbracePower are the first-party
///    precedent for this hook.
///
/// 2. LAW 3, Flawless Strategy. Kokomi CANNOT gain Strength; incoming Strength
///    converts to Charge instead. The conversion sits at
///    TryModifyPowerAmountReceived, which is the chokepoint EVERY source flows
///    through -- cards, companion buffs, enemy-applied. Doing it per-card
///    would leave the other two sources granting real Strength, which is
///    exactly the hole the sim closes at its own apply_power chokepoint.
/// </summary>
public sealed class KokomiResourceHooks : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static KokomiResourceHooks? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<KokomiResourceHooks>(
            ModelDb.GetId<KokomiResourceHooks>());
        yield return _instance;
    }

    public override Task AfterCardExhausted(
        PlayerChoiceContext choiceContext, CardModel card, bool causedByEthereal)
    {
        // CardModel.Owner is the Player; PowerModel.Owner is the Creature.
        // The two differ, and mixing them is a silent type error the compiler
        // happens to catch here only because the helpers take Creature.
        var owner = card.Owner?.Creature;
        if (!KokomiResources.IsKokomi(owner)) return Task.CompletedTask;

        KokomiResources.GainCharge(owner, KokomiConstants.ChargePerExhaust);
        KokomiResources.FindBurst(owner)
            ?.ModifyAmount(KokomiConstants.BurstPerExhaust);
        return Task.CompletedTask;
    }

    /// <summary>
    /// LAW 3. Returning true with modifiedAmount 0 refuses the Strength and
    /// pays Charge instead. The refusal is silent on purpose: her fiction is
    /// that she does not get stronger, she gets better positioned.
    ///
    /// All THREE Strength powers are caught, not just the plain one. Temporary
    /// and Possess variants are separate models, and letting either through
    /// would leave a legal route to Strength on a character whose sheet is
    /// designed around not having one -- the same hole the sim closes at its
    /// apply_power chokepoint.
    /// </summary>
    public override bool TryModifyPowerAmountReceived(
        PowerModel canonicalPower, Creature target, decimal amount,
        Creature applier, out decimal modifiedAmount)
    {
        modifiedAmount = amount;
        if (!KokomiResources.IsKokomi(target)) return false;
        if (canonicalPower is not (MegaCrit.Sts2.Core.Models.Powers.StrengthPower
                                   or MegaCrit.Sts2.Core.Models.Powers.TemporaryStrengthPower
                                   or MegaCrit.Sts2.Core.Models.Powers.PossessStrengthPower))
        {
            return false;
        }
        if (amount <= 0) return false;      // Strength LOSS still lands

        KokomiResources.GainCharge(target, (int)amount);
        modifiedAmount = 0;
        return true;
    }
}

/// <summary>
/// Kokomi's Burst meter. Separate class from Klee's and Furina's because the
/// ceiling is hers (kokomi.yaml burst_max: 20) and because BaseLib keys
/// per-combat instances by resource type.
/// </summary>
public sealed class KokomiBurstResource : BasicCustomResource
{
    public KokomiBurstResource() : base("KLEEMOD_KOKOMI_BURST")
    {
    }

    public override bool ApplySharedModification => false;
}
