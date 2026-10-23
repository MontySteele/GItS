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

namespace KleeMod.Cards.Varka;

/// <summary>
/// Varka's Archaic Tooth Ancient: Four Winds' Ascension made bigger.
/// Orobas's Archaic Tooth turns his starter Four Winds' Ascension into it, as
/// it turns Bash into Break.
///
/// THE REDESIGN (2026-10-13, [USER]: "Archaic Tooth - let's have the upgrade
/// make it AoE and also reduce the cost to 1 when upgraded. That should make
/// it Ancient-worthy for sure, equivalent to Necrobinder's Osty attack
/// getting both a better effect and a better energy rate after upgrading";
/// then "Not exactly. I meant that the ancient starts at 2, and upgrading it
/// at a campfire (or replacing an already-upgraded Ascension) takes it to
/// 1."): cost 2 [1], Retain, "Deal 10 Anemo damage to ALL enemies. Then deal
/// 3 damage per Oath of your current element to each, as that element." The
/// Ascension's numbers on every enemy; the upgrade is the Ascension's, the
/// cost. An upgraded Ascension becomes an upgraded Gale: the vanilla Tooth's
/// <c>GetTranscendenceTransformedCard</c> upgrades the made card when the
/// starter card was upgraded (sts2.dll, read by decompile 2026-10-13), as it
/// does for Jumpy Dumpty Mk. Omega.
///
/// The second hit is <see cref="VarkaCards.GaleHit"/>: the Ascension's, on
/// ALL enemies, read after the Anemo hit and crediting no Oath. The face's
/// live total is the Ascension's <see cref="VarkaCurrentElementHitVar"/>.
/// (Was, 2026-10-12: cost 1, "Deal 7 [10] Anemo damage to ALL enemies. Swirl
/// every aura. These Swirls pay twice.", off Windbound Execution.)
///
/// THE DOOR: Four Winds' Ascension's generated class implements BaseLib's
/// <c>ITranscendenceCard</c> and names this card
/// (<c>gen_klee_cards.TRANSCENDENCE</c>); BaseLib's postfix adds the pair to
/// <c>ArchaicTooth.TranscendenceUpgrades</c>, which also keeps the vanilla
/// Dusty Tome off it. It is in <c>RosterAncientCards.Varka</c> so its
/// <c>CardModel.Pool</c> resolves to his. Game-side only, like every kit's
/// second Ancient; numbers witnessed by
/// <c>tools/lint_handwritten_parity.ANCIENT_WITNESS</c>.
/// </summary>
public sealed class DandelionGale : CustomCardModel, IElementalCard, ICharacterCard
{
    public Element Element => Element.Anemo;

    public string CharacterId => "varka";

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { CardKeyword.Retain, KleeKeywords.AppliesAnemo };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForCurrentElement(
            ArmKeywordTips.ForOath(
                ArmKeywordTips.ForAscensionNoOath(
                    KleeCardTooltips.ForCard(base.ExtraHoverTips, this, Element.Anemo),
                    this),
                this),
            this);

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("dandelion_gale");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Dandelion Gale"),
        ("description",
            "Deal {Damage:diff()} [gold]Anemo[/gold] damage to ALL enemies. "
          + "Then deal {VkPer:diff()} damage for each [gold]Oath[/gold] of your "
          + "[gold]current element[/gold] to each, as that element."
          + "{InCombat:\n(Deals {VkHit:diff()} damage)|}"),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DamageVar(10m, ValueProp.Move),
            new DynamicVar("VkPer", 3m),
            new VarkaCurrentElementHitVar(),
        };

    // autoAdd: false -- RosterAncientCards.Varka owns membership.
    public DandelionGale()
        : base(2, CardType.Attack, CardRarity.Ancient, TargetType.AllEnemies,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
            .FromCard(this, cardPlay)
            .TargetingAllOpponents(CombatState!)
            .WithElementHitFx(this)
            .SpawningHitVfxOnEachCreature()
            .Execute(choiceContext);
        await VarkaCards.GaleHit(choiceContext, this, cardPlay);
    }

    protected override void OnUpgrade()
    {
        EnergyCost.UpgradeBy(-1);
    }
}
