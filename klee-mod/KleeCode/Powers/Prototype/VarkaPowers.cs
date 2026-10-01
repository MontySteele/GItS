using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// HIS STATUS-BAR BADGE: his current element and its Oath (sec.3: "The seat
/// page and his status bar show it with its Oath"). One badge at a time, the
/// current element's; before his first Knight, "Oath" alone once he has any.
/// The number on the icon is the current element's Oath
/// (<see cref="DisplayAmount"/>, the ledger's, so the badge cannot disagree
/// with the rules), and the in-combat tooltip lists all four counts.
///
/// THE LEDGER IS THE TRUTH (<see cref="VarkaOathLedger"/>); the badge is a
/// view of it that <see cref="OathBadge.Sync"/> keeps current.
/// </summary>
public abstract class OathBadgePower : PowerModel, ILocalizationProvider
{
    /// <summary>The element this badge shows as current, or None.</summary>
    public abstract Element Element { get; }

    /// <summary>The badge's first sentence.</summary>
    protected string Lead => Element == Element.None
        ? "You have no [gold]current element[/gold] yet."
        : $"Your [gold]current element[/gold] is {Element}. "
          + VarkaOath.PayoutSentence(Element);

    public List<(string, string)>? Localization => new()
    {
        ("title", Element == Element.None ? "Oath" : $"{Element} Oath"),
        ("description", Lead),
        ("smartDescription",
            Lead + "\nOath: Pyro {PyroOath}, Hydro {HydroOath}, "
          + "Electro {ElectroOath}, Cryo {CryoOath}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    protected override IEnumerable<DynamicVar> CanonicalVars => new List<DynamicVar>
    {
        new("PyroOath", 0m), new("HydroOath", 0m),
        new("ElectroOath", 0m), new("CryoOath", 0m),
    };

    /// <summary>The current element's Oath (the total, before one).</summary>
    public override int DisplayAmount
    {
        get
        {
            if (!IsMutable || Owner == null) return Amount;
            var ledger = VarkaOathLedger.For(Owner);
            // Elixir of the Four Winds: this turn his cards read all four.
            return Element == Element.None || ledger.AllFourThisTurn
                ? ledger.Total : ledger.Oath(Element);
        }
    }

    /// <summary>Copy the ledger into the tooltip's four numbers and redraw
    /// the icon's.</summary>
    internal void Refresh()
    {
        if (!IsMutable || Owner == null) return;
        var ledger = VarkaOathLedger.For(Owner);
        DynamicVars["PyroOath"].BaseValue = ledger.Oath(Element.Pyro);
        DynamicVars["HydroOath"].BaseValue = ledger.Oath(Element.Hydro);
        DynamicVars["ElectroOath"].BaseValue = ledger.Oath(Element.Electro);
        DynamicVars["CryoOath"].BaseValue = ledger.Oath(Element.Cryo);
        InvokeDisplayAmountChanged();
    }
}

public sealed class PyroOathPower : OathBadgePower
{
    public override Element Element => Element.Pyro;
}

public sealed class HydroOathPower : OathBadgePower
{
    public override Element Element => Element.Hydro;
}

public sealed class ElectroOathPower : OathBadgePower
{
    public override Element Element => Element.Electro;
}

public sealed class CryoOathPower : OathBadgePower
{
    public override Element Element => Element.Cryo;
}

/// <summary>Oath held before his first Knight.</summary>
public sealed class UnswornOathPower : OathBadgePower
{
    public override Element Element => Element.None;
}

/// <summary>Keeps the one badge in step with the ledger.</summary>
public static class OathBadge
{
    /// <summary>The badge this ledger wants, or null for none. PURE.</summary>
    public static System.Type? Wanted(Element current, int total) => current switch
    {
        Element.Pyro => typeof(PyroOathPower),
        Element.Hydro => typeof(HydroOathPower),
        Element.Electro => typeof(ElectroOathPower),
        Element.Cryo => typeof(CryoOathPower),
        _ => total > 0 ? typeof(UnswornOathPower) : null,
    };

    /// <summary>Swap the badge if the current element moved, then refresh
    /// it. Headless (no combat) it does nothing.</summary>
    public static async Task Sync(PlayerChoiceContext choiceContext, Creature varka)
    {
        if (varka.CombatState == null || !VarkaOath.Live(varka)) return;
        var ledger = VarkaOathLedger.For(varka);
        var wanted = Wanted(ledger.Current, ledger.Total);
        foreach (var stale in varka.Powers.OfType<OathBadgePower>()
                     .Where(b => b.GetType() != wanted).ToList())
        {
            await PowerCmd.Remove(stale);
        }
        if (wanted != null && !varka.Powers.Any(p => p.GetType() == wanted))
        {
            switch (ledger.Current)
            {
                case Element.Pyro:
                    await PowerCmd.Apply<PyroOathPower>(choiceContext, varka, 1, varka, null, silent: true);
                    break;
                case Element.Hydro:
                    await PowerCmd.Apply<HydroOathPower>(choiceContext, varka, 1, varka, null, silent: true);
                    break;
                case Element.Electro:
                    await PowerCmd.Apply<ElectroOathPower>(choiceContext, varka, 1, varka, null, silent: true);
                    break;
                case Element.Cryo:
                    await PowerCmd.Apply<CryoOathPower>(choiceContext, varka, 1, varka, null, silent: true);
                    break;
                default:
                    await PowerCmd.Apply<UnswornOathPower>(choiceContext, varka, 1, varka, null, silent: true);
                    break;
            }
        }
        foreach (var badge in varka.Powers.OfType<OathBadgePower>())
        {
            badge.Refresh();
        }
        await SyncLeft(choiceContext, varka, ledger);
    }

    /// <summary>The left-element flag this ledger wants, or null. PURE.
    /// </summary>
    public static System.Type? WantedLeft(bool leftThisTurn, Element left,
                                          Element current) =>
        !leftThisTurn || left == current ? null : left switch
        {
            Element.Pyro => typeof(PyroOathLeftPower),
            Element.Hydro => typeof(HydroOathLeftPower),
            Element.Electro => typeof(ElectroOathLeftPower),
            Element.Cryo => typeof(CryoOathLeftPower),
            _ => null,
        };

    /// <summary>
    /// ELEMENT IDENTITIES sec.7 (2026-10-01): "The Oath panel flashes the
    /// old element's count when it stops being current." The element he
    /// left this turn shows beside the badge as its own icon, its count his
    /// Oath of it, applied loud (the game's apply flash) and gone at the end
    /// of the turn, or the moment it is current again.
    /// </summary>
    private static async Task SyncLeft(PlayerChoiceContext choiceContext,
                                       Creature varka, VarkaOathLedger ledger)
    {
        var wanted = WantedLeft(ledger.LeftThisTurn, ledger.LeftElement,
                                ledger.Current);
        foreach (var stale in varka.Powers.OfType<OathLeftPower>()
                     .Where(b => b.GetType() != wanted).ToList())
        {
            await PowerCmd.Remove(stale);
        }
        if (wanted != null && !varka.Powers.Any(p => p.GetType() == wanted))
        {
            switch (ledger.LeftElement)
            {
                case Element.Pyro:
                    await PowerCmd.Apply<PyroOathLeftPower>(choiceContext, varka, 1, varka, null);
                    break;
                case Element.Hydro:
                    await PowerCmd.Apply<HydroOathLeftPower>(choiceContext, varka, 1, varka, null);
                    break;
                case Element.Electro:
                    await PowerCmd.Apply<ElectroOathLeftPower>(choiceContext, varka, 1, varka, null);
                    break;
                case Element.Cryo:
                    await PowerCmd.Apply<CryoOathLeftPower>(choiceContext, varka, 1, varka, null);
                    break;
            }
        }
        foreach (var left in varka.Powers.OfType<OathLeftPower>())
        {
            left.Refresh();
        }
    }
}

/// <summary>
/// ELEMENT IDENTITIES sec.7: the element that stopped being current this
/// turn, beside his badge, its count his Oath of it (kept, not read). Four
/// rounds of seats lost an Oath without noticing (the Varka round,
/// 2026-10-01); this is the flag. Placed and cleared by
/// <see cref="OathBadge.Sync"/>; gone at the end of his turn.
/// </summary>
public abstract class OathLeftPower : PowerModel, ILocalizationProvider
{
    /// <summary>The element he left.</summary>
    public abstract Element Element { get; }

    public List<(string, string)>? Localization => new()
    {
        ("title", $"{Element} Oath (left)"),
        ("description",
            $"Your [gold]current element[/gold] switched away from {Element} "
          + $"this turn. Your {Element} [gold]Oath[/gold] is kept, but your "
          + "cards read your [gold]current element[/gold]'s."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>His Oath of the element he left.</summary>
    public override int DisplayAmount =>
        !IsMutable || Owner == null ? Amount
            : VarkaOathLedger.For(Owner).Oath(Element);

    internal void Refresh()
    {
        if (!IsMutable || Owner == null) return;
        InvokeDisplayAmountChanged();
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }
}

public sealed class PyroOathLeftPower : OathLeftPower
{
    public override Element Element => Element.Pyro;
}

public sealed class HydroOathLeftPower : OathLeftPower
{
    public override Element Element => Element.Hydro;
}

public sealed class ElectroOathLeftPower : OathLeftPower
{
    public override Element Element => Element.Electro;
}

public sealed class CryoOathLeftPower : OathLeftPower
{
    public override Element Element => Element.Cryo;
}

/// <summary>
/// Grand Master's Order (sec.6): "The next Knight you play this turn is
/// played twice." The base game's replay surface (<c>ModifyCardPlayCount</c>),
/// scoped to the turn it was played on. Each replay is a Knight play.
/// </summary>
public sealed class GrandMastersOrderPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Grand Master's Order"),
        ("description",
            "The next [gold]Knight[/gold] you play this turn is played "
          + "{Amount} extra time{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override int ModifyCardPlayCount(
        CardModel card, Creature? target, int playCount)
    {
        if (!VarkaRules.IsKnight(card)) return playCount;
        if (card.Owner?.Creature != Owner) return playCount;
        return playCount + Amount;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!VarkaRules.IsKnight(cardPlay.Card)) return;
        if (cardPlay.Card?.Owner?.Creature != Owner) return;
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
/// Stormward Stance (sec.6): "While your current element has 4 or more Oath,
/// your Anemo Attacks deal 3 more." An additive term on his own powered
/// Attacks whose hit is Anemo, read live.
/// </summary>
public sealed class StormwardStancePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Stormward Stance"),
        ("description",
            "While your [gold]current element[/gold] has "
          + VarkaLaw.StormwardOathNeeded + " or more [gold]Oath[/gold], your "
          + "Anemo Attacks deal [blue]{Amount}[/blue] additional damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The Stance's condition on primitives. PURE.</summary>
    public static bool Applies(bool poweredAttack, bool isAttackCard,
                               Element hit, int currentOath) =>
        poweredAttack && isAttackCard && hit == Element.Anemo
        && currentOath >= VarkaLaw.StormwardOathNeeded;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == null || target == Owner) return 0m;
        return Applies(props.IsPoweredAttack(),
                       cardSource is { Type: CardType.Attack },
                       AuraCmd.ElementOfPlay(cardSource, dealer),
                       VarkaOath.CurrentOath(Owner))
            ? Amount : 0m;
    }
}

/// <summary>
/// Converging Winds (sec.6, the Gale Rare): "Your Swirls react where they
/// land" -- the spread hit is the flat 2 carrying the swirled element; a
/// reaction it sets off lands on that enemy only; a reaction from a spread
/// never Swirls again. A marker read inside the Swirl itself
/// (<c>ReactionEffects.SwirlPays</c>).
/// </summary>
public sealed class ConvergingWindsPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Converging Winds"),
        ("description",
            "Your [gold]Swirls[/gold] react where they land. An "
          + "[gold]Elemental Reaction[/gold] a spread sets off hits only that "
          + "enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;

    /// <summary>Do this dealer's Swirls react where they land? PURE.</summary>
    public static bool Converges(Creature? dealer) =>
        dealer != null
        && dealer.HasPower<ConvergingWindsPower>();

    /// <summary>
    /// THE SPREAD'S ONE DECISION, on primitives: a copy of
    /// <paramref name="spread"/> arriving on an enemy wearing
    /// <paramref name="existing"/> reacts there, instead of replacing it,
    /// only under this power and only where the two elements react. PURE.
    /// </summary>
    public static Reaction SpreadReaction(bool converges, Element spread,
                                          Element existing)
    {
        if (!converges || existing == Element.None || existing == spread)
        {
            return Reaction.None;
        }
        var reaction = ReactionTable.Lookup(existing, spread);
        return reaction == Reaction.Swirl ? Reaction.None : reaction;
    }
}

/// <summary>
/// Boreas Unbound (sec.6): "Whenever your current element changes, gain 1
/// Energy." Paid by <see cref="VarkaOath.SetCurrent"/>, the one place the
/// current element moves.
/// </summary>
public sealed class BoreasUnboundPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Boreas Unbound"),
        ("description",
            "Whenever your [gold]current element[/gold] changes, gain "
          + "[blue]{Amount}[/blue] [gold]Energy[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task OnElementChanged()
    {
        if (Owner.Player == null) return;
        Flash();
        await PlayerCmd.GainEnergy(Amount, Owner.Player);
    }
}

/// <summary>Oath of the Knights (sec.6): "At the start of your turn, gain
/// Block equal to your current element's Oath." Paid by
/// <see cref="VarkaOath.TurnStart"/>; a second copy doubles it.</summary>
public sealed class OathOfTheKnightsPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Oath of the Knights"),
        ("description",
            "At the start of your turn, gain [gold]Block[/gold] equal to your "
          + "[gold]current element[/gold]'s [gold]Oath[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Dawn Wind's March (sec.6, pick 3): "Whenever you gain Oath of
/// your current element, gain 3 Block." Paid by <see cref="VarkaOath.Gain"/>,
/// once per gain.</summary>
public sealed class DawnWindsMarchPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Dawn Wind's March"),
        ("description",
            "Whenever you gain [gold]Oath[/gold] of your [gold]current "
          + "element[/gold], gain [blue]{Amount}[/blue] [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Sworn Brotherhood+ (sec.6; the upgrade since the power cost
/// sweep, 2026-09-30): "At the start of your turn, gain 1
/// Oath of every element." Paid by <see cref="VarkaOath.TurnStart"/>.
/// </summary>
public sealed class SwornBrotherhoodPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sworn Brotherhood"),
        ("description",
            "At the start of your turn, gain [blue]{Amount}[/blue] "
          + "[gold]Oath[/gold] of every element."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Sworn Brotherhood, the base card (power cost sweep,
/// 2026-09-30): "At the start of your turn, gain 1 Oath of your current
/// element." Nothing without a current element. The upgraded card installs
/// <see cref="SwornBrotherhoodPower"/> (every element) instead. Paid in
/// <c>VarkaOath.TurnStart</c>; sim twin: <c>varka_oath</c>'s turn start.
/// </summary>
public sealed class SwornBrotherhoodCurrentPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sworn Brotherhood"),
        ("description",
            "At the start of your turn, gain [blue]{Amount}[/blue] "
          + "[gold]Oath[/gold] of your [gold]current element[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// Amber: Baron Bunny's decoy (pick 2): "Next turn, deal 6 [8] Pyro damage to
/// ALL enemies." At the start of his next turn (<see cref="VarkaOath.TurnStart"/>)
/// the whole amount goes off once, a Pyro hit on every enemy, unpowered, in
/// one Oath scope (at most 1 Pyro Oath), and the badge leaves. It does not
/// change his current element.
/// </summary>
public sealed class VarkaBaronBunnyPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Baron Bunny"),
        ("description",
            "At the start of your turn, deal [blue]{Amount}[/blue] "
          + "[gold]Pyro[/gold] damage to ALL enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task Fire(PlayerChoiceContext choiceContext)
    {
        var amount = Amount;
        var enemies = Owner.CombatState?.HittableEnemies.ToList();
        await PowerCmd.Remove(this);
        if (enemies == null || amount <= 0) return;
        using (VarkaOath.Scope(Owner))
        {
            foreach (var enemy in enemies)
            {
                if (!enemy.IsAlive) continue;
                await ElementalHit.DealWithoutDealerMods(
                    choiceContext, enemy, Element.Pyro, amount, Owner);
            }
        }
    }
}

// ==========================================================================
// THE EXPANSION (review/active/varka-expansion-2026-10-01.md sec.3, ruled
// 2026-10-01). Fifteen Powers. Each is paid at one site in VarkaOath.cs
// (named on the class) or by its own hook; sim twins in
// tier0/engine/varka_oath.py.
// ==========================================================================

/// <summary>Static Field: "The first time each turn you apply Electro, draw 2
/// [3] cards." Paid by <see cref="VarkaOath.NoteApplication"/>, once a turn
/// (<see cref="VarkaOathLedger.TakeStaticField"/>).</summary>
public sealed class StaticFieldPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Static Field"),
        ("description",
            "The first time each turn you apply [gold]Electro[/gold], draw "
          + "[blue]{Amount}[/blue] cards."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task Draw(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player is not { } player || Amount <= 0) return;
        Flash();
        await CardPileCmd.Draw(choiceContext, Amount, player);
    }
}

/// <summary>Unwavering Banner: "Only Knights and cards that name it can
/// change your current element." A marker read by
/// <see cref="VarkaOath.NoteApplication"/>: the open Oath's switch is off;
/// Knights, Change of Guard and Weathervane still move it.</summary>
public sealed class UnwaveringBannerPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Unwavering Banner"),
        ("description",
            "Only [gold]Knights[/gold] and cards that name it can change your "
          + "[gold]current element[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;
}

/// <summary>Cycle of Seasons: "Whenever your current element changes, deal
/// 4 [6] damage to ALL enemies." Paid by <see cref="VarkaOath.SetCurrent"/>;
/// element-less and unpowered, a Power's damage.</summary>
public sealed class CycleOfSeasonsPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Cycle of Seasons"),
        ("description",
            "Whenever your [gold]current element[/gold] changes, deal "
          + "[blue]{Amount}[/blue] damage to ALL enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task OnElementChanged(PlayerChoiceContext choiceContext)
    {
        var enemies = Owner.CombatState?.HittableEnemies.ToList();
        if (enemies == null || Amount <= 0) return;
        Flash();
        foreach (var enemy in enemies)
        {
            if (!enemy.IsAlive) continue;
            await ElementalHit.DealUnelemented(choiceContext, enemy, Amount,
                                               Owner, powered: false);
        }
    }
}

/// <summary>Windborne Resolve (Varka defence, 2026-10-01): "Whenever your
/// current element changes, gain 5 [7] Block." Paid by
/// <see cref="VarkaOath.SetCurrent"/> after Cycle of Seasons; unpowered, a
/// Power's Block (Favonian Standard's and Dawn Wind's March's door).</summary>
public sealed class WindborneResolvePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Windborne Resolve"),
        ("description",
            "Whenever your [gold]current element[/gold] changes, gain "
          + "[blue]{Amount}[/blue] [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task OnElementChanged()
    {
        if (Amount <= 0 || Owner == null) return;
        Flash();
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Unpowered, null,
                                    fast: true);
    }
}

/// <summary>Eye Wall: "Whenever you Swirl this turn, gain 3 Block." Paid by
/// <see cref="VarkaOath.OnSwirl"/>; gone at the end of the turn.</summary>
public sealed class EyeWallPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Eye Wall"),
        ("description",
            "Whenever you [gold]Swirl[/gold] this turn, gain "
          + "[blue]{Amount}[/blue] [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>Assembly at the Cathedral: "Whenever you play a Knight, deal 3
/// [4] damage to a random enemy." Paid by <see cref="VarkaOath.EndPlay"/>,
/// once per play (replays too), element-less and unpowered.</summary>
public sealed class AssemblyAtTheCathedralPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Assembly at the Cathedral"),
        ("description",
            "Whenever you play a [gold]Knight[/gold], deal "
          + "[blue]{Amount}[/blue] damage to a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task OnKnightPlayed(PlayerChoiceContext choiceContext)
    {
        var enemies = Owner.CombatState?.HittableEnemies
            .Where(e => e.IsAlive).ToList();
        if (enemies == null || enemies.Count == 0 || Amount <= 0) return;
        if (Owner.Player is not { } player) return;
        var target = player.RunState.Rng.CombatTargets.NextItem(enemies);
        if (target == null) return;
        Flash();
        await ElementalHit.DealUnelemented(choiceContext, target, Amount, Owner,
                                           powered: false);
    }
}

/// <summary>Wildfire Oath: "While your current element is Pyro, your Swirls'
/// damage hits ALL enemies, plus 1 for each Pyro Oath." A marker read by the
/// Pyro payout (<c>VarkaOath.Pay</c>); its Amount is the per-Oath rate.
/// </summary>
public sealed class WildfireOathPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Wildfire Oath"),
        ("description",
            "While your [gold]current element[/gold] is Pyro, your first "
          + "Attack each turn deals additional damage equal to your Pyro "
          + "[gold]Oath[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// ELEMENT IDENTITIES sec.5 (2026-10-01): one big hit. The turn's first
    /// Attack is armed at the top of its play (<see cref="VarkaOath.BeginPlay"/>,
    /// with every stack); its first powered hit on an enemy takes his Pyro
    /// Oath per stack while Pyro is current as it lands. One hit: "multi-hit
    /// cards do not multiply it". The sim's twin is
    /// <c>varka_oath.take_wildfire</c>.
    /// </summary>
    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == null || target == Owner) return 0m;
        if (!props.IsPoweredAttack() || cardSource == null) return 0m;
        if (!VarkaOath.Live(Owner)) return 0m;
        var ledger = VarkaOathLedger.For(Owner);
        if (!ReferenceEquals(ledger.WildfireCard, cardSource)) return 0m;
        return VarkaOath.WildfireBonus(ledger.Current, ledger.Oath(Element.Pyro),
                                       ledger.WildfireStacks);
    }

    /// <summary>The armed play's first hit spends the arm, paid or not (it
    /// lands after <see cref="ModifyDamageAdditive"/> was asked).</summary>
    public override Task BeforeDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, decimal amount,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (dealer != Owner || cardSource == null || target == Owner
            || !props.IsPoweredAttack() || !VarkaOath.Live(Owner))
        {
            return Task.CompletedTask;
        }
        var ledger = VarkaOathLedger.For(Owner);
        if (ReferenceEquals(ledger.WildfireCard, cardSource))
        {
            if (VarkaOath.WildfireBonus(ledger.Current,
                    ledger.Oath(Element.Pyro), ledger.WildfireStacks) > 0)
            {
                Flash();
            }
            ledger.WildfireCard = null;
        }
        return Task.CompletedTask;
    }
}

/// <summary>
/// Retaliating Tide (element identities sec.4, in Unbroken Tide's place): "At
/// the end of your turn, deal damage equal to your Block, up to your Hydro
/// Oath, to a random enemy." After Oathbound Aegis (which pays at
/// <c>BeforeSideTurnEndEarly</c>), so its Block counts; element-less and
/// unpowered, a Power's damage, like Cycle of Seasons'; once per stack. The
/// sim's twin is <c>varka_oath.turn_end</c>.
/// </summary>
public sealed class RetaliatingTidePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Retaliating Tide"),
        ("description",
            "At the end of your turn, deal damage equal to your "
          + "[gold]Block[/gold], up to your Hydro [gold]Oath[/gold], to a "
          + "random enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>One stack's damage. PURE.</summary>
    public static int DamageFor(int block, int hydroOath) =>
        System.Math.Max(0, System.Math.Min(block, hydroOath));

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player || !VarkaOath.Live(Owner)) return;
        var player = Owner.Player;
        var combat = Owner.CombatState;
        if (player == null || combat == null) return;
        for (var i = 0; i < Amount; i++)
        {
            var damage = DamageFor(Owner.Block,
                                   VarkaOath.Count(Owner, Element.Hydro));
            var living = combat.HittableEnemies.Where(e => e.IsAlive).ToList();
            if (damage <= 0 || living.Count == 0) return;
            Flash();
            var target = player.RunState.Rng.CombatTargets.NextItem(living);
            await ElementalHit.DealUnelemented(choiceContext, target, damage,
                                               Owner, powered: false);
        }
    }
}

/// <summary>Absolute Zero: "While your current element is Cryo, your Swirls
/// apply Vulnerable and Weak to ALL enemies." A marker read by the Cryo
/// payout (<c>VarkaOath.Pay</c>).</summary>
public sealed class AbsoluteZeroPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Absolute Zero"),
        ("description",
            "While your [gold]current element[/gold] is Cryo, your "
          + "[gold]Swirls[/gold] apply [gold]Vulnerable[/gold] and "
          + "[gold]Weak[/gold] to ALL enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;
}

/// <summary>Oath Unto Death: "Whenever you gain Oath of your current
/// element, gain 1 more." Read inside <see cref="VarkaOath.Gain"/>, so the
/// extra point is part of the same gain.</summary>
public sealed class OathUntoDeathPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Oath Unto Death"),
        ("description",
            "Whenever you gain [gold]Oath[/gold] of your [gold]current "
          + "element[/gold], gain [blue]{Amount}[/blue] more."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Wolfpack: "Whenever you play Four Winds' Ascension, add a copy
/// of it to your discard pile." Paid by <see cref="VarkaOath.EndPlay"/>, one
/// copy per stack, upgraded when the played one was.</summary>
public sealed class WolfpackPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Wolfpack"),
        ("description",
            "Whenever you play Four Winds' Ascension, add a copy of it to "
          + "your discard pile."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task OnAscensionPlayed(CardModel played)
    {
        var combat = Owner.CombatState;
        if (combat == null || Owner.Player is not { } player) return;
        Flash();
        for (var i = 0; i < Amount; i++)
        {
            var copy = combat.CreateCard(
                ModelDb.GetById<CardModel>(played.Id), player);
            if (copy == null) continue;
            if (played.IsUpgraded && copy.IsUpgradable && !copy.IsUpgraded)
            {
                copy.UpgradeInternal();
            }
            await CardPileCmd.AddGeneratedCardToCombat(copy, PileType.Discard,
                                                       player);
        }
    }
}

/// <summary>Oathbound Aegis (re-aimed by the Varka defence paper,
/// 2026-10-01): "At the end of your turn, gain Block equal to half your total
/// Oath." Half rounds down; no cap; the upgrade is a cost cut. Amount counts
/// the copies, each paying the half.</summary>
public sealed class OathboundAegisPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Oathbound Aegis"),
        ("description",
            "At the end of your turn, gain [gold]Block[/gold] equal to half "
          + "your total [gold]Oath[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The Block it gives: half the total, rounded down, per copy.
    /// PURE.</summary>
    public static int BlockFor(int totalOath, int copies) =>
        System.Math.Max(0, totalOath / 2) * System.Math.Max(0, copies);

    /// <summary>EARLY (element identities, 2026-10-01): ahead of Retaliating
    /// Tide's <c>BeforeSideTurnEnd</c>, so the Tide reads this Block, the
    /// order the sim's <c>varka_oath.turn_end</c> pays them in.</summary>
    public override async Task BeforeSideTurnEndEarly(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player || !VarkaOath.Live(Owner)) return;
        var block = BlockFor(VarkaOathLedger.For(Owner).Total, Amount);
        if (block <= 0) return;
        Flash();
        await CreatureCmd.GainBlock(Owner, block, ValueProp.Unpowered, null,
                                    fast: true);
    }
}

/// <summary>Weathervane: "At the start of your turn, you may choose an
/// element you have Oath in; it becomes your current element." Paid first
/// in <see cref="VarkaOath.TurnStart"/>, on a cancelable grid.</summary>
public sealed class WeathervanePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Weathervane"),
        ("description",
            "At the start of your turn, you may choose an element you have "
          + "[gold]Oath[/gold] in; it becomes your [gold]current "
          + "element[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;
}

/// <summary>Twin Gales: "Your Swirls pay both your current element and the
/// element Swirled." A marker read by <see cref="VarkaOath.OnSwirl"/>.
/// </summary>
public sealed class TwinGalesPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Twin Gales"),
        ("description",
            "Your [gold]Swirls[/gold] pay both your [gold]current "
          + "element[/gold] and the element Swirled."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;
}

/// <summary>Eye of Stormterror: "The first 3 times you Swirl each turn,
/// draw 1 card." Paid by <see cref="VarkaOath.OnSwirl"/>.</summary>
public sealed class EyeOfStormterrorPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Eye of Stormterror"),
        ("description",
            "The first " + VarkaLaw.EyeOfStormterrorSwirls + " times you "
          + "[gold]Swirl[/gold] each turn, draw [blue]{Amount}[/blue] "
          + "card{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task Draw(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player is not { } player || Amount <= 0) return;
        Flash();
        await CardPileCmd.Draw(choiceContext, Amount, player);
    }
}

/// <summary>The Order Answers: "At the start of your turn, add a random
/// Knight to your hand." Paid last in <see cref="VarkaOath.TurnStart"/>, a
/// pool Knight at its own cost (<see cref="VarkaRules.AddRandomKnight"/>).
/// </summary>
public sealed class TheOrderAnswersPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "The Order Answers"),
        ("description",
            "At the start of your turn, add [blue]{Amount}[/blue] random "
          + "[gold]Knight[/gold]{Amount:plural:|s} to your hand."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}
