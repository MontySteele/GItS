using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Yae;

/// <summary>
/// Yae's Archaic Tooth Ancient (the Yae pass, 2026-10-16,
/// <c>review/active/yae-ancients-relics-2026-10-16.md</c> sec.2; her
/// Elemental Skill's full name): Orobas's Archaic Tooth turns her starter
/// Yakan Evocation into it, as it turns Bash into Break. Skill, 1 Energy, 0
/// upgraded: "Plant a Foxfire Sakura at Level 3. Edit it: Deadline
/// Extension." A totem that hits ALL enemies for 4 at every turn end and
/// never withers, built only from parts she already has
/// (<see cref="YaeCards.SesshouSakura"/>). A second play is a plant of its
/// kind: into a full shrine whose next to wither is a Foxfire Sakura it Levels that
/// one, else the new one stands beside it.
///
/// THE DOOR: Yakan Evocation's generated class implements BaseLib's
/// <c>ITranscendenceCard</c> and names this card
/// (<c>gen_klee_cards.TRANSCENDENCE</c>). The vanilla Tooth's
/// <c>GetTranscendenceTransformedCard</c> (0.111.0, read by decompile
/// 2026-10-16) upgrades the made card when the starter was upgraded and
/// enchants it with a <c>MutableClone</c> of the starter's enchantment, so a
/// Yakan Evocation's Masterpiece (its Published Annotations) rides across
/// ([USER], 2026-10-16: "let's make it so that any existing annotations on
/// the starter card carry over to the Ancient version";
/// <c>YaeAncientsRelicsTests</c> pins it). The vanilla Dusty Tome skips
/// every Tooth card, so her Tome draws <see cref="YaePublishingHouse"/>. In
/// <c>RosterAncientCards.Yae</c> so its <c>CardModel.Pool</c> resolves to
/// hers. Game-side only, as Varka's two are; numbers witnessed by
/// <c>tools/lint_handwritten_parity.ANCIENT_WITNESS</c>.
/// </summary>
public sealed class YakanEvocationSesshouSakura
    : CustomCardModel, ICharacterCard, ISakuraPlanterCard, ISakuraPlantShapeCard
{
    public string CharacterId => YaePrototype.CharacterId;

    /// <summary>One Foxfire Sakura at a Level (the Sakura display's preview).</summary>
    public YaePlantShape SakuraPlantShape => YaePlantShape.PlantLevel;

    public YaeSakuraKind SakuraPlantKind => YaeSakuraKind.Foxfire;

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("yakan_evocation_sesshou_sakura");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Yakan Evocation: Sesshou Sakura"),
        ("description",
            "Plant a [gold]Foxfire Sakura[/gold] at Level {YmAmount:diff()}. "
          + "[gold]Edit[/gold] it: [gold]Deadline Extension[/gold]."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForEdit(
            ArmKeywordTips.ForAnnotation(
                ArmKeywordTips.ForFullShrine(
                    ArmKeywordTips.ForFoxfireSakura(base.ExtraHoverTips, this), this),
                this, YaeAnnotation.DeadlineExtension, true),
            this);

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DynamicVar("YmAmount", 3m),
        };

    // autoAdd: false -- RosterAncientCards.Yae owns membership.
    public YakanEvocationSesshouSakura()
        : base(1, CardType.Skill, CardRarity.Ancient, TargetType.Self,
               autoAdd: false)
    {
    }

    protected override Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay) =>
        YaeCards.SesshouSakura(choiceContext, this, cardPlay);

    protected override void OnUpgrade()
    {
        EnergyCost.UpgradeBy(-1);
    }
}
