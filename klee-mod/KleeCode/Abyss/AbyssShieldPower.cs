using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Abyss;

/// <summary>
/// ABYSS MAGE SHIELD (the Spiral Abyss paper, sec.3): "Elites enter combat
/// with a shield of this act's element, 8 hits deep, that stops all damage.
/// Each hit removes 1, a reaction removes 3, and the counter element breaks
/// it." Amount is the hits left.
///
/// STOPS ALL DAMAGE the way the base game's Intangible caps it: a damage cap
/// (which also spares the wearer's Block and makes previews read 0) and an
/// HP-loss floor for anything that skips the cap. The hit that breaks the
/// shield is itself stopped: the shield is up when it lands.
///
/// A HIT is every damage instance the wearer receives while the shield is up,
/// powered or not (a Bomb, a reaction's splash). Its element is the play's
/// element (<see cref="AuraCmd.ElementOfPlay"/>), so only a card or a rider
/// that names the counter element breaks the shield outright.
///
/// A REACTION is every named reaction resolved on the wearer, reported from
/// <see cref="ReactionEffects.Resolve"/> (the single site every reaction
/// passes). A hit that also reacts removes both: 1 for the hit, 3 for the
/// reaction.
///
/// Only an Abyss run applies it (<see cref="SpiralAbyss"/>), so a normal run
/// never meets it and the reaction call is a no-op there.
/// </summary>
public abstract class AbyssShieldPower : PowerModel, ILocalizationProvider
{
    public abstract Element Element { get; }

    /// <summary>The shield's own icon: the official Abyss Mage shield of its
    /// element. A literal per subclass so <c>validate.ps1</c> S12 can see it
    /// (read by <c>KleePowerIcons</c>).</summary>
    public abstract string IconFile { get; }

    public Element Counter => AbyssElements.CounterOf(Element);

    public List<(string, string)>? Localization => new()
    {
        ("title", $"{Element} Abyss Shield"),
        ("description",
            $"Stops all damage. Each hit removes {AbyssNumbers.MageShieldPerHit} and a "
          + $"reaction removes {AbyssNumbers.MageShieldPerReaction}. "
          + $"A {Counter} hit breaks it."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageCap(
        Creature? target, ValueProp props, Creature? dealer, CardModel? cardSource, CardPlay? cardPlay)
    {
        if (target != base.Owner || base.Amount <= 0) return decimal.MaxValue;
        return 0m;
    }

    public override decimal ModifyHpLostAfterOsty(
        Creature target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (target != base.Owner || base.Amount <= 0) return amount;
        return 0m;
    }

    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, DamageResult result,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (target != base.Owner || dealer == base.Owner) return;
        var hitElement = props.IsPoweredAttack()
            ? AuraCmd.ElementOfPlay(cardSource, dealer)
            : Element.None;
        await SetHits(choiceContext, AbyssRules.ShieldAfterHit(base.Amount, hitElement, Element));
    }

    /// <summary>Called from <see cref="ReactionEffects.Resolve"/> for every
    /// named reaction. Nothing happens unless the target wears a shield.</summary>
    public static async Task NoteReaction(PlayerChoiceContext choiceContext, Creature target)
    {
        var shield = target.Powers.OfType<AbyssShieldPower>().FirstOrDefault();
        if (shield == null) return;
        await shield.SetHits(choiceContext, AbyssRules.ShieldAfterReaction(shield.Amount));
    }

    private async Task SetHits(PlayerChoiceContext choiceContext, int hits)
    {
        if (hits == base.Amount) return;
        Flash();
        if (hits <= 0)
        {
            await PowerCmd.Remove(this);
            return;
        }
        await PowerCmd.ModifyAmount(choiceContext, this, hits - base.Amount, null, null, silent: true);
    }

    /// <summary>Apply the shield of <paramref name="element"/> to an elite.</summary>
    public static async Task Apply(PlayerChoiceContext choiceContext, Creature target, Element element)
    {
        const int hits = AbyssNumbers.MageShieldHits;
        switch (element)
        {
            case Element.Hydro:
                await PowerCmd.Apply<HydroAbyssShieldPower>(choiceContext, target, hits, null, null);
                break;
            case Element.Pyro:
                await PowerCmd.Apply<PyroAbyssShieldPower>(choiceContext, target, hits, null, null);
                break;
            case Element.Electro:
                await PowerCmd.Apply<ElectroAbyssShieldPower>(choiceContext, target, hits, null, null);
                break;
            case Element.Cryo:
                await PowerCmd.Apply<CryoAbyssShieldPower>(choiceContext, target, hits, null, null);
                break;
        }
    }
}

public sealed class HydroAbyssShieldPower : AbyssShieldPower
{
    public override Element Element => Element.Hydro;
    public override string IconFile => "abyss/powers/shield_hydro.png";
}

public sealed class PyroAbyssShieldPower : AbyssShieldPower
{
    public override Element Element => Element.Pyro;
    public override string IconFile => "abyss/powers/shield_pyro.png";
}

public sealed class ElectroAbyssShieldPower : AbyssShieldPower
{
    public override Element Element => Element.Electro;
    public override string IconFile => "abyss/powers/shield_electro.png";
}

public sealed class CryoAbyssShieldPower : AbyssShieldPower
{
    public override Element Element => Element.Cryo;
    public override string IconFile => "abyss/powers/shield_cryo.png";
}
