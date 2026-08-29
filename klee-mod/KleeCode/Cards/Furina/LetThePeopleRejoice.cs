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

namespace KleeMod.Cards.Furina;

/// <summary>
/// Furina's 70-energy kit Burst. It is granted to hand at a full meter,
/// Retained until cast, and never enters draft or transform pools.
/// </summary>
public sealed class LetThePeopleRejoice
    : CustomCardModel, IElementalCard, ICharacterCard
{
    public Element Element => Element.Hydro;

    public string CharacterId => "furina";

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("let_the_people_rejoice");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Let the People Rejoice"),
        // EB-164: the scaling is stated ONCE, inside the number's own
        // sentence, by the generator's rule (1). As a following sentence
        // asserting the Fanfare rider a second time, it read as a further
        // addition on top of a number that already carried that rider.
        ("description",
            "Costs your full [gold]Burst Energy[/gold] meter. "
          + "Deal {CalculatedDamage:diff()} damage to ALL enemies, already "
          + "including [gold]Fanfare[/gold]. Gain 6 [gold]Encore[/gold]."),
    };

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { CardKeyword.Retain, KleeKeywords.AppliesHydro };

    // Track L-C: the rider's arithmetic lives in the hover tip now that the
    // printed number carries it. Same treatment the generator gives its own
    // fanfare riders; hand-written card, so it is wired by hand.
    //
    // The Burst keyword rides the same wire, on the rule codegen applies to
    // the generated faces: this face PRINTS the word ("Costs your full Burst
    // Energy meter"), so it carries the definition. It is also the face that
    // most needs it -- her whole meter is spent here.
    // `tools/lint_keyword_meters.py` holds the two surfaces to one rule.
    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        KleeCardTooltips.ForBurst(
            FurinaRiderTips.ForCard(
                base.ExtraHoverTips, this, fanfarePer: 1, fanfareStep: 4),
            this);

    // Fanfare rider rendered through CalculatedDamageVar (Legibility sprint,
    // 2026-07-24) so the face/hover and the resolved hit share one value path:
    // base 8 + 1*(Fanfare/4). Mirrors the generator's fanfare_calc_rider output;
    // hand-written card, so it is converted by hand.
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[]
        {
            new CalculationBaseVar(8m),
            new ExtraDamageVar(1m),
            new CalculatedDamageVar(ValueProp.Move).WithMultiplier(
                static (card, _) => FurinaResources.ReadableFanfare(card.Owner.Creature) / 4),
        };

    // Energy cost 0 (user ruling 2026-07-23, matching Klee's Sparks 'n'
    // Splash): the charged Burst meter IS the cost -- it empties on cast.
    public LetThePeopleRejoice()
        : base(0, CardType.Attack, CardRarity.Rare,
            TargetType.AllEnemies, autoAdd: false)
    {
        CustomResources<FurinaBurstResource>.SetCanonicalCost(
            this, FurinaResourceConstants.BurstMax);
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.CalculatedDamage)
            .FromCard(this, cardPlay)
            .TargetingAllOpponents(CombatState!)
            .WithHitFx("vfx/vfx_attack_slash")
            .SpawningHitVfxOnEachCreature()
            .Execute(choiceContext);
        FurinaResources.GainEncore(Owner.Creature, 6);
    }

    /// <summary>
    /// "Returns to the kit, no pile" -- tier0 combat.py play_card:
    ///
    ///     if card.kit_card:
    ///         pass                  # returns to the kit, no pile
    ///
    /// That branch is unconditional on card TYPE, and this card is an Attack,
    /// so the default result pile is Discard. Left at the default the cast
    /// copy recirculated: it reshuffled into the draw pile, and because
    /// FurinaKitGrant only dedups against the HAND it granted a fresh copy at
    /// the next full meter regardless -- so every cast permanently added a
    /// Burst to the deck. Klee's kit card never showed this because a played
    /// Power already leaves combat (PileType.None); Furina's card type is the
    /// only reason the divergence was reachable.
    ///
    /// PORTED at v0.111.0 (`EB-171`): the game replaced
    /// `GetResultPileTypeForCardPlay` with `GetResultLocationForCardPlay`,
    /// which returns a `CardLocation` of player / pile / position instead of a
    /// bare pile. The behaviour is unchanged -- `CardModel.Play` still
    /// switches on `resultLocation.pileType` and routes `PileType.None` to
    /// `CardPileCmd.RemoveFromCombat`, and `Owner` / `CardPilePosition.Bottom`
    /// are what the base implementation itself passes on its own
    /// dupe-or-Power branch.
    /// </summary>
    protected override CardLocation GetResultLocationForCardPlay() =>
        new CardLocation(Owner, PileType.None, CardPilePosition.Bottom);

    protected override void OnUpgrade()
    {
        // Kit cards are not smithable.
    }
}
