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
/// Varka's Archaic Tooth Ancient (the Varka review,
/// review/active/varka-review-2026-10-12.md sec.6, ruled 2026-10-12:
/// "Dandelion Gale could be the Replace version"): Orobas's Archaic Tooth
/// turns his starter Windbound Execution into it, as it turns Bash into Break.
/// "Deal 7 [10] Anemo damage to ALL enemies. Swirl every aura. These Swirls
/// pay twice." Cost 1, "like a starter-slot card should". The big Swirl turn
/// the Anemo half builds toward.
///
/// The Anemo hit Swirls each enemy's aura it lands on, inside Crosscurrent's
/// pays-twice window (<see cref="VarkaOathLedger.PaysTwice"/>), so every
/// Swirl this play makes pays his current element twice.
///
/// THE DOOR: Windbound Execution's generated class implements BaseLib's
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
        new[] { KleeKeywords.AppliesAnemo };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForSwirl(
            KleeCardTooltips.ForCard(base.ExtraHoverTips, this, Element.Anemo),
            this);

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("dandelion_gale");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Dandelion Gale"),
        ("description",
            "Deal {Damage:diff()} [gold]Anemo[/gold] damage to ALL enemies. "
          + "[gold]Swirl[/gold] every aura. These [gold]Swirls[/gold] pay "
          + "twice."),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DamageVar(7m, ValueProp.Move),
        };

    // autoAdd: false -- RosterAncientCards.Varka owns membership.
    public DandelionGale()
        : base(1, CardType.Attack, CardRarity.Ancient, TargetType.AllEnemies,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var owner = Owner.Creature;
        var ledger = VarkaOath.Live(owner) ? VarkaOathLedger.For(owner) : null;
        if (ledger != null) ledger.PaysTwice++;
        try
        {
            await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
                .FromCard(this, cardPlay)
                .TargetingAllOpponents(CombatState!)
                .WithElementHitFx(this)
                .SpawningHitVfxOnEachCreature()
                .Execute(choiceContext);
        }
        finally
        {
            if (ledger != null) ledger.PaysTwice--;
        }
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(3m);
    }
}
