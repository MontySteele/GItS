using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards.Kokomi;

/// <summary>
/// Kokomi's Archaic Tooth Ancient (the Ancient audit,
/// review/ruled/ancient-audit-2026-10-12.md, ruled 2026-10-12: "Princess of
/// Watatsumi needs to do more as an Ancient. Perhaps "Gain 9 [12] Block. Draw
/// 2 cards. Or plan: Deal 3 [5] Hydro damage to ALL enemies five times.""):
/// Orobas's Archaic Tooth turns her starter Kurage's Oath into it, as it
/// turns Bash into Break. A bigger Oath, built the way Kurage's Oath is: a
/// two-line Plan card whose now-line is the Block and the draw, and whose Plan
/// line the Bake-Kurage carries out at the start of her next turn.
///
/// Its Power face ("Whenever the Bake-Kurage carries out a Plan, gain 2 Block
/// and draw 1 card.") and that face's plan-bus listener went with the ruling;
/// it overlapped the pool's Kurage Canopy.
///
/// THE DOOR: <c>ProtoKkKuragesOath</c> implements BaseLib's
/// <c>ITranscendenceCard</c> and names this card
/// (<c>gen_klee_cards.TRANSCENDENCE</c>, Dandelion Gale's pattern). The
/// vanilla Dusty Tome skips every Tooth card, so her Tome draws
/// <see cref="DivineStrategy"/>. It is in <c>RosterAncientCards.Kokomi</c> so
/// its <c>CardModel.Pool</c> resolves to hers; reward, transform and shop
/// generation filter Ancient upstream. Numbers witnessed by
/// <c>tools/lint_handwritten_parity.ANCIENT_WITNESS</c>; sim twin the
/// <c>princess_of_watatsumi</c> row in <c>tier0/content/cards/ancients.yaml</c>.
///
/// NAME: "Princess of Watatsumi" is her canon innate passive. Art: the
/// placeholder it had (the ruling: the new card may keep its current art).
/// </summary>
public sealed class PrincessOfWatatsumi
    : CustomCardModel, ICharacterCard, IPlannedCard, INowLineCard
{
    public string CharacterId => "kokomi";

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("prayer_to_the_moon");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Princess of Watatsumi"),
        ("description",
            "Gain {Block:diff()} [gold]Block[/gold]. Draw 2 cards.\n"
          + "Or [gold]plan[/gold]: Deal {PlanDamage:diff()} [gold]Hydro[/gold] "
          + "damage to ALL enemies 5 times."),
    };

    // Kurage's Oath's tips: the Plan word and the Plan line's element.
    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForPlan(
            ArmKeywordTips.ForPlanElement(base.ExtraHoverTips, this), this);

    /// <summary>The card's printed Plan line: 3 [5] Hydro to ALL enemies,
    /// five times. Carried out by the Bake-Kurage at the start of her next
    /// turn (<see cref="KokomiPlan.ResolveAll"/>).</summary>
    public IReadOnlyList<KokomiPlan.Planned> PlanClauses =>
        new[]
        {
            new KokomiPlan.Planned(
                KokomiPlan.Kind.Damage, DynamicVars["PlanDamage"].IntValue,
                KokomiPlan.Aim.AllEnemies, Times: 5),
        };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new BlockVar(9m, ValueProp.Move),
            new CardsVar(2),
            new KokomiPlan.PlanDamageVar(3m),
        };

    // autoAdd: false -- RosterAncientCards.Kokomi owns membership, concatted
    // into KokomiCardPool.GenerateAllCards.
    public PrincessOfWatatsumi()
        : base(1, CardType.Skill, CardRarity.Ancient, KokomiTargets.PetOrSelf,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (KokomiPlan.PlayedOnPet(cardPlay))
        {
            await KokomiPlan.Schedule(
                choiceContext, Owner.Creature, this, PlanClauses);
            if (DivineStrategyPower.NowLine(
                    cardPlay, Owner.Creature, DivineStrategyPower.Aim.None)
                is not { } nowLine) return;
            cardPlay = nowLine;
        }
        await PlayNowLine(choiceContext, cardPlay);
    }

    /// <summary>Where the now-line aims when the Bake-Kurage carries it out
    /// for a Plan: nowhere, it is her own Block and draw.</summary>
    public DivineStrategyPower.Aim NowLineAim => DivineStrategyPower.Aim.None;

    /// <summary>The now-line: "Gain 9 [12] Block. Draw 2 cards."</summary>
    public async Task PlayNowLine(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block, cardPlay);
        await CardPileCmd.Draw(choiceContext, DynamicVars.Cards.BaseValue, Owner);
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Block.UpgradeValueBy(3m);
        DynamicVars["PlanDamage"].UpgradeValueBy(2m);
    }
}
