using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// RULE 6, the Ceremonial Garment: "a state for a stated number of turns. While
/// she wears it, each of her Attacks that hits Mends her 2."
///
/// A SEPARATE POWER FROM THE SHIPPED <see cref="CeremonialGarmentPower"/>,
/// deliberately, and for the reason <c>BombReactionSparkPower</c> gives one arm
/// over: the shipped Garment is a Charge-scaling damage bonus plus flat Block
/// per Attack, and this one is a Mend per Attack that hits. Re-using it would
/// have re-priced the card without saying so, and the shipped Garment is the
/// Burst this arm's brief retires.
///
/// "THAT HITS" IS TWO HOOKS, AND IT HAS TO BE. An Attack that finds nothing to
/// hit Mends nothing, so the damage event has to be seen; but the Mend is per
/// ATTACK and not per hit, so it cannot be paid from the damage hook itself --
/// a three-hit Attack would Mend 6. <see cref="AfterDamageReceived"/> raises a
/// latch and <see cref="AfterCardPlayed"/> spends it, which pays once per
/// Attack card play that landed on something. The brief's own arithmetic is
/// that reading: script B's "Water's Edge twice (12, Mend 4)" and sec.6.1's
/// "three Attacks each put 2 back".
///
/// THE DURATION IS THE AMOUNT, so re-wearing the Garment extends the window and
/// never doubles the Mend -- the same construction the shipped Garment's own
/// header records, and a tick-down at the end of her turn.
/// </summary>
public sealed class ProtoGarmentPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Ceremonial Garment"),
        ("description",
            "Each of your Attacks that hits [gold]Mends[/gold] you "
          + KokomiOverhaulLaw.GarmentMend
          + ". Lasts {Amount} more turn{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Did an Attack of hers land since the last card play finished?
    /// The latch this file's header explains.</summary>
    private bool _attackHit;

    /// <summary>Read by the pins, which cannot run a combat to raise it.</summary>
    public bool AttackHitPending => _attackHit;

    /// <summary>Test seam and the latch's one raise site.</summary>
    public void NoteAttackHit() => _attackHit = true;

    public override Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, DamageResult result,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (dealer != Owner) return Task.CompletedTask;
        if (!props.IsPoweredAttack()) return Task.CompletedTask;
        if (cardSource is not { Type: CardType.Attack }) return Task.CompletedTask;
        // BLOCKED DAMAGE IS STILL A HIT. The card says "that hits", not "that
        // takes HP" -- unlike the shipped Bomb's early pop, which reads
        // UnblockedDamage on purpose because its rule is about HP. An Attack
        // eaten whole by enemy Block still hit.
        NoteAttackHit();
        return Task.CompletedTask;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card.Owner?.Creature != Owner) return;
        if (cardPlay.Card.Type != CardType.Attack) return;
        // ONE PAYMENT PER PLAY, and a replayed Attack is a second Attack, so
        // this is deliberately NOT gated on IsFirstInSeries: the game raises
        // this hook once per play in a series and each of those is an Attack
        // that hit.
        if (!_attackHit) return;
        _attackHit = false;
        await KokomiTide.Mend(choiceContext, Owner, KokomiOverhaulLaw.GarmentMend);
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// Song of Pearls: "The pulse Mends 3, and its budget is 12."
///
/// The power stores nothing and does nothing on a hook. The pulse is ONE rule
/// computed in ONE place (<see cref="Relics.TamanooyasCasket.PulseMend"/> and
/// <see cref="Relics.TamanooyasCasket.PulseBudget"/>), so this power's whole
/// job is to be present and readable -- the identical argument
/// <c>ExplosivesWorkshopGrowthPower</c> makes for having one growth number.
///
/// BOTH NUMBERS ARE THE POWER'S, not the card's, which is why they are named
/// constants rather than a printed Amount: the card prints two figures and a
/// power carries one <c>Amount</c>, so putting either on the row would leave
/// the other one homeless.
/// </summary>
public sealed class SongOfPearlsPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Song of Pearls"),
        ("description",
            "The pulse [gold]Mends[/gold] " + KokomiOverhaulLaw.SongOfPearlsMend
          + ", and its budget is " + KokomiOverhaulLaw.SongOfPearlsBudget + "."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// The Clouds Like Waves: "While you are under half HP, the pulse Mends 4."
///
/// A CONDITION READ AT PULSE TIME, not a stored state: "while" is a standing
/// clause, so the relic asks this power when the pulse fires rather than the
/// power writing anything down. <c>Amount</c> is the card's printed 4.
/// </summary>
public sealed class CloudsLikeWavesPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "The Clouds Like Waves"),
        ("description",
            "While you are under half HP, the pulse [gold]Mends[/gold] "
          + "{Amount}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Is she under half HP right now? Public so the relic and any
    /// hover tip read the same arithmetic the pulse uses.</summary>
    public static bool UnderHalf(Creature? kokomi) =>
        kokomi != null && kokomi.CurrentHp * 2 < kokomi.MaxHp;
}

/// <summary>
/// Sango Isshin (Rare): "Mend that would go past your entry HP becomes Hydro
/// damage to a random enemy." The Priestess Rare, and the brief's gloss is that
/// it BREAKS the "never above where you started" rule -- so a full bar stops
/// being wasted healing and becomes a weapon.
///
/// IT IS RESOLVED INSIDE <see cref="KokomiTide.Mend"/> and not on a hook, which
/// is the whole reason it can be trusted: the excess only exists at the moment
/// the cap is applied, and there is exactly one place that applies it. A hook
/// would have to recompute "would have gone past", which is the drift this
/// arrangement makes impossible.
///
/// IT HEALS NOTHING EXTRA (brief sec.10): the conversion is of the excess, so
/// the healing bound is untouched and only the damage is new.
/// </summary>
public sealed class SangoIsshinPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sango Isshin"),
        ("description",
            "[gold]Mend[/gold] that would go past your entry HP becomes Hydro "
          + "damage to a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The conversion. One random living enemy takes the whole
    /// excess as one Hydro hit through the shared pipeline, so it applies,
    /// refreshes or reacts exactly as a Surge does.</summary>
    public static async Task Overflow(
        PlayerChoiceContext choiceContext, Creature kokomi, int excess)
    {
        var combat = kokomi.CombatState;
        if (combat == null || excess <= 0) return;
        var candidates = combat.HittableEnemies.Where(e => !e.IsDead).ToList();
        if (candidates.Count == 0) return;
        var target = combat.RunState.Rng.CombatTargets.NextItem(candidates);
        if (target == null) return;
        await ElementalHit.Deal(
            choiceContext, target, Element.Hydro, excess, kokomi);
    }
}

/// <summary>
/// Treatise: "Whenever a Plan resolves, draw 1." The card that turns the
/// Strategist's delay into cards.
///
/// It rides the plan bus rather than the turn, which is what "whenever" has to
/// mean under rule 8: three Plans resolving in one turn-start is three draws,
/// and the Art of War's extra now-resolution pays too.
/// </summary>
public sealed class TreatisePower
    : PowerModel, ILocalizationProvider, IKokomiPlanListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Treatise"),
        ("description",
            "Whenever a [gold]Plan[/gold] resolves, draw {Amount} "
          + "card{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public async Task OnPlanResolved(
        PlayerChoiceContext choiceContext, Creature kokomi)
    {
        if (kokomi != Owner) return;                 // co-op: your plans only
        var player = Owner?.Player;
        if (player == null) return;
        await CardPileCmd.Draw(choiceContext, Amount, player);
    }
}

/// <summary>
/// The Art of War (Rare): "Plans also happen now." Rule 8's delay is gone.
///
/// It stores nothing and hooks nothing. <see cref="KokomiPlan.Schedule"/> asks
/// for it at the one moment the question can be asked -- as a Plan is written
/// -- for the reason Sango Isshin sits inside the Mend: the extra resolution is
/// a property of the WRITING, and a hook would have to reconstruct which Plans
/// were new.
/// </summary>
public sealed class TheArtOfWarPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "The Art of War"),
        ("description", "[gold]Plans[/gold] also happen now."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// Orders: "Whenever you play a Companion, Tide +2." The card that makes the
/// Commander loop feed the jellyfish.
///
/// PER PLAY AND NOT PER CARD: a Companion played twice by The General's Banner
/// pays twice, because the game raises this hook once per play in a series and
/// each of those is a Companion being played.
/// </summary>
public sealed class OrdersPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Orders"),
        ("description",
            "Whenever you play a [gold]Companion[/gold], [gold]Tide[/gold] "
          + "+{Amount}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card is not ICompanionCard) return;
        if (cardPlay.Card.Owner?.Creature != Owner) return;
        await KokomiTide.Gain(choiceContext, Owner, Amount);
    }
}

/// <summary>
/// Vanguard's grant: "The next Companion you play this turn costs 0."
///
/// THE SHAPE IS <see cref="CompanionCostThisTurnPower"/>'s and
/// <see cref="ReplayNextCompanionPower"/>'s, taken together and for their own
/// reasons: the cost move rides <c>TryModifyEnergyCostInCombat</c> (the same
/// surface the Spark zeroing uses) and the grant is consumed by the next
/// Companion play and expires at the END of the turn it was written on -- the
/// ratified same-turn boundary (FLAG-1 / R114, family X11), which is what the
/// card's own "this turn" says.
///
/// ZERO, NOT A DISCOUNT. The card prints "costs 0", so this sets rather than
/// subtracts; a subtraction would be a different card on an expensive
/// Companion.
/// </summary>
public sealed class NextCompanionFreePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Vanguard"),
        ("description",
            "The next [gold]Companion[/gold] you play this turn costs 0."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (card is not ICompanionCard) return false;
        if (card.Owner?.Creature != Owner) return false;
        if (originalCost <= 0m) return false;
        modifiedCost = 0m;
        return true;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card is not ICompanionCard) return;
        if (cardPlay.Card.Owner?.Creature != Owner) return;
        if (!cardPlay.IsLastInSeries) return;
        await PowerCmd.Remove(this);
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// The General's Banner (Rare): "The first Companion you play each turn is
/// played twice." The Commander Rare, and the brief's gloss is that it breaks
/// the one-play rule.
///
/// TWICE MEANS ONE EXTRA PLAY, through <c>ModifyCardPlayCount</c> -- the game's
/// own replay surface, and the one
/// <see cref="ReplayNextCompanionPower"/> already uses, so the extra play is a
/// series on one CardPlay rather than a second hand-rolled play.
///
/// "FIRST ... EACH TURN" is read off <see cref="KokomiOverhaulLedger"/>'s own
/// per-turn count, which this power is the only writer of. The count is
/// incremented AFTER the series finishes, which is what makes the replay itself
/// not consume the entitlement it was granted by: the play count is read once,
/// at play creation, before any of it has happened.
/// </summary>
public sealed class GeneralsBannerPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "The General's Banner"),
        ("description",
            "The first [gold]Companion[/gold] you play each turn is played "
          + "twice."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override int ModifyCardPlayCount(
        CardModel card, Creature? target, int playCount)
    {
        if (card is not ICompanionCard) return playCount;
        if (card.Owner?.Creature != Owner) return playCount;
        if (Owner == null) return playCount;
        if (KokomiOverhaulLedger.For(Owner).CompanionsPlayedThisTurn > 0)
        {
            return playCount;
        }
        return playCount + 1;
    }

    public override Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card is not ICompanionCard) return Task.CompletedTask;
        if (cardPlay.Card.Owner?.Creature != Owner) return Task.CompletedTask;
        if (!cardPlay.IsLastInSeries) return Task.CompletedTask;
        if (Owner != null) KokomiOverhaulLedger.For(Owner).NoteCompanionPlayed();
        return Task.CompletedTask;
    }
}
