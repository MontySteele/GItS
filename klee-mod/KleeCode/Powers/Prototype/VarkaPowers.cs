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
    }
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
        VarkaPrototype.Enabled && dealer != null
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

/// <summary>Favonian Standard (sec.6, pick 3): "Whenever you play a Knight of
/// your current element, gain 4 [5] Block." Paid by
/// <see cref="VarkaOath.SetCurrent"/>.</summary>
public sealed class FavonianStandardPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Favonian Standard"),
        ("description",
            "Whenever you play a [gold]Knight[/gold] of your [gold]current "
          + "element[/gold], gain [blue]{Amount}[/blue] [gold]Block[/gold]."),
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
