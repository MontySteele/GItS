using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards;

/// <summary>
/// Sheet: cost 0, skill, place_bomb(1, bomb_damage 5).
///
/// The C1 stub dealt the 5 damage immediately, which was power-roughly-right
/// and mechanically wrong -- the whole point of Pop is the delayed
/// place-then-detonate rhythm. Now a real bomb (C2.2).
/// </summary>
public sealed class Pop : CustomCardModel
{
    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("pop");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Pop!"),
        ("description", "Place a [gold]Bomb[/gold] dealing {Damage:diff()} damage."),
    };

    /// <summary>
    /// The bomb's payload. Held as a DynamicVar so upgrades and card text stay
    /// in sync; BombPower stores the resolved number at placement time.
    /// </summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new DamageVar(5m, ValueProp.Move) };

    // autoAdd: false -- KleeCardPool owns membership. See Kaboom.
    public Pop()
        : base(0, CardType.Skill, CardRarity.Basic, TargetType.AnyEnemy, autoAdd: false)
    {
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");

        await BombPower.Place(
            choiceContext, cardPlay.Target, (int)DynamicVars.Damage.BaseValue,
            applier: Owner.Creature, cardSource: this);
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(2m);
    }
}
