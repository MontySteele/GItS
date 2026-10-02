using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Runs;

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

    /// <summary>Touch of Orobas: The Curtain Never Falls, rebuilt for the
    /// Stage (the relics-and-potions paper, 2026-09-27) -- the Ethereal
    /// Spotlight's upgrade, now this starter's.</summary>
    public override RelicModel? GetUpgradeReplacement() =>
        ModelDb.Relic<CurtainNeverFalls>().ToMutable();

    /// <summary>
    /// The opening number is INTERPOLATED from the constant it quotes
    /// (`EB-89`), so a retune of <see cref="FurinaStageLaw.OpeningFanfare"/>
    /// cannot leave the relic telling the player a retired 3.
    /// </summary>
    public override List<(string, string)>? Localization => new()
    {
        ("title", "Salon Solitaire"),
        ("description",
            "Start each combat with Usher in front with [blue]"
          + FurinaStageLaw.OpeningFanfare + "[/blue] [gold]Fanfare[/gold]."),
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

    /// <summary>Whether this relic adds the companion slot to the reward
    /// being built for <paramref name="player"/>: only its own owner's,
    /// once (see <see cref="CompanionSlot.OffersTo"/>).</summary>
    public bool OffersCompanionTo(Player player, CardCreationOptions creationOptions) =>
        CompanionSlot.OffersTo(this, player, creationOptions, player.Character is Furina);

    /// <summary>
    /// Furina's companion reward slot, carried over from the Ethereal
    /// Spotlight this relic replaces. The starter relic is where every roster
    /// character's fourth reward choice lives, and the Stage kept companions
    /// ("Companion cards stay the shared action pool", brief sec.2). The slot
    /// was left off when the relic was written, so a Stage Furina drafted no
    /// companions at all; [USER]'s co-op run caught it (2026-09-27).
    /// </summary>
    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (!OffersCompanionTo(player, creationOptions)) return false;
        var rarity = creationOptions.RarityOdds == CardRarityOddsType.BossEncounter
            ? CardRarity.Rare
            : (CardRarity?)null;
        var offer = CompanionSlot.Roll(player, rarity);
        if (offer == null) return false;
        cardRewardOptions.Add(new CardCreationResult(offer));
        return true;
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
