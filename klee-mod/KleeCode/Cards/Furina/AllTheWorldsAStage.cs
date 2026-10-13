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
// Unqualified, so the witness's var regex reads its Block
// (tools/lint_handwritten_parity.extract_cs).
using static KleeMod.Powers.SpotlightSystem;

namespace KleeMod.Cards.Furina;

/// <summary>
/// Furina's Archaic Tooth Ancient (the Ancient audit,
/// review/ruled/ancient-audit-2026-10-12.md, ruled 2026-10-12: "All the
/// World's a Stage likewise needs a bump - "Gain 8 [11] Block. Spend all your
/// Fanfare and deal that much Hydro damage to ALL enemies twice.""): Orobas's
/// Archaic Tooth turns her starter Rising Applause into it, as it turns Bash
/// into Break. Rising Applause's spend-all, bigger: each of the two hits to
/// ALL enemies deals the amount spent (<see cref="FurinaStage.SpentOrFanfare"/>,
/// the same read and the same <see cref="FurinaStage.SpendAll"/>), so
/// Center of Attention's free Spend never covers it either.
///
/// Its Power face ("At the start of your turn, gain 2 Fanfare.") and that
/// face's per-turn power went with the ruling.
///
/// THE DOOR: <c>ProtoFsStandingOvation</c> (Rising Applause) implements
/// BaseLib's <c>ITranscendenceCard</c> and names this card
/// (<c>gen_klee_cards.TRANSCENDENCE</c>, Dandelion Gale's pattern). The
/// vanilla Dusty Tome skips every Tooth card, so her Tome draws
/// <see cref="CenterOfAttention"/>. It is in <c>RosterAncientCards.Furina</c>
/// so its <c>CardModel.Pool</c> resolves to hers; reward, transform and shop
/// generation filter Ancient upstream. Numbers witnessed by
/// <c>tools/lint_handwritten_parity.ANCIENT_WITNESS</c>; sim twin the
/// <c>all_the_worlds_a_stage</c> row in
/// <c>tier0/content/cards/ancients.yaml</c>.
///
/// Art: The Sea Is My Stage's portrait, as before (the ruling: the new card
/// may keep its current art).
/// </summary>
public sealed class AllTheWorldsAStage
    : CustomCardModel, IElementalCard, ICharacterCard, IStageSpendCard
{
    public Element Element => Element.Hydro;

    public string CharacterId => "furina";

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { KleeKeywords.AppliesHydro };

    // Rising Applause's tips.
    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForFanfare(
            ArmKeywordTips.ForSpend(
                ArmKeywordTips.ForBankDamage(
                    KleeCardTooltips.ForCard(
                        base.ExtraHoverTips, this, Element.Hydro),
                    this),
                this),
            this);

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("the_sea_is_my_stage");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "All the World's a Stage"),
        ("description",
            "Gain {Block:diff()} [gold]Block[/gold]. [gold]Spend[/gold] all "
          + "your [gold]Fanfare[/gold] and deal that much [gold]Hydro[/gold] "
          + "damage to ALL enemies twice."
          + "{InCombat:\n(Deals {CalculatedDamage:diff()} damage)|}"),
    };

    // Rising Applause's vars: the Block, and the hit read off the spend.
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new SpotlitBlockVar(8m),
            new CalculationBaseVar(0m),
            new ExtraDamageVar(1m),
            new FrontFoldedDamageVar(ValueProp.Move).WithMultiplier(
                static (card, _) => FurinaStage.SpentOrFanfare(card)),
        };

    // autoAdd: false -- RosterAncientCards.Furina owns membership (concat
    // into FurinaCardPool.GenerateAllCards).
    public AllTheWorldsAStage()
        : base(1, CardType.Skill, CardRarity.Ancient, TargetType.AllEnemies,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block, cardPlay);
        await FurinaStage.SpendAll(choiceContext, Owner.Creature);
        await DamageCmd.Attack(DynamicVars.CalculatedDamage)
            .WithHitCount(2)
            .FromCard(this, cardPlay)
            .TargetingAllOpponents(CombatState!)
            .WithElementHitFx(this)
            .SpawningHitVfxOnEachCreature()
            .Execute(choiceContext);
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Block.UpgradeValueBy(3m);
    }
}
