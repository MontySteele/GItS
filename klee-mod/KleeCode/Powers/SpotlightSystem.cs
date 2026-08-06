using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

public enum SpotlightMode
{
    None = 0,
    CenterStage = 1,
    GuestCast = 2,
}

public sealed class SpotlightModeResource : BasicCustomResource
{
    public SpotlightModeResource() : base("KLEEMOD_SPOTLIGHT_MODE")
    {
    }
}

public sealed class SpotlightMovedResource : BasicCustomResource
{
    public SpotlightMovedResource() : base("KLEEMOD_SPOTLIGHT_MOVED")
    {
    }
}

public sealed class SpotlightPlaysResource : BasicCustomResource
{
    public SpotlightPlaysResource() : base("KLEEMOD_SPOTLIGHT_PLAYS")
    {
    }
}

public sealed class SpotlightSpendBoostResource : BasicCustomResource
{
    public SpotlightSpendBoostResource() : base("KLEEMOD_SPOTLIGHT_SPEND_BOOST")
    {
    }
}

/// <summary>
/// Spotlight v5. Center Stage marks Furina's own cards and generates Fanfare
/// without changing their numbers. Guest Cast marks every Companion and
/// multiplies printed damage/Block; card-mediated bonuses ride the same pipe.
/// </summary>
public static class SpotlightSystem
{
    public const decimal GuestCastBaseMultiplier = 1.5m;
    public const int FanfarePerCenterStagePlay = 2;

    /// <summary>
    /// C3 -- PendingDraws lifecycle.
    ///
    /// THE LEAK. This is a static dictionary keyed by CardPlay, and a CardPlay
    /// holds Card -> Owner -> Creature -> Player, i.e. the whole run graph.
    /// Entries were removed in exactly two places: ResolvePendingDraw when the
    /// draw actually resolved, and ResetTurn at end of turn. Neither runs on an
    /// ABNORMAL exit -- quit to menu, abandon run, a throw between NotePlay and
    /// the resolve -- so an interrupted play pinned a dead run in memory for
    /// the life of the process. BombPower's per-owner counter names this file
    /// as the counterexample to its own bounded design (audit sec.5).
    ///
    /// WHY NOT BOMBPOWER'S IDIOM VERBATIM. That one keeps a single
    /// `_countCombat` token and clears everything when the combat changes.
    /// The token there is the shared ICombatState; the state reachable from a
    /// Creature here is `Player.PlayerCombatState`, which is PER PLAYER. A
    /// single token over a per-player value would mean each co-op partner's
    /// play cleared the other's pending draw -- trading a leak for a dropped
    /// card, which is worse because it changes play.
    ///
    /// So the generation is recorded PER ENTRY and checked per entry: an entry
    /// survives only while its own owner is still in the combat it was made
    /// in. A partner in the same combat is untouched; an entry whose player
    /// has moved on (or been torn down, giving null) is dropped on the next
    /// touch of the system. That gives the same bound BombPower advertises --
    /// at most the current combat's entries -- without the co-op cost.
    /// </summary>
    private readonly record struct PendingDraw(int Amount, object? Combat);

    private static readonly Dictionary<CardPlay, PendingDraw> PendingDraws = new();

    /// <summary>The combat generation an entry for this play belongs to.</summary>
    private static object? CombatOf(CardPlay play) =>
        play.Card?.Owner?.Creature?.Player?.PlayerCombatState;

    /// <summary>
    /// Drop entries whose owner is no longer in the combat that made them.
    /// Called on every read and write, so the dictionary is bounded by the
    /// live combat rather than by the process.
    /// </summary>
    private static void PurgeStaleEntries()
    {
        foreach (var (play, pending) in PendingDraws.ToList())
        {
            if (!ReferenceEquals(CombatOf(play), pending.Combat))
            {
                PendingDraws.Remove(play);
            }
        }
    }

    private static T? Resource<T>(Creature creature)
        where T : CustomResource, new()
    {
        var combat = creature.Player?.PlayerCombatState;
        return combat == null ? null : CustomResources<T>.Get(combat);
    }

    public static SpotlightMode Mode(Creature creature) =>
        (SpotlightMode)(Resource<SpotlightModeResource>(creature)?.Amount ?? 0);

    /// <summary>
    /// Does this Furina hold the upgraded starter (red-pen R2)? If so BOTH
    /// Spotlight modes are permanently in force.
    ///
    /// A relic query rather than a resource, deliberately: the relic is run
    /// state and survives combats, whereas every Spotlight resource is
    /// per-combat and would have to be re-seeded at every fight start -- one
    /// more thing to forget, and its failure mode is silent.
    /// </summary>
    public static bool BothModes(Creature creature) =>
        creature.Player?.Relics
            .Any(relic => relic is Relics.CurtainNeverFalls) ?? false;

    /// <summary>Is Center Stage's half in force -- her own cards generate
    /// Fanfare? True under the mode, or unconditionally when upgraded.</summary>
    private static bool CenterStageActive(Creature creature) =>
        Mode(creature) == SpotlightMode.CenterStage || BothModes(creature);

    /// <summary>Is Guest Cast's half in force -- Companions are multiplied?
    /// True under the mode, or unconditionally when upgraded.</summary>
    private static bool GuestCastActive(Creature creature) =>
        Mode(creature) == SpotlightMode.GuestCast || BothModes(creature);

    /// <summary>
    /// R2 makes the upgraded starter the SELECTOR-PAYOFF ENABLER: conditions
    /// keying off "moved the Spotlight this turn" are always on.
    ///
    /// That is the whole point of the ruling rather than a side effect. With
    /// the selector card gone there is no designation event left to move, so
    /// without this every selector-payoff card on the sheet would become dead
    /// text the moment the relic was taken -- the upgrade would silently
    /// subtract from her pool while appearing to add to it.
    /// </summary>
    public static bool MovedThisTurn(Creature creature) =>
        BothModes(creature)
        || (Resource<SpotlightMovedResource>(creature)?.Amount ?? 0) > 0;

    public static int PlaysThisTurn(Creature creature) =>
        Resource<SpotlightPlaysResource>(creature)?.Amount ?? 0;

    public static async Task Designate(
        PlayerChoiceContext choiceContext, Creature creature,
        SpotlightMode mode, CardModel? cardSource)
    {
        if (!FurinaResources.IsFurina(creature) || mode == SpotlightMode.None)
        {
            return;
        }
        var resource = Resource<SpotlightModeResource>(creature);
        if (resource == null || resource.Amount == (int)mode) return;
        resource.Amount = (int)mode;
        var moved = Resource<SpotlightMovedResource>(creature);
        if (moved != null) moved.Amount = 1;

        // Animation sprint 2, F1. Deliberately placed AFTER the early-out
        // above, so the beam marks an actual designation and not a re-assert
        // of the mode already in force. This is the single designation funnel
        // (Funnel Contract §3), so one call here covers every entry point.
        Vfx.KleeCombatVfx.SpawnSpotlightShine(creature);

        foreach (var old in creature.Powers
                     .Where(power => power is CenterStagePower
                                     or GuestCastPower)
                     .ToList())
        {
            await PowerCmd.Remove(old);
        }
        if (mode == SpotlightMode.CenterStage)
        {
            await PowerCmd.Apply<CenterStagePower>(
                choiceContext, creature, 1,
                applier: creature, cardSource: cardSource);
        }
        else
        {
            await PowerCmd.Apply<GuestCastPower>(
                choiceContext, creature, 1,
                applier: creature, cardSource: cardSource);
        }
    }

    /// <summary>
    /// R2 reading 1 ([USER], 2026-07-26): the upgrade removes the
    /// EXCLUSIVITY between the two modes, not their TARGETING. Her own cards
    /// are lit by Center Stage's half and Companions by Guest Cast's half, and
    /// when upgraded both halves are live at once -- but neither half reaches
    /// across to the other's card class. So an upgraded Furina still gets no
    /// numeric boost on her own cards, and her Companions still generate no
    /// Fanfare; what she gains is that she no longer has to choose.
    /// </summary>
    public static bool IsSpotlighted(CardModel card)
    {
        var owner = card.Owner?.Creature;
        if (owner == null) return false;
        return (CenterStageActive(owner)
                && card is ICharacterCard { CharacterId: "furina" })
            || (GuestCastActive(owner) && card is ICompanionCard);
    }

    private static int PowerAmount<T>(Creature owner) where T : PowerModel =>
        owner.Powers.OfType<T>().FirstOrDefault()?.Amount ?? 0;

    /// <summary>
    /// The Guest Cast multiplier. Gated on the card being a COMPANION as well
    /// as on the mode -- under R2's upgrade both halves are live, and without
    /// the card-class test the multiplier would leak onto Furina's own cards,
    /// which Center Stage explicitly does not do.
    /// </summary>
    private static decimal OutwardMultiplier(CardModel card)
    {
        if (!IsSpotlighted(card)
            || card is not ICompanionCard
            || !GuestCastActive(card.Owner.Creature))
        {
            return 1m;
        }
        var owner = card.Owner.Creature;
        var percentagePoints =
            PowerAmount<SpotlightMultBonusPower>(owner)
            + PowerAmount<SpotlightMultBonusTurnPower>(owner)
            + (Resource<SpotlightSpendBoostResource>(owner)?.Amount ?? 0);
        return GuestCastBaseMultiplier + percentagePoints / 100m;
    }

    public static decimal PrintedDamage(CardModel card, decimal amount)
    {
        var scaled = Math.Truncate(amount * OutwardMultiplier(card));
        // Same gate as OutwardMultiplier, for the same reason: the flat
        // bonuses are Guest Cast's half and must not reach her own cards when
        // R2's upgrade makes both halves live.
        if (!IsSpotlighted(card)
            || card is not ICompanionCard
            || !GuestCastActive(card.Owner.Creature))
        {
            return scaled;
        }
        return scaled
               + PowerAmount<SpotlightFlatDamagePower>(card.Owner.Creature)
               + PowerAmount<SpotlightFlatDamageTurnPower>(card.Owner.Creature);
    }

    /// <summary>
    /// Spotlight's contribution expressed as a DELTA off a card's printed
    /// damage, for cards that render through a CalculatedDamageVar
    /// (Legibility sprint, 2026-07-24). Because that var computes
    /// <c>base + extra * multiplier</c>, an <c>extra</c> of 1 and this delta
    /// reproduce <see cref="PrintedDamage"/> exactly -- the face, the enemy
    /// hover and the resolved hit then read one value instead of the card
    /// printing its base while Spotlight silently scaled the hit.
    ///
    /// Deliberately NOT a Hook.ModifyDamage participant: that hook applies
    /// every additive contribution before every multiplicative one, whereas
    /// Spotlight multiplies the PRINTED number and adds its flat bonus after,
    /// ahead of Strength/Vulnerable. Routing it through the hook would fold
    /// Strength into the GuestCast multiplier and change resolved damage.
    /// </summary>
    public static decimal PrintedDamageDelta(CardModel card)
    {
        var printed = card.DynamicVars.CalculationBase.BaseValue;
        return PrintedDamage(card, printed) - printed;
    }

    /// <summary>
    /// <see cref="PrintedDamageDelta"/>'s block twin, for cards whose block
    /// renders through the base game's <c>CalculatedBlockVar</c>. Same identity:
    /// <c>base + 1 * delta == PrintedBlock(base)</c>.
    /// </summary>
    public static decimal PrintedBlockDelta(CardModel card)
    {
        var printed = card.DynamicVars.CalculationBase.BaseValue;
        return PrintedBlock(card, printed) - printed;
    }

    public static decimal PrintedBlock(CardModel card, decimal amount) =>
        Math.Truncate(amount * OutwardMultiplier(card));

    public static void ResetTurn(Creature creature)
    {
        var moved = Resource<SpotlightMovedResource>(creature);
        var plays = Resource<SpotlightPlaysResource>(creature);
        var spendBoost = Resource<SpotlightSpendBoostResource>(creature);
        if (moved != null) moved.Amount = 0;
        if (plays != null) plays.Amount = 0;
        if (spendBoost != null) spendBoost.Amount = 0;
        // C3: null-tolerant. This walked `play.Card.Owner.Creature` unguarded,
        // which throws on exactly the half-torn-down entry the purge exists to
        // clear -- and a throw in ResetTurn takes the turn reset with it.
        PurgeStaleEntries();
        foreach (var play in PendingDraws.Keys
                     .Where(play => play.Card?.Owner?.Creature == creature)
                     .ToList())
        {
            PendingDraws.Remove(play);
        }
    }

    public static void NotePlay(CardPlay cardPlay)
    {
        var card = cardPlay.Card;
        if (!cardPlay.IsFirstInSeries || !IsSpotlighted(card)) return;
        // Ownerless plays (autoplay, tokens) reach the card-played broadcast
        // with no Player attached; the same C3 tolerance ResetTurn already
        // takes, for the same reason -- a throw here lands in CombatManager's
        // continuation and reads as a black screen.
        if (card.Owner?.Creature is not { } owner) return;
        var plays = Resource<SpotlightPlaysResource>(owner);
        if (plays == null) return;
        var first = plays.Amount == 0;
        plays.ModifyAmount(1);

        // B2: Leading Role's window spends only on a play it could have
        // discounted. PRINTED cost (Canonical), not the resolved one -- a
        // printed-1 card discounted to 0 must still spend the window, or the
        // discount would re-arm behind its own effect and fire every turn.
        if (card.EnergyCost.Canonical >= 1)
        {
            foreach (var discount in owner.Powers
                         .OfType<SpotlightDiscountPower>())
            {
                discount.NoteQualifyingPlay();
            }
        }

        // Center Stage's half: her OWN cards mint Fanfare. The card-class test
        // is what keeps Guest Cast's "their plays generate no Fanfare" clause
        // true for Companions even when R2's upgrade has both halves live --
        // the upgrade drops the exclusivity, not the targeting.
        if (CenterStageActive(owner)
            && card is ICharacterCard { CharacterId: "furina" })
        {
            FurinaResources.GainFanfare(owner, FanfarePerCenterStagePlay);
        }
        if (!first) return;

        var encore = PowerAmount<SpotlightEncoreFirstPower>(owner);
        if (encore > 0)
        {
            FurinaResources.GainEncore(owner, encore);
        }
        var draw = PowerAmount<SpotlightDrawPower>(owner);
        if (draw > 0)
        {
            PurgeStaleEntries();
            PendingDraws[cardPlay] = new PendingDraw(draw, CombatOf(cardPlay));
        }
    }

    public static async Task ResolvePendingDraw(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // Purge BEFORE the lookup: a pending draw whose combat has changed
        // must not resolve into the new one.
        PurgeStaleEntries();
        if (!PendingDraws.Remove(cardPlay, out var pending) || pending.Amount <= 0)
        {
            return;
        }

        var amount = pending.Amount;
        await CardPileCmd.Draw(
            choiceContext, amount, cardPlay.Card.Owner);
    }

    public static void OnEncoreSpent(Creature creature)
    {
        var boost = PowerAmount<OvationSpendBoostPower>(creature);
        if (boost <= 0) return;
        Resource<SpotlightSpendBoostResource>(creature)?.ModifyAmount(boost);
    }
}

public sealed class CenterStagePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Center Stage"),
        ("description",
            "Furina is Spotlighted. Playing her cards generates "
          + "2 Fanfare; their printed numbers are unchanged."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Single;
}

public sealed class GuestCastPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Guest Cast"),
        ("description",
            "Companion cards are Spotlighted. Their printed damage and Block "
          + "are 50% stronger; their plays generate no Fanfare."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Single;
}

/// <summary>
/// Shared shape for every Spotlight texture power: a Buff counter with NO
/// stack ceiling.
///
/// The 2026-07-24 cap ruling landed in two rounds. Round one dropped the four
/// non-compounding caps and split a CappedSpotlightPower subclass out for the
/// two percentage multipliers (spotlight_mult_bonus, ovation_spend_boost).
/// Round two -- after a 2000-run x 2-seed A/B showed the whole cap set moving
/// run success by at most +0.5pp (favorable, p~0.02) -- uncapped those two as
/// well, to match base StS where Power dupes always stack. That emptied
/// CappedSpotlightPower, so it is gone and every Spotlight power lives here.
///
/// KleePowerIcons keys its Spotlight icon off this base type, so keeping the
/// common base (rather than folding straight into PowerModel) keeps the icon
/// match a single case. The two multipliers are genuinely compounding and were
/// FLAGGED for a ceiling re-check when difficulty calibration makes the
/// spotlight plan viable enough to measure them.
/// </summary>
public abstract class SpotlightPower : PowerModel
{
    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

public sealed class SpotlightDiscountPower
    : SpotlightPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Leading Role"),
        ("description",
            "The first [gold]Spotlighted[/gold] card each turn costs "
          + "{Amount} less."),
    };

    /// <summary>
    /// B2 (playtest-2, 2026-07-28): Leading Role's OWN first-play window,
    /// counting only Spotlighted plays whose PRINTED cost is >= 1.
    ///
    /// It cannot reuse <see cref="SpotlightSystem.PlaysThisTurn"/>, which
    /// counts EVERY Spotlighted play. This power skips `originalCost &lt;= 0`
    /// -- it has nothing to discount -- but the shared counter had already
    /// ticked, so a free Spotlighted play consumed a window it could never
    /// use. Ethereal Spotlight's token is an ICharacterCard with
    /// CharacterId "furina", so under Center Stage it IS a Spotlighted
    /// Furina card and it arrives every turn: the discount read as dead.
    ///
    /// The shared counter keeps counting everything, because Ovation, the
    /// reserve cap, spotlight_draw and spotlight_encore_first all want free
    /// plays counted. Only the discount needed its own window.
    ///
    /// Mutated ONLY from <see cref="SpotlightSystem.NotePlay"/>, never from
    /// the cost query below -- the query is called speculatively to draw
    /// costs on cards in hand, and per-peer state written from a display
    /// path is what desynced co-op on 2026-07-27 (see
    /// PreventExhaustWardPower).
    /// </summary>
    private int _qualifyingPlaysThisTurn;

    public override Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature == Owner) _qualifyingPlaysThisTurn = 0;
        return Task.CompletedTask;
    }

    internal void NoteQualifyingPlay() => _qualifyingPlaysThisTurn++;

    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (card.Owner?.Creature != Owner
            || !SpotlightSystem.IsSpotlighted(card)
            || _qualifyingPlaysThisTurn > 0
            || originalCost <= 0m)
        {
            return false;
        }
        modifiedCost = Math.Max(0m, originalCost - Amount);
        return modifiedCost != originalCost;
    }
}

public sealed class SpotlightDrawPower
    : SpotlightPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Supporting Cast"),
        ("description",
            "The first [gold]Spotlighted[/gold] card each turn draws "
          + "{Amount} card{Amount:plural:|s}."),
    };
}

public sealed class SpotlightMultBonusPower
    : SpotlightPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Top Billing"),
        ("description",
            "[gold]Spotlighted[/gold] Companion numbers are {Amount}% "
          + "stronger this combat."),
    };
}

public sealed class SpotlightMultBonusTurnPower
    : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Limelight"),
        ("description",
            "[gold]Spotlighted[/gold] Companion numbers are {Amount}% "
          + "stronger this turn."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side == CombatSide.Player) await PowerCmd.Remove(this);
    }
}

public sealed class SpotlightFlatDamagePower
    : SpotlightPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Star of the Show"),
        ("description",
            "[gold]Spotlighted[/gold] Companion damage gains {Amount}."),
    };
}

public sealed class SpotlightFlatDamageTurnPower
    : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Stage Lights"),
        ("description",
            "[gold]Spotlighted[/gold] Companion damage gains {Amount} "
          + "this turn."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side == CombatSide.Player) await PowerCmd.Remove(this);
    }
}

public sealed class OvationSpendBoostPower
    : SpotlightPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Standing Ovation"),
        ("description",
            "Whenever you spend Encore, [gold]Spotlighted[/gold] Companion "
          + "numbers are {Amount}% stronger this turn."),
    };
}

public sealed class SpotlightEncoreFirstPower
    : SpotlightPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Ovation Trickle"),
        ("description",
            "The first [gold]Spotlighted[/gold] card each turn grants "
          + "{Amount} Encore."),
    };
}
