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
/// none is re-derived C#-side.
///
/// THE CHECKLIST IS NOW A GATE. This table used to live in the PR body and be
/// kept by discipline -- which meant a sim-side retune that nobody mirrored
/// produced a green build playing to numbers no simulation ever endorsed.
/// tools/lint_constant_parity.py compares every row below against tier0 by
/// value, and fails on any C# constant that is neither mirrored nor declared
/// unmirrored with a reason. Adding a constant here without touching that
/// table is a build failure, on purpose.
///
/// | C# constant         | sim source                               |
/// |---------------------|------------------------------------------|
/// | ChargePerExhaust    | constants.py CHARGE_PER_EXHAUST = 1       |
/// | BurstPerExhaust     | constants.py KOKOMI_BURST_PER_EXHAUST=2   |
/// | BurstPerReaction    | constants.py BURST_PER_REACTION = 5       |
/// | KurageDuration      | constants.py KURAGE_DURATION = 1          |
/// | KuragePulseBase     | constants.py KURAGE_PULSE_BASE = 4        |
/// | KuragePulsePerChg   | constants.py KURAGE_PULSE_PER_CHARGE = 4  |
/// | KuragePulseBlock    | constants.py KURAGE_PULSE_BLOCK = 0       |
/// | GarmentAttackBlock  | constants.py GARMENT_ATTACK_BLOCK = 2     |
/// | GarmentTurns        | constants.py CEREMONIAL_GARMENT_TURNS = 3 |
/// | GarmentChargeDivisor| constants.py GARMENT_CHARGE_DIVISOR = 2   |
/// | ConscriptCostDelta  | constants.py CONSCRIPT_COST_DELTA = -1    |
/// | BurstMax            | characters/kokomi.yaml burst_max: 20      |
/// </summary>
public static class KokomiConstants
{
    public const int ChargePerExhaust = 1;
    public const int BurstPerExhaust = 2;

    /// <summary>
    /// tier0 BURST_PER_REACTION = 5, and tier0 BURST_PER_SKILL_TAG = 5 is
    /// <see cref="BurstConstants.PerSkillTag"/>. Both sim gates are
    /// `if p.burst_max` -- UNIVERSAL to anyone carrying a meter, not
    /// Klee-scoped -- so she is paid on the same lines Klee and Furina are.
    /// Aliased here rather than reaching for Klee's constant at her call
    /// sites, so her economy reads in one place.
    /// </summary>
    public const int BurstPerReaction = 5;
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

    /// <summary>
    /// tier0 GARMENT_CHARGE_DIVISOR = 2. While the Garment holds, her attacks
    /// gain +1 damage per this much Charge -- the "scaled down per hit" read
    /// (kickoff §2.2, Shape B). Was 4 until the v0.3 charge-curve pass found
    /// the meter reading ~4x under the Regent-common benchmark: at /4 a node-4
    /// bank of 8 paid +2 per attack, which is decoration rather than a scaling
    /// identity. Do not re-derive it here -- constants.py is LAW.
    /// </summary>
    public const int GarmentChargeDivisor = 2;
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

    /// <summary>
    /// Cards currently in the exhaust pile. The scaling term behind her
    /// exhaust-pile finishers (pearl_barrage, depths_judgment): the pile IS
    /// the record of everything she has rotated off the line, so a card that
    /// reads it is reading her whole game so far.
    ///
    /// Static and null-tolerant because CalculatedVar previews call it with
    /// no target while nothing is hovered.
    /// </summary>
    public static int ExhaustPileCount(Creature? creature)
    {
        var owner = creature?.Player;
        if (owner == null) return 0;
        return CardPile.Get(PileType.Exhaust, owner)?.Cards.Count ?? 0;
    }

    internal static KokomiBurstResource? FindBurst(Creature? creature)
    {
        var owner = creature?.Player;
        if (owner?.Character is not IKokomiCharacter) return null;
        var combatState = owner.PlayerCombatState;
        if (combatState == null) return null;
        return CustomResources<KokomiBurstResource>.Get(combatState);
    }

    /// <summary>Current Burst meter, 0 for non-Kokomi owners.</summary>
    public static int GetBurst(Creature? creature) => FindBurst(creature)?.Amount ?? 0;

    /// <summary>
    /// The single Burst gain funnel. Every source lands here -- the exhaust
    /// funnel, the skill-tag bonus, reactions -- so the gauge cannot go stale
    /// behind a gain and so the economy stays one place to instrument.
    /// Accrual is UNCAPPED past the max (the sim never clamps; the grant check
    /// is `>=` and casting resets to 0 -- overflow is lost at cast, not gain).
    /// </summary>
    public static void GainBurst(Creature? creature, int amount)
    {
        if (amount <= 0) return;
        var resource = FindBurst(creature);
        if (resource == null) return;
        resource.ModifyAmount(amount);
        Vfx.GaugeBridge.Refresh(creature!);
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
        KokomiResources.GainBurst(owner, KokomiConstants.BurstPerExhaust);
        return Task.CompletedTask;
    }

    /// <summary>
    /// Sim order (combat.py play_card): the requires-full drain FIRST, then
    /// the skill-tag bonus, both once per play rather than once per replay.
    /// The game fires card hooks once per replay in a series, so IsFirstInSeries
    /// is what reproduces "once per play_card call" -- an unguarded hook would
    /// double-grant where the sim grants once.
    ///
    /// The skill-tag half is UNIVERSAL in the sim (`if p.burst_max`, not
    /// `if klee`), and she has burst_max 20, so her skill-tagged cards pay the
    /// same 5 Klee's do. Missing this made her meter fill from exhausts alone,
    /// which is roughly half the sim's rate -- the Burst would have felt
    /// unreachable in play and correct in the model.
    /// </summary>
    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        if (!cardPlay.IsFirstInSeries) return Task.CompletedTask;
        KokomiBurstResource.DrainOnPlay(cardPlay.Card);
        var owner = cardPlay.Card.Owner?.Creature;
        if (cardPlay.Card is ISkillTagCard && KokomiResources.IsKokomi(owner))
        {
            KokomiResources.GainBurst(owner, BurstConstants.PerSkillTag);
        }
        return Task.CompletedTask;
    }

    /// <summary>
    /// Grant check sites, the sim's three grant_charged_kit calls: after the
    /// turn-start draw, after every card played, and at turn end before the
    /// flush. Her income arrives at all three -- exhausts and skill tags land
    /// inside plays, the Kurage's pulse reactions land in the turn-end
    /// broadcast, and an Ancient's turn-start drip lands at the top.
    /// </summary>
    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await KokomiKitGrant.GrantIfCharged(choiceContext, cardPlay.Card.Owner);
    }

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        await KokomiKitGrant.GrantIfCharged(choiceContext, player);
    }

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        foreach (var creature in participants)
        {
            if (creature.Player is { } player && KokomiResources.IsKokomi(creature))
            {
                await KokomiKitGrant.GrantIfCharged(choiceContext, player);
            }
        }
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
/// "At the start of your turn, gain Amount Charge." The engine behind her
/// Ancient card (see Cards/Kokomi/PrincessOfWatatsumi.cs).
///
/// This is the ONE place in the mod where Charge accrues without a card
/// leaving the deck, and that is the point of an Ancient: it is the only
/// door out of her central bargain. It is also why the number is small --
/// the pulse reads the bank at KuragePulsePerCharge, so a drip compounds
/// against a multiplier rather than adding to a total.
/// </summary>
public sealed class ChargePerTurnPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Princess of Watatsumi"),
        ("description",
            "At the start of your turn, gain {Amount} [gold]Charge[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return Task.CompletedTask;
        KokomiResources.GainCharge(Owner, (int)Amount);
        return Task.CompletedTask;
    }
}

/// <summary>
/// Kokomi's Burst meter. Separate class from Klee's and Furina's because the
/// ceiling is hers (kokomi.yaml burst_max: 20) and because BaseLib keys
/// per-combat instances by resource type.
///
/// The three guards below are NOT boilerplate -- each one closes an exposure
/// the other two meters paid for in a playtest, and a meter that ships
/// without them is a meter that can be cast off empty or cast twice.
/// </summary>
public sealed class KokomiBurstResource : BasicCustomResource
{
    public KokomiBurstResource() : base("KLEEMOD_KOKOMI_BURST")
    {
    }

    /// <summary>
    /// The meter is not an energy cost and must not be discounted like one.
    /// BaseLib forwards SetToFreeThisTurn / SetToFreeThisCombat onto every
    /// custom-resource cost unless the resource opts out here. A "this card is
    /// free" effect landing on the kit card would zero the meter cost -- see
    /// <see cref="DrainOnPlay"/> for why that is catastrophic rather than
    /// merely generous.
    /// </summary>
    public override bool ApplySharedModification => false;

    /// <summary>
    /// The cast gate is `requires: burst_energy_full` (tier0 card_playable):
    /// it reads the CANONICAL 20, never a discounted number. BaseLib's default
    /// CanAfford compares against the cost AFTER modifiers, and custom costs
    /// run through Hook.ModifyEnergyCostInCombat -- the hook cost reducers
    /// use. Without this override any cost reducer in range makes the Burst
    /// castable on an empty meter.
    /// </summary>
    public override bool CanAfford(CardModel card, int cost)
    {
        var canonical = CustomResources<KokomiBurstResource>.CanonicalCost(card);
        return canonical < 0 ? base.CanAfford(card, cost) : Amount >= canonical;
    }

    /// <summary>
    /// DELIBERATE NO-OP; the drain lives in <see cref="DrainOnPlay"/>, called
    /// from <see cref="KokomiResourceHooks.BeforeCardPlayed"/>. Same idiom and
    /// the same reason as Klee's -- see KleeBurstResource.DrainOnPlay for the
    /// infinite-Burst bug this shape exists to prevent (CardCmd.AutoPlay skips
    /// SpendResources entirely, so a drain riding the cost machinery is not
    /// called on every play path).
    /// </summary>
    public override Task<bool> Spend<T>(
        ICombatState combatState, AbstractModel? spender, int amount, bool optional)
    {
        return Task.FromResult(true);
    }

    /// <summary>
    /// Sim law, verbatim (combat.py play_card): `p.burst_energy = 0` on a
    /// requires-full play. Overflow past the max is lost at CAST, never
    /// clamped at gain, so this zeroes rather than subtracting.
    ///
    /// Gated on the card CARRYING a burst cost rather than on the concrete
    /// card type, which keeps it correct for any future kit card of hers.
    /// </summary>
    public static void DrainOnPlay(CardModel card)
    {
        if (CustomResources<KokomiBurstResource>.Cost(card) == null) return;
        var owner = card.Owner;
        if (owner == null) return;
        var resource = KokomiResources.FindBurst(owner.Creature);
        if (resource == null) return;
        resource.Amount = 0;
        Vfx.GaugeBridge.Refresh(owner.Creature);
    }
}

/// <summary>
/// Kokomi's kit-grant, port of tier0 grant_charged_kit (combat.py v1.9).
/// Same four rules Klee's and Furina's carry, and for the same reasons:
///   - grant only at a FULL meter (`>=`, because accrual is uncapped);
///   - never a duplicate: a copy already in hand blocks the grant;
///   - a full hand DEFERS, never drops -- the meter stays full so the next
///     check re-offers it. The hand-size test has to live HERE, before the
///     add, because the game's full-hand behaviour for
///     AddGeneratedCardToCombat is redirect-to-discard, and a kit card in a
///     pile recirculates the Burst as loot;
///   - the granted copy is fresh each time (the cast copy leaves combat).
/// </summary>
public static class KokomiKitGrant
{
    public static async Task GrantIfCharged(
        PlayerChoiceContext choiceContext, Player? owner)
    {
        if (owner?.Character is not IKokomiCharacter) return;
        var playerCombatState = owner.PlayerCombatState;
        var combatState = owner.Creature.CombatState;
        if (playerCombatState == null || combatState == null) return;

        // Rules read the RESOURCE, never a display surface.
        var resource =
            CustomResources<KokomiBurstResource>.Get(playerCombatState);
        if (resource.Amount < KokomiConstants.BurstMax) return;

        var hand = CardPile.Get(PileType.Hand, owner);
        if (hand == null
            || hand.Cards.Any(card => card is Cards.Kokomi.CeremonialGarment)
            || hand.Cards.Count >= CardPile.MaxCardsInHand)
        {
            return;
        }

        var burst = combatState.CreateCard<Cards.Kokomi.CeremonialGarment>(owner);
        await CardPileCmd.AddGeneratedCardToCombat(burst, PileType.Hand, owner);
    }
}
