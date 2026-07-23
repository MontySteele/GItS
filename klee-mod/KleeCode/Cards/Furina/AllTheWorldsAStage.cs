using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Furina;

/// <summary>
/// Furina's Ancient-rarity card: the Encore engine. Dusty Tome is its only
/// door -- reward, transform and shop generation all filter
/// CardRarity.Ancient upstream, so membership in RosterAncientCards.Furina
/// does not make it rollable. DustyTome.AfterObtained upgrades the grant, so
/// the card is designed to be read at its upgraded numbers.
///
/// User ruling 2026-07-23 (act-2 Darv softlock fix): "an Encore engine
/// effect ... scaled to the rest of the Ancient rewards". A steady Encore
/// drip is Furina's whole economy at once: it funds Salon ticks, absorbs
/// post-Block damage, and every point gained mints Fanfare. Hand-written and
/// outside the ratified sheets: the sim models neither events nor relics,
/// so Ancient cards are game-side-only content (DECISIONS entry 2026-07-23).
/// Title pending the naming/lore audit.
/// </summary>
public sealed class AllTheWorldsAStage : CustomCardModel, ICharacterCard
{
    public string CharacterId => "furina";

    // Art: deliberate reuse of The Sea Is My Stage's portrait until the art
    // pass assigns the ancient its own crop (look-pass item, not a blocker).
    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("the_sea_is_my_stage");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "All the World's a Stage"),
        ("description",
            "At the start of your turn, gain {PowerAmount:diff()} "
          + "[gold]Encore[/gold]."),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DynamicVar("PowerAmount", 5m)
        };

    // autoAdd: false -- RosterAncientCards.Furina owns membership (concat
    // into FurinaCardPool.GenerateAllCards).
    public AllTheWorldsAStage()
        : base(1, CardType.Power, CardRarity.Ancient, TargetType.Self, autoAdd: false)
    {
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<EncorePerTurnPower>(
            choiceContext, Owner.Creature, DynamicVars["PowerAmount"].IntValue,
            applier: Owner.Creature, cardSource: this);
    }

    protected override void OnUpgrade()
    {
        DynamicVars["PowerAmount"].UpgradeValueBy(2m);
    }
}
