#if PROTOTYPE_CARDS
using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Models.Relics;

namespace KleeMod.Relics;

/// <summary>
/// SALON SOLITAIRE -- the stage arm's starting relic (brief sec.3 rule 2).
///
/// "At the start of each combat the Gentilhomme Usher takes the front seat at
/// 3 Fanfare."
///
/// DEFECT'S FREE LIGHTNING ORB, AS A BODY, which is the brief's own analogy
/// and the reason the opening is a RELIC rather than an Innate card. The stage
/// is empty at the start of every fight because pets live one combat (rule 1),
/// and sec.6 names "a fight she enters with a thin deck of summons" as an
/// intended weakness -- an intended weakness, not an intended blank first
/// turn. R260 answered the same question one arm over and [USER] took the
/// relic over Innate there too: "one free Osty".
///
/// IT REPLACES THE ETHEREAL SPOTLIGHT, which is a replacement rather than an
/// addition: the Spotlight in both modes is retired by this brief (sec.2), so
/// a run carrying it would print a rule the arm has turned off. The swap is
/// <c>FurinaStageRoster.StartingRelics</c>'s, one seam, so an arm-off Furina
/// still opens with the Spotlight byte for byte.
///
/// USHER AND NOT A ROLL (sec.10 default 1, an E). Fixed for legibility: the
/// front seat is the one that absorbs, the one Spend pays from and the one
/// that regenerates, and a rolled opening decides all three for the player
/// before they have seen a card. Random is the alternative if fight one reads
/// as samey, and it is one word here.
///
/// THE WHOLE FILE IS QUARANTINED by <c>#if PROTOTYPE_CARDS</c> rather than by
/// living under <c>Powers/Prototype/</c>, for <c>TamakushiCasket</c>'s reason:
/// <c>tools/lint_unique_names.py</c> reads relic display names out of
/// <c>klee-mod/KleeCode/Relics/*.cs</c> and nowhere else, and R69 put relic
/// names in the same namespace as card names. A prototype relic hidden from
/// that lint could mint a name a shipped card already owns.
/// </summary>
public sealed class SalonSolitaire : CustomRelicModel
{
    public SalonSolitaire() : base(autoAdd: false)
    {
    }

    public override RelicRarity Rarity => RelicRarity.Starter;

    /// <summary>
    /// The opening number is INTERPOLATED from the constant it quotes
    /// (`EB-89`), so a retune of <see cref="FurinaStageLaw.OpeningFanfare"/>
    /// cannot leave the relic telling the player a retired 3.
    /// </summary>
    public override List<(string, string)>? Localization => new()
    {
        ("title", "Salon Solitaire"),
        ("description",
            "Start each combat with the [gold]Gentilhomme Usher[/gold] in the "
          + "front seat at [blue]" + FurinaStageLaw.OpeningFanfare
          + "[/blue] [gold]Fanfare[/gold]."),
    };

    /// <summary>
    /// The relic's sentence, made true by the relic.
    ///
    /// THE SITE IS <c>TamakushiCasket.BeforeCombatStart</c>'s: the pet is
    /// fielded before the first turn rather than on it, because the stage is
    /// what the first intent is posted against and a body that arrived after
    /// the intent would be a buffer the player could not have planned around.
    /// <c>FurinaStage.OpenCombat</c> is idempotent on a lit stage, so a
    /// future kit install that makes the same sentence true costs one list
    /// check.
    /// </summary>
    public override async Task BeforeCombatStart()
    {
        var furina = Owner?.Creature;
        if (!FurinaStage.LiveFor(furina)) return;
        await FurinaStage.OpenCombat(furina);
    }

    /// <summary>
    /// FALLBACK ICON, borrowed from the relic whose slot this takes. Art is
    /// commissioned when a slice is ACCEPTED, not before -- the rule the
    /// Casket and the overhaul power icons both follow.
    /// </summary>
    protected override string IconBaseName => "snake_ring";

    public override string PackedIconPath =>
        KleePck.Path("furina/relics/ethereal_spotlight.png")
        ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("furina/relics/ethereal_spotlight.png")
        ?? base.BigIconPath;
}
#endif
