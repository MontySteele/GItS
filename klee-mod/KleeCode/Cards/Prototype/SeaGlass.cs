using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Prototype;

/// <summary>
/// SEA GLASS -- Sea Glass Harvest's token (the status batch, 2026-10-01,
/// review/active/kokomi-status-batch-2026-10-01.md sec.2): 0, "Gain 1 [2]
/// Energy. Exhaust." Defect's Fuel with the draw the base game nerfed off it
/// left off ("this batch keeps Energy and draw on separate cards").
///
/// A TOKEN, HAND-WRITTEN, IN NO POOL, Open the Casket's shape: only Sea Glass
/// Harvest's Plan makes one, by transforming a status or curse in hand
/// (<see cref="Powers.KokomiStatusBatch.TransformStatuses"/>); Sea Glass+ is
/// this card upgraded. In <c>KokomiOffPoolCards</c> so <c>CardModel.Pool</c>
/// resolves. Sim twin: <c>kokomi_plan.sea_glass_card</c>. Art: placeholder.
/// </summary>
public sealed class SeaGlass : CustomCardModel, ICharacterCard
{
    public string CharacterId => "kokomi";

    /// <summary>The art key. No painting yet.</summary>
    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("kk_sea_glass");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Sea Glass"),
        ("description",
            "Gain {IfUpgraded:show:2|1} [gold]Energy[/gold]."),
    };

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { CardKeyword.Exhaust };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        System.Array.Empty<DynamicVar>();

    public SeaGlass()
        : base(0, CardType.Skill, CardRarity.Token, TargetType.Self,
               autoAdd: false)
    {
    }

    /// <summary>The Energy it gives: 1, or 2 upgraded.</summary>
    public static int EnergyFor(bool upgraded) => upgraded ? 2 : 1;

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PlayerCmd.GainEnergy(EnergyFor(IsUpgraded), Owner);
    }

    protected override void OnUpgrade()
    {
    }
}
