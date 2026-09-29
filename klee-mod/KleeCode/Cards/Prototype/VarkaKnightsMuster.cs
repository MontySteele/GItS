using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards.Prototype;

/// <summary>
/// KNIGHTS' MUSTER -- Varka's starter Knight (sec.10.2: "Skill, 0: Choose a
/// Knight: deal 4 [6] of their element"; sec.4: "a companion card").
///
/// HAND-WRITTEN, NOT A SHEET ROW, because its hit's element is CHOSEN at
/// play: the sheet grammar carries one element per card (a companion row's
/// <c>element:</c>) and a four-way choice cannot be a <c>choose_one</c> (the
/// choose-a-card screen takes at most three cards). The choice is
/// <see cref="VarkaRules.ChooseKnight"/>'s grid, the one Favonius Drill's
/// generated <c>knight_aura</c> opens too, and the hit carries the chosen
/// element through <see cref="HitElement.Carry"/>, the scope every generated
/// per-hit element takes -- so a Pyro Muster on a Hydro aura Vaporizes its
/// own 4, exactly as a Pyro hit would.
///
/// A KNIGHT CARD: a Companion card in his personal pool, so Grand Master's
/// Order repeats it and the repeat may choose a different Knight (sec.9.6).
/// A Skill, so Boreas's Fang never reads it.
/// </summary>
public sealed class ProtoVkKnightsMuster : CustomCardModel, ICompanionCard
{
    /// <summary>The printed hit, 4 upgraded to 6.</summary>
    public const int Damage = 4;
    public const int UpgradeDamage = 2;

    public int Star => 4;

    public Element CompanionElement => Element.None;

    public string? PersonalPool => VarkaPrototype.CharacterId;

    public string? Nation => "mondstadt";

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("proto_vk_knights_muster");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Knights' Muster"),
        ("description",
            "Choose a [gold]Knight[/gold]: deal {Damage:diff()} damage of "
          + "their element."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForKnight(base.ExtraHoverTips, this);

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new DamageVar(Damage, ValueProp.Move) };

    public ProtoVkKnightsMuster()
        : base(0, CardType.Skill, CardRarity.Basic, TargetType.AnyEnemy,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");
        var element = await VarkaRules.ChooseKnight(choiceContext, Owner);
        if (element == Element.None) return;
        using (HitElement.Carry(this, element))
        {
            await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
                .FromCard(this, cardPlay)
                .Targeting(cardPlay.Target)
                .WithHitFx("vfx/vfx_attack_slash")
                .Execute(choiceContext);
        }
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(UpgradeDamage);
    }
}

/// <summary>
/// One Knight on the choose-a-Knight grid. A FACE, never played and never in
/// a pile, but a pool member (<c>VarkaRoster.Members</c>), because a card in
/// no pool throws "You monster!" the moment the screen draws it (EB-150). It
/// wears the Knight's own card art. Each is a direct <c>ModalOptionCard</c>
/// so <c>tools/lint_pool_membership.py</c> can see it.
/// </summary>
public sealed class KnightOptionAmber : ModalOptionCard
{
    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("proto_vk_amber_baron_bunny");

    public override List<(string, string)>? Localization =>
        KnightFace.For("Amber", Element.Pyro);
}

public sealed class KnightOptionBarbara : ModalOptionCard
{
    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("proto_vk_barbara_show_begin");

    public override List<(string, string)>? Localization =>
        KnightFace.For("Barbara", Element.Hydro);
}

public sealed class KnightOptionLisa : ModalOptionCard
{
    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("proto_vk_lisa_violet_arc");

    public override List<(string, string)>? Localization =>
        KnightFace.For("Lisa", Element.Electro);
}

public sealed class KnightOptionKaeya : ModalOptionCard
{
    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("proto_vk_kaeya_frostgnaw");

    public override List<(string, string)>? Localization =>
        KnightFace.For("Kaeya", Element.Cryo);
}

/// <summary>The four faces' one wording: the Knight's name and element.
/// </summary>
internal static class KnightFace
{
    internal static List<(string, string)> For(string name, Element element) =>
        new()
        {
            ("title", name),
            ("description", $"[gold]{element}[/gold]."),
        };
}
